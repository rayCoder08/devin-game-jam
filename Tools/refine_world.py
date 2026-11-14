import unreal as u
L=u.get_editor_subsystem(u.LevelEditorSubsystem);A=u.get_editor_subsystem(u.EditorActorSubsystem)
assert L.load_level('/Game/Maps/CandyWorld')
for a in A.get_all_level_actors():
 if a.get_actor_label()=='Otter candy carnival mascot':
  u.log('OTTER_PREVIOUS_ROTATION '+str(a.get_actor_rotation()))
  a.set_actor_rotation(u.Rotator(pitch=0,yaw=0,roll=0),False)
  center,extent=a.get_actor_bounds(False)
  a.set_actor_location(a.get_actor_location()+u.Vector(1150-center.x,200-center.y,-10-(center.z-extent.z)),False,False)
 if a.get_actor_label()=='Otter lilac display stand':a.set_actor_location(u.Vector(1150,200,-55),False,False)
assert L.save_current_level()
u.log('CANDY_WORLD_REFINED')
