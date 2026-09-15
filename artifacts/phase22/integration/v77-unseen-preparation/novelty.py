"""Read prior project evidence and archives; never execute target source."""
import hashlib
import json
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
inventory = json.loads((OUT / 'workspace-inventory.json').read_text())
names = sorted(set(inventory['tracked'] + inventory['ignored'] + inventory['untracked']))
identities = ['awwaiid/mcp-server-taskwarrior', 'nick-holmquist/proxmox-mcp']
terms = [x.casefold() for x in identities] + ['mcp-server-taskwarrior', 'nick-holmquist', 'proxmox-mcp', 'awwaiid']
text_files, matches, archive_refs, members, failures = {}, [], {}, {}, []
source_suffixes = {'.py', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}
seen_archives = {}
for name in names:
    p = ROOT / name
    if p.is_symlink() or not p.is_file() or p.is_relative_to(OUT):
        continue
    if p.suffix in source_suffixes | {'.json', '.md', '.yaml', '.yml', '.txt', '.patch', '.diff', '.toml'}:
        data = p.read_bytes()
        text_files[name] = sha(data)
        folded = data.decode(errors='replace').casefold()
        for term in terms:
            if term in folded:
                matches.append({'path': name, 'term': term})
        if p.suffix in source_suffixes:
            members.setdefault(sha(data), []).append(name)
    if name.endswith('.tar.gz') and '/evidence-' not in name:
        digest = sha(p.read_bytes())
        archive_refs[name] = digest
        if digest in seen_archives:
            continue
        seen_archives[digest] = name
        try:
            with tarfile.open(p, 'r:gz') as archive:
                for item in archive:
                    if item.isfile() and item.size <= 16 * 1024 * 1024:
                        stream = archive.extractfile(item)
                        data = stream.read()
                        members.setdefault(sha(data), []).append(name + '::' + item.name)
                        if Path(item.name).suffix in source_suffixes | {'.json', '.md', '.toml'}:
                            folded = data.decode(errors='replace').casefold()
                            for term in terms:
                                if term in folded:
                                    matches.append({'path': name + '::' + item.name, 'term': term})
        except (OSError, tarfile.TarError) as exc:
            failures.append({'path': name, 'error': str(exc)})
overlaps = {}
for label in ['taskwarrior', 'proxmox']:
    for version in ['vulnerable', 'fixed']:
        receipt = json.loads((OUT / f'research/source-archives/{label}-{version}.tar.json').read_text())
        overlaps[label + '-' + version] = {
            n: {'sha256': d, 'prior_paths': members[d]}
            for n, d in receipt['files_sha256'].items() if d in members
        }
result = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'precuration_freeze_sha256': sha((OUT / 'scope-and-precuration-freeze.json').read_bytes()),
          'identities_and_fork_parent_checked': identities, 'text_files_sha256': text_files, 'archive_sha256': archive_refs,
          'distinct_archives_read': len(seen_archives), 'distinct_member_or_source_hashes': len(members),
          'name_matches': matches, 'archive_read_failures': failures, 'overlaps': overlaps,
          'method': 'Complete baseline inventory text and bounded regular archive-member reads, including prior source-selection archives and copied materialized trees. No archive extraction, target import, scanner or comparator. Byte overlap is reviewed separately; common licenses, empty modules and standard tooling are not evidence of repository reuse.',
          'limits': 'Recorded project exposure only. Same-agent post-freeze curation; no independent human review, training-data novelty or proof against arbitrarily transformed copies.',
          'observations': 0, 'paid_calls': 0}
with (OUT / 'novelty-comparison.json').open('x') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(json.dumps({'name_matches': matches, 'failures': failures, 'distinct_archives': len(seen_archives),
                  'overlap_source_files': {k: [n for n in v if Path(n).suffix in source_suffixes] for k, v in overlaps.items()}}, indent=2))
