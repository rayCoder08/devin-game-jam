const $=id=>document.getElementById(id);
const stored=localStorage.getItem('cupcakeClientId');const clientId=stored||crypto.randomUUID();localStorage.setItem('cupcakeClientId',clientId);
$('room').value=(new URLSearchParams(location.search).get('room')||'').toUpperCase();
let ws,slot=-1,ready=false,motion=false,motionReceived=false,beta=0,gamma=0,neutralBeta=0,neutralGamma=0,hit=false,retry=500,wake,manualClose=false;
let stick={x:0,y:0};let reconnectTimer;
for(let i=0;i<5;i++)$('pips').append(Object.assign(document.createElement('span'),{className:'pip'}));
function send(m){if(ws?.readyState===WebSocket.OPEN)ws.send(JSON.stringify(m));}
async function keepAwake(){try{wake=await navigator.wakeLock?.request('screen');}catch{}}
function zero(){stick={x:0,y:0};hit=false;send({t:'in',x:0,y:0,hit:false});$('thumb').style.transform='';}
function status(text,online){$('connection').textContent=text;$('dot').classList.toggle('online',online);}
function connect(){
 clearTimeout(reconnectTimer);if(manualClose)return;
 ws=new WebSocket(`${location.protocol==='https:'?'wss:':'ws:'}//${location.host}/phone`);
 ws.onopen=()=>{retry=500;status('CONNECTED',true);send({t:'join',code:$('room').value.trim().toUpperCase(),clientId});};
 ws.onmessage=e=>{let m;try{m=JSON.parse(e.data);}catch{return;}
  if(m.t==='joined'){slot=m.slot;$('join').classList.add('hidden');$('game').classList.remove('hidden');$('name').textContent=slot===0?'STRAWBERRY':'CHOCOLATE';document.body.style.background=m.color;document.documentElement.style.background=m.color;document.body.style.color=slot===0?'#321a27':'#fff2dc';if(ready)send({t:'ready'});keepAwake();}
  if(m.t==='full'||m.t==='error'){$('message').textContent=m.message||'This bakery already has two players.';manualClose=true;ws.close();$('enable').disabled=false;}
  if(m.t==='state'){[...$('pips').children].forEach((p,i)=>p.classList.toggle('empty',i>=m.pips));$('pips').setAttribute('aria-label',`${m.pips} frosting pips`);$('rematch').classList.toggle('hidden',m.phase!=='matchEnd');if(ready)$('hint').textContent=m.phase==='lobby'?'Waiting for the other cupcake...':m.phase==='countdown'?'Get ready to chomp!':m.phase==='tiebreak'?'Golden Crumb! One pip. Make it count.':m.phase==='matchEnd'?'Fresh batch? Tap Rematch.':'Tilt to move. HIT bites nearby or swings your cane.';}
 };
 ws.onclose=()=>{status('RECONNECTING…',false);zero();if(!manualClose){reconnectTimer=setTimeout(connect,retry);retry=Math.min(5000,retry*1.7);}};
 ws.onerror=()=>status('CONNECTING…',false);
}
$('enable').onclick=async()=>{
 if(!/^[A-Z]{4}$/.test($('room').value.trim().toUpperCase())){$('message').textContent='Enter the four-letter room code.';return;}
 $('enable').disabled=true;manualClose=false;
 try{if(typeof DeviceOrientationEvent==='undefined')throw Error('No motion');if(typeof DeviceOrientationEvent.requestPermission==='function'){motion=(await DeviceOrientationEvent.requestPermission())==='granted';}else motion=window.isSecureContext;}catch{motion=false;}
 $('joystick').classList.toggle('hidden',motion);$('tilt').classList.toggle('hidden',!motion);$('ready').textContent=motion?'READY — SET NEUTRAL TILT':'READY — LET’S CHOMP';connect();
 setTimeout(()=>{if(motion&&!motionReceived){motion=false;$('joystick').classList.remove('hidden');$('tilt').classList.add('hidden');$('calibrate').classList.add('hidden');$('ready').textContent='READY — LET’S CHOMP';}},1500);
};
window.addEventListener('deviceorientation',e=>{if(e.beta!==null&&e.gamma!==null)motionReceived=true;if(e.beta!==null)beta=e.beta;if(e.gamma!==null)gamma=e.gamma;});
function calibrate(){neutralBeta=beta;neutralGamma=gamma;zero();}
$('ready').onclick=()=>{calibrate();ready=true;send({t:'ready'});$('ready').classList.add('hidden');$('calibrate').classList.toggle('hidden',!motion);$('hit').disabled=false;$('hint').textContent='Waiting for the other cupcake...';keepAwake();};
$('calibrate').onclick=calibrate;
$('rematch').onclick=()=>{send({t:'rematch'});$('rematch').classList.add('hidden');};
let audioContext;
function clickSound(){try{audioContext||=new (window.AudioContext||window.webkitAudioContext)();audioContext.resume();const osc=audioContext.createOscillator(),gain=audioContext.createGain();osc.type='sine';osc.frequency.setValueAtTime(650,audioContext.currentTime);osc.frequency.exponentialRampToValueAtTime(300,audioContext.currentTime+.07);gain.gain.setValueAtTime(.08,audioContext.currentTime);gain.gain.exponentialRampToValueAtTime(.001,audioContext.currentTime+.08);osc.connect(gain);gain.connect(audioContext.destination);osc.start();osc.stop(audioContext.currentTime+.09);}catch{}}
$('hit').addEventListener('pointerdown',e=>{e.preventDefault();if(!ready)return;hit=true;$('hit').classList.add('pressed');setTimeout(()=>$('hit').classList.remove('pressed'),110);clickSound();});
function joystick(e){const r=$('joystick').getBoundingClientRect();let x=(e.clientX-r.left-r.width/2)/55,y=(e.clientY-r.top-r.height/2)/55,n=Math.hypot(x,y);if(n>1){x/=n;y/=n;}stick={x,y};$('thumb').style.transform=`translate(${x*40}px,${y*40}px)`;}
let pointer=null;$('joystick').onpointerdown=e=>{pointer=e.pointerId;$('joystick').setPointerCapture(pointer);joystick(e);};$('joystick').onpointermove=e=>{if(e.pointerId===pointer)joystick(e);};
for(const type of ['pointerup','pointercancel','lostpointercapture'])$('joystick').addEventListener(type,()=>{pointer=null;zero();});
function axis(degrees){const v=Math.abs(degrees);return v<5?0:Math.sign(degrees)*Math.min(1,(v-5)/20);}
setInterval(()=>{if(!ready||document.hidden)return;let x=motion?axis(gamma-neutralGamma):stick.x,y=motion?axis(beta-neutralBeta):stick.y;if(matchMedia('(orientation:landscape)').matches){x=y=0;}const n=Math.hypot(x,y);if(n>1){x/=n;y/=n;}send({t:'in',x,y,hit});hit=false;},1000/30);
document.addEventListener('visibilitychange',()=>{zero();if(!document.hidden){keepAwake();if(ws?.readyState!==WebSocket.OPEN)connect();}});
window.addEventListener('pagehide',zero);
for(const event of ['gesturestart','dblclick'])document.addEventListener(event,e=>e.preventDefault(),{passive:false});
