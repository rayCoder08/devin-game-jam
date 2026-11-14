#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/HUD.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "CupcakeRules.h"
#include "CupcakeRuntime.generated.h"

class UStaticMeshComponent;
class USceneComponent;
class UCapsuleComponent;
class UTexture2D;
class USoundBase;
class IWebSocket;
class ACameraActor;

UCLASS()
class CUPCAKECANNIBAL_API UPhoneInputSubsystem : public UGameInstanceSubsystem {
 GENERATED_BODY()
public:
 virtual void Initialize(FSubsystemCollectionBase& Collection) override;
 virtual void Deinitialize() override;
 void Pump(float Delta);
 void SendState(int Slot,const Bakery::Player& Player,const FString& Phase);
 void Connect();
 void Receive(const FString& Message);
 TSharedPtr<IWebSocket> Socket;
 Bakery::Input Inputs[2];
 double LastInput[2]={-1000,-1000};
 bool Joined[2]={false,false};
 bool Ready[2]={false,false};
 bool Rematch=false;
 FString RoomCode=TEXT("----"),PublicUrl,Connection=TEXT("Starting relay connection");
 float Retry=0;
 FString LastState[2];
 double LastDebugState[2]={0,0};
 UPROPERTY() TObjectPtr<UTexture2D> QR;
 bool DownloadingQR=false;
};

UCLASS()
class CUPCAKECANNIBAL_API ACupcakePawn : public APawn {
 GENERATED_BODY()
public:
 ACupcakePawn();
 void Setup(int Slot);
 void Sync(const Bakery::Player& State,float Time);
 UPROPERTY(VisibleAnywhere) TObjectPtr<UCapsuleComponent> Capsule;
 UPROPERTY(VisibleAnywhere) TObjectPtr<USceneComponent> VisualRoot;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Model;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> Ring;
 UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> HeldCane;
 FVector ModelScale=FVector(1);
 int PlayerSlot=0;
};

UCLASS()
class CUPCAKECANNIBAL_API ACupcakeGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 ACupcakeGameMode();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 void BuildArena();
 void OnEvents(unsigned Events);
 void Rematch();
 Bakery::Match Match;
 UPROPERTY() TArray<TObjectPtr<ACupcakePawn>> Players;
 UPROPERTY() TObjectPtr<AActor> CanePickup;
 UPROPERTY() TObjectPtr<ACameraActor> ArenaCamera;
 UPROPERTY(EditAnywhere,Category="Story") FString StoryLine=TEXT("One secret recipe. Two hungry cupcakes. Only one sweetest survivor.");
 UPROPERTY(EditAnywhere,Category="Audio") TMap<FName,TObjectPtr<USoundBase>> AudioCues;
 UPROPERTY(EditAnywhere,Category="Rules") float MoveSpeed=450;
 UPROPERTY(EditAnywhere,Category="Rules") float BiteRange=165;
 UPROPERTY(EditAnywhere,Category="Rules") float BiteCooldown=.6f;
 UPROPERTY(EditAnywhere,Category="Rules") float HitImmunity=.8f;
 UPROPERTY(EditAnywhere,Category="Rules") float CaneRange=300;
 UPROPERTY(EditAnywhere,Category="Rules") float CaneWindup=.4f;
 UPROPERTY(EditAnywhere,Category="Rules") float CaneRespawn=6;
 UPROPERTY(EditAnywhere,Category="Rules") float RoundTime=60;
 UPROPERTY(EditAnywhere,Category="Rules") int32 RoundsToWin=2;
 float Accumulator=0,WorldTime=0;
 bool PendingHit[2]={false,false};
 bool AutoDemo=false;
 FString GetPhaseName()const;
};

UCLASS()
class CUPCAKECANNIBAL_API ACupcakeHUD : public AHUD {
 GENERATED_BODY()
public:
 virtual void DrawHUD() override;
 void Text(const FString& S,float X,float Y,float Size,FLinearColor C,bool Center=false);
 void Panel(float X,float Y,float W,float H,FLinearColor Color);
};
