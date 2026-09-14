"""Preserve initial failures and prove the single prototype-boundary correction."""
import ast,copy,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;base=out.parent;root=out.parents[3];prior=base/'v71-four-source-correctness'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=read(out/'candidate-commit.json');head=c['source'];oldhead=c['parent']
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
assert not subprocess.check_output(['git','diff','HEAD'])
for name,d in c['candidate_engineering_files_sha256'].items():assert sha(root/name)==d,name
path='src/sentinel/static/typescript_path_flow.py'
old_source=subprocess.check_output(['git','show',oldhead+':'+path],text=True)
actual=ast.parse((root/path).read_text());reference=ast.parse(old_source);removed=[]
needle=ast.dump(ast.parse('property_name == "__proto__"',mode='eval').body)
for node in ast.walk(actual):
 if isinstance(node,ast.BoolOp) and isinstance(node.op,ast.Or):
  selected=[value for value in node.values if ast.dump(value)==needle]
  if selected:removed.extend(selected);node.values=[value for value in node.values if value not in selected]
assert len(removed)==1 and ast.dump(actual)==ast.dump(reference)
failed=read(base/'v71-prototype-property-control.json');assert failed['exit_code']==1
partial=read(base/'v71-full-suite.json');assert partial['exit_code']==2
hosted=read(base/'v71-candidate-quality/packet.json')
assert not hosted['engineering_passed'] and hosted['runs']['ci']['conclusion']=='cancelled'
assert hosted['runs']['docs']['conclusion']=='success'
p=copy.deepcopy(read(prior/'source-assessment.json'))
p['historical_initial_source_assessment']={'path':str((prior/'source-assessment.json').relative_to(root)),'sha256':sha(prior/'source-assessment.json'),'source':p['source'],'qualification':'The first source assessment preceded the newly found prototype-property bypass. Its actual statements/checks remain retained; it is not final engineering evidence.'}
p.update(source=head,recorded_at=datetime.now(timezone.utc).isoformat(),candidate_commit_sha256=sha(out/'candidate-commit.json'),intake_sha256=sha(out/'intake.json'),changes=c['changes_from_prior_engineering'])
p['changes_assessed'][0]['conservative_boundaries']+=' Special __proto__ parameter properties are rejected because ordinary emitted assignments can mutate the receiver prototype; this retains the pre-existing explicit prototype-assignment boundary rather than silently constructing a field marker.'
p['changes_assessed'][0]['checks']+=' The final224focused cases include the new prototype-property rejection control.'
p['prototype_correction']={'prior_source':oldhead,'product_file':path,'single_added_guard':'property_name == "__proto__"','inverse_ast_equals_prior_source':True,'prior_source_file_sha256':hashlib.sha256(old_source.encode()).hexdigest(),'candidate_source_file_sha256':sha(root/path),'reason':'The first implementation assigned instance markers directly for all named parameter properties, bypassing the existing Assign handler that invalidates __proto__ writes. No target execution or TypeScript compiler assumption is needed to retain that conservative boundary.','remaining_scope':'No other product semantic change from42d6c7c. Original constructor/URL corrections remain subject to actual approved corpus evaluation.'}
p['failures_preserved'] += [
 {'check':'v71-prototype-property-control','outcome':'Failed: scanner-owned new Writer({save:unknown}).save(args.path) was still treated as the class method when its constructor parameter property was named __proto__. This is a source-established bypass of the existing conservative prototype-mutation boundary, not a corpus finding or runtime exploit claim.'},
 {'check':'v71-full-suite','outcome':'Deliberately interrupted after1408passed/36skipped in682.16seconds, exit2, once the independent prototype control failed. Initial process-name filter found no lowercase-python match and sent no signal; exact macOS Python PID70409 was then verified and interrupted normally. Partial JUnit/log remain retained; no JSON coverage report was emitted on interruption, and no complete local pass exists.'},
 {'check':'v71-hosted-retention','outcome':'CI34845266890 deliberately cancelled, docs34845266900passed. All resulting151artifact files and complete available logs retained; engineering_passedfalse. This is not new accepted full engineering. Corrected source receives a new full matrix.'},
 {'check':'v72-focused','outcome':'224passed, including actual prototype rejection, the original class/URL cases and complete discovery/worker checks.'}]
for label in ['v72-focused','v72-final-lint','v72-final-format','v72-final-types']:
 r=read(base/(label+'.json'));assert r['exit_code']==0
 assert sha(base/(label+'.patch'))==r['diff_sha256'] and sha(base/r['untracked_source_archive'])==r['untracked_source_sha256']
 p['checks'][label]={'receipt_sha256':sha(base/(label+'.json')),'log_sha256':sha(base/(label+'.log')),'exit_code':0,'source_commit':r['source_commit'],'diff_sha256':r['diff_sha256'],'command':r['command']}
p['initial_engineering_evidence_sha256']={str(path.relative_to(root)):sha(path) for path in [base/'v71-prototype-property-control.json',base/'v71-prototype-property-control.log',base/'v71-full-suite.json',base/'v71-full-suite-junit.xml',base/'v71-candidate-quality/packet.json',prior/'prototype-engineering-stop.json']}
p['assessment_helper_correction']='Initial V72source assessment passed the inverse-AST proof then failed while requiring an interrupted-run JSON coverage report that was never emitted. The helper/configuration mistake and exact original source are retained; no missing coverage artifact is invented.'
p['prepared_v71_helpers']='The earlier proposed future freeze/regression/reconciliation helpers were not executed, no V71evaluation proposal/approval/token exists, and no budget opened. Current preparation occurs only in V72; all earlier helpers remain preserved as preparation history.'
assert not any((prior/n).exists() for n in ['freeze.json','evaluation-proposal.json','evaluation-authorization.json','execution-consumed.json','audit.json'])
with (out/'source-assessment.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
print('Single prototype guard inverse-AST proof passed; first failures and interrupted engineering retained.')
