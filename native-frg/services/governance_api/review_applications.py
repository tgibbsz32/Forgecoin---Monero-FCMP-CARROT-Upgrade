"""Local-only reviewer of applications; never expose via public API."""
import argparse
from services.governance_api import applications

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("approve","reject","audit"))
    p.add_argument("application_id",type=int)
    p.add_argument("--reviewer",default="")
    p.add_argument("--reason",default="")
    a=p.parse_args()
    if a.action=="audit":
        for event in applications.audit(a.application_id):
            print(event)
        return
    if not a.reviewer.strip() or not a.reason.strip():
        p.error("review requires --reviewer and --reason")
    try:
        print(applications.review(a.application_id,a.action,a.reviewer,a.reason))
    except ValueError as exc:
        p.error(str(exc))

if __name__=="__main__":
    main()
