import bpy,os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'CandyCarnival','SourceArt','CandyCarnival.blend'))
obj=bpy.data.objects['SM_10_Peppermint_Gate_00']
coords=[v.co.copy() for v in obj.data.vertices]
lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
scale=1.30/(hi.z-lo.z)
for v in obj.data.vertices:v.co=(v.co-center)*scale
obj.name='SM_CandyCane';obj.data.update()
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
out=os.path.join(ROOT,'DemoSource');os.makedirs(out,exist_ok=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(out,'SM_CandyCane.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',bake_anim=False)
print('CUPCAKE_CANE_READY')
