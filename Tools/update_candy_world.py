"""Reuse the reference-video CandyCarnival world, add an otter mascot, import team audio."""
import unreal as u, os, math, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EL=u.EditorAssetLibrary; AT=u.AssetToolsHelpers.get_asset_tools()
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem); ACT=u.get_editor_subsystem(u.EditorActorSubsystem)
SME=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
dest='/Game/Props/Otter'
task=u.AssetImportTask()
for k,v in {'filename':os.path.join(ROOT,'DemoSource','Otter_with_symmetrica.glb'),'destination_path':dest,'automated':True,'save':True,'replace_existing':True,'async_':False}.items():task.set_editor_property(k,v)
if not EL.list_assets(dest,recursive=True):AT.import_asset_tasks([task])
assets=[EL.load_asset(p) for p in EL.list_assets(dest,recursive=True)]
meshes=[a for a in assets if isinstance(a,u.StaticMesh)]
assert meshes,'Otter import failed'
mesh=max(meshes,key=lambda a:SME.get_number_verts(a,0))
if mesh.get_path_name().split('.')[0]!=dest+'/SM_Otter':assert EL.rename_asset(mesh.get_path_name(),dest+'/SM_Otter')
mesh=EL.load_asset(dest+'/SM_Otter'); SME.remove_collisions(mesh); SME.add_simple_collisions(mesh,u.ScriptCollisionShapeType.CAPSULE)
for a in assets:
 if isinstance(a,u.Texture2D):a.set_editor_property('max_texture_size',2048);EL.save_loaded_asset(a)
EL.save_loaded_asset(mesh)
# Reassemble the complete saved scenery in a separate gameplay map.
if EL.does_asset_exist('/Game/Maps/CandyWorld'):
 assert LEVEL.load_level('/Game/Maps/CandyWorld'); ACT.destroy_actors(ACT.get_all_level_actors())
else:assert LEVEL.new_level('/Game/Maps/CandyWorld')
for path in EL.list_assets('/Game/CandyCarnival/Meshes'):
 sm=EL.load_asset(path)
 if not isinstance(sm,u.StaticMesh) or 'MarqueeCollision' in sm.get_name():continue
 a=ACT.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));a.set_actor_label(sm.get_name());a.set_folder_path('CandyCarnival')
 a.static_mesh_component.set_static_mesh(sm);a.static_mesh_component.set_collision_profile_name('BlockAll')
 if 'Cloud' in sm.get_name():a.static_mesh_component.set_cast_shadow(False)
for a in ACT.get_all_level_actors():
 if isinstance(a,u.StaticMeshActor):
  sm=a.static_mesh_component.static_mesh
  if not sm:continue
  name=sm.get_name()
  # Preserve the original terrain, winding paths, marquees, hills, clouds and stalls.
  a.set_actor_scale3d(a.get_actor_scale3d()*0.65)
  a.set_actor_location(a.get_actor_location()*0.65+u.Vector(0,-1600,-110),False,False)
  if any(t in name for t in ['Peppermint','Candy_Apple','Popcorn','Welcoming']):
   b=sm.get_bounds(); loc=a.get_actor_location(); s=a.get_actor_scale3d().x
   cx=loc.x+b.origin.x*s;cy=loc.y+b.origin.y*s;r=math.hypot(cx,cy)
   # Keep decorative props outside the playable plate and clear of both players.
   if r<1400:
    f=1400/max(1,r);a.set_actor_location(loc+u.Vector(cx*(f-1),cy*(f-1),0),False,False)
sun=ACT.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,1500));sun.set_actor_rotation(u.Rotator(pitch=-35,yaw=-30,roll=0),False)
sun.light_component.set_mobility(u.ComponentMobility.MOVABLE);sun.light_component.set_intensity(3.4);sun.light_component.set_light_color(u.LinearColor(1,.91,.79))
sky=ACT.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,800));sky.light_component.set_mobility(u.ComponentMobility.MOVABLE);sky.light_component.set_intensity(2.3)
sky.light_component.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sky.light_component.set_cubemap(EL.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
sky.light_component.set_editor_property('lower_hemisphere_is_black',False)
dome=ACT.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));dome.set_actor_label('Original turquoise candy sky');dome.static_mesh_component.set_static_mesh(EL.load_asset('/Engine/BasicShapes/Sphere'));dome.set_actor_scale3d(u.Vector(1500,1500,1500))
dome.static_mesh_component.set_material(0,EL.load_asset('/Game/CandyCarnival/Materials/M_CandySky'));dome.static_mesh_component.set_cast_shadow(False);dome.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
pp=ACT.spawn_actor_from_class(u.PostProcessVolume,u.Vector());pp.set_editor_property('unbound',True);s=pp.get_editor_property('settings')
for k,v in {'auto_exposure_method':u.AutoExposureMethod.AEM_MANUAL,'auto_exposure_bias':0.0,'auto_exposure_apply_physical_camera_exposure':False,'bloom_intensity':.18,'ambient_occlusion_intensity':.65,'motion_blur_amount':0.0}.items():s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
pp.set_editor_property('settings',s)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',u.load_class(None,'/Script/CupcakeCannibal.CupcakeGameMode'))
# Otter mascot on a small lilac display plinth beside the arena.
def place(sm,label,x,y,z,height,mat=None):
 a=ACT.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,z));a.set_actor_label(label)
 a.set_folder_path('Mascot');c=a.static_mesh_component;c.set_static_mesh(sm);b=sm.get_bounds();s=height/max(.001,2*b.box_extent.z)
 a.set_actor_scale3d(u.Vector(s,s,s));a.set_actor_location(u.Vector(x-b.origin.x*s,y-b.origin.y*s,z-(b.origin.z-b.box_extent.z)*s),False,False)
 c.set_collision_profile_name('BlockAll')
 if mat:c.set_material(0,EL.load_asset(mat))
 return a
stand=place(EL.load_asset('/Engine/BasicShapes/Cylinder'),'Otter lilac display stand',1150,200,-100,90,'/Game/CandyCarnival/Materials/M_Lilac')
stand.set_actor_scale3d(u.Vector(3.0,3.0,.9))
otter=place(mesh,'Otter candy carnival mascot',1150,200,-10,380)
otter.set_actor_rotation(u.Rotator(pitch=0,yaw=0,roll=0),False)
assert LEVEL.save_current_level()
mapping={'countdown':'wav/countdown_tick.wav','go':'wav/countdown_go.wav','hit':'wav/cane_hit.wav','pickup':'wav/cane_pickup.wav','sunWarn':'wav/sun_warning.wav','roundWin':'wav/round_win.wav','matchWin':'wav/match_win.wav','tiebreak':'wav/tiebreak_start.wav','introVoice':'wav/countdown_321_cupcake.wav','hurtStrawberry':'wav/hurt_strawberry.wav','hurtChocolate':'wav/hurt_chocolate.wav','music':'music/cupcake_brawl.wav'}
tasks=[]
for cue,source in mapping.items():
 t=u.AssetImportTask()
 for k,v in {'filename':os.path.join(ROOT,'audio',source),'destination_path':'/Game/Audio/Cues','destination_name':cue,'automated':True,'save':True,'replace_existing':True}.items():t.set_editor_property(k,v)
 tasks.append(t)
AT.import_asset_tasks(tasks)
assert all(t.imported_object_paths for t in tasks)
music=EL.load_asset('/Game/Audio/Cues/music');music.set_editor_property('looping',True);EL.save_loaded_asset(music)
assert EL.save_directory('/Game',only_if_is_dirty=True,recursive=True)
json.dump({'environment':'CandyCarnival reference-video map','player_height_cm':208,'otter':dest+'/SM_Otter','otter_height_cm':380,'otter_collision':'simple capsule','audio_sources':mapping,'placeholder_cues_remaining':['bite','caneSwing','melt']},open(os.path.join(ROOT,'Tests','scene-update.json'),'w'),indent=2)
u.log('CANDY_WORLD_UPDATE_COMPLETE')
