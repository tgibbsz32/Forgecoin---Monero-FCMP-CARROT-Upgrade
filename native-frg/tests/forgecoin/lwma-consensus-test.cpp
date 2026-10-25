#include <cassert>
#include <fstream>
#include <iostream>
#include "cryptonote_basic/forgecoin_difficulty.h"
int main(int argc,char**argv){
 assert(argc==2);std::ifstream in(argv[1]);assert(in);
 std::uint64_t height;bool mainnet;std::size_t n,count=0;cryptonote::difficulty_type expected;
 while(in>>height>>mainnet>>n>>expected){
  std::vector<std::uint64_t> ts(n);std::vector<cryptonote::difficulty_type> cs(n);
  for(std::size_t i=0;i<n;++i){in>>ts[i]>>cs[i];assert(in);}
  auto actual=cryptonote::next_forgecoin_difficulty(ts,cs,120,height,mainnet);
  if(actual!=expected){std::cerr<<"Mismatch "<<count<<" height "<<height<<" expected "<<expected<<" actual "<<actual<<"\n";return 1;}
  ++count;
 }
 assert(in.eof());assert(count>1000);
 std::vector<std::uint64_t> ts(91,1);std::vector<cryptonote::difficulty_type> cs(90,1);
 assert(cryptonote::forgecoin_lwma(ts,cs,120)==0);
 std::cout<<count<<" consensus vectors passed\n";
}
