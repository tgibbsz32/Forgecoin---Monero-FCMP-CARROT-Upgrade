# ForgeCoin difficulty regression tests

Run `python make_vectors.py` here to generate 1,231 independent expected-result vectors. Compile lwma-consensus-test.cpp together with ../../src/cryptonote_basic/difficulty.cpp using C++17, with include paths ../../src, ../../contrib/epee/include, and ../../external/easylogging++. Boost headers are required. Run the executable with lwma-vectors.txt as its argument. Do not compile with NDEBUG: assertions are part of this standalone test.

The cases preserve 424 historical blocks, exercise heights 499/500/599/600/699/700/701, compare full history and the newest 91 samples, verify unaffected non-mainnet calculations, and cover timestamp normalization, insufficient/mismatched input, non-increasing cumulative work, timestamp overflow, and large 128-bit work. Run on both Windows x64 and ARM64 before deployment.

The real chain must use the normal difficulty calculation. Fixed difficulty is only appropriate for isolated offline integration tests of version transitions, wallet scanning and reorganizations.

## Isolated native-PoW competing-chain test

`isolated_reorg.py` copies a **stopped** candidate checkpoint into two new directories,
verifies the expected RPC height and tip, and mines divergent branches with real PoW.
It submits B's blocks to A over offline loopback RPC, checks that non-heavier forks
do not replace A, verifies adoption of the heavier fork and orphan status of the
displaced blocks, then restarts both daemons to verify persistence.

Use the candidate binary matching the checkpoint's network identity. This is an
opt-in integration test; it is not a test of the repository's default binary unless
that binary was built from the matching candidate source. Do not supply a running
database. The script copies only `lmdb/data.mdb`, never wallet keys, existing RPC
credentials, peer lists, or daemon configuration. Output must be a new directory
outside the source checkpoint. Ports default to 40580/40581 and 40680/40681;
all nodes run `--offline`, with loopback RPC/P2P and ZMQ disabled.

```text
python tests/forgecoin/isolated_reorg.py --daemon PATH_TO_CANDIDATE --checkpoint PATH_TO_STOPPED_DATA_DIR --expected-height 17 --expected-tip VERIFIED_TIP --address CANDIDATE_MINING_ADDRESS --output NEW_OUTPUT_DIRECTORY
```

The standard-library-only runner defaults to six mining threads and a 30-minute
timeout per branch. It saves full block blobs, RPC observations, daemon logs, binary
and source hashes, and a handoff after each completed phase. Exit zero and
`evidence.json` with `passed: true` are required. A timeout is an incomplete test,
not evidence that consensus failed. On failure, preserve the output directory and
inspect the error and logs before using a different new output directory.

This covers consensus block submission, not P2P transport, wallet rewinds,
transaction-pool restoration, ARM64 agreement, adversarial timestamps, or a
shorter-but-higher-work branch. Those remain separate release gates.
