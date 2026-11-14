"""Blender: export fitted UCX hulls without modifying the render meshes.

Disconnected decorations stay disconnected. Canopies/walls/canes are split into
short sections to preserve entrances and the spaces underneath curved shapes.
"""
import bpy, bmesh, math, os, json, itertools
import numpy as np
from mathutils import Vector
from math import sin, cos, pi
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'SourceArt','CollisionFBX');os.makedirs(OUT,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'SourceArt','CandyCarnival.blend'))
originals=sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name)
bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
DIRECTIONS=np.array([tuple(v.co.normalized()) for v in bm.verts]);bm.free()
# 42 support directions bound every small hull's complexity independently.
assert len(DIRECTIONS)==42
active=None;proxies=[];report=[];hull_keys=set()
def ground(x,y):return .40*sin(x*.072)+.34*cos(y*.087)+.20*sin((x+y)*.13)
def mesh(name,verts,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def hull(points):
 p=np.asarray(points,dtype=float)
 if len(p)<4:return
 p=np.unique(np.round(p,6),axis=0)
 if len(p)>42:p=p[np.unique(np.argmax(p@DIRECTIONS.T,axis=0))]
 # Give single-sided cloth a thin physical surface.
 if np.linalg.matrix_rank(p-p.mean(axis=0),tol=.0001)<3:
  _,_,vh=np.linalg.svd(p-p.mean(axis=0));p=np.concatenate((p+vh[-1]*.025,p-vh[-1]*.025))
 name='UCX_'+active.name+'_'+str(len(proxies)).zfill(3)
 bm=bmesh.new()
 for q in p:bm.verts.new(q)
 bm.verts.ensure_lookup_table();result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
 # Remove unused interior points so cooked hulls remain small.
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
 if len(me.polygons)<4:raise RuntimeError('Degenerate hull '+name)
 key=tuple(sorted(tuple(round(c,4) for c in v.co) for v in me.vertices))
 if key in hull_keys:
  bpy.data.meshes.remove(me);return
 hull_keys.add(key)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.display_type='WIRE';proxies.append(o)
 return o
def rod(a,b,r,n=8,r2=None):
 a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');d=(b-a).length
 hull([tuple(a+q@Vector((rr*cos(t*2*pi/n),rr*sin(t*2*pi/n),z))) for z,rr in [(0,r),(d,r if r2 is None else r2)] for t in range(n)])
def ellipsoid(center,radii):
 hull(np.asarray(center)+DIRECTIONS*np.asarray(radii))
def box(lo,hi):hull(list(itertools.product(*zip(lo,hi))))
def island_sets(o):
 parent=list(range(len(o.data.vertices)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for e in o.data.edges:
  a,b=map(find,e.vertices)
  if a!=b:parent[b]=a
 parts={}
 for i in range(len(parent)):parts.setdefault(find(i),[]).append(i)
 return list(parts.values())
def points(o,ids):return np.asarray([tuple(o.matrix_world@o.data.vertices[i].co) for i in ids])
def bounds(p):return p.min(axis=0),p.max(axis=0)
def export(obs,path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',bake_anim=False,mesh_smooth_type='FACE')
def shell(x,y,r0,r1,z0,z1,a,b,thick=.12):
 hull([(x+rr*cos(t),y+rr*sin(t),zz+offset) for rr,zz in [(r0,z0),(r1,z1)] for t in (a,(a+b)/2,b) for offset in (-thick/2,thick/2)])
def tent(x,y,r,h,peak,main=False):
 z=ground(x,y)
 # 4 radial bands x 16 wedges; thin roof, open occupied volume below.
 for j in range(4):
  t0=j/4;t1=(j+1)/4
  for i in range(16):shell(x,y,.08+r*t0,.08+r*t1,z+h+(peak-h)*(1-t0)**2,z+h+(peak-h)*(1-t1)**2,2*pi*i/16,2*pi*(i+1)/16,.18)
 for i in range(16):
  a=2*pi*i/16;b=2*pi*(i+1)/16
  hull([(x+rr*cos(t),y+rr*sin(t),zz) for rr in (r-.06,r+.07) for t in (a,(a+b)/2,b) for zz in (z+h-.90,z+h)])
 if main:
  for i in range(32):
   a=2*pi*i/32;b=2*pi*(i+1)/32
   if abs(math.atan2(sin((a+b)/2+pi/2),cos((a+b)/2+pi/2)))<.39:continue
   hull([(x+rr*cos(t),y+rr*sin(t),zz) for rr in (r*.9-.08,r*.9+.08) for t in (a,b) for zz in (z,z+h-.25)])
  rod((x,y,z+.05),(x,y,z+.30),r*.9,16)
  ey=y-r*.9-.1;w=r*.34;eh=h*.68
  for side in (-1,1):
   rod((x+side*w,ey,z),(x+side*w,ey,z+eh),.23)
   ellipsoid((x+side*(w+.5),ey+.13,z+h*.47),(.98,.46,h*.46))
  for i in range(12):
   a=i*pi/12;b=(i+1)*pi/12
   rod((x-w*cos(a),ey,z+eh+w*sin(a)),(x-w*cos(b),ey,z+eh+w*sin(b)),.24)
 else:
  for i in range(8):
   a=2*pi*i/8;px=x+r*.9*cos(a);py=y+r*.9*sin(a);rod((px,py,z),(px,py,z+h),.115)
  rod((x,y,z+.35),(x,y,z+.7),r*.77,16)
  rod((x,y,z+.7),(x,y,z+2),r*.72,16)
 rod((x,y,z+peak-.2),(x,y,z+peak+2.9),.10)
 ellipsoid((x,y,z+peak+.25),(.35,.35,.40))
 # Pennant split in 4 pieces so its curved silhouette stays close.
 for i in range(4):
  ps=[]
  for t in (i/4,(i+.5)/4,(i+1)/4):
   for j in (0,1):
    for d in (-.025,.025):ps.append((x+t*2.8,y+.30*sin(t*6)+d,z+peak+2.6-j*(1-t*.7)*1.2-.25*t))
  hull(ps)
TENTS=[(0,35,11,9,23,True),(-23,22,5.1,5.2,11.5,False),(23,27,5.5,5.6,12,False),(-24,43,4.5,5,10.5,False),(25,48,4.8,5.3,11.6,False)]
CANES=[(-8,-29,6.5,1.8,0),(8,-27,7.5,2,pi),(-9,-4,8,2,0),(10,1,7.7,1.9,pi),(-10,20,8.7,2.1,0),(11,20,8.7,2.1,pi)]
APPLES=[(-18,-24,1.15),(19,-18,1.3),(-20,-6,1.5),(20,8,1.1),(-32,8,1.25),(32,17,1.4),(-35,34,1.2),(36,40,1.3),(-43,17,1),(43,4,1.15)]
def bitten_head(o,ids,center):
 bm=bmesh.new();vmap={i:bm.verts.new(o.data.vertices[i].co) for i in ids}
 for f in o.data.polygons:
  if all(i in vmap for i in f.vertices):bm.faces.new([vmap[i] for i in f.vertices])
 for signs in itertools.product((-1,1),repeat=3):
  part=bm.copy()
  for ax,sign in enumerate(signs):
   normal=[0,0,0];normal[ax]=1
   bmesh.ops.bisect_plane(part,geom=list(part.verts)+list(part.edges)+list(part.faces),plane_co=center,plane_no=normal,dist=.00001,clear_inner=sign>0,clear_outer=sign<0)
  hull([tuple(v.co) for v in part.verts]);part.free()
 bm.free()
for active in originals:
 proxies=[];hull_keys=set();name=active.name;kind=int(name[3:5]);print('COLLISION',name,flush=True)
 if kind<=3:
  # Low-resolution collision-only surfaces, kept separate from visible mesh detail.
  v=[];f=[]
  if kind==1:
   nx=ny=50
   for j in range(ny+1):
    y=-80+j*180/ny
    for i in range(nx+1):x=-90+i*180/nx;v.append((x,y,ground(x,y)))
  else:
   nx=2 if kind==2 else 1;ny=80;width=5.8 if kind==2 else 2.6;offset=0 if kind==2 else -4.25
   for j in range(ny+1):
    y=-70+j*108/ny;cx=5*sin((y+28)*.075)*max(0,min(1,(34-y)/16))
    for i in range(nx+1):
     x=cx+offset+width*(i/nx-.5);v.append((x,y,ground(x,y)+(.08 if kind==2 else .075)+.035*sin(i*pi/nx)))
  for j in range(ny):
   for i in range(nx):a=j*(nx+1)+i;f.extend([(a,a+1,a+nx+2),(a,a+nx+2,a+nx+1)])
  low=mesh('COL_'+name,v,f);export([low],os.path.join(OUT,low.name+'.fbx'))
  report.append({'name':name,'mode':'surface','file':low.name+'.fbx','collision_mesh':low.name,'triangles':len(f)})
  bpy.data.objects.remove(low,do_unlink=True);continue
 if 5<=kind<=9:tent(*TENTS[kind-5])
 elif kind==10:
  x,y,h,r,turn=CANES[int(name[-2:])];z=ground(x,y)
  def pt(a):return (x+r*(1-cos(a))*cos(turn),y+r*(1-cos(a))*sin(turn),z+h+r*sin(a))
  rod((x,y,z),(x,y,z+h),.245)
  for i in range(12):rod(pt(i*pi/12),pt((i+1)*pi/12),.255)
  rod((x,y,z),(x,y,z+.18),.55,12)
 else:
  islands=island_sets(active);ps=[points(active,ids) for ids in islands]
  if kind==11:
   index=int(name[-2:]);head=max(range(len(ps)),key=lambda i:len(ps[i]))
   for i,p in enumerate(ps):
    if i==head and index in (0,1,3,5):
     x,y,s=APPLES[index];bitten_head(active,islands[i],(x,y,ground(x,y)+4.5*s))
    else:hull(p)
  elif kind==12:
   # One fitted bucket hull, one hull around the popcorn mound.
   bucket=max(ps,key=lambda p:np.ptp(p[:,2])/(max(np.ptp(p[:,0]),.01)))
   # Carton wall is the island with 64 vertices; topping spheres have 70.
   bucket=next(p for p in ps if len(p)==64)
   top=float(bucket[:,2].max());hull(bucket)
   hull(np.concatenate([p for p in ps if p[:,2].max()>top+.01]))
  elif kind==13:
   for p in ps:
    if max(np.ptp(p,axis=0))>.25:hull(p)
  elif kind==14:
   stems=[p for p in ps if np.ptp(p[:,2])>.20 and max(np.ptp(p[:,:2],axis=0))<.08]
   for stem in stems:
    c=stem.mean(axis=0)
    near=[p for p in ps if np.linalg.norm(p.mean(axis=0)[:2]-c[:2])<.37]
    hull(np.concatenate(near))
  elif kind in (16,17):
   for p in ps:
    if len(p)<10:hull(np.concatenate((p+np.array((0,.025,0)),p-np.array((0,.025,0)))))
    else:
     lo,hi=bounds(p)
     for j in range(10):
      q=p[(p[:,0]>=lo[0]+(hi[0]-lo[0])*j/10-.05)&(p[:,0]<=lo[0]+(hi[0]-lo[0])*(j+1)/10+.05)]
      hull(q)
  elif kind==18:
   for x,y in [(-8,-17),(-6.3,-16.7),(-4.8,-16.9)]:
    near=[p for p in ps if abs(p.mean(axis=0)[0]-x)<.81 and abs(p.mean(axis=0)[1]-y)<.8]
    p=np.concatenate(near);z=ground(x,y)
    hull(p[p[:,2]<=z+.95]);hull(p[p[:,2]>=z+.75])
  else:
   for p in ps:hull(p)
 if not proxies:raise RuntimeError('No hulls generated for '+name)
 export([active]+proxies,os.path.join(OUT,name+'.fbx'))
 report.append({'name':name,'mode':'convex','file':name+'.fbx','hulls':len(proxies),'max_vertices':max(len(o.data.vertices) for o in proxies),'collision_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in proxies)})
 for o in proxies:bpy.data.objects.remove(o,do_unlink=True)
json.dump({'assets':report,'max_support_directions':42,'surface_triangles':sum(e.get('triangles',0) for e in report),'total_hulls':sum(e.get('hulls',0) for e in report)},open(os.path.join(ROOT,'SourceArt','collision_manifest.json'),'w'),indent=2)
print('CANDY_COLLISION_GEOMETRY_COMPLETE',sum(e.get('hulls',0) for e in report),flush=True)
