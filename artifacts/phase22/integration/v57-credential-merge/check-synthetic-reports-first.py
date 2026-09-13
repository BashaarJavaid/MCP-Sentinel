"""Compare complete ordered credential rule output on retained synthetic test patterns."""
import ast,hashlib,json
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import sentinel.static.path_flow as path_flow
import sentinel.static.rules.sent016 as credential
from sentinel.static.http_discovery import handlers
from sentinel.static.model import RuleRunState
from sentinel.static.rules.sent012 import analyze
from tests.test_python_discovery import program

OUT=Path(__file__).resolve().parent
namespace=dict(vars(path_flow));tree=ast.parse((OUT/'baseline-path-flow.py').read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'combine','_combine'}]
exec(compile(tree,'baseline_value_kernel','exec'),namespace)
old_combine=namespace['combine'];new_combine=path_flow.combine
namespace=dict(vars(credential),combine=old_combine)
tree=ast.parse((OUT/'baseline-sent016.py').read_text())
tree.body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CredentialFlow']
exec(compile(tree,'baseline_credential_flow','exec'),namespace)
old_flow=namespace['CredentialFlow']
cases=[('token = token or os.environ["OPERATOR_TOKEN"]',1),('if not token: token = os.getenv("OPERATOR_TOKEN")',1),('if not token: raise HTTPException(401)\n    token = token or os.environ["OPERATOR_TOKEN"]',0),('if not other: raise HTTPException(401)\n    token = token or os.environ["OPERATOR_TOKEN"]',1),('if not token: raise HTTPException(401)\n    token = other\n    token = token or os.environ["OPERATOR_TOKEN"]',1),('token = token or ""',0),('operator = os.environ["OPERATOR_TOKEN"]',0)]
rows=[]
for body,expected in cases:
    source='from fastapi import FastAPI, Request, HTTPException\nimport os\nimport requests\napp = FastAPI()\n@app.get("/data")\nasync def fetch(request: Request):\n    token = request.headers.get("Authorization")\n    other = request.headers.get("X-Other-Token")\n    '+body+'\n    return requests.get("https://api.example.com/", headers={"Authorization": token})\n'
    outputs=[]
    for flow_type,kernel in [(old_flow,old_combine),(credential.CredentialFlow,new_combine)]:
        index=program({'server.py':source});state=RuleRunState()
        with patch.object(path_flow,'combine',kernel),patch.object(credential,'combine',kernel):
            analyze(index,state,flow=flow_type(index,state,float('inf')),entries=(*index.tools(),*handlers(index)))
        result=json.loads(json.dumps(asdict(state),default=lambda value:value.model_dump(mode='json')))
        assert len(state.matches)==expected,(body,len(state.matches),expected)
        outputs.append(result)
    assert outputs[0]==outputs[1],body
    rows.append({'source':source,'expected_matches':expected,'entire_ordered_rule_state_equal':True,'baseline':outputs[0],'candidate':outputs[1]})
record={'passed':True,'cases':rows,'case_source':'Existing tests/test_credential_fallback.py::test_http_credential_selection patterns; scanner-owned synthetic source only.','compared':'All ordered StaticMatch findings/captures, warnings, visits, exemptions and skip_reason. No fields excluded and no list sorting.','baseline_files_sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['baseline-path-flow.py','baseline-sent016.py']},'candidate_files_sha256':{str(Path(m.__file__).relative_to(Path.cwd())):hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for m in [path_flow,credential]},'corpus_observations':0,'profiles':0,'paid_calls':0,'target_execution':False}
with (OUT/'synthetic-reports.json').open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
print('Seven retained synthetic HTTP credential patterns preserve complete ordered rule output, including four detections and three negatives.')
