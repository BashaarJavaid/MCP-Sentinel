"""Verify local source members and package metadata against the candidate Git blobs."""
import hashlib
import json
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path('/private/tmp/mcp-phase22-options')
OUT = Path(__file__).resolve().parent
HEAD = 'cec0322e904bbf63c33cd95796e7289101a93e5d'
sys.path.insert(0, str(ROOT))
from scripts.smoke_wheel import _check_archives

sha = lambda data: hashlib.sha256(data).hexdigest()
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == HEAD
assert not subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT)
tracked = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', HEAD], cwd=ROOT, text=True).splitlines())
dist = OUT/'distributions'
wheel, = dist.glob('*.whl')
sdist, = dist.glob('*.tar.gz')
_check_archives(wheel, sdist)
rows = []
for path in [wheel, sdist]:
    if path.suffix == '.whl':
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            members = {n: archive.read(n) for n in archive.namelist() if not n.endswith('/')}
        mapping = {}
        for name in members:
            if name.startswith('sentinel/_fixtures/'):
                mapping[name] = 'tests/fixtures/'+name.removeprefix('sentinel/_fixtures/')
            elif name.startswith('sentinel/_schemas/'):
                mapping[name] = 'schemas/'+name.removeprefix('sentinel/_schemas/')
            elif name.startswith('sentinel/'):
                mapping[name] = 'src/'+name
    else:
        with tarfile.open(path) as archive:
            assert not any(m.issym() or m.islnk() for m in archive.getmembers())
            members = {m.name: archive.extractfile(m).read() for m in archive if m.isfile()}
        mapping = {n: n.split('/', 1)[1] for n in members if n.split('/', 1)[1] in tracked}
    checked = []
    for name, source in mapping.items():
        blob = subprocess.check_output(['git', 'show', HEAD+':'+source], cwd=ROOT)
        assert blob == members[name] == (ROOT/source).read_bytes(), (path.name, name)
        checked.append({'member': name, 'source_path': source, 'sha256': sha(blob)})
    assert any(r['source_path'] == 'src/sentinel/static/path_flow.py' for r in checked)
    assert any(r['source_path'] == 'src/sentinel/static/typescript_path_flow.py' for r in checked)
    rows.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()), 'source_members': checked, 'metadata_members': [n for n in members if n not in mapping]})
packet = {'candidate': HEAD, 'distributions': rows, 'metadata_and_entrypoints_valid': True,
          'qualification': 'Local wheel/sdist source, schema and fixture bytes match actual candidate Git blobs. Existing package metadata/entrypoint checks pass. Hosted installation, Docker and isolation results remain pending and are separately bound.',
          'new_corpus_observations': 0, 'paid_calls': 0}
with (OUT/'candidate-distributions.json').open('x') as stream:
    json.dump(packet, stream, indent=2)
    stream.write('\n')
print('Verified both local distribution source member sets against', HEAD)
