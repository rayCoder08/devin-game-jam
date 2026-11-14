import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem);level.load_level('/Game/Maps/CakeLand')
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,u.PostProcessVolume):
  s=a.get_editor_property('settings')
  for k,v in {'auto_exposure_apply_physical_camera_exposure':False,'auto_exposure_bias':0.3,'bloom_intensity':.18,'ambient_occlusion_intensity':.6}.items():
   s.set_editor_property('override_'+k,True);s.set_editor_property(k,v)
  a.set_editor_property('settings',s)
 if isinstance(a,u.SkyLight):a.light_component.set_mobility(u.ComponentMobility.MOVABLE);a.light_component.set_editor_property('intensity',1.6)
 if isinstance(a,u.DirectionalLight):a.light_component.set_mobility(u.ComponentMobility.MOVABLE)
assert level.save_current_level()
u.log('CUPCAKE_MAP_POLISHED')
