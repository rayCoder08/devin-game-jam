"""Generate original reusable geometry and export grouped FBX scenery. Blender 5.x."""
import bpy, math, random, json, os
from mathutils import Vector
from math import sin, cos, pi
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'SourceArt', 'Meshes')
os.makedirs(OUT, exist_ok=True)
random.seed(1411)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=1.0
PALETTE = {
 'StrawberrySugar': ((.72,.24,.36),.82), 'RoseHill': ((.57,.18,.30),.9),
 'BlushHill': ((.91,.40,.49),.87), 'GoldenBiscuit': ((.91,.57,.19),.67),
 'Caramel': ((.43,.105,.035),.26), 'Cream': ((1,.88,.68),.43),
 'Vanilla': ((1,.96,.86),.36), 'Raspberry': ((.72,.025,.10),.24),
 'AppleGlaze': ((.69,.012,.044),.16), 'AppleFlesh': ((.98,.71,.35),.57),
 'Mint': ((.15,.62,.43),.43), 'Aqua': ((.08,.47,.59),.36),
 'Lavender': ((.42,.25,.64),.52), 'Lilac': ((.69,.49,.79),.57),
 'Gold': ((.94,.57,.13),.29), 'Chocolate': ((.15,.047,.026),.4),
 'Ink': ((.04,.014,.022),.3), 'Coral': ((1,.26,.30),.4),
 'Popcorn': ((1,.84,.42),.7), 'Cloud': ((1,.96,.90),1.0),
 'Bulb': ((1,.74,.35),.25), 'Sky': ((.20,.63,.85),1)
}
M={}
for name,(color,rough) in PALETTE.items():
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough
 M[name]=m
groups={}; current=''
def group(name):
 global current
 current=name; groups.setdefault(name,[])
 print('BUILDING',name,flush=True)
def finish(o,mat):
 o.data.materials.append(M[mat]); groups[current].append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def mesh(name,verts,faces,mat,indices=None,mats=None):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o)
 finish(o,mat)
 if mats:
  for m in mats:o.data.materials.append(M[m])
 if indices:
  for p,i in zip(o.data.polygons,indices):p.material_index=i
 return o
def ball(p,s,mat,seg=20,rings=12):
 v=[];f=[]
 for j in range(rings+1):
  t=pi*j/rings
  for i in range(seg):
   a=2*pi*i/seg;v.append((s[0]*sin(t)*cos(a),s[1]*sin(t)*sin(a),s[2]*cos(t)))
 for j in range(rings):
  for i in range(seg):a=j*seg+i;b=j*seg+(i+1)%seg;f.append((a,a+seg,b+seg,b))
 o=mesh('Soft_round_form',v,f,mat);o.location=p;return o
def rod(a,b,r,mat,vertices=12,r2=None):
 a,b=Vector(a),Vector(b); d=b-a
 q=d.to_track_quat('Z','Y');v=[];f=[]
 for j,rr in enumerate((r,r if r2 is None else r2)):
  for i in range(vertices):t=2*pi*i/vertices;v.append(a+q@Vector((rr*cos(t),rr*sin(t),j*d.length)))
 for i in range(vertices):k=(i+1)%vertices;f.append((i,k,k+vertices,i+vertices))
 f.append(tuple(reversed(range(vertices))));f.append(tuple(range(vertices,vertices*2)))
 return mesh('Candy_rod',v,f,mat)
def tube(points,r,mat,sides=10):
 vs=[];fs=[]
 for i,p in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
  t=tangent.normalized();ref=Vector((0,1,0)) if abs(t.y)<.92 else Vector((1,0,0));u=t.cross(ref).normalized();v=t.cross(u).normalized()
  for j in range(sides):vs.append(Vector(p)+r*(u*cos(2*pi*j/sides)+v*sin(2*pi*j/sides)))
 for i in range(len(points)-1):
  for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;fs.append((a,b,b+sides,a+sides))
 return mesh('Piped_detail',vs,fs,mat)
def torus(p,major,minor,mat,rotation=(0,0,0)):
 v=[];f=[];n=48;k=10
 for i in range(n):
  a=i*2*pi/n
  for j in range(k):b=j*2*pi/k;v.append(((major+minor*cos(b))*cos(a),(major+minor*cos(b))*sin(a),minor*sin(b)))
 for i in range(n):
  for j in range(k):f.append((i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k))
 o=mesh('Candy_ring',v,f,mat);o.location=p;o.rotation_euler=rotation;return o
def ground_z(x,y):return .40*sin(x*.072)+.34*cos(y*.087)+.20*sin((x+y)*.13)
def surface(x,y,dz=0):return (x,y,ground_z(x,y)+dz)
def pathx(y):return 5*sin((y+28)*.075)*max(0,min(1,(34-y)/16))
def ribbon(name,offset,width,mat,lift):
 vs=[];fs=[]
 for i in range(241):
  y=-70+i*108/240;x=pathx(y)
  for j in range(7):
   xx=x+offset+width*(j/6-.5);vs.append((xx,y,ground_z(xx,y)+lift+.035*sin(j*pi/6)))
 for i in range(240):
  for j in range(6):a=i*7+j;fs.append((a,a+1,a+8,a+7))
 mesh(name,vs,fs,mat)
group('01_Strawberry_Meadow')
vs=[];fs=[];n=100
for j in range(n+1):
 y=-80+j*180/n
 for i in range(n+1):
  x=-90+i*180/n;vs.append((x,y,ground_z(x,y)))
for j in range(n):
 for i in range(n):a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
mesh('Rolling_sugar_ground',vs,fs,'StrawberrySugar')
group('02_Winding_Biscuit_Path');ribbon('Golden_path',0,5.8,'GoldenBiscuit',.08)
group('03_Caramel_Stream');ribbon('Caramel_ribbon',-4.25,2.6,'Caramel',.075)
group('04_Distant_Sherbet_Hills')
for i in range(24):
 a=2*pi*i/24;x=68*cos(a);y=12+72*sin(a)
 ball(surface(x,y,-1),(random.uniform(12,23),random.uniform(15,24),random.uniform(6,15)),['RoseHill','BlushHill','Lilac'][i%3],32,16)

def tent(name,x,y,r,h,peak,c1,c2,main=False):
 group(name);z=ground_z(x,y)
 # Tensioned fabric roof: concave swoop and slightly scalloped hem.
 n=128; nr=18;v=[];f=[];ids=[]
 for j in range(nr+1):
  t=j/nr;rr=.08+r*t;zz=h+(peak-h)*(1-t)**2.0
  for i in range(n+1):
   a=2*pi*i/n;v.append((x+rr*cos(a),y+rr*sin(a),z+zz-.18*sin(a*16)**2*t**8))
 for j in range(nr):
  for i in range(n):a=j*(n+1)+i;f.append((a,a+n+1,a+n+2,a+1));ids.append((i//8)%2)
 mesh('Striped_silk_canopy',v,f,c1,ids,[c2])
 # Wide upper scallops, gold piping and radial seams.
 for k in range(16):
  a=2*pi*k/16;pts=[]
  for q in range(13):
   b=a+2*pi/16*q/12;pts.append((x+r*cos(b),y+r*sin(b),z+h-.25-.65*sin(pi*q/12)))
  vv=[(p[0],p[1],z+h) for p in pts]+pts;ff=[(i,i+1,i+14,i+13) for i in range(12)]
  mesh('Scalloped_valance',vv,ff,c1 if k%2==0 else c2);tube(pts,.065,'Gold',8)
  a+=pi/16
  seam=[]
  for j in range(21):
   t=j/20;rr=.08+r*t;seam.append((x+rr*cos(a),y+rr*sin(a),z+h+(peak-h)*(1-t)**2+.035))
  tube(seam,.035,'Cream',6)
 # Walls with a generous entrance opening facing negative Y.
 if main:
  v=[];f=[];ids=[]
  for i in range(128):
   a=2*pi*i/128;b=2*pi*(i+1)/128
   if abs(math.atan2(sin((a+b)/2+pi/2),cos((a+b)/2+pi/2)))<.38:continue
   p=len(v);rr=r*.90
   v.extend([(x+rr*cos(a),y+rr*sin(a),z),(x+rr*cos(b),y+rr*sin(b),z),(x+rr*cos(b),y+rr*sin(b),z+h-.25),(x+rr*cos(a),y+rr*sin(a),z+h-.25)])
   f.append((p,p+1,p+2,p+3));ids.append((i//8)%2)
  mesh('Striped_tent_walls',v,f,c1,ids,[c2])
  # Framed welcoming entrance, gathered curtain lobes.
  ey=y-r*.9-.1;w=r*.34;eh=h*.68
  pts=[(x-w,ey,z+t*eh/15) for t in range(16)]
  pts += [(x-w*cos(pi*t/36),ey,z+eh+w*sin(pi*t/36)) for t in range(37)]
  pts += [(x+w,ey,z+eh*(1-t/15)) for t in range(16)]
  tube(pts,.23,'Cream',12);tube([(p[0],p[1]-.11,p[2]) for p in pts],.085,'Gold',8)
  for side in (-1,1):
   for k in range(3):ball((x+side*(w+.2+k*.30),ey+.13,z+h*.47),( .45,.45,h*.46),'Raspberry',20,16)
   torus((x+side*(w+.55),ey-.2,z+eh*.5),.53,.10,'Gold',(pi/2,0,0))
  rod((x,y,z+.05),(x,y,z+.30),r*.9,'GoldenBiscuit',64)
 else:
  for i in range(8):
   a=i*2*pi/8;px=x+r*.9*cos(a);py=y+r*.9*sin(a)
   rod((px,py,z),(px,py,z+h),.11,'Cream')
  rod((x,y,z+.35),(x,y,z+.7),r*.77,'Cream',48)
  rod((x,y,z+.7),(x,y,z+1.85),r*.68,c1,48)
  rod((x,y,z+1.85),(x,y,z+2),r*.72,'GoldenBiscuit',48)
 # Finial and flowing flag.
 rod((x,y,z+peak-.2),(x,y,z+peak+2.9),.09,'Gold');ball((x,y,z+peak+.25),(.35,.35,.4),'Gold')
 v=[];f=[]
 for i in range(17):
  t=i/16
  for j in range(2):v.append((x+t*2.8,y+.30*sin(t*6),z+peak+2.6-j*(1-t*.7)*1.2-.25*t))
 for i in range(16):f.append((2*i,2*i+2,2*i+3,2*i+1))
 mesh('Silk_pennant',v,f,'Gold')
 # Decorative marquee bulbs around eave.
 for i in range(48 if main else 24):
  a=2*pi*i/(48 if main else 24);ball((x+r*cos(a),y+r*sin(a),z+h-.18),(.095,.095,.11),'Bulb',10,6)
tent('05_Grand_Bonbon_Pavilion',0,35,11,9,23,'Vanilla','Raspberry',True)
tent('06_Lavender_Macaron_Stall',-23,22,5.1,5.2,11.5,'Lavender','Lilac')
tent('07_Peach_Popcorn_Stall',23,27,5.5,5.6,12,'Coral','Cream')
tent('08_Mint_Sweetshop',-24,43,4.5,5,10.5,'Aqua','Mint')
tent('09_Berry_Sweetshop',25,48,4.8,5.3,11.6,'Raspberry','Cream')

def cane(name,x,y,h,r,turn=0):
 group(name);z=ground_z(x,y);points=[]
 for i in range(41):points.append(Vector((0,0,h*i/40)))
 for i in range(1,49):
  a=pi*i/48;points.append(Vector((r*(1-cos(a)),0,h+r*sin(a))))
 # One smooth tube with a diagonal helical stripe, not stacked rings.
 n=24;v=[];f=[];idx=[]
 for i,p in enumerate(points):
  t=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized();u=Vector((0,1,0));w=t.cross(u)
  for j in range(n+1):
   a=2*pi*j/n+i*.22;q=p+.24*(u*cos(a)+w*sin(a));v.append((x+q.x*cos(turn)-q.y*sin(turn),y+q.x*sin(turn)+q.y*cos(turn),z+q.z))
 for i in range(len(points)-1):
  for j in range(n):a=i*(n+1)+j;f.append((a,a+1,a+n+2,a+n+1));idx.append(1 if j%12<5 else 0)
 mesh('Peppermint_hook',v,f,'Vanilla',idx,['Raspberry'])
 rod(surface(x,y),surface(x,y,.18),.55,'Gold',32)
for i,(x,y,h,r,t) in enumerate([(-8,-29,6.5,1.8,0),(8,-27,7.5,2,pi),(-9,-4,8,2,0),(10,1,7.7,1.9,pi),(-10,20,8.7,2.1,0),(11,20,8.7,2.1,pi)]):cane('10_Peppermint_Gate_%02d'%i,x,y,h,r,t)

def apple(name,x,y,s=1,bite=False):
 group(name);z=ground_z(x,y);h=4.5*s;R=2.05*s
 rod((x,y,z),(x+.15*s,y,z+h+1.7*s),.16*s,'GoldenBiscuit',16)
 # Lobed silhouette, dimpled crown and glossy sugar shell.
 v=[];f=[];nu=64;nv=40
 for j in range(nv+1):
  t=pi*j/nv
  for i in range(nu+1):
   a=2*pi*i/nu;rr=R*sin(t)*(1+.045*cos(5*a)*sin(t));zz=R*cos(t)*.94
   zz-=.32*s*math.exp(-(t/.28)**2)
   v.append((x+rr*cos(a),y+rr*sin(a),z+h+zz))
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;f.append((a,a+nu+1,a+nu+2,a+1))
 o=mesh('Candied_apple',v,f,'AppleGlaze')
 if bite:
  # Three overlapping real bites expose a pale interior surface.
  o.data.materials.append(M['AppleFlesh'])
  for dx,dz,rad in [(1.65,.55,.93),(1.74,-.12,.74),(1.15,1.12,.72)]:
   cut=ball((x+dx*s,y-1.14*s,z+h+dz*s),(rad*s,rad*s,rad*s),'AppleFlesh',32,20)
   mod=o.modifiers.new('Scalloped_bite','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;mod.solver='EXACT';mod.material_mode='TRANSFER'
   bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
   groups[current].remove(cut);bpy.data.objects.remove(cut,do_unlink=True)
 # Wooden stick above fruit, mint candy leaf, pooled sugar foot.
 rod((x,y,z+h+R-.35*s),(x+.27*s,y,z+h+R+1.0*s),.12*s,'Chocolate',12)
 leaf=ball((x+.65*s,y,z+h+R+.16*s),(.75*s,.29*s,.11*s),'Mint');leaf.rotation_euler[1]=-.30
 ball(surface(x,y,.12),(.75*s,.7*s,.16*s),'Cream')
for i,(x,y,s) in enumerate([(-18,-24,1.15),(19,-18,1.3),(-20,-6,1.5),(20,8,1.1),(-32,8,1.25),(32,17,1.4),(-35,34,1.2),(36,40,1.3),(-43,17,1),(43,4,1.15)]):apple('11_Candy_Apple_%02d'%i,x,y,s,i in (0,1,3,5))

def popcorn(name,x,y,s=1):
 group(name);z=ground_z(x,y);n=32;v=[];f=[];ids=[]
 for j in range(2):
  for i in range(n):a=2*pi*i/n;rr=(.8 if j==0 else 1.15)*s;v.append((x+rr*cos(a),y+rr*sin(a),z+j*2.1*s))
 for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n));ids.append((i//2)%2)
 mesh('Striped_popcorn_carton',v,f,'Vanilla',ids,['Coral'])
 torus((x,y,z+2.1*s),1.15*s,.065*s,'Gold')
 for i in range(32):
  a=random.uniform(0,2*pi);r=random.uniform(0,.95)*s;zz=z+2.1*s+(.5*(1-r/(1.2*s))+random.uniform(0,.25))*s
  p=(x+r*cos(a),y+r*sin(a),zz)
  for j in range(3):ball((p[0]+random.uniform(-.14,.14)*s,p[1]+random.uniform(-.14,.14)*s,p[2]+random.uniform(-.1,.1)*s),(.24*s,.22*s,.24*s),'Popcorn' if i%3==0 else 'Cream',10,6)
for i,(x,y,s) in enumerate([(-11,-18,1),(13,-9,1.2),(-13,14,1.3),(18,30,1),(-28,27,.9)]):popcorn('12_Popcorn_%02d'%i,x,y,s)

# Cotton candy shrubs, gumdrop clusters, sugar flowers, and scattered confetti.
group('13_Gumdrop_Gardens')
for i in range(95):
 x=random.uniform(-43,43);y=random.uniform(-40,62)
 if abs(x-pathx(y))<9 or (abs(x)<14 and y>23):continue
 z=ground_z(x,y);s=random.uniform(.5,1.25);col=['Mint','Lilac','Cream','Coral','Aqua'][i%5]
 ball((x,y,z+.50*s),(.85*s,.80*s,.70*s),col,16,10)
 for j in range(5):
  a=random.uniform(0,2*pi);t=random.uniform(.15,1.2);ball((x+.82*s*sin(t)*cos(a),y+.77*s*sin(t)*sin(a),z+.50*s+.70*s*cos(t)),(.045,.045,.045),'Vanilla',8,4)
group('14_Sugar_Flowers')
for i in range(72):
 y=random.uniform(-45,27);x=pathx(y)+random.choice([-1,1])*random.uniform(7,12)
 z=ground_z(x,y);h=random.uniform(.25,.75)
 rod((x,y,z),(x,y,z+h),.025,'Mint',6)
 for j in range(5):a=j*2*pi/5;ball((x+.18*cos(a),y+.18*sin(a),z+h),(.17,.15,.085),'Cream' if i%3 else 'Lilac',10,6)
 ball((x,y,z+h+.055),(.09,.09,.06),'Gold',10,6)
group('15_Rainbow_Sprinkles')
for i in range(420):
 x=random.uniform(-38,38);y=random.uniform(-43,60)
 if abs(x-pathx(y))<6 or (abs(x)<12 and y>23):continue
 z=ground_z(x,y)+.055;a=random.uniform(0,2*pi);l=random.uniform(.12,.23)
 rod((x,y,z),(x+l*cos(a),y+l*sin(a),z),.035,['Cream','Gold','Mint','Lilac','Raspberry'][i%5],7)

def bunting(name,a,b):
 group(name);pts=[]
 for i in range(61):
  t=i/60;p=Vector(a).lerp(Vector(b),t);p.z-=1.6*sin(pi*t);pts.append(p)
 tube(pts,.035,'Chocolate',6)
 for i in range(1,20):
  t=i/20;p=Vector(a).lerp(Vector(b),t);p.z-=1.6*sin(pi*t)
  v=[p+Vector((-.34,0,-.04)),p+Vector((.34,0,-.04)),p+Vector((.07,.12,-.85))]
  mesh('Candy_pennant',v,[(0,1,2)],['Cream','Coral','Mint','Gold','Lilac'][i%5])
bunting('16_Festival_Bunting_Left',(-23,22,9),(-10,20,9))
bunting('17_Festival_Bunting_Right',(11,20,9),(23,27,10))

# Small friendly cupcake sculptures echo the trio in the first drawing.
group('18_Cupcake_Welcoming_Committee')
for k,(x,y,col) in enumerate([(-8,-17,'Cream'),(-6.3,-16.7,'Mint'),(-4.8,-16.9,'Chocolate')]):
 z=ground_z(x,y);n=64;v=[];f=[]
 for j in range(2):
  for i in range(n):a=2*pi*i/n;r=(.38+j*.14)+.025*cos(a*16);v.append((x+r*cos(a),y+r*sin(a),z+.25+j*.65))
 for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
 mesh('Pleated_cupcake_wrapper',v,f,'GoldenBiscuit' if k<2 else 'Chocolate')
 for j in range(4):
  rr=.53-j*.12;ball((x,y,z+.97+j*.22),(rr,rr,.27),col)
 for s in (-1,1):
  ball((x+s*.17,y-.45,z+1.06),(.052,.044,.085),'Ink',12,8)
  ball((x+s*.17-.014,y-.486,z+1.09),(.015,.013,.022),'Vanilla',8,6)
  ball((x+s*.29,y-.43,z+.94),(.09,.025,.047),'Coral')
  rod((x+s*.42,y,z+.68),(x+s*.72,y-.06,z+.57),.035,'Chocolate',8)
  ball((x+s*.74,y-.06,z+.57),(.075,.065,.07),'Cream')
  ball((x+s*.23,y-.12,z+.13),(.15,.23,.10),'Chocolate')
 tube([(x-.10+.20*t/12,y-.49,z+.96-.055*sin(pi*t/12)) for t in range(13)],.018,'Ink',6)
 ball((x,y,z+1.83),(.15,.15,.15),'Raspberry')
 rod((x,y,z+1.95),(x+.06,y,z+2.10),.018,'Chocolate',8)

# Marshmallow clouds are clustered silhouettes with broad, soft highlights.
group('19_Marshmallow_Clouds')
for x,y,z,s in [(-31,58,30,1),(32,68,36,1.2),(-44,18,27,.75),(42,2,33,.65),(-5,82,38,.9)]:
 for dx,dz,r in [(-5,0,3.7),(-1,1,4.6),(3,0,3.6),(6,-.3,2.8),(0,3,3.5)]:ball((x+dx*s,y,z+dz*s),(r*s,2.7*s,r*.68*s),'Cloud',24,14)

# Export original grouped assets, preserving world-space layout and material slots.
manifest=[]
for name,obs in groups.items():
 if not obs:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_'+name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Triangulation avoids downstream n-gon ambiguity.
 mod=o.modifiers.new('Triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
 uv=o.data.uv_layers.new(name='UVMap')
 for face in o.data.polygons:
  axis=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=axis]
  for li in face.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=(co[axes[0]]*.25,co[axes[1]]*.25)
 filename=o.name+'.fbx'
 bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,filename),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',bake_anim=False,mesh_smooth_type='FACE',use_mesh_modifiers=True)
 manifest.append({'name':o.name,'file':filename,'materials':[m.name for m in o.data.materials],'vertices':len(o.data.vertices),'triangles':len(o.data.polygons)})
with open(os.path.join(ROOT,'SourceArt','manifest.json'),'w') as f:json.dump({'assets':manifest,'materials':PALETTE},f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'SourceArt','CandyCarnival.blend'))
print('CANDY_MODELS_COMPLETE',len(manifest),sum(a['triangles'] for a in manifest))
