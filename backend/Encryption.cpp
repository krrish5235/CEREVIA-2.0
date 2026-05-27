#include "Encryption.h"
#include <sstream>      // Used for converting data into string streams
#include <iomanip>      // Used for formatting hex output
using namespace std;

// Performs XOR encryption/decryption on the given data using the provided key.
// XOR operation is reversible, so the same function works for both encryption and decryption.
static string xorData(const string &data, const string &key) {
    if (key.empty()) return data;
    string out = data;
    for (size_t i = 0; i < data.size(); ++i) {
        out[i] = data[i] ^ key[i % key.size()];
    }
    return out;
}

// Converts binary encrypted data into hexadecimal format.
// This makes the encrypted data safe to store in text-based storage like databases.
static string toHex(const string &data) {
    ostringstream oss;      // Output string stream used to build the hex string
    oss << hex << setfill('0');     // Format output as hexadecimal and pad with leading zero if needed
    for (unsigned char c : data) {
        oss << setw(2) << static_cast<int>(c);      // Convert each byte of data into 2-digit hexadecimal representation
    }
    return oss.str();
}
// Converts hexadecimal encoded string back into binary data.
// This is required before decrypting the data.
static string fromHex(const string &hex) {
    string out;
    out.reserve(hex.size() / 2);
    for (size_t i = 0; i + 1 < hex.size(); i += 2) {
        string byteStr = hex.substr(i, 2);
        char byte = static_cast<char>(strtol(byteStr.c_str(), nullptr, 16));
        out.push_back(byte);
    }
    return out;
}
// Encrypts plain text using XOR encryption and converts result to hex format.
string Encryption::encrypt(const string &plain, const string &key) {
    return toHex(xorData(plain, key));  // First apply XOR encryption, then convert encrypted binary to hex string
}   
// Decrypts encrypted hex string using the same XOR key.
string Encryption::decrypt(const string &cipherHex, const string &key) {
    string bin = fromHex(cipherHex);    // Convert stored hex string back to binary encrypted data
    return xorData(bin, key);   // Apply XOR again using same key to retrieve original plaintext
}