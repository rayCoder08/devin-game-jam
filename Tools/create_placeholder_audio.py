"""Temporary synthesized cues; replace with the team's later voice/SFX files."""
import math,wave,struct,os,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out=os.path.join(ROOT,'DemoSource','Audio');os.makedirs(out,exist_ok=True)
tones={'countdown':(520,.13),'go':(1040,.25),'bite':(190,.10),'hit':(120,.13),'caneSwing':(750,.18),'pickup':(980,.15),'sunWarn':(420,.4),'melt':(160,.22),'roundWin':(880,.42),'matchWin':(1100,.6),'tiebreak':(650,.32)}
for name,(freq,seconds) in tones.items():
 rate=24000;values=[]
 for i in range(int(seconds*rate)):
  t=i/rate;env=min(1,t/.008)*max(0,1-t/seconds)**1.7
  chirp=(1-t/seconds*.45) if name in ('bite','hit','melt','caneSwing') else 1+t/seconds*.2
  values.append(struct.pack('<h',int(6500*env*(.8*math.sin(2*math.pi*freq*chirp*t)+.2*math.sin(4*math.pi*freq*t)))))
 with wave.open(os.path.join(out,name+'.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(values))
json.dump({'status':'temporary synthesized tones','replace_with':'team-provided voice lines and sound effects','cues':list(tones)},open(os.path.join(out,'README.json'),'w'),indent=2)
