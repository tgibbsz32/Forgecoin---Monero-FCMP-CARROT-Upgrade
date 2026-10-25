// Offline RandomX light-mode reference generator. Not a pool share verifier.
#include "randomx.h"
#include <cstdio>
#include <iostream>
#include <string>
int digit(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}
bool decode(const std::string& input,std::string& output){
 if(input.size()%2)return false;output.clear();
 for(size_t i=0;i<input.size();i+=2){int a=digit(input[i]),b=digit(input[i+1]);if(a<0||b<0)return false;output.push_back(char(16*a+b));}
 return true;
}
int main(int argc,char**argv){
 if(argc!=3){std::cerr<<"usage: randomx_reference <seed_hex> <blob_hex>\n";return 2;}
 std::string seed,blob;
 if(!decode(argv[1],seed)||seed.size()!=32||!decode(argv[2],blob)||blob.empty()||blob.size()>262144){std::cerr<<"invalid input\n";return 2;}
 randomx_cache* cache=randomx_alloc_cache(RANDOMX_FLAG_DEFAULT);if(!cache)return 3;
 randomx_init_cache(cache,seed.data(),seed.size());
 randomx_vm* vm=randomx_create_vm(RANDOMX_FLAG_DEFAULT,cache,nullptr);
 if(!vm){randomx_release_cache(cache);return 4;}
 unsigned char output[32];randomx_calculate_hash(vm,blob.data(),blob.size(),output);
 for(unsigned char b:output)std::printf("%02x",b);std::printf("\n");
 randomx_destroy_vm(vm);randomx_release_cache(cache);return 0;
}
