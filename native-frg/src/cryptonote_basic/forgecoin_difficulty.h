#pragma once
#include <algorithm>
#include <cstdint>
#include <limits>
#include <vector>
#include "difficulty.h"

namespace cryptonote {
constexpr std::uint64_t FORGE_DIFFICULTY_FLOOR_HEIGHT = 500;
constexpr std::uint64_t FORGE_MINIMUM_DIFFICULTY = 500000;
constexpr std::uint64_t FORGE_DIFFICULTY_MILLION_HEIGHT = 600;
constexpr std::uint64_t FORGE_MINIMUM_DIFFICULTY_MILLION = 1000000;
constexpr std::uint64_t FORGE_LWMA_HEIGHT = 700;
constexpr std::size_t FORGE_LWMA_WINDOW = 90;
constexpr std::uint8_t FORGE_LWMA_VERSION = 19;
constexpr std::size_t FORGE_LWMA_TIMESTAMP_WINDOW = 11;
constexpr std::uint64_t FORGE_LWMA_FUTURE_LIMIT = FORGE_LWMA_WINDOW * 120 / 20;

template<typename Difficulty>
Difficulty apply_forgecoin_difficulty_floor(Difficulty calculated, std::uint64_t height, bool mainnet)
{
  const std::uint64_t minimum = height >= FORGE_DIFFICULTY_MILLION_HEIGHT
    ? FORGE_MINIMUM_DIFFICULTY_MILLION : FORGE_MINIMUM_DIFFICULTY;
  if (mainnet && height >= FORGE_DIFFICULTY_FLOOR_HEIGHT && calculated != 0 && calculated < minimum)
    return Difficulty(minimum);
  return calculated;
}

// LWMA-1 design: https://github.com/zawy12/difficulty-algorithms/issues/3
// ForgeCoin integer variant: use the newest N+1 samples (no lag), normalize
// non-increasing timestamps, cap each solve interval at 6*T, and apply 0.99 bias.
// 256-bit intermediates avoid rounding average work early and prevent overflow.
// Activation uses existing history; all three chain paths supply the same suffix.
inline difficulty_type forgecoin_lwma(const std::vector<std::uint64_t>& timestamps,
    const std::vector<difficulty_type>& cumulative, std::uint64_t target)
{
  constexpr std::size_t n = FORGE_LWMA_WINDOW;
  if (timestamps.size() != cumulative.size() || timestamps.size() < n + 1 || target != 120)
    return 0;
  const std::size_t start = timestamps.size() - n - 1;
  std::uint64_t previous = timestamps[start];
  std::uint64_t weighted = 0;
  for (std::size_t i = 1; i <= n; ++i)
  {
    if (cumulative[start+i] <= cumulative[start+i-1] || previous == std::numeric_limits<std::uint64_t>::max())
      return 0;
    const std::uint64_t current = std::max(timestamps[start+i], previous+1);
    weighted += i * std::min(6*target, current-previous);
    previous = current;
  }
  weighted = std::max(weighted, n*n*target/20);
  const boost::multiprecision::uint256_t work = cumulative.back()-cumulative[start];
  const boost::multiprecision::uint256_t result = work*target*(n+1)*99/(200*weighted);
  if (result > std::numeric_limits<difficulty_type>::max())
    return 0;
  return std::max(difficulty_type(1), result.convert_to<difficulty_type>());
}

inline difficulty_type next_forgecoin_difficulty(const std::vector<std::uint64_t>& timestamps,
    const std::vector<difficulty_type>& cumulative, std::uint64_t target,
    std::uint64_t height, bool mainnet)
{
  const difficulty_type calculated = mainnet && height >= FORGE_LWMA_HEIGHT
    ? forgecoin_lwma(timestamps, cumulative, target)
    : next_difficulty(timestamps, cumulative, target);
  return apply_forgecoin_difficulty_floor(calculated, height, mainnet);
}
}
