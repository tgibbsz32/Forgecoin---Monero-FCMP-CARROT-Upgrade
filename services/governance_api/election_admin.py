"""Local election operations only. No HTTP admin privileges or remote deployment."""
import argparse
import json
from services.governance_api import elections

def main():
    p=argparse.ArgumentParser(description="ForgeCoin practice-election operator (LOCAL ONLY)")
    sub=p.add_subparsers(dest="command",required=True)
    c=sub.add_parser("create");c.add_argument("category",choices=sorted(elections.CATEGORIES));c.add_argument("title");c.add_argument("--weights-json",help="Local JSON file mapping staker wallet to demo integer weight")
    sub.add_parser("list")
    x=sub.add_parser("close");x.add_argument("election_id",type=int)
    t=sub.add_parser("tally");t.add_argument("election_id",type=int)
    args=p.parse_args()
    try:
        if args.command=="create":
            weights=None
            if args.weights_json:
                with open(args.weights_json,encoding="utf-8") as handle:
                    weights=json.load(handle)
                if not isinstance(weights,dict):
                    p.error("Expected a JSON object of wallet => integer weight")
            print(json.dumps({"election_id":elections.create(args.category,args.title,weights=weights),"binding":False}))
        elif args.command=="list": print(json.dumps(elections.list_elections(),indent=2))
        elif args.command=="close":
            elections.close(args.election_id);print("Closed practice election",args.election_id)
        else:print(json.dumps(elections.tally(args.election_id),indent=2))
    except (ValueError,OSError) as exc:
        p.error(str(exc))

if __name__=="__main__": main()
