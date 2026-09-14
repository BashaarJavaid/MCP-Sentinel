"""Bind every retained report occurrence to source bytes; no target execution."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];ASSETS=OUT.parent/'v69-uncapped-four-repository';DEST=OUT/'first-faf-assessment'
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.phase22_corpus import frozen,input_files
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(ASSETS/'evaluation-proposal.json');p['repositories']=[{'id':g,**v} for g,v in p['groups'].items() if g=='faf-read-root'];items={};sources={};caseof={}
for case in p['repositories']:
    manifest=frozen(approval_path=ROOT/case['source_freeze_approval']);snap={s.revision:s for s in manifest.snapshots}
    for i in manifest.inputs:
        if i.id in case['input_ids']:
            items[i.id]=i;caseof[i.id]=case
            if i.snapshot not in sources:sources[i.snapshot]=input_files(i,snap[i.snapshot],ROOT)
contexts={};rows=[]
for path in sorted((OUT/'raw').glob('19-first-faf-read-root-vulnerable/*/report.json')):
    if path.parent.name not in items:continue
    d=read(path);item=items[path.parent.name];files=sources[item.snapshot];case=caseof[item.id]
    def context(file,line=None,binding=None):
        source_path=(Path(case['condition_review']['path']).parent/'condition-review.json')
        scan_root=read(ROOT/source_path)['scan_root']
        full_path=(Path(scan_root)/file).as_posix();data=files[full_path];lines=data.decode().splitlines();key=f'{item.snapshot}:{file}:{line or binding}'
        if key in contexts:return key
        c={'repository':case['repository'],'case_id':case['id'],'snapshot':item.snapshot,'path':file,'archive_path':full_path,'source_sha256':hashlib.sha256(data).hexdigest()}
        if line:
            assert 0<line<=len(lines),(file,line)
            c.update(line=line,statement=lines[line-1],excerpt=[f'{n+1}: {lines[n]}' for n in range(max(0,line-5),min(len(lines),line+5))])
            if file.endswith('.py'):
                scopes=[n for n in ast.walk(ast.parse(data)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.lineno<=line<=n.end_lineno]
                c['scope']=min(scopes,key=lambda n:n.end_lineno-n.lineno).name if scopes else 'module'
        else:
            base=binding.split('.')[0];occ=[n+1 for n,t in enumerate(lines) if re.search(r'(?<![\w$])'+re.escape(base)+r'(?![\w$])',t)]
            if not occ:
                markers={'tools/list metadata':'ListToolsRequestSchema','dynamic tool description':'description','launch state':'mcp.run'}
                assert binding in markers,(file,binding)
                base=markers[binding];occ=[n+1 for n,t in enumerate(lines) if base in t]
            if not occ and binding=='dynamic tool description':
                c.update(binding=binding,source_location_precision='file-only conceptual diagnostic',occurrence_lines=[],full_source=data.decode(),qualification='No literal description marker occurs in this file; the diagnostic supplies no line. Preserve the entire verified source without inventing an identifier occurrence or callsite.')
            else:
                assert occ,(file,binding)
                c.update(binding=binding,base_identifier=base,occurrence_lines=occ,excerpt=[f'{n+1}: {lines[n]}' for n in range(max(0,occ[0]-3),min(len(lines),occ[0]+3))])
        contexts[key]=c;return key
    findings=[];diagnostics=[];surfaces=[]
    for f in d['findings']:
        loc=f['location'];findings.append({'finding':f,'context':context(loc['path'],loc['range']['start_line']),'flow_contexts':[context(l['path'],l['range']['start_line']) for l in f['evidence'].get('flow_locations',[]) if l.get('kind')=='file']})
    coverage=d['static_analysis']['coverage']
    for kind,entries in [('warning',d['warnings']),('unresolved_flow',coverage['unresolved_flows'])]:
        for index,w in enumerate(entries):
            match=re.fullmatch(r'(SENT-\d+) at (.+):(\d+): (.+)',w['message']);binding=re.fullmatch(r"(.+): cannot resolve TypeScript binding '(.+)'",w['message'])
            if match:key=context(match[2],int(match[3]))
            elif binding:key=context(binding[1],binding=binding[2])
            else:
                assert w['message']=='src/engram/server.py: unresolved launch state; analyzing the unconfigured handler as well',w
                key=context('src/engram/server.py',binding='launch state')
            diagnostics.append({'kind':kind,'index':index,'diagnostic':w,'context':key})
    for index,s in enumerate(coverage['surfaces']):
        loc=s['location'];surfaces.append({'index':index,'surface':s,'context':context(loc['path'],loc['range']['start_line'])})
    rows.append({'input_id':item.id,'batch':path.parent.parent.name.split('-',1)[1].removesuffix('-'+item.id),'case_id':case['id'],'snapshot':item.snapshot,'label':item.label,'report':str(path.relative_to(ROOT)),'report_sha256':sha(path),'findings':findings,'diagnostics':diagnostics,'surfaces':surfaces,'coverage':coverage})
with (DEST/'inventory.json').open('x') as f:json.dump({'rows':rows,'contexts':contexts,'source_files':{rev:{name:hashlib.sha256(data).hexdigest() for name,data in files.items()} for rev,files in sources.items()}},f,indent=2);f.write('\n')
print('Source inventory:',len(rows),'reports;',len(contexts),'unique contexts; every occurrence bound.')
