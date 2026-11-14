using UnrealBuildTool;
public class CupcakeCannibal : ModuleRules {
 public CupcakeCannibal(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore","WebSockets","Json","JsonUtilities","HTTP","ImageWrapper","RenderCore","SlateCore"});
 }
}
