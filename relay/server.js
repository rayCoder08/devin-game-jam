import express from 'express';
import http from 'node:http';
import {randomInt} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {WebSocketServer,WebSocket} from 'ws';
import QRCode from 'qrcode';

export function createRelay({publicUrl=process.env.PUBLIC_URL||'',roomCode}={}) {
 const alphabet='ABCDEFGHJKLMNPQRSTUVWXYZ';
 const code=roomCode||Array.from({length:4},()=>alphabet[randomInt(alphabet.length)]).join('');
 const url=publicUrl.replace(/\/$/,'');
 const app=express(),server=http.createServer(app);
 const sockets=new WebSocketServer({noServer:true,maxPayload:2048});
 const slots=[null,null];let game=null;
 const send=(ws,m)=>{if(ws?.readyState===WebSocket.OPEN)ws.send(JSON.stringify(m));};
 const room=()=>({t:'room',code,url});
 app.disable('x-powered-by');
 app.use(express.static(path.join(path.dirname(fileURLToPath(import.meta.url)),'public')));
 app.get('/health',(_req,res)=>res.json({application:'cupcake-cannibal',ok:true,code,url,game:game?.readyState===WebSocket.OPEN,players:slots.map(s=>!!s?.ws)}));
 app.get('/qr.png',async(_req,res)=>{try {if(!url)return res.status(503).send('Set PUBLIC_URL to the HTTPS tunnel URL.');res.type('png').send(await QRCode.toBuffer(`${url}/play.html?room=${code}`,{width:320,margin:2,color:{dark:'#261021',light:'#fff7ee'}}));}catch{res.sendStatus(500);}});
 server.on('upgrade',(req,socket,head)=>{
  const pathname=new URL(req.url,'http://localhost').pathname;
  if(!['/ue','/phone'].includes(pathname)){socket.destroy();return;}
  if(pathname==='/ue'&&(req.headers['cf-connecting-ip']||!['127.0.0.1','::1','::ffff:127.0.0.1'].includes(req.socket.remoteAddress))){socket.write('HTTP/1.1 403 Forbidden\r\n\r\n');socket.destroy();return;}
  if(pathname==='/ue'&&game?.readyState===WebSocket.OPEN){socket.write('HTTP/1.1 409 Conflict\r\n\r\n');socket.destroy();return;}
  sockets.handleUpgrade(req,socket,head,ws=>sockets.emit('connection',ws,pathname));
 });
 sockets.on('connection',(ws,kind)=>{
  let slot=-1;let lastInput=0;ws.isAlive=true;ws.on('pong',()=>ws.isAlive=true);
  if(kind==='/ue'){
   game=ws;send(ws,room());
   slots.forEach((s,i)=>{if(s?.ws){send(ws,{t:'joined',slot:i});if(s.ready)send(ws,{t:'ready',slot:i});}});
  }
  ws.on('message',raw=>{
   let m;try{m=JSON.parse(raw.toString());}catch{return;}if(!m||typeof m!=='object')return;
   if(kind==='/ue'){
    if(m.t==='state'&&Number.isInteger(m.slot)&&m.slot>=0&&m.slot<2){const s=slots[m.slot];if(s){s.state=m;send(s.ws,m);}}return;
   }
   if(m.t==='join'){
    if(slot>=0)return;
    if(typeof m.code!=='string'||m.code.toUpperCase()!==code){send(ws,{t:'error',message:'That room code does not match.'});return;}
    if(typeof m.clientId!=='string'||!/^[a-zA-Z0-9_-]{8,80}$/.test(m.clientId)){send(ws,{t:'error',message:'Please reload this controller.'});return;}
    let found=slots.findIndex(s=>s?.clientId===m.clientId);
    if(found<0)found=slots.findIndex(s=>s===null||(!s.ws&&Date.now()-s.leftAt>30000));
    if(found<0){send(ws,{t:'full'});return;}
    slot=found;const previous=slots[slot];
    slots[slot]={clientId:m.clientId,ws,ready:false,leftAt:0,state:previous?.state};
    if(previous?.ws&&previous.ws!==ws)previous.ws.close(1000,'Controller reconnected');
    send(ws,{t:'joined',slot,code,color:slot===0?'#f76b9b':'#77503d'});send(game,{t:'joined',slot});
    if(slots[slot].state)send(ws,slots[slot].state);return;
   }
   if(slot<0||slots[slot]?.ws!==ws)return;
   if(m.t==='ready'){slots[slot].ready=true;send(game,{t:'ready',slot});return;}
   if(m.t==='rematch'){send(game,{t:'rematch'});return;}
   if(m.t==='in'&&slots[slot].ready){
    const now=Date.now();if(now-lastInput<12)return;lastInput=now;
    if(!Number.isFinite(m.x)||!Number.isFinite(m.y))return;
    let x=Math.max(-1,Math.min(1,m.x)),y=Math.max(-1,Math.min(1,m.y));const n=Math.hypot(x,y);if(n>1){x/=n;y/=n;}
    send(game,{t:'in',slot,x,y,hit:m.hit===true});
   }
  });
  ws.on('error',()=>{});
  ws.on('close',()=>{
   if(kind==='/ue'){if(game===ws)game=null;return;}
   if(slot>=0&&slots[slot]?.ws===ws){slots[slot].ws=null;slots[slot].ready=false;slots[slot].leftAt=Date.now();send(game,{t:'left',slot});}
  });
 });
 const heartbeat=setInterval(()=>{for(const ws of sockets.clients){if(!ws.isAlive){ws.terminate();continue;}ws.isAlive=false;ws.ping();}},10000);
 heartbeat.unref();
 return {app,server,code,slots,close:async()=>{clearInterval(heartbeat);for(const ws of sockets.clients)ws.terminate();await new Promise(resolve=>server.close(resolve));}};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const ix=process.argv.indexOf('--url');const relay=createRelay({publicUrl:process.env.PUBLIC_URL||(ix>=0?process.argv[ix+1]:'')});
 const port=Number(process.env.PORT||3000);relay.server.listen(port,'0.0.0.0',()=>{
  console.log(`Cupcake Cannibal relay: http://localhost:${port} | room ${relay.code}`);
  console.log('For iPhone motion: set PUBLIC_URL to your HTTPS tunnel and restart the relay.');
 });
}
