"""Verify recovered protected state and record delayed Docker reclamation, read only."""
import hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path(__file__).resolve().parent;prev=out.parent/'v67-invalidation-regression';root=out.parents[3]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(*args):return subprocess.check_output(args,text=True)
binding=read(prev/'documentation-binding.json')
for n,d in binding['user_files_sha256'].items():assert sha(root/n)==d,n
assert not run('git','ls-files','--deleted')
assert not run('git','diff','--cached')
r=read(prev/'restored-launch-preflight.json');assert r['passed'] and not r['budget_consumed'] and r['profile_attempts']==0
w=read(prev/'worktree-restoration.json');assert w['passed'] and w['restored_files']==25941 and w['existing_files_overwritten']==0
s=read(prev/'sealed-evidence-restoration.json');assert s['passed'] and s['existing_files_overwritten']==0
c=read(prev/'base-image-cleanup.json');assert c['passed'] and len(c['removed_image_ids'])==5
assert set(run('docker','ps','-aq','--no-trunc').splitlines())==set(c['containers_before'])
assert set(run('docker','volume','ls','-q').splitlines())==set(c['volumes_before'])
images=set(run('docker','image','ls','-aq','--no-trunc').splitlines())
assert not images & set(c['removed_image_ids'])
assert set(c['approved_images'])<=images
raw=Path('/Users/bashaarjavaid/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw')
allocated=raw.stat().st_blocks*512;vfs=os.statvfs(root)
names=['launch-preflight-failure.json','diagnostic-preflight.json','diagnostic-authorization.json','worktree-restoration-plan.json','worktree-restoration.json','sealed-evidence-restoration.json','user-document-restoration-detection.json','user-document-restoration-final.json','restored-launch-preflight.json','docker-cleanup-started.json','docker-cleanup.json','base-image-cleanup-started.json','base-image-cleanup.json']
a={'passed':True,'recorded_at':datetime.now(timezone.utc).isoformat(),'evidence_sha256':{str((prev/n).relative_to(root)):sha(prev/n) for n in names},'initial_launch':'Read-only preflight failed before token/output/input; restored exact verified bytes and resumed the same still-unused approval once. Initial process-start commentary was corrected; premature preparation assertion retained.','disappearance_cause':'Unknown. User suggested limited disk space; no evidence establishes ENOSPC or a cleanup process as the cause. Host had roughly35GB available during inspection.','restoration':{'tracked_files':25941,'apfs_clones':24737,'blob_writes':1204,'git_links':6,'expanded_evidence_files':7667,'archives_verified':95,'protected_user_documents_restored':2,'protected_user_documents_verified':9,'existing_files_overwritten':0,'heads_indexes_preserved':True,'original_session_commands_executed':False,'raw_private_session_logs_published':False},'docker':{'authorization':'User requested checking Docker and freeing unneeded storage.','selected_cache_entries':2,'cache_entries_removed':0,'cache_prune_reported_bytes':0,'selected_unused_public_images_removed':5,'logical_image_summary_before_gb':9.151,'logical_image_summary_after_gb':6.261,'logical_summary_drop_gb':2.89,'containers_preserved':7,'volumes_preserved':65,'approved_runtime_images_preserved':c['approved_images'],'allocated_bytes_before':c['raw_allocated_bytes_before'],'allocated_bytes_now':allocated,'delayed_physical_bytes_reclaimed':c['raw_allocated_bytes_before']-allocated,'host_available_bytes_now':vfs.f_bavail*vfs.f_frsize,'qualification':'Rounded Docker logical image totals differ from physical sparse-disk reclamation. Initial immediate physical delta was zero and remains preserved; this later read is supplemental. Host free-space changes include unrelated filesystem activity. No global prune, project-image deletion, volume/container removal or daemon configuration change.','summary_now':run('docker','system','df')},'profile_budget':'Exactly one actual profile after restored preflight; now closed. No second token or target execution.','helper_failures':['buildx du incompatible verbose/format options; read-only inventory retried with supported output','image inspect missing Config.Labels and string Size display assumptions corrected in read-only inspection','initial public-image guard expected empty RepoTags, but Docker returned exact digest-qualified tags; failed before mutation, corrected helper and original retained','guessed helper/path lookups corrected using listings; no source or measurement effect'],'paid_calls':0,'technical_acceptance_received':False,'phase22_complete':False}
with (out/'recovery-assessment.json').open('x') as f:json.dump(a,f,indent=2);f.write('\n')
print(json.dumps({'restoration':a['restoration'],'physical_bytes_reclaimed':a['docker']['delayed_physical_bytes_reclaimed'],'host_available_bytes':a['docker']['host_available_bytes_now']}))
