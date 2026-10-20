# ForgeCoin difficulty regression tests

Run `python make_vectors.py` here to generate 1,231 independent expected-result vectors. Compile lwma-consensus-test.cpp together with ../../src/cryptonote_basic/difficulty.cpp using C++17, with include paths ../../src, ../../contrib/epee/include, and ../../external/easylogging++. Boost headers are required. Run the executable with lwma-vectors.txt as its argument. Do not compile with NDEBUG: assertions are part of this standalone test.

The cases preserve 424 historical blocks, exercise heights 499/500/599/600/699/700/701, compare full history and the newest 91 samples, verify unaffected non-mainnet calculations, and cover timestamp normalization, insufficient/mismatched input, non-increasing cumulative work, timestamp overflow, and large 128-bit work. Run on both Windows x64 and ARM64 before deployment.

The real chain must use the normal difficulty calculation. Fixed difficulty is only appropriate for isolated offline integration tests of version transitions, wallet scanning and reorganizations.
