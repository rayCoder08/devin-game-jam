param([switch]$Game)
$ErrorActionPreference='Stop'
$ueRoot='C:\Program Files\Epic Games\UE_5.6'
$target=if($Game){'CupcakeCannibal'}else{'CupcakeCannibalEditor'}
& "$ueRoot\Engine\Build\BatchFiles\Build.bat" $target Win64 Development "-Project=$PSScriptRoot\CupcakeCannibal.uproject" -WaitMutex -NoHotReloadFromIDE
exit $LASTEXITCODE
