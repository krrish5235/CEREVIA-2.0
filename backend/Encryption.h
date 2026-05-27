#ifndef ENCRYPTION_H
#define ENCRYPTION_H
#include <string>
using namespace std;
class Encryption {
public:
    // Encrypts plain text using XOR operation with a key
    // and converts the result into hexadecimal format.
    // This helps safely store encrypted data in text-based storage like databases.
    // Simple XOR + hex "encryption" (demo only, not real AES security)
    static string encrypt(const string &plain, const string &key);
    // Decrypts hexadecimal encrypted data back to the original text.
    // It first converts hex back to binary and then applies XOR with the same key.
    static string decrypt(const string &cipherHex, const string &key);
};
#endif
