#include "CupcakeRuntime.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

ACupcakePawn::ACupcakePawn(){
 Capsule=CreateDefaultSubobject<UCapsuleComponent>(TEXT("SolidCupcake"));Capsule->InitCapsuleSize(64,104);RootComponent=Capsule;
 Capsule->SetCollisionProfileName(TEXT("Pawn"));Capsule->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
 VisualRoot=CreateDefaultSubobject<USceneComponent>(TEXT("AnimatedVisual"));VisualRoot->SetupAttachment(RootComponent);
 Model=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MeshyCharacter"));Model->SetupAttachment(VisualRoot);Model->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Ring=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlayerColor"));Ring->SetupAttachment(RootComponent);Ring->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 HeldCane=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HeldCandyCane"));HeldCane->SetupAttachment(VisualRoot);HeldCane->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void ACupcakePawn::Setup(int Slot){
 PlayerSlot=Slot;
 UStaticMesh* Mesh=LoadObject<UStaticMesh>(nullptr,Slot==0?TEXT("/Game/Models/Strawberry/SM_Strawberry.SM_Strawberry"):TEXT("/Game/Models/Chocolate/SM_Chocolate.SM_Chocolate"));
 if(!Mesh)Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere"));
 Model->SetStaticMesh(Mesh);auto Bounds=Mesh->GetBounds();float Scale=208.f/FMath::Max(1.f,Bounds.BoxExtent.Z*2);ModelScale=FVector(Scale);Model->SetRelativeScale3D(ModelScale);
 Model->SetRelativeLocation(FVector(-Bounds.Origin.X*Scale,-Bounds.Origin.Y*Scale,-104-(Bounds.Origin.Z-Bounds.BoxExtent.Z)*Scale));
 Ring->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));Ring->SetRelativeScale3D(FVector(1.65,1.65,.035));Ring->SetRelativeLocation(FVector(0,0,-101));
 Ring->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,Slot==0?TEXT("/Game/CandyCarnival/Materials/M_Raspberry.M_Raspberry"):TEXT("/Game/CandyCarnival/Materials/M_Chocolate.M_Chocolate")));
 auto CaneMesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Props/SM_CandyCane.SM_CandyCane"));HeldCane->SetStaticMesh(CaneMesh);
 if(CaneMesh)HeldCane->SetRelativeScale3D(FVector(130.f/FMath::Max(.001f,2*CaneMesh->GetBounds().BoxExtent.Z)));
 HeldCane->SetRelativeLocation(FVector(60,20,0));HeldCane->SetRelativeRotation(FRotator(0,20,-25));HeldCane->SetVisibility(false);
}
void ACupcakePawn::Sync(const Bakery::Player& S,float Time){
 SetActorLocation(FVector(S.pos.x,S.pos.y,104));
 const float Angle=FMath::RadiansToDegrees(FMath::Atan2(S.face.y,S.face.x));
 VisualRoot->SetRelativeRotation(FRotator(0,Angle-90,0));
 float Bob=FMath::Sin(Time*7+PlayerSlot)*2.5f;
 VisualRoot->SetRelativeLocation(FVector(S.flash>0?FMath::Sin(Time*80)*4:0,0,Bob));
 Model->SetVisibility(S.immune<=0||FMath::Fmod(Time,.14f)<.085f);
 HeldCane->SetVisibility(S.cane);HeldCane->SetRelativeRotation(FRotator(0,S.windup>=0?FMath::Sin(Time*20)*30:20,-25));
}
