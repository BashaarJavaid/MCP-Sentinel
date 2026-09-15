"""Bind the completed final full suite to its committed product and tests."""
import hashlib,json,subprocess
from pathlib import Path
r=Path.cwd();b=r/'artifacts/phase22/integration';o=b/'v29-loopback-fix';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.loads((b/'v29-full-suite.json').read_text());source='f85a90f9ba2d1c43019e8505b977d57f3476a9c9'
assert meta['exit_code']==0 and meta['source_commit']==source
patch=b/'v29-full-suite.patch';assert sha(patch)==meta['diff_sha256']
if patch.read_bytes():
 assert not subprocess.check_output(['git','apply','--numstat','--include=src/**','--include=tests/**','--include=scripts/**',str(patch)])
inputs=['src','tests','scripts','schemas','pyproject.toml','uv.lock','action.yml','README.md','CHANGELOG.md','LICENSE']
assert not subprocess.check_output(['git','diff',source,'--',*inputs])
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',source,'--',*inputs],text=True).splitlines()
files={}
for name in paths:
 assert not (r/name).is_symlink(), name
 data=subprocess.check_output(['git','show',source+':'+name]);assert (r/name).read_bytes()==data;files[name]=sha(r/name)
archive=b/meta['untracked_source_archive'];assert sha(archive)==meta['untracked_source_sha256']
p={'corrected_scanner':source,'actual_full_suite_source':meta['source_commit'],'full_suite_sha256':sha(b/'v29-full-suite.json'),'wrapper_patch_sha256':sha(patch),'untracked_source_archive_sha256':sha(archive),'current_product_tests_packages_equal_corrected_commit':True,'file_sha256':files,'qualification':'The full suite started after the final product/test commit; no product/test/script changes are present in its captured patch or current tree. Later workflow/docs changes have separate hosted verification.'};(o/'local-source-binding.json').write_text(json.dumps(p,indent=2)+'\n');print('Bound final full suite to',source,len(files),'Git source/test/package files.')
