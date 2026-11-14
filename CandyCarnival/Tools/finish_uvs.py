"""Add stable per-face box UVs to the generated source assets before reimport."""
import bpy,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'SourceArt','CandyCarnival.blend'))
for obj in list(bpy.context.scene.objects):
 if obj.type!='MESH':continue
 me=obj.data;uv=me.uv_layers.active or me.uv_layers.new(name='UVMap')
 for face in me.polygons:
  n=face.normal;axis=max(range(3),key=lambda a:abs(n[a]));axes=[a for a in range(3) if a!=axis]
  for li in face.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co
   uv.data[li].uv=(co[axes[0]]*.25,co[axes[1]]*.25)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'SourceArt','Meshes',obj.name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',bake_anim=False,mesh_smooth_type='FACE',use_mesh_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'SourceArt','CandyCarnival.blend'))
print('CANDY_UVS_COMPLETE',flush=True)
