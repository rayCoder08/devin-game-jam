"""Final sky, soft fill, marquee and saved presentation adjustments."""
import unreal as u
import os,json
ML=u.MaterialEditingLibrary;EL=u.EditorAssetLibrary
BASE='/Game/CandyCarnival';ACT=u.get_editor_subsystem(u.EditorActorSubsystem)
def setp(o,k,v):o.set_editor_property(k,v)
def ex(m,c,x=0,y=0):return ML.create_material_expression(m,c,x,y)
def rgb(m,c):
 e=ex(m,u.MaterialExpressionConstant3Vector);setp(e,'constant',u.LinearColor(*c,1));return e
def wire(a,b,p=''):
 pins=ML.get_material_expression_input_names(b)
 if p not in pins and len(pins)==1:p=str(pins[0])
 if not ML.connect_material_expressions(a,'',b,p):raise RuntimeError('Material wire failed '+str(pins))
m=EL.load_asset(BASE+'/Materials/M_CandySky');ML.delete_all_material_expressions(m)
setp(m,'two_sided',True);setp(m,'shading_model',u.MaterialShadingModel.MSM_UNLIT)
pos=ex(m,u.MaterialExpressionWorldPosition);mask=ex(m,u.MaterialExpressionComponentMask)
for k in ('r','g','a'):setp(mask,k,False)
setp(mask,'b',True);wire(pos,mask)
mul=ex(m,u.MaterialExpressionMultiply);setp(mul,'const_b',.000018);wire(mask,mul,'A')
add=ex(m,u.MaterialExpressionAdd);setp(add,'const_b',.18);wire(mul,add,'A')
sat=ex(m,u.MaterialExpressionSaturate);wire(add,sat)
lerp=ex(m,u.MaterialExpressionLinearInterpolate);wire(rgb(m,(.58,.82,.92)),lerp,'A');wire(rgb(m,(.065,.40,.72)),lerp,'B');wire(sat,lerp,'Alpha')
assert ML.connect_material_property(lerp,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
ML.recompile_material(m);EL.save_loaded_asset(m)
# A little emissive fill preserves a soft marshmallow cloud silhouette.
cloud=EL.load_asset(BASE+'/Materials/M_Cloud');ML.delete_all_material_expressions(cloud)
ML.connect_material_property(rgb(cloud,(1,.97,.92)),'',u.MaterialProperty.MP_BASE_COLOR)
ML.connect_material_property(rgb(cloud,(.36,.40,.43)),'',u.MaterialProperty.MP_EMISSIVE_COLOR)
rough=ex(cloud,u.MaterialExpressionConstant);setp(rough,'r',1);ML.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
ML.recompile_material(cloud);EL.save_loaded_asset(cloud)
actors=ACT.get_all_level_actors()
for a in actors:
 if isinstance(a,u.SkyLight):
  a.light_component.set_intensity(2.3);a.light_component.set_light_color(u.LinearColor(1,.98,.96))
 # Avoid adding duplicates on repeat captures.
 if a.get_actor_label().startswith('Marquee -'):ACT.destroy_actor(a)
def spawn(cls,label,pos):
 a=ACT.spawn_actor_from_class(cls,u.Vector(*pos));a.set_actor_label(label);a.set_folder_path('Scenery/05');return a
for label,p,scale,material in [('Marquee - gilt oval',(0,-2460,1080),(7,.30,1.8),'Gold'),('Marquee - raspberry enamel',(0,-2437,1080),(6.65,.18,1.52),'Raspberry')]:
 a=spawn(u.StaticMeshActor,label,p)
 collision_mesh=EL.load_asset(BASE+'/Meshes/SM_MarqueeCollision') if EL.does_asset_exist(BASE+'/Meshes/SM_MarqueeCollision') else None
 a.static_mesh_component.set_static_mesh(collision_mesh or EL.load_asset('/Engine/BasicShapes/Sphere.Sphere'));a.set_actor_scale3d(u.Vector(*scale));a.static_mesh_component.set_material(0,EL.load_asset(BASE+'/Materials/M_'+material))
 if collision_mesh:a.static_mesh_component.set_collision_profile_name('BlockAll');a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS)
 else:a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
text=spawn(u.TextRenderActor,'Marquee - Candy Carnival',(0,-2423,1064));text.set_actor_rotation(u.Rotator(pitch=0,yaw=90,roll=0),False)
tc=text.get_component_by_class(u.TextRenderComponent);tc.set_text('CANDY CARNIVAL');tc.set_world_size(46);tc.set_text_render_color(u.Color(255,239,192));tc.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report_path=os.path.join(u.Paths.project_dir(),'Tools','build_report.json')
if os.path.exists(report_path):
 report=json.load(open(report_path));report['actors']=len(ACT.get_all_level_actors());report['polish']='Sky gradient, soft fill, marshmallow clouds, gold marquee';json.dump(report,open(report_path,'w'),indent=2)
u.log('CANDY_POLISH_COMPLETE')
