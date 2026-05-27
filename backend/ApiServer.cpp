
#define WIN32_LEAN_AND_MEAN // makes compilation faster in windows
#define NOMINMAX            // Prevents Windows from defining min and max macros which conflict with C++ std::min and std::max
#include "ApiServer.h"      //APIServer.h contains initialization and declaration of API Server
#include "Database.h"
#include "MoodTracker.h"
#include "JournalManager.h"
#include "libs/json/json.hpp" // JSON library used to parse and create JSON data for API communication
#include <fstream>            // Used for file reading and writing operations
#include <cctype>             // Provides functions for character operations like checking spaces
#include <iostream>
#include <stdexcept> // Provides standard exception classes for error handling
#include <string>
#include <winsock2.h>        // Windows socket library used for network communication
#include <ws2tcpip.h>        // Provides additional TCP/IP networking utilities for Windows sockets
using json = nlohmann::json; // Creates a shorter alias 'json' for the nlohmann JSON library bcoz when workign with web, we need this library nlohmann::json
using namespace std;
#pragma comment(lib, "ws2_32.lib") // Links the Windows socket library required for network communication - without this, the networking functions won't work

// Global objects used by the API server to interact with database, mood tracking, and journal management
Database db;
MoodTracker mood(db);
JournalManager journal(db);

// Removes leading and trailing spaces from a string
static string trim(const string &s)
{
    size_t start = 0;
    while (start < s.size() && isspace(static_cast<unsigned char>(s[start])))
    {
        start++;
    }
    size_t end = s.size();
    while (end > start && isspace(static_cast<unsigned char>(s[end - 1])))
    {
        end--;
    }
    return s.substr(start, end - start);
}

// Extracts the body part of an HTTP request after the headers
static string extractBody(const string &req)
{
    size_t headerEnd = req.find("\r\n\r\n");
    if (headerEnd == string::npos)
    {
        return "";
    }
    string body = req.substr(headerEnd + 4);
    while (!body.empty() && (body.back() == '\n' || body.back() == '\r' || body.back() == ' '))
    {
        body.pop_back();
    }
    return body;
}

// Sends a full HTTP response to the client including headers and JSON body
static void sendHttp(SOCKET client, int statusCode, const string &statusText, const string &body)
{
    string response =
        "HTTP/1.1 " + to_string(statusCode) + " " + statusText + "\r\n""Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n""Access-Control-Allow-Headers: Content-Type\r\n"
        "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n""Connection: close\r\n"
        "Content-Length: " + to_string(body.size()) + "\r\n\r\n" + body;
    send(client, response.c_str(), static_cast<int>(response.size()), 0);
}

// Sends a successful HTTP 200 response with JSON body
static void sendResponse(SOCKET client, const string &body)
{
    sendHttp(client, 200, "OK", body);
}

// Sends an HTTP error response like 400, 404, or 500
static void sendError(SOCKET client, int code, const string &body)
{
    if (code == 404)
    {
        sendHttp(client, 404, "Not Found", body);
        return;
    }
    if (code == 500)
    {
        sendHttp(client, 500, "Internal Server Error", body);
        return;
    }
    sendHttp(client, 400, "Bad Request", body);
}

// Handles CORS preflight OPTIONS request for browsers
static void sendOptions(SOCKET client)
{
    string response = "HTTP/1.1 204 No Content\r\n""Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Headers: Content-Type\r\n""Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
        "Connection: close\r\n\r\n";
    send(client, response.c_str(), static_cast<int>(response.size()), 0);
}

// Starts the API server, initializes Winsock, listens for client requests, and handles all API routes
void ApiServer::start(int port)
{
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        cerr << "[API] WSAStartup failed." << endl;
        return;
    }
    SOCKET server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == INVALID_SOCKET)
    {
        cerr << "[API] socket() failed: " << WSAGetLastError() << endl;
        WSACleanup();
        return;
    }
    BOOL reuseAddr = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR,
               reinterpret_cast<const char *>(&reuseAddr), sizeof(reuseAddr));
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(port);
    if (::bind(server_fd, reinterpret_cast<sockaddr *>(&serverAddr), sizeof(serverAddr)) == SOCKET_ERROR)
    {
        cerr << "[API] bind() failed on port " << port << ": " << WSAGetLastError() << endl;
        closesocket(server_fd);
        WSACleanup();
        return;
    }
    if (::listen(server_fd, SOMAXCONN) == SOCKET_ERROR)
    {
        cerr << "[API] listen() failed: " << WSAGetLastError() << endl;
        closesocket(server_fd);
        WSACleanup();
        return;
    }
    cout << "[API] Backend running at http://127.0.0.1:" << port << endl;
    while (true)
    {
        SOCKET client = ::accept(server_fd, nullptr, nullptr);
        if (client == INVALID_SOCKET)
        {
            cerr << "[API] accept() failed: " << WSAGetLastError() << endl;
            continue;
        }
        char buffer[4096];
        int bytes = recv(client, buffer, sizeof(buffer), 0);
        if (bytes <= 0)
        {
            closesocket(client);
            continue;
        }
        string req(buffer, bytes);
        size_t lengthPos = req.find("Content-Length:");
        if (lengthPos != string::npos)
        {
            size_t lineEnd = req.find("\r\n", lengthPos);
            string lenStr = req.substr(lengthPos + 15, lineEnd - (lengthPos + 15));
            int bodyLen = 0;
            try
            {
                bodyLen = stoi(trim(lenStr));
            }
            catch (const exception &)
            {
                sendError(client, 400, "{\"error\":\"invalid content-length\"}");
                closesocket(client);
                continue;
            }
            if (bodyLen < 0)
            {
                sendError(client, 400, "{\"error\":\"invalid content-length\"}");
                closesocket(client);
                continue;
            }
            size_t bodyStart = req.find("\r\n\r\n");
            if (bodyStart != string::npos)
            {
                size_t alreadyHave = req.size() - (bodyStart + 4);
                while (alreadyHave < static_cast<size_t>(bodyLen))
                {
                    bytes = recv(client, buffer, sizeof(buffer), 0);
                    if (bytes <= 0)
                    {
                        break;
                    }
                    req.append(buffer, bytes);
                    alreadyHave += bytes;
                }
            }
        }
        if (req.rfind("OPTIONS", 0) == 0)
        {
            sendOptions(client);
            closesocket(client);
            continue;
        }
        try
        {
            if (req.find("POST /login") != string::npos)
            {
                string body = extractBody(req);
                if (body.empty())
                {
                    sendResponse(client, "{\"success\":false}");
                    closesocket(client);
                    continue;
                }
                json j = json::parse(body);
                string pin = j.value("pin", "");
                bool ok = !pin.empty() && db.checkPIN(pin);
                sendResponse(client, ok ? "{\"success\":true}" : "{\"success\":false}");
            }
            else if (req.find("POST /register") != string::npos)
            {
                string body = extractBody(req);
                if (body.empty())
                {
                    sendResponse(client, "{\"success\":false}");
                    closesocket(client);
                    continue;
                }

                json j = json::parse(body);
                string pin = j.value("pin", "");
                bool ok = !pin.empty() && db.setPIN(pin);
                sendResponse(client, ok ? "{\"success\":true}" : "{\"success\":false}");
            }
            else if (req.find("POST /mood/add") != string::npos)
            {
                string body = extractBody(req);
                mood.addMood(body);
                sendResponse(client, "{\"message\":\"Mood saved\"}");
            }
            else if (req.find("GET /mood/all") != string::npos)
            {
                sendResponse(client, mood.getAllMoods());
            }
            else if (req.find("POST /journal/add") != string::npos)
            {
                string body = extractBody(req);
                journal.addEntry(body);
                sendResponse(client, "{\"message\":\"Journal saved\"}");
            }
            else if (req.find("GET /journal/all") != string::npos)
            {
                sendResponse(client, journal.getAll());
            }
            else if (req.find("GET /journal/count") != string::npos)
            {
                sendResponse(client, journal.getCountJSON());
            }
            else if (req.find("GET /stats/averageMood") != string::npos)
            {
                sendResponse(client, mood.getAverageMoodPercent());
            }
            else if (req.find("GET /eq/resources") != string::npos)
{
    sendResponse(client, mood.getEQResources());
}
            else if (req.find("GET /stats/frequentMood") != string::npos)
            {
                sendResponse(client, mood.getFrequentMood());
            }
            else if (req.find("GET /stats/latestMood") != string::npos)
            {
                sendResponse(client, mood.getLatestMood());
            }
            else if (req.find("GET /stats/weeklyMood") != string::npos)
            {
                sendResponse(client, mood.getWeeklyStats());
            }
            else if (req.find("GET /suggestion/today") != string::npos)
            {
                sendResponse(client, mood.getSuggestion());
            }
            else if (req.find("GET /auth/question") != string::npos)
            {
                sendResponse(client, db.getSecurityQuestion());
            }
            else if (req.find("POST /auth/verify") != string::npos)
            {
                string body = extractBody(req);
                json j = json::parse(body);
                string answer = j.value("answer", "");
                bool ok = !answer.empty() && db.verifySecurityAnswer(answer);
                sendResponse(client, ok ? "{\"verified\":true}" : "{\"verified\":false}");
            }
            else if (req.find("GET /stats/crisis") != string::npos)
            {
                sendResponse(client, mood.checkCrisisStatus());
            }
            else if (req.find("POST /mood/reset") != string::npos)
            {
                sqlite3_exec(db.getHandle(), "DELETE FROM moods", nullptr, nullptr, nullptr);
                sendResponse(client, "{\"success\":true}");
            }
            else if (req.find("POST /journal/reset") != string::npos)
            {
                sqlite3_exec(db.getHandle(), "DELETE FROM journals", nullptr, nullptr, nullptr);
                sendResponse(client, "{\"success\":true}");
            }
            else if (req.find("GET /emergency/contact") != string::npos)
            {
                sendResponse(client, db.getEmergencyContact());
            }
            else if (req.find("POST /auth/reset") != string::npos)
            {
                string body = extractBody(req);
                json j = json::parse(body);
                string newPin = j.value("newPin", "");
                bool ok = !newPin.empty() && db.setPIN(newPin);
                sendResponse(client, ok ? "{\"success\":true}" : "{\"success\":false}");
            }
            else if (req.find("GET /health") != string::npos)
            {
                sendResponse(client, "{\"status\":\"ok\"}");
            }
            else
            {
                sendError(client, 404, "{\"status\":\"unknown route\"}");
            }
        }
        catch (const exception &e)
        {
            cerr << "[API] Request handling exception: " << e.what() << endl;
            sendError(client, 500, "{\"error\":\"request failed\"}");
        }
        closesocket(client);
    }
    closesocket(server_fd);
    WSACleanup();
    //close everything every route, every socket
}