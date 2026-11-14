param([string]$UnrealRoot='C:\Program Files\Epic Games\UE_5.6')
$repoRoot=Split-Path -Parent $PSScriptRoot
& "$UnrealRoot\Engine\Build\BatchFiles\RunUAT.bat" BuildCookRun "-project=$repoRoot\CupcakeCannibal.uproject" -noP4 -platform=Win64 -clientconfig=Development -build -cook -stage -pak -archive "-archivedirectory=$repoRoot\Builds" -nocompileeditor -skipbuildeditor -utf8output
exit $LASTEXITCODE
