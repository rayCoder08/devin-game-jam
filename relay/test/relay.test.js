import test from 'node:test';import assert from 'node:assert/strict';import {WebSocket} from 'ws';import {createRelay} from '../server.js';
const message=ws=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('message timeout')),2500);ws.once('message',raw=>{clearTimeout(timer);resolve(JSON.parse(raw));});});
async function open(url){const ws=new WebSocket(url);await new Promise((ok,no)=>{ws.once('open',ok);ws.once('error',no);});return ws;}
test('room pairing, slot authority, input clamp, disconnect and reconnect',async()=>{
 const r=createRelay({roomCode:'CAKE',publicUrl:'https://example.com'});await new Promise(ok=>r.server.listen(0,'127.0.0.1',ok));const base=`ws://127.0.0.1:${r.server.address().port}`;
 try{
  const ue=new WebSocket(base+'/ue');const room=await message(ue);assert.equal(room.code,'CAKE');
  const a=await open(base+'/phone');let recv=message(a);a.send(JSON.stringify({t:'join',code:'WRNG',clientId:'phone-one'}));assert.equal((await recv).t,'error');
  recv=message(a);let game=message(ue);a.send(JSON.stringify({t:'join',code:'CAKE',clientId:'phone-one'}));assert.equal((await recv).slot,0);assert.equal((await game).t,'joined');
  game=message(ue);a.send(JSON.stringify({t:'ready'}));assert.equal((await game).t,'ready');
  game=message(ue);a.send(JSON.stringify({t:'in',slot:1,x:10,y:10,hit:true}));const input=await game;assert.equal(input.slot,0);assert.ok(Math.hypot(input.x,input.y)<=1.001);assert.equal(input.hit,true);
  recv=message(a);ue.send(JSON.stringify({t:'state',slot:0,pips:3,phase:'playing'}));assert.equal((await recv).pips,3);
  game=message(ue);a.close();assert.equal((await game).t,'left');
  const again=await open(base+'/phone');recv=message(again);game=message(ue);again.send(JSON.stringify({t:'join',code:'CAKE',clientId:'phone-one'}));assert.equal((await recv).slot,0);await game;
  const health=await fetch(`http://127.0.0.1:${r.server.address().port}/health`).then(x=>x.json());assert.equal(health.game,true);
  const qr=await fetch(`http://127.0.0.1:${r.server.address().port}/qr.png`);assert.equal(qr.status,200);assert.equal(qr.headers.get('content-type'),'image/png');
 }finally{await r.close();}
});
