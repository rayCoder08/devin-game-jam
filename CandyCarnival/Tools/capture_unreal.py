"""UE editor screenshot pass. Run after building the map; ticks allow rendering to settle."""
import unreal as u
import os,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/CandyCarnival/Maps/CandyCarnival')
polish=os.path.join(ROOT,'Tools','polish_unreal.py')
scope={'__file__':polish,'__name__':'__main__'}
exec(compile(open(polish,encoding='utf-8').read(),polish,'exec'),scope,scope)
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
cameras=sorted([a for a in actors if isinstance(a,u.CameraActor)],key=lambda a:a.get_actor_label())
start=time.time();stage=0;handle=None;task=None;next_at=start+12
world=u.EditorLevelLibrary.get_editor_world()
for cmd in ['r.ScreenPercentage 100','r.Shadow.MaxResolution 2048','r.PostProcessAAQuality 6','r.SSR.Quality 3']:
 u.SystemLibrary.execute_console_command(world,cmd)
def tick(dt):
 global stage,handle,start,task,next_at
 now=time.time()
 if task is not None:
  if task.is_task_done():
   u.log('CANDY_CAPTURE_FINISHED '+str(stage));task=None;stage+=1;next_at=now+5
  return
 if stage<len(cameras) and now>next_at:
  cam=cameras[stage]
  u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
  filename=os.path.join(ROOT,'Previews',['CandyCarnival_Hero.png','CandyCarnival_Path.png','CandyCarnival_Apples.png','CandyCarnival_Overview.png'][stage])
  u.log('CANDY_CAPTURE_REQUEST '+filename)
  task=u.AutomationLibrary.take_high_res_screenshot(1920,1080,filename,camera=cam,delay=2.0)
 elif stage==len(cameras) and now>next_at:
  u.unregister_slate_post_tick_callback(handle)
  u.log('CANDY_CAPTURE_COMPLETE')
  u.SystemLibrary.quit_editor()
handle=u.register_slate_post_tick_callback(tick)
