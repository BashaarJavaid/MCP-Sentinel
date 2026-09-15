"""Source-bound inventory and induction for the approved private-set domain."""
import ast, hashlib, json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((OUT/'authorization.json').read_text());assert a['decision']=='approved'
classes={};uses=[];indirect=[];callers=[];files={}
for p in sorted((ROOT/'src').rglob('*.py')):
 text=p.read_text();tree=ast.parse(text);parents={c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)};name=str(p.relative_to(ROOT));files[name]=sha(p)
 for n in ast.walk(tree):
  if isinstance(n,ast.ClassDef):classes[n.name]={'file':name,'bases':[ast.unparse(b) for b in n.bases],'node':n}
  if isinstance(n,ast.Attribute) and n.attr=='invalidated_objects':
   q=parents[n];uses.append({'file':name,'line':n.lineno,'context':ast.unparse(q)})
   assert isinstance(n.value,ast.Name) and n.value.id=='self'
   assert isinstance(q,(ast.AnnAssign,ast.Assign,ast.Compare,ast.BinOp,ast.Attribute,ast.Call)),ast.unparse(q)
  if isinstance(n,ast.Constant) and isinstance(n.value,str) and 'invalidated_objects' in n.value:indirect.append({'file':name,'line':n.lineno,'value':n.value})
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in {'statement','initialize','http_initialize','function','invalidate'}:callers.append({'file':name,'line':n.lineno,'call':ast.unparse(n)})
assert not indirect,indirect
subclasses={'TypeScriptPathFlow'}
while True:
 next_set=subclasses|{k for k,v in classes.items() if set(v['bases'])&subclasses}
 if next_set==subclasses:break
 subclasses=next_set
assert subclasses=={'TypeScriptPathFlow','RegistrationFlow','HTTPRegistrationFlow','ShellFlow','TypeScriptOptionFlow','TypeScriptURLFlow','TypeScriptCredentialFlow'},subclasses
reflections=[]
for k in subclasses:
 for n in ast.walk(classes[k]['node']):
  if isinstance(n,ast.Attribute) and n.attr=='__dict__':reflections.append(ast.unparse(n))
  if isinstance(n,ast.Call) and any(isinstance(x,ast.Name) and x.id=='self' for x in n.args):
   assert ast.unparse(n)=='copy.deepcopy(self, memo.copy())',ast.unparse(n)
   reflections.append({'permitted_copy':ast.unparse(n),'line':n.lineno})
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {'eval','exec','setattr','delattr','vars'}:raise AssertionError(ast.unparse(n))
assert reflections==[{'permitted_copy':'copy.deepcopy(self, memo.copy())','line':2417}],reflections
p=ROOT/'src/sentinel/static/typescript_path_flow.py'
assert sha(p)==a['baseline_files_sha256'][str(p.relative_to(ROOT))]
proof={
 'passed':True,'authorization_sha256':sha(OUT/'authorization.json'),'source_files_sha256':files,'uses':uses,'subclasses':{k:{x:y for x,y in classes[k].items() if x!='node'} for k in sorted(subclasses)},'callers':callers,'indirect_attribute_strings':indirect,'whole_flow_copy':reflections,
 'induction':[
 'Initialization creates a builtin set. invalidate only adds the Value key, its record root, and known SDK class identity; no removal, replacement argument, or raw-set return occurs.',
 'All direct reads are membership/intersection or the named If copy/union operations. No private-set reference is stored in another flow field, Value, closure, callback, warning, match, or report. No string attribute lookup/export occurs anywhere in src.',
 'The only whole-flow escape is http_initialize deepcopy after initialize has returned. Its memo shares only program, RuleRunState, source files and AST dictionaries; it does not contain an invalidation set. The private set and any preexisting local aliases are copied together, and each fork is local to its route.',
 'Expression, pattern, call, member, guard, constructors, initialized globals/imports and all shipped subclass overrides either leave this set unchanged or transitively invoke invalidate/statement. Unknown target calls and custom hooks are abstractly interpreted; their receiver/argument invalidations remain unchanged and no target code executes.',
 'Block/definition/expression/return/throw and unsupported statements compose these operations. Return and throw preserve any earlier invalidations. Try handlers/finally, for/while/switch branches and URL exact-iteration/special-try overrides compose the same monotone operations; termination changes reachability only.',
 'Inductive If step: let B be a fresh copy after condition evaluation. Each feasible arm starts with its own B copy; by induction its final A contains B. Reusing first completed A therefore gives the same union as B union A. Later arms still start from independent B copies. Nested If obeys the same induction. With zero feasible arms the original fresh B copy remains.',
 'No completed arm reference escapes through shipped code, so later union cannot alter another field. Any alias existing before If still refers to the original set, which neither version mutates after making B. Errors, deadline exceptions and interruptions leave self pointing to the same current arm partial set: final assignment/merge is not reached in either version.',
 'Only the exact two previously injected scanner callbacks clearing the set or capturing completed-arm references are prospectively outside the explicitly approved domain. Their historical full deltas and strict failure remain unchanged; no other failure is excluded.'
 ],'target_execution':False,'corpus_observations':0,'profiles':0,'paid_calls':0}
(OUT/'production-domain-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Production domain established:',len(uses),'direct uses;',len(subclasses),'flow classes;',len(callers),'entry/mutation calls. HTTP deepcopy explicitly assessed.')
