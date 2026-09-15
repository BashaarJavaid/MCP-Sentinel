"""Preserve the initial scope wording; distinguish four-worker and five-rule runs."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
p=OUT/'report-equivalence.json';old=p.read_bytes();(OUT/'initial-report-scope.json').write_bytes(old);d=json.loads(old)
d['scope']='All static result fields and ordered findings, warnings, summaries and source coverage on Python/TypeScript/mixed owned fixtures, each serial and parallel, with the four worker rules SENT-012/014/015/016 selected. SENT-013 was separately covered in existing full rule-state tests. The additional five-rule-report-equivalence.json binds all five selected rules in complete reports.'
d['scope_wording_correction']={'original_sha256':hashlib.sha256(old).hexdigest(),'reason':'The inherited worker fixture selects four FLOW_RULES. The initial sentence incorrectly said all five requested rules executed in these particular six observations. Actual four-rule results were valid and unchanged; a separately retained six-report run now selects SENT-012 through016 explicitly.'}
p.write_text(json.dumps(d,indent=2)+'\n')
print('Preserved initial scope statement; four-worker report results unchanged and distinguished from explicit five-rule comparisons.')
