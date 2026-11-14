// Run with the relay and the Unreal demo open. Uses actual /phone connections.
import {WebSocket} from 'ws';import fs from 'node:fs';
const base='http://127.0.0.1:3000';
const health=await fetch(base+'/health').then(x=>x.json());
if(!health.game)throw Error('Unreal is not connected to the relay.');
const events=[];let ended=false,ready=0,rematched=false,finished=false;const lastRecord=['',''];
const sockets=[];const assigned=[-1,-1];const phase=['',''];const points=[0,0];const positions=[{x:-350,y:-190},{x:350,y:190}];
let interval;
const deadline=setTimeout(()=>finish('Timed out waiting for a complete match'),50000);
function record(slot,m){if(m.t==='state'){const key=[m.phase,m.pips,m.points].join(':');if(key===lastRecord[m.slot])return;lastRecord[m.slot]=key;}events.push({time:new Date().toISOString(),slot,...m});console.log(JSON.stringify({slot,...m}));}
function finish(error){if(finished)return;finished=true;clearTimeout(deadline);clearInterval(interval);for(const s of sockets)s.close();fs.mkdirSync('../Tests',{recursive:true});fs.writeFileSync('../Tests/live-demo.json',JSON.stringify({passed:!error,error:error||null,events},null,2));if(error){console.error(error);process.exitCode=1;}}
for(let i=0;i<2;i++){
 const ws=new WebSocket('ws://127.0.0.1:3000/phone');sockets.push(ws);
 ws.on('open',()=>ws.send(JSON.stringify({t:'join',code:health.code,clientId:'demo-test-player-'+i})));
 ws.on('message',raw=>{const m=JSON.parse(raw);record(i,m);
  if(m.t==='joined'){assigned[i]=m.slot;ws.send(JSON.stringify({t:'ready'}));ready++;}
  if(m.t==='full'||m.t==='error')finish('Controller could not join: '+JSON.stringify(m));
  if(m.t==='state'){
   if(Number.isFinite(m.x)&&Number.isFinite(m.y))positions[m.slot]={x:m.x,y:m.y};
   phase[i]=m.phase;points[i]=m.points;
   if(m.phase==='matchEnd'&&!ended){ended=true;console.log('LIVE_MATCH_COMPLETED');setTimeout(()=>ws.send(JSON.stringify({t:'rematch'})),300);}
   if(ended&&m.phase==='countdown'&&m.points===0&&!rematched){rematched=true;console.log('LIVE_REMATCH_CONFIRMED');setTimeout(()=>finish(),500);}
  }
 });
}
let tick=0;
interval=setInterval(()=>{if(ready<2||rematched)return;tick++;
 for(let i=0;i<2;i++)if(sockets[i].readyState===WebSocket.OPEN){
  // Spawn locations are opposite corners. The winning player bites every .8 s.
  const player=assigned[i],other=1-player;let x=positions[other].x-positions[player].x,y=positions[other].y-positions[player].y;const distance=Math.hypot(x,y);if(distance){x/=distance;y/=distance;}
  const speed=player===1?0:distance>130?1:.15;
  sockets[i].send(JSON.stringify({t:'in',x:x*speed,y:y*speed,hit:player===0&&tick%26===0}));
 }
},1000/30);
