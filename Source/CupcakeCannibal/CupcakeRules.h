#pragma once
#include <array>
#include <cmath>
#include <algorithm>
#include <string>

// Deterministic, engine-independent match rules. Simulation advances at 60 Hz.
namespace Bakery {
struct V2 {
 float x=0,y=0;
 V2 operator+(V2 b)const{return{x+b.x,y+b.y};}
 V2 operator-(V2 b)const{return{x-b.x,y-b.y};}
 V2 operator*(float s)const{return{x*s,y*s};}
 float length()const{return std::sqrt(x*x+y*y);}
 V2 unit()const{float n=length();return n>.0001f?(*this)*(1.f/n):V2{};}
};
inline float dot(V2 a,V2 b){return a.x*b.x+a.y*b.y;}
struct Input { V2 move; bool hit=false; };
struct Player {
 V2 pos,face,knock;
 int pips=5,crumbs=0,points=0;
 float cooldown=0,immune=0,windup=-1,flash=0;
 bool cane=false,ready=false;
};
enum class Phase{Lobby,Countdown,Playing,Tiebreak,RoundResult,MatchEnd};
struct Settings {
 int pips=5,roundsToWin=2,maxRestarts=3;
 float biteRange=110,biteArc=70,biteCooldown=.6f,immunity=.8f;
 float caneRange=240,caneArc=100,caneWindup=.4f,caneRespawn=6;
 float knockback=300,speed=450,roundTime=60,tiebreakTime=10,resultDelay=3;
 float playerRadius=44;
};
struct Obstacle{V2 pos;float radius;};
struct Match {
 Settings cfg;
 std::array<Player,2> p;
 std::array<Obstacle,3> obstacles{{{{-290,150},72},{{270,-110},68},{{40,360},55}}};
 Phase phase=Phase::Lobby;
 float clock=0,phaseTime=0,caneTimer=0,calloutTime=0;
 int restarts=0,winner=-1,round=1,sunIndex=0;
 bool caneAvailable=true,coinChoice=false;
 unsigned eventMask=0;
 std::string reason,callout;
 enum Event {Bite=1,CaneWindup=2,CaneHit=4,Pickup=8,SunWarn=16,Melt=32,RoundEnd=64,MatchEnd=128,TiebreakStart=256,Countdown=512};
 Match(){positions();}
 void positions(){p[0].pos={-350,-190};p[1].pos={350,190};p[0].face={1,0};p[1].face={-1,0};}
 void announce(const std::string& text,float duration=1.1f){callout=text;calloutTime=duration;}
 void resetRound(){
  for(auto& a:p){int points=a.points;bool ready=a.ready;a=Player{};a.pips=cfg.pips;a.points=points;a.ready=ready;}
  positions();clock=phaseTime=0;sunIndex=restarts=0;winner=-1;caneAvailable=true;caneTimer=0;
 }
 void start(){resetRound();phase=Phase::Countdown;eventMask|=Countdown;announce("3",1);}
 void rematch(){int n=0;for(auto& a:p){a=Player{};a.ready=true;++n;}round=1;start();}
 bool inArc(int i,float range,float arc)const{
  V2 d=p[1-i].pos-p[i].pos;float n=d.length();
  return n<=range&&(n<.001f||dot(p[i].face,d.unit())>=std::cos(arc*.5f*3.14159265f/180.f));
 }
 void constrain(Player& a){
  float edge=834-cfg.playerRadius;if(a.pos.length()>edge)a.pos=a.pos.unit()*edge;
  for(auto& o:obstacles){V2 d=a.pos-o.pos;float n=d.length(),r=cfg.playerRadius+o.radius;if(n<r)a.pos=o.pos+(n>.001f?d.unit():V2{1,0})*r;}
 }
 void enterTiebreak(){
  phase=Phase::Tiebreak;clock=0;phaseTime=0;caneAvailable=false;caneTimer=0;
  for(auto& a:p){a.pips=1;a.cane=false;a.windup=-1;a.cooldown=a.immune=0;a.knock={};}
  positions();eventMask|=TiebreakStart;announce("GOLDEN CRUMB!",2);
 }
 void award(int who,const std::string& why){
  if(phase==Phase::RoundResult||phase==Phase::MatchEnd)return;
  winner=who;reason=why;++p[who].points;phase=Phase::RoundResult;phaseTime=0;eventMask|=RoundEnd;
  announce((who==0?"STRAWBERRY":"CHOCOLATE")+std::string(" WINS!"),3);
 }
 void restartTie(){
  if(restarts>=cfg.maxRestarts){award(coinChoice?1:0,"Sugar rush coin flip!");return;}
  ++restarts;enterTiebreak();announce("GOLDEN CRUMB - AGAIN!",1.5f);
 }
 void evaluate(){
  if(phase==Phase::Tiebreak){
   if((p[0].pips==0)!=(p[1].pips==0))award(p[0].pips>0?0:1,"Golden Crumb");
   else if((p[0].pips==0&&p[1].pips==0)||clock>=cfg.tiebreakTime)restartTie();
   return;
  }
  if((p[0].pips==0)!=(p[1].pips==0)){award(p[0].pips>0?0:1,"Knockout");return;}
  if(p[0].pips>0&&p[1].pips>0&&clock<cfg.roundTime)return;
  if(p[0].pips!=p[1].pips){award(p[0].pips>p[1].pips?0:1,"More frosting");return;}
  if(p[0].crumbs!=p[1].crumbs){award(p[0].crumbs>p[1].crumbs?0:1,"Crumbs");return;}
  enterTiebreak();
 }
 void step(float dt,const std::array<Input,2>& input){
  eventMask=0;calloutTime=std::max(0.f,calloutTime-dt);phaseTime+=dt;
  if(phase==Phase::Lobby){for(int i=0;i<2;++i)if(input[i].hit)p[i].ready=true;if(p[0].ready&&p[1].ready)start();return;}
  if(phase==Phase::Countdown){
   int before=int(phaseTime-dt),after=int(phaseTime);
   if(phaseTime>=3){phase=Phase::Playing;phaseTime=0;announce("GO!",1);}
   else if(after!=before){announce(std::to_string(3-after),1);eventMask|=Countdown;}return;
  }
  if(phase==Phase::RoundResult){if(phaseTime>=cfg.resultDelay){if(p[winner].points>=cfg.roundsToWin){phase=Phase::MatchEnd;eventMask|=MatchEnd;}else{++round;start();}}return;}
  if(phase==Phase::MatchEnd)return;
  float oldClock=clock;clock+=dt;
  for(int i=0;i<2;++i){auto& a=p[i];a.cooldown=std::max(0.f,a.cooldown-dt);a.immune=std::max(0.f,a.immune-dt);a.flash=std::max(0.f,a.flash-dt);
   V2 v=input[i].move;if(v.length()>1)v=v.unit();if(v.length()>.05f)a.face=v.unit();
   a.pos=a.pos+v*(cfg.speed*dt)+a.knock*dt;a.knock=a.knock*std::max(0.f,1.f-9.f*dt);constrain(a);
  }
  V2 between=p[1].pos-p[0].pos;float separation=between.length();
  float diameter=2*cfg.playerRadius;if(separation<diameter){V2 push=(separation>.001f?between.unit():V2{1,0})*((diameter-separation)*.5f);p[0].pos=p[0].pos-push;p[1].pos=p[1].pos+push;constrain(p[0]);constrain(p[1]);}
  if(phase==Phase::Playing){
   if(!caneAvailable&&!p[0].cane&&!p[1].cane){caneTimer-=dt;if(caneTimer<=0)caneAvailable=true;}
   if(caneAvailable)for(int i=0;i<2;++i)if(p[i].pos.length()<80){p[i].cane=true;caneAvailable=false;eventMask|=Pickup;announce("CANDY CANE!",.8f);break;}
  }
  std::array<int,2> damage{{0,0}},earned{{0,0}};std::array<V2,2> knock;
  // Read both targets' pre-damage immunity, then apply both hits together.
  auto hit=[&](int i,bool cane){int j=1-i;if(p[j].immune<=0){++damage[j];earned[i]+=cane?1:2;knock[j]=(p[j].pos-p[i].pos).unit()*cfg.knockback;eventMask|=cane?CaneHit:Bite;}};
  for(int i=0;i<2;++i){auto& a=p[i];
   if(a.windup>=0){a.windup-=dt;if(a.windup<=0){if(inArc(i,cfg.caneRange,cfg.caneArc))hit(i,true);a.windup=-1;a.cane=false;caneTimer=cfg.caneRespawn;}}
   if(input[i].hit){
    if(inArc(i,cfg.biteRange,cfg.biteArc)){if(a.cooldown<=0){a.cooldown=cfg.biteCooldown;hit(i,false);}}
    else if(a.cane&&a.windup<0){a.windup=cfg.caneWindup;eventMask|=CaneWindup;}
   }
  }
  for(int i=0;i<2;++i){p[i].crumbs+=earned[i];if(damage[i]){p[i].pips=std::max(0,p[i].pips-damage[i]);p[i].immune=cfg.immunity;p[i].knock=knock[i];p[i].flash=.3f;}}
  if(eventMask&Bite)announce("CHOMP!",.6f);else if(eventMask&CaneHit)announce("SWEET HIT!",.6f);
  if(phase==Phase::Playing){
   const float ticks[4]={30,45,55,58};
   for(float t:ticks)if(oldClock<t-1&&clock>=t-1){eventMask|=SunWarn;announce("SUN!",1);}
   while(sunIndex<4&&clock>=ticks[sunIndex]){for(auto& a:p){a.pips=std::max(0,a.pips-1);a.flash=.35f;}++sunIndex;eventMask|=Melt;}
  }
  evaluate();
 }
};
}
