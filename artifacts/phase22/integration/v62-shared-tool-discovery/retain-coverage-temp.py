"""Retain and remove only completed-suite coverage temporaries absent at intake."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;base=out.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(base/'v62-full-suite.json')['exit_code']==0
assert read(out/'owned-final.json')['owned_processes']==[]
a=read(base/'shared-discovery-intake-20260914/intake.json')
# The intake was recorded before this continuation's checks; inspect its exact status text.
statuses=[v for k,v in a.items() if 'status' in k and isinstance(v,str)]
assert statuses and all('.coverage.' not in v for v in statuses),statuses
untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines())
files=sorted(p for p in root.glob('.coverage.*') if p.name in untracked)
assert all(p.is_file() and not p.is_symlink() and p.name.startswith('.coverage.MacBookAir_lan.pid') for p in files)
archive=out/'completed-suite-coverage-temporaries.tar.gz';assert not archive.exists()
rows={p.name:sha(p) for p in files}
with tarfile.open(archive,'w:gz') as t:
 for p in files:t.add(p,arcname=p.name,recursive=False)
with tarfile.open(archive) as t:
 assert {m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t}==rows
for p in files:assert sha(p)==rows[p.name];p.unlink()
(out/'coverage-temp-retention.json').write_text(json.dumps({'files_sha256':rows,'archive_sha256':sha(archive),'combined_coverage_sha256':sha(base/'v62-full-suite-coverage.json'),'qualification':'Only untracked coverage temporaries absent at intake, after completed suite and owned-process check. Exact raw files archived and verified before removal. Main .coverage and combined reports retained.'},indent=2)+'\n')
print('Archived and removed',len(files),'completed-suite coverage temporaries.')
