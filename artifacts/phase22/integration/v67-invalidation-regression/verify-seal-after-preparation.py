"""Verify completed seals after all helper preparation has stopped."""
import hashlib,json,tarfile
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
for version in range(1,96):
 index=json.loads((base/f'evidence-v{version}.json').read_text())
 assert sha((base/index['archive']).read_bytes())==index['sha256']
 with tarfile.open(base/index['archive']) as archive:
  members=archive.getmembers();assert len(members)==len(index['files'])
  for member,row in zip(members,index['files'],strict=True):
   assert member.isfile() and member.name==row['path'] and member.size==row['bytes']
   assert sha(archive.extractfile(member).read())==row['sha256']
   if version==95:assert sha((base/row['path']).read_bytes())==row['sha256']
latest=json.loads((base/'evidence-v95.json').read_text());names={r['path'] for r in latest['files']}
result={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'archives_verified':95,'current_seal_members_verified_against_expanded_files':len(latest['files']),'seal95_sha256':latest['sha256'],'preparation_timing_disclosure':'The bind-delivery.py and deliver.py helpers were prepared while seal95 execution had not yet returned. This supplemental verification runs after that preparation and seal execution both stopped. It rechecks every archive/member and every seal95 member against final expanded bytes; original seal/command results are retained. Any post-seal helpers are delivered directly, without rewriting seal95.','helper_membership':{n:(out.name+'/'+n in names) for n in ['bind-delivery.py','deliver.py']},'paid_calls':0}
with (out/'seal-postwrite-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('All95 archives/members and every current seal95 expanded member verified after helper preparation stopped.')
