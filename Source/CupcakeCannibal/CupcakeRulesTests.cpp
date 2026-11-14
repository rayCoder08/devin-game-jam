#include "CupcakeRules.h"
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FCupcakeRulesTest,"Cupcake.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FCupcakeRulesTest::RunTest(const FString&){
 using namespace Bakery;const float dt=1.f/60;
 auto combat=[](){Match m;m.phase=Phase::Playing;m.p[0].pos={-48,-250};m.p[1].pos={48,-250};m.p[0].face={1,0};m.p[1].face={-1,0};return m;};
 std::array<Input,2> hit0{{{{},true},{{},false}}},both{{{{},true},{{},true}}},idle{};
 {auto m=combat();m.step(dt,hit0);TestEqual(TEXT("unanswered bite costs one pip"),m.p[1].pips,4);TestEqual(TEXT("bite earns two crumbs"),m.p[0].crumbs,2);TestEqual(TEXT("attacker intact"),m.p[0].pips,5);m.step(dt,hit0);TestEqual(TEXT("cooldown prevents repeat"),m.p[1].pips,4);}
 {auto m=combat();m.p[1].pos={130,-250};m.p[0].cane=true;m.caneAvailable=false;m.step(dt,hit0);TestTrue(TEXT("cane has windup"),m.p[0].windup>0);TestEqual(TEXT("no immediate damage"),m.p[1].pips,5);for(int i=0;i<25;i++)m.step(dt,idle);TestEqual(TEXT("cane hit"),m.p[1].pips,4);TestEqual(TEXT("cane one crumb"),m.p[0].crumbs,1);TestFalse(TEXT("cane consumed"),m.p[0].cane);TestFalse(TEXT("cane delayed respawn"),m.caneAvailable);for(int i=0;i<365;i++)m.step(dt,idle);TestTrue(TEXT("cane respawns"),m.caneAvailable);}
 {auto m=combat();m.p[0].pips=1;m.p[1].pips=2;m.p[0].immune=m.p[1].immune=5;m.clock=29.99f;m.step(dt,idle);TestTrue(TEXT("sun knockout ends round"),m.phase==Phase::RoundResult);TestEqual(TEXT("sun ignores immunity"),m.p[0].pips,0);TestEqual(TEXT("sun awards opponent once"),m.p[1].points,1);m.step(dt,idle);TestEqual(TEXT("point not duplicated"),m.p[1].points,1);TestEqual(TEXT("sun no crumbs"),m.p[1].crumbs,0);}
 {auto m=combat();m.p[0].pos={-500,0};m.p[1].pos={500,0};for(int i=0;i<3602;i++)m.step(dt,idle);TestTrue(TEXT("untouched round reaches tiebreak"),m.phase==Phase::Tiebreak);TestEqual(TEXT("tiebreak one pip"),m.p[0].pips,1);TestFalse(TEXT("no cane in tiebreak"),m.caneAvailable);}
 {auto m=combat();m.enterTiebreak();m.p[0].pos={-48,-250};m.p[1].pos={48,-250};m.step(dt,both);TestTrue(TEXT("simultaneous tie bites restart"),m.phase==Phase::Tiebreak);TestEqual(TEXT("restart counted"),m.restarts,1);TestEqual(TEXT("no tie point"),m.p[0].points+m.p[1].points,0);TestEqual(TEXT("both reset to one pip"),m.p[0].pips+m.p[1].pips,2);for(int i=0;i<3;i++){m.clock=10;m.step(dt,idle);}TestTrue(TEXT("coin flip after three restarts"),m.phase==Phase::RoundResult);}
 {auto m=combat();m.p[0].pips=m.p[1].pips=1;m.step(dt,both);TestTrue(TEXT("simultaneous ordinary KO uses crumbs then tie"),m.phase==Phase::Tiebreak);}
 {auto m=combat();m.p[0].cane=true;m.caneAvailable=false;m.step(dt,hit0);TestEqual(TEXT("bite while holding cane"),m.p[1].pips,4);TestTrue(TEXT("bite keeps cane"),m.p[0].cane);}
 {auto m=combat();m.p[1].pips=1;m.p[0].points=1;m.step(dt,hit0);for(int i=0;i<182;i++)m.step(dt,idle);TestTrue(TEXT("first to two completes match"),m.phase==Phase::MatchEnd);m.rematch();TestEqual(TEXT("rematch clears score"),m.p[0].points,0);TestTrue(TEXT("rematch countdown"),m.phase==Phase::Countdown);}
 {auto m=combat();m.p[0].pos={789,0};std::array<Input,2> in{};in[0].move={1,0};for(int i=0;i<60;i++)m.step(dt,in);TestTrue(TEXT("plate confines movement"),m.p[0].pos.length()<=790.1f);}
 {auto m=combat();m.cfg.playerRadius=64;m.cfg.biteRange=165;m.step(dt,hit0);TestTrue(TEXT("larger players remain solid"),(m.p[1].pos-m.p[0].pos).length()>=127.9f);TestEqual(TEXT("larger players can still bite at contact"),m.p[1].pips,4);m.p[0].pos={900,0};m.constrain(m.p[0]);TestTrue(TEXT("larger capsule stays inside plate"),m.p[0].pos.length()<=770.1f);}
 return true;
}
#endif
