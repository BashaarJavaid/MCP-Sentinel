"""Download an immutable public source archive and validate without executing it."""
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/private/tmp/mcp-phase22-options')
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from scripts.phase20_corpus import archive_files, tree_digest

label, repository, revision = sys.argv[1:]
assert len(revision) == 40 and all(c in '0123456789abcdef' for c in revision)
assert '/' not in label
out = Path(__file__).resolve().parent / 'research/source-archives'
out.mkdir(exist_ok=True)
path = out / (label + '.tar.gz')
assert not path.exists()
url = f'https://codeload.github.com/{repository}/tar.gz/{revision}'
with urllib.request.urlopen(url, timeout=60) as response:
    data = response.read(64 * 1024 * 1024 + 1)
    assert len(data) <= 64 * 1024 * 1024
    retrieved_url = response.url
path.write_bytes(data)
receipt = {'retrieved_at': datetime.now(timezone.utc).isoformat(), 'url': url, 'retrieved_url': retrieved_url, 'repository': repository, 'revision': revision, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'target_execution': False}
try:
    files = archive_files(data, strip_root=True)
    receipt['tree_sha256'] = tree_digest(files)
    receipt['files_sha256'] = {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
    receipt['safe_archive_parsing_passed'] = True
    print(label, len(files), 'files;', len(data), 'archive bytes; license paths:', [name for name in files if 'license' in name.lower()][:15])
except Exception as error:
    receipt['safe_archive_parsing_passed'] = False
    receipt['error'] = repr(error)
    raise
finally:
    path.with_suffix('.json').write_text(json.dumps(receipt, indent=2) + '\n')
