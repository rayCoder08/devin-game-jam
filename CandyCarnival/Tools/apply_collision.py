"""UE 5.6: update collision in the existing level; preserve scene and materials."""
import unreal as u, os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='/Game/CandyCarnival';EL=u.EditorAssetLibrary
AT=u.AssetToolsHelpers.get_asset_tools();SME=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
ACT=u.get_editor_subsystem(u.EditorActorSubsystem);LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)
DATA=json.load(open(os.path.join(ROOT,'SourceArt','collision_manifest.json')))
MAP=BASE+'/Maps/CandyCarnival'
assert not LEVEL.is_in_play_in_editor(),'Stop Play mode before applying collision.'
current_world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
if current_world.get_name()!='CandyCarnival':assert LEVEL.load_level(MAP)
u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 0')
def setp(o,k,v):o.set_editor_property(k,v)
def import_mesh(filename,name,folder,keep_materials=None):
 task=u.AssetImportTask()
 for k,v in {'filename':os.path.join(ROOT,'SourceArt','CollisionFBX',filename),'destination_path':folder,'destination_name':name,'automated':True,'save':True,'replace_existing':True,'replace_existing_settings':True}.items():setp(task,k,v)
 opt=u.FbxImportUI()
 for k,v in {'import_mesh':True,'import_as_skeletal':False,'import_materials':False,'import_textures':False,'automated_import_should_detect_type':False,'mesh_type_to_import':u.FBXImportType.FBXIT_STATIC_MESH}.items():setp(opt,k,v)
 for k,v in {'combine_meshes':True,'auto_generate_collision':False,'one_convex_hull_per_ucx':True,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'transform_vertex_to_absolute':True,'normal_import_method':u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS}.items():setp(opt.static_mesh_import_data,k,v)
 setp(task,'options',opt);setp(task,'factory',u.FbxFactory());AT.import_asset_tasks([task])
 mesh=EL.load_asset(folder+'/'+name);assert mesh,'Import failed '+name
 if keep_materials:
  for i,slot in enumerate(mesh.get_editor_property('static_materials')):
   key=str(slot.get_editor_property('imported_material_slot_name'))
   material=keep_materials.get(key)
   if material:mesh.set_material(i,material)
 return mesh
report={'assets':[],'surface_triangles':DATA['surface_triangles'],'source_collision_hulls':DATA['total_hulls'],'sky_collision':False}
for entry in DATA['assets']:
 mesh=EL.load_asset(BASE+'/Meshes/'+entry['name']);assert mesh
 prior={str(s.get_editor_property('imported_material_slot_name')):s.get_editor_property('material_interface') for s in mesh.get_editor_property('static_materials')}
 if entry['mode']=='surface':
  low=import_mesh(entry['file'],entry['collision_mesh'],BASE+'/Collision')
  setp(low,'has_navigation_data',False);assert EL.save_loaded_asset(low)
  SME.remove_collisions(mesh)
  setp(mesh,'complex_collision_mesh',low)
  setp(mesh.get_editor_property('body_setup'),'collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 else:
  mesh=import_mesh(entry['file'],entry['name'],BASE+'/Meshes',prior)
  setp(mesh,'complex_collision_mesh',None)
  setp(mesh.get_editor_property('body_setup'),'collision_trace_flag',u.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX)
  count=SME.get_convex_collision_count(mesh)
  assert count>=entry['hulls'],'Missing hulls: '+entry['name']+' '+str(count)+' / '+str(entry['hulls'])
 setp(mesh,'customized_collision',True)
 body=mesh.get_editor_property('body_setup');setp(body,'double_sided_geometry',True)
 assert EL.save_loaded_asset(mesh),'Could not save '+entry['name']
 report['assets'].append({'name':entry['name'],'mode':entry['mode'],'convex_hulls':SME.get_convex_collision_count(mesh),'simple_shapes':SME.get_simple_collision_count(mesh),'surface_triangles':entry.get('triangles',0)})
 u.log('CANDY_COLLISION_APPLIED '+entry['name'])

# A project-owned convex sphere deforms correctly with the marquee's oval scale.
# Never change the engine sphere used by the sky or by other projects.
marquee_path=BASE+'/Meshes/SM_MarqueeCollision'
marquee=EL.load_asset(marquee_path) if EL.does_asset_exist(marquee_path) else EL.duplicate_asset('/Engine/BasicShapes/Sphere.Sphere',marquee_path)
SME.remove_collisions(marquee)
assert SME.add_simple_collisions(marquee,u.ScriptCollisionShapeType.NDOP26)>=0
setp(marquee.get_editor_property('body_setup'),'collision_trace_flag',u.CollisionTraceFlag.CTF_USE_SIMPLE_AS_COMPLEX);setp(marquee,'customized_collision',True);assert EL.save_loaded_asset(marquee)
collidable=[]
for actor in ACT.get_all_level_actors():
 if not isinstance(actor,u.StaticMeshActor):continue
 comp=actor.static_mesh_component;label=actor.get_actor_label()
 actor.modify();comp.modify()
 if label=='Turquoise sky gradient':
  comp.set_collision_profile_name('NoCollision')
  comp.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
  continue
 if label.startswith('Marquee -'):
  material=comp.get_material(0);comp.set_static_mesh(marquee);comp.set_material(0,material)
 comp.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 comp.set_collision_profile_name('BlockAll')
 comp.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
 comp.set_editor_property('generate_overlap_events',False)
 collidable.append(label)
assert LEVEL.save_current_level();assert EL.save_directory(BASE,only_if_is_dirty=True,recursive=True)
report['collidable_actors']=collidable
report['total_convex_hulls']=sum(e['convex_hulls'] for e in report['assets'])+SME.get_convex_collision_count(marquee)
json.dump(report,open(os.path.join(ROOT,'Tools','collision_report.json'),'w'),indent=2)
u.log('CANDY_COLLISION_COMPLETE '+str(len(collidable))+' actors; '+str(report['total_convex_hulls'])+' convex hulls; '+str(report['surface_triangles'])+' terrain triangles')
