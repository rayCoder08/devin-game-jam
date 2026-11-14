import unreal as u,os,json,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem)
EDITOR=u.get_editor_subsystem(u.UnrealEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
meshes=[a for a in actors if isinstance(a,u.StaticMeshActor)]
missing=[]
for a in meshes:
 c=a.static_mesh_component
 for i in range(c.get_num_materials()):
  if not c.get_material(i):missing.append(a.get_actor_label()+':'+str(i))
for a in actors:
 if isinstance(a,u.TextRenderActor):
  c=a.get_component_by_class(u.TextRenderComponent)
  u.log('CANDY_TEXT '+str(c.get_editor_property('relative_rotation'))+' font='+str(c.get_editor_property('font'))+' material='+str(c.get_material(0))+' bounds='+str(a.get_actor_bounds(False)))
report={'actors':len(actors),'static_mesh_actors':len(meshes),'cameras':sum(isinstance(a,u.CameraActor) for a in actors),'missing_materials':missing}
assert not missing
start=time.time();stage=0;pawn=None;origin=None;handle=None
LEVEL.editor_request_begin_play()
def tick(dt):
 global stage,pawn,origin,handle,start
 elapsed=time.time()-start
 if stage==0 and elapsed>3:
  gw=EDITOR.get_game_world();pawn=u.GameplayStatics.get_player_pawn(gw,0)
  report['play_started']=LEVEL.is_in_play_in_editor();report['pawn']=pawn.get_class().get_name() if pawn else None
  if not pawn:raise RuntimeError('No explorer pawn spawned')
  origin=pawn.get_actor_location();report['start']=[origin.x,origin.y,origin.z];stage=1;start=time.time()
 elif stage==1:
  pawn.add_movement_input(pawn.get_actor_forward_vector(),1,True)
  if elapsed>1.5:
   pos=pawn.get_actor_location();distance=(pos-origin).length();report['movement_distance_cm']=distance
   assert distance>100,'Explorer did not move'
   report['default_movement_bindings']=pawn.get_editor_property('add_default_movement_bindings')
   LEVEL.editor_request_end_play();stage=2;start=time.time()
 elif stage==2 and elapsed>2:
  json.dump(report,open(os.path.join(ROOT,'Tools','verification.json'),'w'),indent=2)
  u.log('CANDY_VERIFIED '+json.dumps(report));u.unregister_slate_post_tick_callback(handle);u.SystemLibrary.quit_editor()
handle=u.register_slate_post_tick_callback(tick)
