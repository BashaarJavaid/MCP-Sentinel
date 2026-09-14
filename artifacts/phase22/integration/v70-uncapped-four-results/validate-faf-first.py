"""Validate the completed first FAF input while the same sequence continues."""
import hashlib,importlib.util,json,sys
from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parents[3];prep=out.parent/'v69-uncapped-four-repository';dest=out/'first-faf-assessment';dest.mkdir(exist_ok=False)
sys.path[:0]=[str(root/'src'),str(root)]
from sentinel.report.validate_json import validate_report_data
from sentinel.report.validate_sarif import validate_sarif_data
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('runner',prep/'evaluate.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
p=read(prep/'evaluation-proposal.json');packet=read(out/'raw/packet.json');assert packet['scanner']==p['scanner']
rows=packet['attempts'][18:19];assert len(rows)==1 and rows[0]['state']=='completed' and rows[0]['input_id']=='faf-read-root-vulnerable'
first={};checked=[]
for row,expected in zip(rows,p['order'][18:19],strict=True):
 assert all(row[k]==v for k,v in expected.items());r.completed(row['timing'])
 folder=out/'raw'/row['directory'];path=folder/row['input_id']/'report.json';report=read(path);result=read(folder/'results.json');g=p['groups'][row['group']]
 assert result['scanner']==p['scanner'] and result['manifest_sha256']==g['manifest_sha256'] and result['model_calls']==0 and not result['requests']
 assert result['authorization_sha256']==sha(root/g['source_freeze_approval'])
 assert len(result['outcomes'])==1 and result['outcomes'][0]['state']=='completed' and result['outcomes'][0]['report_sha256']==sha(path)
 assert sha(path.parent/'configuration.json')==g['inputs'][row['input_id']]['configuration_sha256']
 runtime=read(folder.with_name(folder.name+'-runtime-policy.json'));assert runtime['runtime_policy_sha256']==p['runtime_policy_sha256'] and runtime['scanner_deadline_seconds'] is None
 validate_report_data(report);validate_sarif_data(read(path.with_suffix('.sarif')))
 assert report['analysisComplete'] and report['executionSuccessful']
 canonical=r.supervisor.clean(report,set(p['volatile_exclusions']))
 if row['batch']=='first':first[row['input_id']]=canonical
 else:assert canonical==first[row['input_id']] and row['ordered_repeat_equal']
 checked.append({**row,'report_sha256':sha(path),'sarif_sha256':sha(path.with_suffix('.sarif')),'finding_count':len(report['findings']),'warning_count':len(report['warnings']),'surface_count':len(report['static_analysis']['coverage']['surfaces'])})
d={'passed':True,'scanner':p['scanner'],'proposal_sha256':sha(prep/'evaluation-proposal.json'),'approval_sha256':sha(prep/'evaluation-authorization.json'),'observations':checked,'completed':1,'entire_ordered_pairs_equal':0,'source_assessment_pending':True,'four_repository_sequence_complete':False,'FAF_excluded_from_this_partial_validation':False,'budget_closed':False,'new_inputs':0,'paid_calls':0,'qualification':'Only the completed first FAF vulnerable observation. The other five FAF observations remain in the active24-observation experiment; this is not a new batch or closed budget.'}
(dest/'validation.json').write_text(json.dumps(d,indent=2)+'\n');print('Validated first FAF vulnerable output and cleanup; no repeat yet, full sequence remains active.')
