"""Local-only development reviewer command. Do not expose through HTTP or remote shell."""
import argparse
from services.governance_api.app import decode_pubkey
from services.governance_api import registry

def main():
    parser=argparse.ArgumentParser(description="ForgeCoin local role review (development only)")
    parser.add_argument("action", choices=("approve","revoke","history"))
    parser.add_argument("wallet",help="Solana wallet public key")
    parser.add_argument("role",nargs="?",choices=sorted(registry.ROLES))
    parser.add_argument("--reviewer")
    parser.add_argument("--reason")
    args=parser.parse_args()
    decode_pubkey(args.wallet)
    if args.action=="history":
        for item in registry.history(args.wallet):
            print(item)
        return
    if not args.role or not args.reviewer or not args.reason:
        parser.error("decisions require role, --reviewer and --reason")
    registry.decide(args.wallet,args.role,args.action,args.reviewer,args.reason)
    print(args.action,"recorded for",args.role,"on",args.wallet)

if __name__=="__main__":
    main()
