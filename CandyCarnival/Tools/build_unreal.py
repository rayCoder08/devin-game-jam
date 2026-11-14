"""Run in UE 5.6 using -ExecutePythonScript. Imports assets and saves an editable map."""
import unreal as u
import os, json, math, traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=json.load(open(os.path.join(ROOT,'SourceArt','manifest.json')))
BASE='/Game/CandyCarnival'
AT=u.AssetToolsHelpers.get_asset_tools()
EL=u.EditorAssetLibrary
ML=u.MaterialEditingLibrary
ACT=u.get_editor_subsystem(u.EditorActorSubsystem)
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)
def prop(o,k,v):o.set_editor_property(k,v)
def expr(m,cls,x=0,y=0):return ML.create_material_expression(m,cls,x,y)
def scalar(m,value,x=-300,y=100):
 n=expr(m,u.MaterialExpressionConstant,x,y);prop(n,'r',value);return n
def color(m,value,x=-450,y=0):
 n=expr(m,u.MaterialExpressionConstant3Vector,x,y);prop(n,'constant',u.LinearColor(*value,1));return n
def connect(a,out,b,inp):
 if ML.connect_material_expressions(a,out,b,inp):return
 pins=ML.get_material_expression_input_names(b)
 if len(pins)==1 and ML.connect_material_expressions(a,out,b,str(pins[0])):return
 raise RuntimeError('Cannot connect material pin '+inp+' on '+str(b))
materials={}
def create_material(name,c,rough):
 path=BASE+'/Materials/M_'+name
 if EL.does_asset_exist(path):
  materials[name]=EL.load_asset(path);return
 m=EL.load_asset(path) if EL.does_asset_exist(path) else AT.create_asset('M_'+name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
 ML.delete_all_material_expressions(m)
 prop(m,'two_sided',True)
 base=color(m,c);output=base
 if name not in ('Ink','Bulb','Sky','Cloud'):
  noise=expr(m,u.MaterialExpressionNoise,-900,-200);prop(noise,'scale',.15 if rough>.6 else .035);prop(noise,'levels',2);prop(noise,'quality',1);prop(noise,'output_min',0);prop(noise,'output_max',1)
  dark=color(m,[v*.84 for v in c],-450,-140)
  lerp=expr(m,u.MaterialExpressionLinearInterpolate,-150,0);connect(dark,'',lerp,'A');connect(base,'',lerp,'B');connect(noise,'',lerp,'Alpha');output=lerp
 ML.connect_material_property(output,'',u.MaterialProperty.MP_BASE_COLOR)
 ML.connect_material_property(scalar(m,rough),'',u.MaterialProperty.MP_ROUGHNESS)
 ML.connect_material_property(scalar(m,.35,-300,200),'',u.MaterialProperty.MP_SPECULAR)
 if name=='Gold':ML.connect_material_property(scalar(m,.55,-300,300),'',u.MaterialProperty.MP_METALLIC)
 if name=='Bulb':
  em=color(m,[v*3 for v in c],-300,400);ML.connect_material_property(em,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
 ML.recompile_material(m);EL.save_loaded_asset(m);materials[name]=m
for name,(c,r) in DATA['materials'].items():create_material(name,c,r)
u.log('CANDY_MATERIALS_COMPLETE')

# Force stable legacy FBX importing so filenames and material slots remain deterministic.
u.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
assets=[]
for entry in DATA['assets']:
 path=BASE+'/Meshes/'+entry['name']
 source_file=os.path.join(ROOT,'SourceArt','Meshes',entry['file'])
 asset_file=os.path.join(ROOT,'Content','CandyCarnival','Meshes',entry['name']+'.uasset')
 if EL.does_asset_exist(path) and os.path.getmtime(asset_file)>=os.path.getmtime(source_file):sm=EL.load_asset(path)
 else:
  task=u.AssetImportTask();prop(task,'filename',os.path.join(ROOT,'SourceArt','Meshes',entry['file']));prop(task,'destination_path',BASE+'/Meshes');prop(task,'destination_name',entry['name']);prop(task,'automated',True);prop(task,'save',True);prop(task,'replace_existing',True)
  options=u.FbxImportUI();prop(options,'import_mesh',True);prop(options,'import_as_skeletal',False);prop(options,'import_materials',False);prop(options,'import_textures',False);prop(options,'automated_import_should_detect_type',False);prop(options,'mesh_type_to_import',u.FBXImportType.FBXIT_STATIC_MESH)
  sd=options.static_mesh_import_data
  for k,v in {'combine_meshes':True,'auto_generate_collision':False,'generate_lightmap_u_vs':False,'convert_scene':True,'convert_scene_unit':True,'force_front_x_axis':False,'transform_vertex_to_absolute':True,'normal_import_method':u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS}.items():prop(sd,k,v)
  prop(task,'options',options);prop(task,'factory',u.FbxFactory());AT.import_asset_tasks([task])
  paths=task.get_editor_property('imported_object_paths');sm=EL.load_asset(paths[0]) if paths else EL.load_asset(path)
 if not sm:raise RuntimeError('Import failed: '+entry['name'])
 slots=sm.get_editor_property('static_materials')
 for i,s in enumerate(slots):
  sn=str(s.get_editor_property('imported_material_slot_name'))
  key=sn if sn in materials else str(s.get_editor_property('material_slot_name'))
  if key not in materials:
   key=next((n for n in materials if sn.startswith(n)),None)
  if key:sm.set_material(i,materials[key])
  else:u.log_warning('Unknown material slot: '+sn)
 body=sm.get_editor_property('body_setup')
 if body:prop(body,'collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 EL.save_loaded_asset(sm);assets.append((entry,sm))
 u.log('CANDY_IMPORTED '+entry['name']+' bounds='+str(sm.get_bounds()))

MAP=BASE+'/Maps/CandyCarnival'
if EL.does_asset_exist(MAP):
 LEVEL.load_level(MAP)
 ACT.destroy_actors(ACT.get_all_level_actors())
else:LEVEL.new_level(MAP)
def spawn(cls,label,loc=(0,0,0),rot=None,folder=None):
 a=ACT.spawn_actor_from_class(cls,u.Vector(*loc),rot or u.Rotator());a.set_actor_label(label)
 if folder:a.set_folder_path(folder)
 return a
for entry,sm in assets:
 a=spawn(u.StaticMeshActor,entry['name'][3:],folder='Scenery/'+entry['name'][3:5]);c=a.static_mesh_component;c.set_static_mesh(sm)
 c.set_mobility(u.ComponentMobility.STATIC);c.set_collision_profile_name('BlockAll')
 if 'Cloud' in entry['name']:c.set_cast_shadow(False);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)

# Coordinates are determined from an asymmetric imported landmark rather than guessed.
hero=next(sm for e,sm in assets if e['name']=='SM_05_Grand_Bonbon_Pavilion')
center=hero.get_bounds().origin
u.log('CANDY_HERO_CENTER '+str(center))
# FBX preserves X and reflects Y under the legacy importer. Detect that here.
if abs(center.y)>abs(center.x):
 YSIGN=1 if center.y>0 else -1
 def xyz(x,y,z):return (x*100,y*100*YSIGN,z*100)
else:
 XSIGN=1 if center.x>0 else -1
 def xyz(x,y,z):return (y*100*XSIGN,x*100,z*100)

sun=spawn(u.DirectionalLight,'Warm afternoon sunlight',rot=u.Rotator(pitch=-32,yaw=0,roll=0),folder='Lighting')
lc=sun.get_component_by_class(u.DirectionalLightComponent);lc.set_mobility(u.ComponentMobility.MOVABLE);lc.set_intensity(3.4);lc.set_light_color(u.LinearColor(1,.91,.79));prop(lc,'light_source_angle',3.5);prop(lc,'dynamic_shadow_distance_movable_light',20000)
sky=spawn(u.SkyLight,'Soft turquoise sky fill',folder='Lighting');sc=sky.get_component_by_class(u.SkyLightComponent);sc.set_mobility(u.ComponentMobility.MOVABLE);sc.set_intensity(2.3)
cube=EL.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap.DaylightAmbientCubemap')
if cube:prop(sc,'source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP);sc.set_cubemap(cube)
prop(sc,'lower_hemisphere_is_black',False)
sc.set_light_color(u.LinearColor(.84,.92,1))

# A clean illustrated sky gradient with physically shaded scene assets.
sky_mat=EL.load_asset(BASE+'/Materials/M_CandySky') if EL.does_asset_exist(BASE+'/Materials/M_CandySky') else AT.create_asset('M_CandySky',BASE+'/Materials',u.Material,u.MaterialFactoryNew())
ML.delete_all_material_expressions(sky_mat)
prop(sky_mat,'two_sided',True);prop(sky_mat,'shading_model',u.MaterialShadingModel.MSM_UNLIT)
wn=expr(sky_mat,u.MaterialExpressionWorldPosition,-800,0);mask=expr(sky_mat,u.MaterialExpressionComponentMask,-600,0)
for k in ('r','g','a'):prop(mask,k,False)
prop(mask,'b',True);connect(wn,'',mask,'Input')
scale=expr(sky_mat,u.MaterialExpressionMultiply,-450,0);prop(scale,'const_b',.000015);connect(mask,'',scale,'A')
add=expr(sky_mat,u.MaterialExpressionAdd,-300,0);prop(add,'const_b',.25);connect(scale,'',add,'A');sat=expr(sky_mat,u.MaterialExpressionSaturate,-170,0);connect(add,'',sat,'Input')
lerp=expr(sky_mat,u.MaterialExpressionLinearInterpolate,0,0);connect(color(sky_mat,(.70,.86,.90)),'',lerp,'A');connect(color(sky_mat,(.10,.45,.73)),'',lerp,'B');connect(sat,'',lerp,'Alpha');ML.connect_material_property(lerp,'',u.MaterialProperty.MP_EMISSIVE_COLOR);ML.recompile_material(sky_mat);EL.save_loaded_asset(sky_mat)
dome=spawn(u.StaticMeshActor,'Turquoise sky gradient',folder='Lighting');dome.static_mesh_component.set_static_mesh(EL.load_asset('/Engine/BasicShapes/Sphere.Sphere'));dome.set_actor_scale3d(u.Vector(1500,1500,1500));dome.static_mesh_component.set_material(0,sky_mat);dome.static_mesh_component.set_cast_shadow(False);dome.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)

pp=spawn(u.PostProcessVolume,'Candy color and soft contact shadows',folder='Lighting');prop(pp,'unbound',True)
ps=pp.get_editor_property('settings')
for k,v in {'auto_exposure_method':u.AutoExposureMethod.AEM_MANUAL,'auto_exposure_bias':0.0,'auto_exposure_apply_physical_camera_exposure':False,'bloom_intensity':.18,'ambient_occlusion_intensity':.65,'ambient_occlusion_radius':120.0,'ambient_occlusion_quality':80.0,'vignette_intensity':.10,'motion_blur_amount':0.0}.items():prop(ps,'override_'+k,True);prop(ps,k,v)
prop(pp,'settings',ps)
def camera(label,eye,target,fov):
 loc=u.Vector(*xyz(*eye));rot=u.MathLibrary.find_look_at_rotation(loc,u.Vector(*xyz(*target)))
 a=spawn(u.CameraActor,label,(loc.x,loc.y,loc.z),rot,'Cameras');a.camera_component.set_field_of_view(fov);prop(a.camera_component,'aspect_ratio',16/9);return a
hero_cam=camera('01 - Candy Valley Hero',(18,-53,17),(-1,22,8),61)
camera('02 - Along the Peppermint Path',(-1,-26,3.1),(0,29,9),67)
camera('03 - Candy Apple Grove',(29,-29,7),(9,13,6),63)
camera('04 - Festival Overlook',(46,-36,40),(0,16,3),60)
start=spawn(u.PlayerStart,'Explore from the golden path',xyz(1,-38,2.2),u.MathLibrary.find_look_at_rotation(u.Vector(*xyz(1,-38,2)),u.Vector(*xyz(0,35,2))),'Gameplay')
# DefaultPawn supplies mouse look + WASD flight without requiring compiled code.
world=LEVEL.get_current_level().get_outer() if False else u.EditorLevelLibrary.get_editor_world()
factory=u.BlueprintFactory();prop(factory,'parent_class',u.GameModeBase)
gm=EL.load_asset(BASE+'/Blueprints/BP_CarnivalExplore') if EL.does_asset_exist(BASE+'/Blueprints/BP_CarnivalExplore') else AT.create_asset('BP_CarnivalExplore',BASE+'/Blueprints',u.Blueprint,factory)
if gm:
 defaults=u.get_default_object(gm.generated_class());prop(defaults,'default_pawn_class',u.DefaultPawn)
 prop(world.get_world_settings(),'default_game_mode',gm.generated_class());EL.save_loaded_asset(gm)
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(hero_cam.get_actor_location(),hero_cam.get_actor_rotation())
LEVEL.save_current_level();EL.save_directory(BASE,only_if_is_dirty=True,recursive=True)
polish=os.path.join(ROOT,'Tools','polish_unreal.py')
polish_scope={'__file__':polish,'__name__':'__main__'}
exec(compile(open(polish,encoding='utf-8').read(),polish,'exec'),polish_scope,polish_scope)
if os.path.exists(os.path.join(ROOT,'SourceArt','collision_manifest.json')):
 collision_script=os.path.join(ROOT,'Tools','apply_collision.py')
 collision_scope={'__file__':collision_script,'__name__':'__main__'}
 exec(compile(open(collision_script,encoding='utf-8').read(),collision_script,'exec'),collision_scope,collision_scope)
hero_pos=hero_cam.get_actor_location()
summary={'map':MAP,'actors':len(ACT.get_all_level_actors()),'meshes':len(assets),'materials':len(materials)+1,'triangles':sum(e['triangles'] for e in DATA['assets']),'hero_camera':[hero_pos.x,hero_pos.y,hero_pos.z],'hero_rotation':str(hero_cam.get_actor_rotation())}
json.dump(summary,open(os.path.join(ROOT,'Tools','build_report.json'),'w'),indent=2)
u.log('CANDY_BUILD_COMPLETE '+json.dumps(summary))
