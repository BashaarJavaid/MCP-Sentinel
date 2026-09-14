"""Check complete unresolved-ID coverage and helper syntax without producing final review."""
import ast,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;BASE=OUT.parent
for folder in [OUT,BASE/'v74-prior-language-preparation']:
 for path in folder.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
tree=ast.parse((OUT/'reconcile.py').read_text());constants={}
for node in tree.body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'limits','new','current_ids'}:constants[node.targets[0].id]=ast.literal_eval(node.value)
old=json.loads((BASE/'v72-prototype-property-correction/audit.json').read_text());rows=old['requirements']+old['additional_scope_requirements'];limits=set(constants['limits'])|{f'V{n}-REGRESSION-GATE' for n in [46,49,53,58,60,63,67]};human={'R84','V43-ACCEPTANCE-CLOSEOUT'};deferred={'R77','R78'}
nonpassed={r['id'] for r in rows if r['disposition']!='passed'}
assert nonpassed==limits|constants['current_ids']|human|deferred|{'V72-DELIVERY'},nonpassed-(limits|constants['current_ids']|human|deferred|{'V72-DELIVERY'})
new=constants['new'];assert len(new)==15 and not set(x[0] for x in new)&set(r['id'] for r in rows)
assert len(rows)+len(new)==422 and len(limits)+sum(x[2]=='proposed documented limitation awaiting decision' for x in new)==23
assert not (OUT/'audit.json').exists() and not (OUT/'acceptance-proposal.json').exists() and not (BASE/'evidence-v99.json').exists()
print('Prepared review covers every prior non-passed ID:422planned rows,23proposedlimitations. No final review/audit/seal or technical acceptance produced.')
