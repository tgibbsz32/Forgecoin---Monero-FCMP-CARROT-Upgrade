// Standalone C++ arithmetic oracle for offline research ONLY.
// It mirrors inspected native check_hash threshold semantics; does NOT
// call the linked ForgeCoin implementation or compute RandomX digests.
#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <string>
using boost::multiprecision::cpp_int;
int hex_digit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}
int main() {
    const cpp_int limit = (cpp_int(1) << 256) - 1;
    const cpp_int max_diff = (cpp_int(1) << 128) - 1;
    std::string diff_text, digest;
    while (std::cin >> diff_text >> digest) {
        cpp_int difficulty = 0, hash = 0;
        bool valid = !diff_text.empty() && digest.size() == 64;
        for (char c : diff_text) {
            if (c < '0' || c > '9') { valid = false; break; }
            difficulty = difficulty * 10 + (c - '0');
        }
        if (difficulty < 1 || difficulty > max_diff) valid = false;
        if (valid) for (int i = 31; i >= 0; --i) {
            int hi = hex_digit(digest[2*i]);
            int lo = hex_digit(digest[2*i+1]);
            if (hi < 0 || lo < 0) { valid = false; break; }
            hash = (hash << 8) | (hi*16+lo);
        }
        if (!valid) std::cout << "ERROR\n";
        else std::cout << (hash * difficulty <= limit ? "PASS\n" : "FAIL\n");
    }
}
