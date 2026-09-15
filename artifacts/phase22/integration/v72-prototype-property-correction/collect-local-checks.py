"""Bind full local engineering and zero-call compatibility to the actual candidate."""
import hashlib,importlib.metadata,json,subprocess,sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=read(out/'candidate-commit.json');head=c['source']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','diff','HEAD'])
states=Counter('failed' if n.find('failure') is not None or n.find('error') is not None else 'skipped' if n.find('skipped') is not None else 'passed' for n in ET.parse(base/'v72-full-suite-junit.xml').getroot().iter('testcase'))
assert states=={'passed':2450,'skipped':36},states
cov=read(base/'v72-full-suite-coverage.json')
assert cov['meta']['branch_coverage'] and cov['totals']['percent_covered']>=80
assert 100*cov['totals']['covered_branches']/cov['totals']['num_branches']>=80
labels=['source-assessment-corrected','final-lint','final-format','final-types','focused','full-suite','lock','schema','notices','artifacts','candidate-docs','build','candidate-distributions','runtime-requirements','dependency-audit','production-capture','runtime-reuse','demo-validation','policy-synthetic','policy-boundaries']
checks={}
for label in labels:
 name='v72-'+label;r=read(base/(name+'.json'));assert r['exit_code']==0,name
 assert sha(base/(name+'.patch'))==r['diff_sha256']
 assert sha(base/r['untracked_source_archive'])==r['untracked_source_sha256']
 checks[name]={'command':r['command'],'source_commit':r['source_commit'],'receipt_sha256':sha(base/(name+'.json')),'log_sha256':sha(base/(name+'.log')),'diff_sha256':r['diff_sha256']}
for name,d in c['candidate_engineering_files_sha256'].items():assert sha(root/name)==d,name
replay=read(base/'v72-production-capture-revalidation/packet.json')
assert replay['source']==head and replay['model_calls']==0 and len(replay['requests'])==6 and all(r['accepted'] for r in replay['requests'])
p={'candidate':head,'states':dict(states),'coverage_totals':cov['totals'],'coverage_metric':'Configured percent_covered is combined statement/branch coverage; actual branch-only coverage is separately required >=80%.','junit_sha256':sha(base/'v72-full-suite-junit.xml'),'coverage_sha256':sha(base/'v72-full-suite-coverage.json'),'checks':checks,'candidate_engineering_files_sha256':c['candidate_engineering_files_sha256'],'changes_from_prior_engineering':c['changes_from_prior_engineering'],'precommit_checks':'The retained per-command patches and candidate commit bind the focused checks to actual final source. Added explicit nonempty-discovery assertion is verified by its focused check and the full suite. No old-source full suite is relabeled current.','candidate_commit_receipt_sha256':sha(out/'candidate-commit.json'),'source_assessment_sha256':sha(out/'source-assessment.json'),'python':sys.version,'packages':{n:importlib.metadata.version(n) for n in ['semgrep','mcp','pytest','pydantic']},'runtime_binding_sha256':sha(out/'compatibility.json'),'production_replay_sha256':sha(base/'v72-production-capture-revalidation/packet.json'),'hosted_engineering':'Separately retained actual matrix/job/log/package audit.','new_corpus_observations':0,'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (out/'local-checks.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
print('Verified',dict(states),'combined coverage',cov['totals']['percent_covered'],'branch-only',cov['totals']['percent_branches_covered'])
