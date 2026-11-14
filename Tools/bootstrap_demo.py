"""Import repository player GLBs, reuse the candy cane, and create CakeLand."""
import unreal as u,os,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EL=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools()
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem);ACT=u.get_editor_subsystem(u.EditorActorSubsystem)
SME=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
report={'players':[]}
for who,source in [('Strawberry','Meshy_AI_cupcake_character_leg_1114201729_image-to-3d-texture.glb'),('Chocolate','Meshy_AI_Mint_Chocolate_Cupcak_1114201753_image-to-3d-texture.glb')]:
 dest='/Game/Models/'+who
 task=u.AssetImportTask()
 for k,v in {'filename':os.path.join(ROOT,source),'destination_path':dest,'automated':True,'save':True,'replace_existing':True,'async_':False}.items():task.set_editor_property(k,v)
 AT.import_asset_tasks([task])
 assets=[EL.load_asset(p) for p in EL.list_assets(dest,recursive=True)]
 meshes=[a for a in assets if isinstance(a,u.StaticMesh)]
 assert meshes,'No GLB mesh imported for '+who
 meshes.sort(key=lambda a:SME.get_number_verts(a,0),reverse=True)
 mesh=meshes[0];path=dest+'/SM_'+who
 if mesh.get_path_name().split('.')[0]!=path:assert EL.rename_asset(mesh.get_path_name(),path)
 mesh=EL.load_asset(path);SME.remove_collisions(mesh);SME.add_simple_collisions(mesh,u.ScriptCollisionShapeType.CAPSULE)
 for a in assets:
  if isinstance(a,u.Texture2D):a.set_editor_property('max_texture_size',2048);EL.save_loaded_asset(a)
 assert EL.save_loaded_asset(mesh)
 report['players'].append({'name':who,'source':source,'asset':path,'mesh_count':len(meshes),'vertices':SME.get_number_verts(mesh,0)})
# Same cane silhouette as CandyCarnival, centered and scaled to a handheld prop.
task=u.AssetImportTask();opt=u.FbxImportUI();opt.import_mesh=True;opt.import_materials=False;opt.import_textures=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False
for k,v in {'filename':os.path.join(ROOT,'DemoSource','SM_CandyCane.fbx'),'destination_path':'/Game/Props','destination_name':'SM_CandyCane','automated':True,'save':True,'replace_existing':True,'options':opt,'factory':u.FbxFactory()}.items():task.set_editor_property(k,v)
u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Interchange.FeatureFlags.Import.FBX 0')
AT.import_asset_tasks([task]);cane=EL.load_asset('/Game/Props/SM_CandyCane');assert cane
for i,slot in enumerate(cane.get_editor_property('static_materials')):
 name=str(slot.get_editor_property('imported_material_slot_name'));mat=EL.load_asset('/Game/CandyCarnival/Materials/M_'+name)
 if mat:cane.set_material(i,mat)
EL.save_loaded_asset(cane)
assert LEVEL.new_level('/Game/Maps/CakeLand')
def actor(cls,pos,label):
 a=ACT.spawn_actor_from_class(cls,u.Vector(*pos));a.set_actor_label(label);return a
sun=actor(u.DirectionalLight,(0,0,1000),'Warm bakery sun');sun.set_actor_rotation(u.Rotator(pitch=-52,yaw=-35,roll=0),False);sun.light_component.set_editor_property('intensity',3.4);sun.light_component.set_light_color(u.LinearColor(1,.89,.75,1))
sky=actor(u.SkyLight,(0,0,800),'Soft sky fill');sky.light_component.set_editor_property('intensity',1.3);sky.light_component.set_editor_property('real_time_capture',True)
actor(u.SkyAtmosphere,(0,0,0),'Atmosphere')
floor=actor(u.StaticMeshActor,(0,0,-135),'Pink bakery floor');floor.static_mesh_component.set_static_mesh(EL.load_asset('/Engine/BasicShapes/Cube.Cube'));floor.set_actor_scale3d(u.Vector(120,120,1));floor.static_mesh_component.set_material(0,EL.load_asset('/Game/CandyCarnival/Materials/M_StrawberrySugar'))
pp=actor(u.PostProcessVolume,(0,0,0),'Gentle candy grading');pp.set_editor_property('unbound',True)
settings=pp.get_editor_property('settings');settings.set_editor_property('override_auto_exposure_method',True);settings.set_editor_property('auto_exposure_method',u.AutoExposureMethod.AEM_MANUAL);settings.set_editor_property('override_auto_exposure_bias',True);settings.set_editor_property('auto_exposure_bias',0.6);settings.set_editor_property('override_auto_exposure_apply_physical_camera_exposure',True);settings.set_editor_property('auto_exposure_apply_physical_camera_exposure',False);pp.set_editor_property('settings',settings)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/CupcakeCannibal.CupcakeGameMode'))
assert LEVEL.save_current_level();assert EL.save_directory('/Game',only_if_is_dirty=True,recursive=True)
json.dump(report,open(os.path.join(ROOT,'Tools','demo_assets.json'),'w'),indent=2)
u.log('CUPCAKE_BOOTSTRAP_COMPLETE '+str(report))
