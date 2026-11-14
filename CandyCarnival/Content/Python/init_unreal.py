"""Optional automated preview pass; normal editor launches are unaffected."""
import unreal, os, time
if any(flag in unreal.SystemLibrary.get_command_line() for flag in ('-CandyCapture','-CandyVerify','-CandyCollisionTest')):
 _candy_begin=time.time()
 _candy_handle=None
 def _candy_start(dt):
  global _candy_handle
  if time.time()-_candy_begin<4:return
  unreal.unregister_slate_post_tick_callback(_candy_handle)
  filename='verify_collision_play.py' if '-CandyCollisionTest' in unreal.SystemLibrary.get_command_line() else ('verify_unreal.py' if '-CandyVerify' in unreal.SystemLibrary.get_command_line() else 'capture_unreal.py')
  script=os.path.abspath(os.path.join(unreal.Paths.project_dir(),'Tools',filename))
  scope={'__file__':script,'__name__':'__main__'}
  exec(compile(open(script,encoding='utf-8').read(),script,'exec'),scope,scope)
 _candy_handle=unreal.register_slate_post_tick_callback(_candy_start)
