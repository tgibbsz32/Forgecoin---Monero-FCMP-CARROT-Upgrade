// Link directly against ForgeCoin's built libcryptonote_basic.a.
// This is an offline differential harness; it does not hash with RandomX.
#include "cryptonote_basic/difficulty.h"
#include <iostream>
#include <string>
int nibble(char c) {
    if (c >= '0' && c <= '9') return c-'0';
    if (c >= 'a' && c <= 'f') return c-'a'+10;
    if (c >= 'A' && c <= 'F') return c-'A'+10;
    return -1;
}
int main() {
    std::string diff, digest;
    while (std::cin >> diff >> digest) {
        if (diff.empty() || digest.size()!=64) {std::cout<<"ERROR\n";continue;}
        cryptonote::difficulty_type difficulty=0;
        bool valid=true;
        for(char ch:diff) {
            if(ch<'0'||ch>'9') {valid=false;break;}
            difficulty=difficulty*10+(ch-'0');
        }
        crypto::hash hash{};
        for(int i=0;i<32;i++) {
            const int a=nibble(digest[2*i]),b=nibble(digest[2*i+1]);
            if(a<0||b<0) {valid=false;break;}
            reinterpret_cast<unsigned char*>(&hash)[i]=static_cast<unsigned char>((a<<4)|b);
        }
        if(!valid||difficulty==0) {std::cout<<"ERROR\n";continue;}
        std::cout<<(cryptonote::check_hash(hash,difficulty)?"PASS\n":"FAIL\n");
    }
}
