using UnrealBuildTool;
public class CupcakeCannibalEditorTarget : TargetRules {
 public CupcakeCannibalEditorTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Editor; DefaultBuildSettings = BuildSettingsVersion.V5;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_6;
  ExtraModuleNames.Add("CupcakeCannibal");
 }
}
