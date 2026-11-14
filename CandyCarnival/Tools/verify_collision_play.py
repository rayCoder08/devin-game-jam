"""Run saved-mesh sweep tests and drive the actual explorer into obstacles."""
import unreal as u,os,json,time,math,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTOMATED='-CandyCollisionTest' in u.SystemLibrary.get_command_line()
def finish_editor():
 if AUTOMATED:u.SystemLibrary.quit_editor()
tests=os.path.join(ROOT,'Tools','verify_collision.py')
scope={'__file__':tests,'__name__':'__main__'}
try:exec(compile(open(tests,encoding='utf-8').read(),tests,'exec'),scope,scope)
except Exception:
 u.log_error(traceback.format_exc());finish_editor();raise
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem);ED=u.get_editor_subsystem(u.UnrealEditorSubsystem)
z=(.40*math.sin(-8*.072)+.34*math.cos(-29*.087)+.20*math.sin((-8-29)*.13)+2)*100
cases=[('cane stops explorer',(-950,2900,z),(1,0,0)),('wall stops explorer',(1300,-3500,200),(-1,0,0)),('doorway admits explorer',(0,-2200,200),(0,-1,0))]
started=time.time();phase='startup';index=0;pawn=None;handle=None;results=[]
LEVEL.editor_request_begin_play()
def tick(dt):
 global started,phase,index,pawn,handle
 try:
  elapsed=time.time()-started
  if phase=='startup' and elapsed>3:
   pawn=u.GameplayStatics.get_player_pawn(ED.get_game_world(),0);assert pawn
   phase='place'
  elif phase=='place':
   name,p,d=cases[index];pawn.get_movement_component().stop_movement_immediately();pawn.set_actor_location(u.Vector(*p),False,True)
   phase='move';started=time.time()
  elif phase=='move':
   pawn.add_movement_input(u.Vector(*cases[index][2]),1,True)
   if elapsed>1.6:
    p=pawn.get_actor_location()
    passed=(p.x<=-850 if index==0 else p.x>=1020 if index==1 else p.y<-2850)
    result={'test':cases[index][0],'passed':passed,'position':[p.x,p.y,p.z]};results.append(result)
    assert passed,str(result)
    u.log('CANDY_COLLISION_PLAY '+str(result));index+=1
    if index<len(cases):phase='place'
    else:LEVEL.editor_request_end_play();phase='finish';started=time.time()
  elif phase=='finish' and elapsed>2:
   path=os.path.join(ROOT,'Tools','collision_verification.json');report=json.load(open(path));report['play_tests']=results
   json.dump(report,open(path,'w'),indent=2);u.log('CANDY_COLLISION_PLAY_VERIFIED');u.unregister_slate_post_tick_callback(handle);finish_editor()
 except Exception:
  u.log_error(traceback.format_exc());u.unregister_slate_post_tick_callback(handle)
  if LEVEL.is_in_play_in_editor():LEVEL.editor_request_end_play()
  finish_editor()
handle=u.register_slate_post_tick_callback(tick)
