import argparse
import json
from pathlib import Path
import sys
from .audit import audit, replay
from .packaging import verified_package

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['audit','replay','package','release','serve','staging']);parser.add_argument('--root',type=Path,default=Path.cwd());parser.add_argument('--out',type=Path,default=Path('artifacts/contract.json'));parser.add_argument('--receipt',type=Path,default=Path('artifacts/contract.json'));parser.add_argument('--port',type=int,default=4187);args=parser.parse_args()
    if args.command=='serve':
        from .server import serve
        serve(args.port);return 0
    if args.command=='audit':
        r=audit(args.root);args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return 0 if r['status']=='PASS' else 2
    r=json.loads(args.receipt.read_text());verdict=replay(args.root,r)
    if args.command=='staging':
        from .staging import check_staging
        verdict=check_staging(args.root,r);args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(verdict,indent=2)+'\n');print(json.dumps(verdict,indent=2));return 0
    if args.command in ('package','release'):
        artifact=verified_package(args.root,r)
        verdict['artifact']=str(artifact)
        verdict['status']='VERIFIED_PACKAGE_CREATED' if args.command=='package' else 'MANUAL_RELEASE_PACKAGE_READY'
    print(json.dumps(verdict,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError) as e:print(str(e),file=sys.stderr);raise SystemExit(2)
