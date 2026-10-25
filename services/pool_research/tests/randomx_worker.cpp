// Persistent light-mode synthetic-work helper. No nonce search or network I/O.
#include "randomx.h"
#include <cstdio>
#include <iostream>
#include <string>

int digit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}
bool decode(const std::string& input, std::string& output) {
    if (input.size() % 2) return false;
    output.clear();
    for (size_t i = 0; i < input.size(); i += 2) {
        int a = digit(input[i]), b = digit(input[i + 1]);
        if (a < 0 || b < 0) return false;
        output.push_back(char(16 * a + b));
    }
    return true;
}
struct State {
    randomx_cache* cache = nullptr;
    randomx_vm* vm = nullptr;
    ~State() {
        if (vm) randomx_destroy_vm(vm);
        if (cache) randomx_release_cache(cache);
    }
};
int main() {
    State state;
    std::string previous;
    // Bound both process lifetime and frame allocation. Requests are tagged;
    // an old response cannot satisfy a subsequent request in the parent.
    for (unsigned request = 1; request <= 64; ++request) {
        std::string line;
        char c;
        bool complete = false;
        while (std::cin.get(c)) {
            if (c == '\n') { complete = true; break; }
            if (line.size() >= 524400) return 2;
            line.push_back(c);
        }
        if (!complete) return line.empty() ? 0 : 2;
        auto first = line.find(' '), second = line.find(' ', first + 1);
        if (first == std::string::npos || second == std::string::npos ||
            line.substr(0, first) != std::to_string(request)) return 2;
        std::string seed, blob;
        if (second - first - 1 != 64 || line.size() - second - 1 > 524288 ||
            !decode(line.substr(first + 1, 64), seed) ||
            !decode(line.substr(second + 1), blob) || blob.empty()) return 2;
        if (!state.cache) state.cache = randomx_alloc_cache(RANDOMX_FLAG_DEFAULT);
        if (!state.cache) return 3;
        if (seed != previous) {
            if (state.vm) { randomx_destroy_vm(state.vm); state.vm = nullptr; }
            randomx_init_cache(state.cache, seed.data(), seed.size());
            state.vm = randomx_create_vm(RANDOMX_FLAG_DEFAULT, state.cache, nullptr);
            if (!state.vm) return 4;
            previous = seed;
        }
        unsigned char digest[32];
        randomx_calculate_hash(state.vm, blob.data(), blob.size(), digest);
        std::printf("%u ", request);
        for (auto byte : digest) std::printf("%02x", byte);
        std::printf("\n");
        std::fflush(stdout);
    }
    return 0;
}
