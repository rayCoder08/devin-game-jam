#include "CupcakeRuntime.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "DrawDebugHelpers.h"
#include "Materials/MaterialInterface.h"
#include "Sound/SoundBase.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/FileHelper.h"

ACupcakeGameMode::ACupcakeGameMode(){PrimaryActorTick.bCanEverTick=true;DefaultPawnClass=nullptr;HUDClass=ACupcakeHUD::StaticClass();}
static AStaticMeshActor* Shape(UWorld* W,const TCHAR* MeshPath,FVector P,FVector S,const TCHAR* Mat){
 auto A=W->SpawnActor<AStaticMeshActor>(P,FRotator::ZeroRotator);A->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 A->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,MeshPath));A->SetActorScale3D(S);A->SetActorEnableCollision(false);
 if(Mat)A->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,Mat));return A;
}
static AStaticMeshActor* Prop(UWorld* W,const TCHAR* Path,FVector P,float Height){
 auto Mesh=LoadObject<UStaticMesh>(nullptr,Path);if(!Mesh)return nullptr;auto B=Mesh->GetBounds();float S=Height/FMath::Max(1.f,2*B.BoxExtent.Z);
 auto A=Shape(W,Path,P,FVector(S),nullptr);A->SetActorLocation(P-FVector(B.Origin.X*S,B.Origin.Y*S,(B.Origin.Z-B.BoxExtent.Z)*S));return A;
}
void ACupcakeGameMode::BuildArena(){
 const TCHAR* Cylinder=TEXT("/Engine/BasicShapes/Cylinder.Cylinder");
 Shape(GetWorld(),Cylinder,FVector(0,0,-65),FVector(18,18,1),TEXT("/Game/CandyCarnival/Materials/M_Lilac.M_Lilac"));
 Shape(GetWorld(),Cylinder,FVector(0,0,-20),FVector(17,17,.35),TEXT("/Game/CandyCarnival/Materials/M_GoldenBiscuit.M_GoldenBiscuit"));
 for(int i=0;i<56;i++){float A=i*2*PI/56;Shape(GetWorld(),TEXT("/Engine/BasicShapes/Sphere.Sphere"),FVector(845*FMath::Cos(A),845*FMath::Sin(A),-8),FVector(.64,.64,.44),TEXT("/Game/CandyCarnival/Materials/M_Cream.M_Cream"));}
 for(int i=0;i<3;i++){const auto& O=Match.obstacles[i];Prop(GetWorld(),i==1?TEXT("/Game/CandyCarnival/Meshes/SM_12_Popcorn_00.SM_12_Popcorn_00"):TEXT("/Game/CandyCarnival/Meshes/SM_11_Candy_Apple_02.SM_11_Candy_Apple_02"),FVector(O.pos.x,O.pos.y,0),i==1?170:210);}
 Shape(GetWorld(),Cylinder,FVector(0,0,5),FVector(1.5,1.5,.08),TEXT("/Game/CandyCarnival/Materials/M_Gold.M_Gold"));
 CanePickup=Prop(GetWorld(),TEXT("/Game/Props/SM_CandyCane.SM_CandyCane"),FVector(0,0,30),130);
 ArenaCamera=GetWorld()->SpawnActor<ACameraActor>(FVector(0,2250,1900),FRotator::ZeroRotator);
 ArenaCamera->SetActorRotation((FVector(0,-260,50)-ArenaCamera->GetActorLocation()).Rotation());ArenaCamera->GetCameraComponent()->SetFieldOfView(74);
}
void ACupcakeGameMode::BeginPlay(){
 Super::BeginPlay();BuildArena();
 Match.cfg.speed=MoveSpeed;Match.cfg.playerRadius=64;Match.cfg.biteRange=BiteRange;Match.cfg.biteCooldown=BiteCooldown;Match.cfg.immunity=HitImmunity;Match.cfg.caneRange=CaneRange;Match.cfg.caneWindup=CaneWindup;Match.cfg.caneRespawn=CaneRespawn;Match.cfg.roundTime=RoundTime;Match.cfg.roundsToWin=RoundsToWin;
 for(int i=0;i<2;i++){auto P=GetWorld()->SpawnActor<ACupcakePawn>();P->Setup(i);Players.Add(P);P->Sync(Match.p[i],0);}
 if(auto PC=UGameplayStatics::GetPlayerController(this,0)){PC->SetViewTarget(ArenaCamera);PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameOnly());}
 AutoDemo=FParse::Param(FCommandLine::Get(),TEXT("DemoBots"));
 if(AutoDemo){Match.p[0].ready=Match.p[1].ready=true;Match.start();}
 const TCHAR* Names[]={TEXT("countdown"),TEXT("go"),TEXT("bite"),TEXT("hit"),TEXT("caneSwing"),TEXT("pickup"),TEXT("sunWarn"),TEXT("melt"),TEXT("roundWin"),TEXT("matchWin"),TEXT("tiebreak"),TEXT("introVoice"),TEXT("hurtStrawberry"),TEXT("hurtChocolate"),TEXT("music")};
 for(auto Name:Names){FString Path=FString::Printf(TEXT("/Game/Audio/Cues/%s.%s"),Name,Name);if(auto Sound=LoadObject<USoundBase>(nullptr,*Path,nullptr,LOAD_NoWarn))AudioCues.Add(FName(Name),Sound);}
 if(auto Music=AudioCues.Find(TEXT("music")))UGameplayStatics::SpawnSound2D(this,*Music,.18f);
 UE_LOG(LogTemp,Display,TEXT("CUPCAKE_DEMO_READY: two Meshy players, cake arena, keyboard controls, rules and phone client"));
}
void ACupcakeGameMode::Rematch(){Match.rematch();}
FString ACupcakeGameMode::GetPhaseName()const{
 switch(Match.phase){case Bakery::Phase::Lobby:return TEXT("lobby");case Bakery::Phase::Countdown:return TEXT("countdown");case Bakery::Phase::Playing:return TEXT("playing");case Bakery::Phase::Tiebreak:return TEXT("tiebreak");case Bakery::Phase::RoundResult:return TEXT("roundResult");default:return TEXT("matchEnd");}
}
void ACupcakeGameMode::OnEvents(unsigned Events){
 struct Cue{unsigned Bit;const TCHAR* Name;};const Cue Cues[]={{Bakery::Match::Bite,TEXT("bite")},{Bakery::Match::CaneWindup,TEXT("caneSwing")},{Bakery::Match::CaneHit,TEXT("hit")},{Bakery::Match::Pickup,TEXT("pickup")},{Bakery::Match::SunWarn,TEXT("sunWarn")},{Bakery::Match::Melt,TEXT("melt")},{Bakery::Match::RoundEnd,TEXT("roundWin")},{Bakery::Match::MatchEnd,TEXT("matchWin")},{Bakery::Match::TiebreakStart,TEXT("tiebreak")},{Bakery::Match::Countdown,TEXT("countdown")}};
 for(auto C:Cues)if(Events&C.Bit){
  if(C.Bit==Bakery::Match::Countdown&&AudioCues.Contains(TEXT("introVoice"))){if(Match.phaseTime<.1f)UGameplayStatics::PlaySound2D(this,AudioCues[TEXT("introVoice")],.75f);continue;}
  if(auto S=AudioCues.Find(FName(C.Name)))if(*S)UGameplayStatics::PlaySound2D(this,*S,.7f);
 }
}
void ACupcakeGameMode::Tick(float Delta){
 Super::Tick(Delta);WorldTime+=Delta;auto PC=UGameplayStatics::GetPlayerController(this,0);if(!PC)return;
 PC->bAutoManageActiveCameraTarget=false;
 if(PC->GetViewTarget()!=ArenaCamera){PC->SetViewTarget(ArenaCamera);PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameOnly());}
 // Opt-in packaged smoke test exercises actual PlayerController keyboard input.
 if(FParse::Param(FCommandLine::Get(),TEXT("DemoKeyboardTest"))){
  static int Stage=0;static float StartX=0,StartY=0;static bool FirstMoved=false;
  auto Key=[&](FKey K,EInputEvent E){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,E,E==IE_Pressed?1.f:0.f));};
  if(Stage==0&&WorldTime>1){Key(EKeys::F,IE_Pressed);Key(EKeys::Enter,IE_Pressed);Stage=1;}
  else if(Stage==1&&WorldTime>1.2){Key(EKeys::F,IE_Released);Key(EKeys::Enter,IE_Released);Stage=2;}
  else if(Stage==2&&WorldTime>5){StartX=Match.p[0].pos.x;Key(EKeys::D,IE_Pressed);Stage=3;}
  else if(Stage==3&&WorldTime>5.5){Key(EKeys::D,IE_Released);FirstMoved=Match.p[0].pos.x>StartX+100;StartY=Match.p[1].pos.y;Key(EKeys::Up,IE_Pressed);Stage=4;}
  else if(Stage==4&&WorldTime>6){Key(EKeys::Up,IE_Released);bool Passed=FirstMoved&&Match.p[1].pos.y<StartY-100&&Match.phase==Bakery::Phase::Playing;
   FString Dir=FPaths::ProjectDir()/TEXT("Tests");IFileManager::Get().MakeDirectory(*Dir,true);
   FString Result=FString::Printf(TEXT("{\"passed\":%s,\"test\":\"Packaged keyboard ready, countdown, P1 D and P2 Up movement\",\"p1_x\":%.2f,\"p2_y\":%.2f}"),Passed?TEXT("true"):TEXT("false"),Match.p[0].pos.x,Match.p[1].pos.y);
   FFileHelper::SaveStringToFile(Result,*(Dir/TEXT("keyboard-demo.json")));UE_LOG(LogTemp,Display,TEXT("CUPCAKE_KEYBOARD_TEST %s"),*Result);Stage=5;
  }else if(Stage==5&&WorldTime>8)FPlatformMisc::RequestExit(false);
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("DemoScreenshot"))){
  static bool LobbyShot=false,PlayShot=false;
  FString Dir=FPaths::ProjectDir()/TEXT("Previews");IFileManager::Get().MakeDirectory(*Dir,true);
  if(!LobbyShot&&WorldTime>4){FScreenshotRequest::RequestScreenshot(Dir/TEXT("Cupcake_Lobby.png"),true,false);LobbyShot=true;}
  if(!PlayShot&&Match.phase==Bakery::Phase::Playing&&Match.clock>2){FScreenshotRequest::RequestScreenshot(Dir/TEXT("Cupcake_Gameplay.png"),true,false);PlayShot=true;}
 }
 auto Phone=GetGameInstance()->GetSubsystem<UPhoneInputSubsystem>();Phone->Pump(Delta);
 if(Match.phase==Bakery::Phase::MatchEnd&&(PC->WasInputKeyJustPressed(EKeys::R)||PC->WasInputKeyJustPressed(EKeys::Enter)||PC->WasInputKeyJustPressed(EKeys::LeftMouseButton)||Phone->Rematch)){Rematch();Phone->Rematch=false;}
 else Phone->Rematch=false;
 std::array<Bakery::Input,2> In;
 In[0].move={(float)(PC->IsInputKeyDown(EKeys::D)-PC->IsInputKeyDown(EKeys::A)),(float)(PC->IsInputKeyDown(EKeys::S)-PC->IsInputKeyDown(EKeys::W))};
 In[1].move={(float)(PC->IsInputKeyDown(EKeys::Right)-PC->IsInputKeyDown(EKeys::Left)),(float)(PC->IsInputKeyDown(EKeys::Down)-PC->IsInputKeyDown(EKeys::Up))};
 PendingHit[0]|=PC->WasInputKeyJustPressed(EKeys::F);PendingHit[1]|=PC->WasInputKeyJustPressed(EKeys::Enter);
 for(int i=0;i<2;i++){
  if(FPlatformTime::Seconds()-Phone->LastInput[i]<=.5)In[i].move=Phone->Inputs[i].move;
  PendingHit[i]|=Phone->Inputs[i].hit;Phone->Inputs[i].hit=false;
  if(Match.phase==Bakery::Phase::Lobby&&Phone->Ready[i])Match.p[i].ready=true;
  if(AutoDemo){In[i].move=(Match.p[1-i].pos-Match.p[i].pos).unit();PendingHit[i]|=FMath::Fmod(WorldTime+(i*.18f),.75f)<Delta;}
 }
 Accumulator+=FMath::Min(Delta,.1f);
 if(FParse::Param(FCommandLine::Get(),TEXT("DemoTrace"))&&int(WorldTime)!=int(WorldTime-Delta))UE_LOG(LogTemp,Display,TEXT("DEMO_TRACE phase=%s time=%.2f p0=(%.1f,%.1f) p1=(%.1f,%.1f) input0=(%.2f,%.2f) input1=(%.2f,%.2f) hit=%d,%d fresh=%.2f,%.2f"),*GetPhaseName(),Match.clock,Match.p[0].pos.x,Match.p[0].pos.y,Match.p[1].pos.x,Match.p[1].pos.y,In[0].move.x,In[0].move.y,In[1].move.x,In[1].move.y,PendingHit[0],PendingHit[1],FPlatformTime::Seconds()-Phone->LastInput[0],FPlatformTime::Seconds()-Phone->LastInput[1]);
 while(Accumulator>=1.f/60){
  for(int i=0;i<2;i++){In[i].hit=PendingHit[i];PendingHit[i]=false;}
  auto Before=Match.phase;int OldPips[2]={Match.p[0].pips,Match.p[1].pips};
  Match.coinChoice=FMath::RandBool();Match.step(1.f/60,In);OnEvents(Match.eventMask);
  if(Match.eventMask&(Bakery::Match::Bite|Bakery::Match::CaneHit))for(int i=0;i<2;i++)if(Match.p[i].pips<OldPips[i]){
   if(auto Hurt=AudioCues.Find(i==0?TEXT("hurtStrawberry"):TEXT("hurtChocolate")))UGameplayStatics::PlaySound2D(this,*Hurt,.65f);
  }
  if(Before==Bakery::Phase::Countdown&&Match.phase==Bakery::Phase::Playing){if(auto Sound=AudioCues.Find(TEXT("go")))if(*Sound)UGameplayStatics::PlaySound2D(this,*Sound,.7f);}
  Accumulator-=1.f/60;
 }
 for(int i=0;i<2;i++){Players[i]->Sync(Match.p[i],WorldTime);Phone->SendState(i,Match.p[i],GetPhaseName());
  if(Match.p[i].windup>=0){auto& P=Match.p[i];FVector Center(P.pos.x,P.pos.y,5);float A=FMath::Atan2(P.face.y,P.face.x);for(int j=0;j<16;j++){float A0=A+FMath::DegreesToRadians(-50+j*100.f/16),A1=A+FMath::DegreesToRadians(-50+(j+1)*100.f/16);DrawDebugLine(GetWorld(),Center+FVector(FMath::Cos(A0),FMath::Sin(A0),0)*CaneRange,Center+FVector(FMath::Cos(A1),FMath::Sin(A1),0)*CaneRange,FColor::Yellow,false,0,0,5);}}
 }
 if(CanePickup){CanePickup->SetActorHiddenInGame(!Match.caneAvailable);CanePickup->SetActorLocation(FVector(0,0,35+FMath::Sin(WorldTime*3)*8));CanePickup->SetActorRotation(FRotator(0,WorldTime*60,0));}
}
