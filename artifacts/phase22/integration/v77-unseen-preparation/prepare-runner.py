"""Adapt the retained normal-policy evaluator to the six newly frozen records."""
import ast,difflib
from pathlib import Path
OUT=Path(__file__).resolve().parent;OLD=OUT.parent/'v74-prior-language-preparation'
s=(OLD/'evaluate.py').read_text()
s=s.replace('Proposed181-observation local exposed regression and compatibility sequence','Proposed12-observation first-frozen two-repository sequence').replace('== 181','== 12').replace('== 98','== 6')
s=s.replace('receipt["intake_sha256"] == sha(ASSETS / "intake.json")','receipt["precuration_freeze_sha256"] == sha(ASSETS / "scope-and-precuration-freeze.json")')
s=s.replace('    from scripts.phase20_corpus import validate\n    from scripts.phase22_corpus import frozen','    from unseen_corpus import frozen')
s=s.replace('manifest = validate() if group.endswith("historical") else frozen(approval_path=Path.cwd() / g["source_freeze_approval"])','manifest = frozen(approval_path=ASSETS / "source-freeze-authorization.json")')
s=s.replace('phase22_approval=Path.cwd() / g["source_freeze_approval"] if g["source_freeze_approval"] else None','phase22_approval=ASSETS / "source-freeze-authorization.json"')
s=s.replace('sha(Path.cwd() / g["source_freeze_approval"])','sha(ASSETS / "source-freeze-authorization.json")')
start=s.index('def condition(');end=s.index('\n\ndef child(',start)
s=s[:start]+'''def condition(report, witness):
    matches = [f for f in report["findings"] if f["rule_id"] == witness["rule_id"] and f.get("location", {}).get("path") == witness["path"] and f.get("location", {}).get("range", {}).get("start_line") == witness["sink_line"]]
    return {"source_assessment_pending": True, "condition_passed": None,
            "provisional_sink_candidates": len(matches),
            "qualification": "Rule/path/line candidates only. Full source assessment must establish named caller, boundary, sink and supported negatives."}
''' + s[end:]
s=s.replace('with patch.object(harness, "load_configuration", checked):','from unseen_corpus import frozen\n    with patch.object(harness, "load_configuration", checked), patch.object(harness, "frozen_phase22", frozen):')
s=s.replace('judgement = condition(report, json.loads((ROOT / expected["reference_report"]).read_text()), expected["assessment"], item.label, set(proposal["volatile_exclusions"]), proposal["witnesses"].get(group, {}).get(input_id))','judgement = condition(report, proposal["witnesses"][input_id])')
s=s.replace('            identity(observation["group"])\n            assert time.monotonic() + 1815 < stop, "Insufficient whole-input allowance"\n','')
start=s.index('def selfcheck():');end=s.index('\n\nif __name__',start)
s=s[:start]+'''def selfcheck():
    prior.selfcheck()
    witness = {"rule_id": "SENT-002", "path": "synthetic.ts", "sink_line": 2}
    hit = {"rule_id": "SENT-002", "location": {"path": "synthetic.ts", "range": {"start_line": 2}}}
    assert condition({"findings": [hit]}, witness)["provisional_sink_candidates"] == 1
    assert condition({"findings": []}, witness)["condition_passed"] is None
    assert condition({"findings": [{**hit, "rule_id": "SENT-012"}]}, witness)["provisional_sink_candidates"] == 0
''' + s[end:]
# Artifact-local schema is loaded only after the caller has bound the intended scanner imports.
needle='    signal.signal(signal.SIGTERM, supervisor.stopped)'
s=s.replace(needle,'''    schema_spec = importlib.util.spec_from_file_location("unseen_corpus", ASSETS / "corpus.py")
    schema = importlib.util.module_from_spec(schema_spec)
    sys.modules["unseen_corpus"] = schema
    schema_spec.loader.exec_module(schema)
''' + needle)
# Exact source approval is subordinate to the numerical approval; admission never invents one.
needle='    assert receipt["precuration_freeze_sha256"] == sha(ASSETS / "scope-and-precuration-freeze.json")'
s=s.replace(needle,needle+'''
    source_receipt = json.loads((ASSETS / "source-freeze-authorization.json").read_text())
    assert source_receipt["parent_authorization_sha256"] == sha(APPROVAL)
    assert source_receipt["corpus"] == {"manifest": proposal["manifest"]["path"], "sha256": proposal["manifest"]["sha256"], "freeze_approved": True, "input_ids": proposal["input_order"], "treatments": ["rules"]}
''')
ast.parse(s);(OUT/'evaluate.py').write_text(s)
launch=(OLD/'launch.py').read_text().replace('v75-prior-language-results','v78-unseen-results').replace("'observations_maximum': 181","'observations_maximum': 12")
ast.parse(launch);(OUT/'launch.py').write_text(launch)
(OUT/'runner-delta.patch').write_text(''.join(difflib.unified_diff((OLD/'evaluate.py').read_text().splitlines(True),s.splitlines(True),fromfile='v74/evaluate.py',tofile='v77/evaluate.py')))
print('Prepared normal 1800/10/15 runner, no target access or authorization/token creation.')
