/* ForgeCoin FCMP++ backend integration tests. No daemon, wallet or network.
 * Exercises the pinned upstream C ABI with real SAL proofs and rejection cases.
 */
#include <stdio.h>
#include <string.h>
#include "fcmp++.h"

#define CHECK(condition) do { if (!(condition)) { \
  fprintf(stderr, "FCMP ABI check failed at line %d: %s\n", __LINE__, #condition); return 1; \
} } while (0)

int main(void)
{
  struct OutputTuple output;
  memset(&output, 0x66, sizeof(output));
  /* Canonical Ed25519 generator encoding; x=1, y=0 gives O=xG+yT=G. */
  output.O[0] = output.I[0] = output.C[0] = 0x58;
  uint8_t x[32] = {1}, y[32] = {0}, message[32] = {42};
  struct FcmpRerandomizedOutputCompressed randomized;
  uint8_t proof[FCMP_PP_SAL_PROOF_SIZE_V1], key_image[32];
  CHECK(rerandomize_output(output, &randomized) == 0);
  CHECK(fcmp_pp_prove_sal(message, x, y, &randomized, proof, key_image) == 0);
  CHECK(memcmp(key_image, output.I, 32) == 0);
  CHECK(fcmp_pp_verify_sal(message, &randomized.input, key_image, proof));

  message[0] ^= 1;
  CHECK(!fcmp_pp_verify_sal(message, &randomized.input, key_image, proof));
  message[0] ^= 1;
  proof[0] ^= 1;
  CHECK(!fcmp_pp_verify_sal(message, &randomized.input, key_image, proof));
  proof[0] ^= 1;
  key_image[0] ^= 1;
  CHECK(!fcmp_pp_verify_sal(message, &randomized.input, key_image, proof));
  key_image[0] ^= 1;
  x[0] = 2;
  CHECK(fcmp_pp_prove_sal(message, x, y, &randomized, proof, key_image) < 0);

  struct HeliosPoint h = helios_hash_init_point(), decoded_h;
  struct SelenePoint s = selene_hash_init_point(), decoded_s;
  uint8_t encoded[32], roundtrip[32];
  helios_point_to_bytes(&h, encoded);
  CHECK(helios_point_from_bytes(encoded, &decoded_h) == 0);
  helios_point_to_bytes(&decoded_h, roundtrip);
  CHECK(memcmp(encoded, roundtrip, 32) == 0);
  selene_point_to_bytes(&s, encoded);
  CHECK(selene_point_from_bytes(encoded, &decoded_s) == 0);
  selene_point_to_bytes(&decoded_s, roundtrip);
  CHECK(memcmp(encoded, roundtrip, 32) == 0);
  memset(encoded, 0xff, sizeof(encoded));
  struct SeleneScalar scalar;
  CHECK(selene_scalar_from_bytes(encoded, &scalar) < 0);
  puts("FCMP Rust/C ABI: valid SAL, tampered message/proof/key image, wrong opening, curve roundtrips and noncanonical scalar passed");
  return 0;
}
