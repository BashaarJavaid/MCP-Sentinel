"""Clarify preflight versus input/cleanup timing before proposal delivery."""
import hashlib,json,shutil
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parents[3];p=out/'diagnostic-proposal.json';old=out/'initial-diagnostic-proposal.json';assert not old.exists();shutil.copyfile(p,old)
d=json.loads(p.read_text());before='All configuration/materialization/analysis/report and diagnostic preflight/cleanup overhead remains within the whole-input1800-second ceiling.'
after='The attempted-input1800-second timer starts before child imports/preflight and includes configuration, materialization, analysis, reports and sampling overhead. Cleanup has its separate15-second allowance. Read-only launcher source/provenance preflight occurs before budget consumption; it performs no scan.'
assert before in d['instrumentation'];d['instrumentation']=d['instrumentation'].replace(before,after)
d['files_sha256'][str(Path(__file__).resolve().relative_to(root))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
p.write_text(json.dumps(d,indent=2)+'\n');print('Clarified unchanged input/cleanup accounting; initial preparation retained. No execution or timing change.')
