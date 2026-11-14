using UnrealBuildTool;
public class CupcakeCannibalTarget : TargetRules {
 public CupcakeCannibalTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Game; DefaultBuildSettings = BuildSettingsVersion.V5;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
  ExtraModuleNames.Add("CupcakeCannibal");
 }
}
