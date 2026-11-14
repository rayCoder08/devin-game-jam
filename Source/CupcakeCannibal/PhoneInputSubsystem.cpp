#include "CupcakeRuntime.h"
#include "WebSocketsModule.h"
#include "IWebSocket.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"
#include "Interfaces/IHttpRequest.h"
#include "ImageUtils.h"
#include "Engine/Texture2D.h"

void UPhoneInputSubsystem::Initialize(FSubsystemCollectionBase& C){Super::Initialize(C);}
void UPhoneInputSubsystem::Deinitialize(){if(Socket){Socket->OnMessage().Clear();Socket->OnConnected().Clear();Socket->OnConnectionError().Clear();Socket->OnClosed().Clear();Socket->Close();Socket.Reset();}Super::Deinitialize();}
void UPhoneInputSubsystem::Connect(){
 if(Socket){Socket->OnMessage().Clear();Socket->OnConnected().Clear();Socket->OnConnectionError().Clear();Socket->OnClosed().Clear();Socket->Close();}
 Socket=FWebSocketsModule::Get().CreateWebSocket(TEXT("ws://127.0.0.1:3000/ue"));
 Socket->OnConnected().AddWeakLambda(this,[this](){Connection=TEXT("Relay connected");LastState[0].Empty();LastState[1].Empty();});
 Socket->OnConnectionError().AddWeakLambda(this,[this](const FString&){Connection=TEXT("Relay offline");});
 Socket->OnClosed().AddWeakLambda(this,[this](int32,const FString&,bool){Connection=TEXT("Relay offline");for(int i=0;i<2;i++){Inputs[i]={};Joined[i]=false;Ready[i]=false;LastInput[i]=-1000;}});
 Socket->OnMessage().AddWeakLambda(this,[this](const FString& M){Receive(M);});Socket->Connect();
}
void UPhoneInputSubsystem::Pump(float Delta){
 if(FParse::Param(FCommandLine::Get(),TEXT("NoPhone"))){Connection=TEXT("Keyboard only");return;}
 Retry-=Delta;if((!Socket||!Socket->IsConnected())&&Retry<=0){Retry=2;Connect();}
 double Now=FPlatformTime::Seconds();for(int i=0;i<2;i++)if(Now-LastInput[i]>.5)Inputs[i].move={};
 if(!PublicUrl.IsEmpty()&&!QR&&!DownloadingQR){
  DownloadingQR=true;auto Request=FHttpModule::Get().CreateRequest();Request->SetURL(TEXT("http://127.0.0.1:3000/qr.png"));Request->SetVerb(TEXT("GET"));
  Request->OnProcessRequestComplete().BindWeakLambda(this,[this](FHttpRequestPtr,FHttpResponsePtr Response,bool Ok){DownloadingQR=false;if(Ok&&Response.IsValid()&&Response->GetResponseCode()==200)QR=FImageUtils::ImportBufferAsTexture2D(Response->GetContent());});Request->ProcessRequest();
 }
}
void UPhoneInputSubsystem::Receive(const FString& Message){
 TSharedPtr<FJsonObject> Obj;auto Reader=TJsonReaderFactory<>::Create(Message);if(!FJsonSerializer::Deserialize(Reader,Obj)||!Obj)return;
 FString Type;if(!Obj->TryGetStringField(TEXT("t"),Type))return;
 if(Type==TEXT("room")){Obj->TryGetStringField(TEXT("code"),RoomCode);FString Next;if(Obj->TryGetStringField(TEXT("url"),Next)&&Next!=PublicUrl){PublicUrl=Next;QR=nullptr;}return;}
 if(Type==TEXT("rematch")){Rematch=true;return;}
 double S;if(!Obj->TryGetNumberField(TEXT("slot"),S))return;int Slot=(int)S;if(Slot<0||Slot>1)return;
 if(Type==TEXT("left")){Inputs[Slot]={};Joined[Slot]=false;Ready[Slot]=false;LastInput[Slot]=-1000;return;}
 if(Type==TEXT("joined")){Joined[Slot]=true;return;}
 if(Type==TEXT("ready")){Ready[Slot]=true;Joined[Slot]=true;return;}
 if(Type==TEXT("in")){
  double X=0,Y=0;bool Hit=false;Obj->TryGetNumberField(TEXT("x"),X);Obj->TryGetNumberField(TEXT("y"),Y);Obj->TryGetBoolField(TEXT("hit"),Hit);
  if(!FMath::IsFinite(X)||!FMath::IsFinite(Y))return;
  Inputs[Slot].move={(float)FMath::Clamp(X,-1.0,1.0),(float)FMath::Clamp(Y,-1.0,1.0)};Inputs[Slot].hit|=Hit;LastInput[Slot]=FPlatformTime::Seconds();Joined[Slot]=true;
 }
}
void UPhoneInputSubsystem::SendState(int Slot,const Bakery::Player& P,const FString& Phase){
 if(!Socket||!Socket->IsConnected())return;
 bool Debug=FParse::Param(FCommandLine::Get(),TEXT("DemoTrace"));
 if(Debug&&FPlatformTime::Seconds()-LastDebugState[Slot]<.1)return;
 FString M=FString::Printf(TEXT("{\"t\":\"state\",\"slot\":%d,\"color\":\"%s\",\"pips\":%d,\"points\":%d,\"phase\":\"%s\"}"),Slot,Slot==0?TEXT("#f76b9b"):TEXT("#77503d"),P.pips,P.points,*Phase);
 if(Debug)M=M.LeftChop(1)+FString::Printf(TEXT(",\"x\":%.1f,\"y\":%.1f}"),P.pos.x,P.pos.y);
 if(M!=LastState[Slot]){Socket->Send(M);LastState[Slot]=M;LastDebugState[Slot]=FPlatformTime::Seconds();}
}
