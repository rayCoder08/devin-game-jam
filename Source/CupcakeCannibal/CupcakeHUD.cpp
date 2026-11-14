#include "CupcakeRuntime.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/Texture2D.h"
#include "CanvasItem.h"
#include "Kismet/GameplayStatics.h"

void ACupcakeHUD::Panel(float X,float Y,float W,float H,FLinearColor C){DrawRect(C,X,Y,W,H);}
void ACupcakeHUD::Text(const FString& S,float X,float Y,float Size,FLinearColor C,bool Center){
 Size*=2.0f;
 auto Font=GEngine->GetLargeFont();float W,H;GetTextSize(S,W,H,Font,Size);
 FCanvasTextItem T(FVector2D(Center?X-W*.5f:X,Y),FText::FromString(S),Font,C);T.Scale=FVector2D(Size);
 T.EnableShadow(FLinearColor(0.08,.02,.05,.40));Canvas->DrawItem(T);
}
void ACupcakeHUD::DrawHUD(){
 Super::DrawHUD();auto G=Cast<ACupcakeGameMode>(UGameplayStatics::GetGameMode(this));if(!G||!Canvas)return;
 auto& M=G->Match;float W=Canvas->SizeX,H=Canvas->SizeY,S=FMath::Min(W/1920.f,H/1080.f);
 FLinearColor Cream(1,.94,.82,1),Ink(.12,.045,.085,1),Pink(.96,.27,.49,1),Cocoa(.35,.16,.09,1),Gold(1,.72,.20,1);
 Panel(0,0,W,145*S,FLinearColor(.10,.025,.07,.90));
 for(int i=0;i<2;i++){
  float X=i==0?48*S:W-460*S;FLinearColor C=i==0?Pink:Cocoa;
  Panel(X,28*S,410*S,8*S,C);Text(i==0?TEXT("STRAWBERRY"):TEXT("CHOCOLATE"),X,46*S,1.3f*S,Cream);
  for(int j=0;j<5;j++)Panel(X+j*53*S,95*S,43*S,23*S,j<M.p[i].pips?C:FLinearColor(.26,.19,.22,1));
  for(int j=0;j<2;j++)Text(j<M.p[i].points?TEXT("*"):TEXT("o"),X+(305+j*43)*S,86*S,1.5f*S,j<M.p[i].points?Gold:Cream);
 }
 Text(FString::Printf(TEXT("ROUND %d  /  FIRST TO 2"),M.round),W*.5f,24*S,.85f*S,Cream,true);
 int Seconds=FMath::Max(0,FMath::CeilToInt((M.phase==Bakery::Phase::Tiebreak?M.cfg.tiebreakTime:M.cfg.roundTime)-M.clock));
 Text(FString::Printf(TEXT("%02d"),Seconds),W*.5f,58*S,2.3f*S,M.phase==Bakery::Phase::Tiebreak?Gold:Cream,true);
 if(M.phase==Bakery::Phase::Playing){const float Ticks[]={30,45,55,58};if(M.sunIndex<4)Text(FString::Printf(TEXT("SUN IN %ds"),FMath::Max(0,FMath::CeilToInt(Ticks[M.sunIndex]-M.clock))),W*.5f,H-53*S,.85f*S,Ink,true);}
 if(M.phase==Bakery::Phase::Tiebreak)Text(TEXT("ONE PIP. FIRST UNCONTESTED BITE WINS."),W*.5f,H-53*S,.8f*S,Ink,true);
 auto Phone=GetGameInstance()->GetSubsystem<UPhoneInputSubsystem>();
 if(M.phase==Bakery::Phase::Lobby){
  Panel(0,145*S,W,H-145*S,FLinearColor(.08,.015,.05,.35));
  float X=W*.5f-580*S,Y=H*.5f-280*S;
  Panel(X,Y,1160*S,620*S,FLinearColor(.12,.04,.075,.96));Panel(X,Y,1160*S,8*S,Pink);
  Text(TEXT("CUPCAKE CANNIBAL"),W*.5f,Y+48*S,2.25f*S,Cream,true);
  Text(G->StoryLine,W*.5f,Y+124*S,.72f*S,Cream,true);
  Text(TEXT("TILT. CHOMP. TAKE THE CAKE."),W*.5f,Y+180*S,1.05f*S,Gold,true);
  Text(TEXT("JOIN THE BAKERY"),X+65*S,Y+260*S,1.1f*S,Cream);
  Text(TEXT("Scan with your phone. Enable Motion, then Ready."),X+65*S,Y+310*S,.70f*S,Cream);
  Text(TEXT("ROOM  ")+Phone->RoomCode,X+65*S,Y+360*S,1.65f*S,Gold);
  if(!Phone->PublicUrl.IsEmpty())Text(Phone->PublicUrl,X+65*S,Y+416*S,.52f*S,Cream);
  else Text(TEXT("Phone pairing appears when the relay is connected."),X+65*S,Y+416*S,.58f*S,Cream);
  for(int i=0;i<2;i++)Text(FString(i==0?TEXT("STRAWBERRY  "):TEXT("CHOCOLATE  "))+(M.p[i].ready?TEXT("READY!"):TEXT("WAITING...")),X+65*S,Y+(490+i*44)*S,.85f*S,M.p[i].ready?Gold:Cream);
  if(Phone->QR)DrawTextureSimple(Phone->QR,X+840*S,Y+265*S,250*S/FMath::Max(1,Phone->QR->GetSizeX()));
 }
 if(M.phase==Bakery::Phase::RoundResult||M.phase==Bakery::Phase::MatchEnd){
  bool End=M.phase==Bakery::Phase::MatchEnd;Panel(0,145*S,W,H-145*S,FLinearColor(.08,.015,.05,.50));
  float X=W*.5f-450*S,Y=H*.5f-185*S;Panel(X,Y,900*S,430*S,FLinearColor(.12,.04,.075,.97));Panel(X,Y,900*S,8*S,Gold);
  Text(End?TEXT("SWEET VICTORY!"):TEXT("ROUND SERVED!"),W*.5f,Y+35*S,1.25f*S,Gold,true);
  Text(M.winner==0?TEXT("STRAWBERRY WINS!"):TEXT("CHOCOLATE WINS!"),W*.5f,Y+103*S,1.8f*S,Cream,true);
  Text(UTF8_TO_TCHAR(M.reason.c_str()),W*.5f,Y+180*S,.90f*S,Gold,true);
  Text(FString::Printf(TEXT("FROSTING  %d : %d      CRUMBS  %d : %d"),M.p[0].pips,M.p[1].pips,M.p[0].crumbs,M.p[1].crumbs),W*.5f,Y+238*S,.95f*S,Cream,true);
  Text(End?TEXT("REMATCH  -  TAP YOUR PHONE OR CLICK HERE"):TEXT("NEXT ROUND COMING RIGHT UP..."),W*.5f,Y+330*S,.85f*S,Cream,true);
 }else if(M.calloutTime>0&&M.phase!=Bakery::Phase::Lobby){
  bool Sun=M.callout=="SUN!";if(Sun)Panel(0,145*S,W,H-145*S,FLinearColor(1,.65,.04,.15));
  Text(UTF8_TO_TCHAR(M.callout.c_str()),W*.5f,190*S,M.phase==Bakery::Phase::Countdown?3.5f*S:1.65f*S,Sun?Gold:Cream,true);
 }
}
