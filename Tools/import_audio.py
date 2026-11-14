"""Import named demo cues. The game discovers /Game/Audio/Cues/<cue> on start."""
import unreal as u,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tasks=[]
for filename in sorted(os.listdir(os.path.join(ROOT,'DemoSource','Audio'))):
 if not filename.endswith('.wav'):continue
 task=u.AssetImportTask()
 for k,v in {'filename':os.path.join(ROOT,'DemoSource','Audio',filename),'destination_path':'/Game/Audio/Cues','destination_name':os.path.splitext(filename)[0],'automated':True,'save':True,'replace_existing':True}.items():task.set_editor_property(k,v)
 tasks.append(task)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
assert all(t.imported_object_paths for t in tasks)
u.log('CUPCAKE_AUDIO_IMPORTED '+str(len(tasks)))
