"""Reopen saved assets; verify fitted blocking surfaces and traversal clearance."""
import unreal as u,os,json,math,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACT=u.get_editor_subsystem(u.EditorActorSubsystem);ED=u.get_editor_subsystem(u.UnrealEditorSubsystem)
LEVEL=u.get_editor_subsystem(u.LevelEditorSubsystem);world=ED.get_editor_world()
actors=ACT.get_all_level_actors();statics=[a for a in actors if isinstance(a,u.StaticMeshActor)]
results=[]
def vec(p):return u.Vector(p[0]*100,-p[1]*100,p[2]*100)
def ground(x,y):return .40*math.sin(x*.072)+.34*math.cos(y*.087)+.20*math.sin((x+y)*.13)
def sweep(name,start,end,radius,expect,only=None):
 ignored=[a for a in statics if only and not a.get_actor_label().startswith(only)]
 hit=u.SystemLibrary.sphere_trace_single(world,vec(start),vec(end),radius*100,u.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignored,u.DrawDebugTrace.NONE,True)
 actual=hit is not None
 results.append({'test':name,'blocked':actual,'expected':expect})
 assert actual==expect,name+' unexpected collision result: '+str(hit)
 u.log('CANDY_COLLISION_TEST '+name+' PASS')
# Every physical scene mesh is collidable, including formerly disabled clouds/sign.
for a in statics:
 enabled=a.static_mesh_component.get_collision_enabled()!=u.CollisionEnabled.NO_COLLISION
 assert enabled==(a.get_actor_label()!='Turquoise sky gradient'),a.get_actor_label()
 assert a.static_mesh_component.static_mesh
sweep('ground surface',(-3,-37,2),(-3,-37,-2),.10,True,'01_')
sweep('golden path surface',(0,20,3),(0,20,-1),.10,True,'02_')
sweep('caramel surface',(-4.25,34,3),(-4.25,34,-1),.10,True,'03_')
for i,(x,y,h,r,t) in enumerate([(-8,-29,6.5,1.8,0),(8,-27,7.5,2,math.pi),(-9,-4,8,2,0),(10,1,7.7,1.9,math.pi),(-10,20,8.7,2.1,0),(11,20,8.7,2.1,math.pi)]):
 z=ground(x,y)
 sweep('cane '+str(i)+' shaft',(x-1,y,z+2),(x+1,y,z+2),.15,True,'10_Peppermint_Gate_%02d'%i)
 # Pass below the middle of the hook, not through its supporting stalk.
 hx=x+r*math.cos(t);hy=y+r*math.sin(t)
 sweep('cane '+str(i)+' open hook',(hx,hy-1,z+h-.5),(hx,hy+1,z+h-.5),.25,False,'10_Peppermint_Gate_%02d'%i)
sweep('grand tent doorway',(0,22,2),(0,31,2),.42,False,'05_')
sweep('grand tent interior',(0,31,2),(3,36,2),.42,False,'05_')
sweep('grand tent wall',(13,35,2),(8,35,2),.30,True,'05_')
sweep('grand tent roof',(5,35,24),(5,35,10),.15,True,'05_')
sweep('stall open aisle',(-26.9,16,2.9),(-26.9,26,2.9),.20,False,'06_')
sweep('stall countertop',(-23,22,4),(-23,22,1),.15,True,'06_')
for i,(x,y,s) in enumerate([(-18,-24,1.15),(19,-18,1.3),(-20,-6,1.5),(20,8,1.1),(-32,8,1.25),(32,17,1.4),(-35,34,1.2),(36,40,1.3),(-43,17,1),(43,4,1.15)]):
 z=ground(x,y)+4.5*s
 sweep('apple '+str(i)+' fruit',(x-4*s,y,z),(x,y,z),.15,True,'11_Candy_Apple_%02d'%i)
 sweep('apple '+str(i)+' slender stick',(x-.8,y,ground(x,y)+1),(x+.8,y,ground(x,y)+1),.1,True,'11_Candy_Apple_%02d'%i)
sweep('space between apple trees',(-9,-24,4),(9,-24,4),.35,False,'11_')
for i,(x,y,s) in enumerate([(-11,-18,1),(13,-9,1.2),(-13,14,1.3),(18,30,1),(-28,27,.9)]):
 z=ground(x,y)+s
 sweep('popcorn '+str(i)+' bucket',(x-3*s,y,z),(x,y,z),.15,True,'12_Popcorn_%02d'%i)
sweep('marquee oval', (0,21,10.8),(0,26,10.8),.15,True,'Marquee -')
json.dump({'tests':results,'passed':len(results),'static_mesh_actors':len(statics),'collidable_actors':len(statics)-1},open(os.path.join(ROOT,'Tools','collision_verification.json'),'w'),indent=2)
u.log('CANDY_COLLISION_VERIFIED '+str(len(results))+' checks passed')
