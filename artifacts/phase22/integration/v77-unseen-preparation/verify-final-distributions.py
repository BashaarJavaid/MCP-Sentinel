"""Verify final docs-aware distributions while reusing byte-identical hosted code tests."""
import hashlib,json,subprocess,tarfile,zipfile
from email.parser import BytesParser
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not subprocess.check_output(['git','diff','cec0322','--','src','tests','scripts','schemas','pyproject.toml','uv.lock','.github','action.yml','Makefile','LICENSE','CHANGELOG.md'])
tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],text=True).splitlines())
hosted=list((BASE/'v72-candidate-quality/artifacts/ci/portunusmcp-sentinel-dist').glob('*.whl'));assert len(hosted)==1
with zipfile.ZipFile(hosted[0]) as z:hosted_code={n:z.read(n) for n in z.namelist() if n.startswith('sentinel/') and not n.endswith('/')}
rows=[]
for path in sorted((OUT/'final-distributions').iterdir()):
 if path.name=='.gitignore':
  assert path.read_bytes()==b'*';continue
 if path.suffix=='.whl':
  with zipfile.ZipFile(path) as z:
   assert z.testzip() is None;members={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
  assert {n:d for n,d in members.items() if n.startswith('sentinel/')}==hosted_code
  mapping={}
  for n in members:
   if n.startswith('sentinel/_fixtures/'):mapping[n]='tests/fixtures/'+n.removeprefix('sentinel/_fixtures/')
   elif n.startswith('sentinel/_schemas/'):mapping[n]='schemas/'+n.removeprefix('sentinel/_schemas/')
   elif n.startswith('sentinel/'):mapping[n]='src/'+n
 else:
  assert path.name.endswith('.tar.gz')
  with tarfile.open(path) as t:
   assert not any(m.issym() or m.islnk() for m in t.getmembers());members={m.name:t.extractfile(m).read() for m in t if m.isfile()}
  mapping={n:n.split('/',1)[1] for n in members if n.split('/',1)[1] in tracked}
 metadata_name=next(n for n in members if n.endswith('/METADATA') or n.endswith('/PKG-INFO'))
 metadata=BytesParser().parsebytes(members[metadata_name])
 assert metadata.get_payload(decode=True).rstrip(b'\n')==(ROOT/'README.md').read_bytes().rstrip(b'\n')
 checked=[]
 for n,source in mapping.items():
  assert (ROOT/source).read_bytes()==members[n],(path.name,n)
  if source!='README.md':assert subprocess.check_output(['git','show','cec0322:'+source])==members[n]
  checked.append({'member':n,'source_path':source,'sha256':sha(members[n]),'binding':'current status-only documentation' if source=='README.md' else 'exact hostedcec0322 Git blob'})
 assert any(x['source_path']=='src/sentinel/static/rules/sent015.py' for x in checked)
 rows.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes()),'source_members':checked,'metadata_members':[n for n in members if n not in mapping]})
assert len(rows)==2
p={'hosted_source':'cec0322e904bbf63c33cd95796e7289101a93e5d','scanner':'cec0322e904bbf63c33cd95796e7289101a93e5d','README_sha256':sha((ROOT/'README.md').read_bytes()),'distributions':rows,'wheel_product_schema_fixture_members_byte_identical_to_hosted':True,'qualification':'Final README status documentation changes package long-description metadata only. Newly built wheel/sdist source members match current files; every non-README source member equals its testedcec0322 Git blob. Hosted installed-wheel matrix, Docker and isolation results retain actualcec0322 artifacts; no new hosted run is claimed for docs-only delivery.'}
path=OUT/'final-distributions.json';assert not path.exists();path.write_text(json.dumps(p,indent=2)+'\n');print('Verified final wheel/sdist source members and exact hosted code/schema/fixture bytes.')
