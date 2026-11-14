param([switch]$Phones,[switch]$Editor,[string]$PublicUrl='',[string]$UnrealRoot='C:\Program Files\Epic Games\UE_5.6')
$ErrorActionPreference='Stop'
$projectPath=Join-Path $PSScriptRoot 'CupcakeCannibal.uproject'
$editorPath=Join-Path $UnrealRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$packagedPath=Join-Path $PSScriptRoot 'Builds\Windows\CupcakeCannibal.exe'
$usePackage=(Test-Path -LiteralPath $packagedPath)-and -not $Editor
if(-not $usePackage){
 if(-not(Test-Path -LiteralPath $editorPath)){throw 'Unreal 5.6 was not found. Pass -UnrealRoot with its install folder.'}
 if(-not(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'Binaries\Win64\UnrealEditor-CupcakeCannibal.dll'))){& (Join-Path $PSScriptRoot 'Build.ps1');if($LASTEXITCODE -ne 0){throw 'Build failed. See the compiler output.'}}
}
$relayDir=Join-Path $PSScriptRoot 'relay'
if($Phones){
 if(-not(Test-Path -LiteralPath (Join-Path $relayDir 'node_modules\ws'))){Push-Location $relayDir;try{npm.cmd ci --no-audit --no-fund;if($LASTEXITCODE -ne 0){throw 'Relay install failed'}}finally{Pop-Location}}
 $relayHealth=$null
 try{$relayHealth=Invoke-RestMethod 'http://localhost:3000/health' -TimeoutSec 2}catch{}
 if($relayHealth -and $relayHealth.application -ne 'cupcake-cannibal'){throw 'Port 3000 belongs to another application.'}
 if(-not $relayHealth){
  if(-not $PublicUrl){
   $tunnelCommand=Get-Command cloudflared -ErrorAction SilentlyContinue
   $tunnelExe=if($tunnelCommand){$tunnelCommand.Source}else{Join-Path $PSScriptRoot 'Tools\Local\cloudflared-windows-amd64.exe'}
   if(-not(Test-Path -LiteralPath $tunnelExe)){throw 'Install cloudflared (winget install Cloudflare.cloudflared), or pass -PublicUrl for an existing tunnel.'}
   $tunnelLog=Join-Path $PSScriptRoot 'tunnel.log'
   Start-Process -FilePath $tunnelExe -ArgumentList 'tunnel --url http://localhost:3000 --no-autoupdate' -WindowStyle Hidden -RedirectStandardError $tunnelLog -RedirectStandardOutput (Join-Path $PSScriptRoot 'tunnel-stdout.log') | Out-Null
   $until=(Get-Date).AddSeconds(45)
   while((Get-Date)-lt $until -and -not $PublicUrl){Start-Sleep -Seconds 1;if(Test-Path -LiteralPath $tunnelLog){$match=[regex]::Match([System.IO.File]::ReadAllText($tunnelLog),'https://[a-z0-9-]+\.trycloudflare\.com');if($match.Success){$PublicUrl=$match.Value}}}
   if(-not $PublicUrl){throw 'Tunnel URL was not ready. Run without -Phones for the keyboard demo.'}
  }
  Start-Process -FilePath (Get-Command node).Source -ArgumentList @('server.js','--url',('"'+$PublicUrl+'"')) -WorkingDirectory $relayDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $PSScriptRoot 'relay-server.log') -RedirectStandardError (Join-Path $PSScriptRoot 'relay-error.log') | Out-Null
  Write-Host "Phone controller: $PublicUrl/play.html"
 }else{Write-Host "Using running relay, room $($relayHealth.code), URL $($relayHealth.url)"}
}
Write-Host 'Keyboard fallback: P1 WASD + F, P2 arrow keys + Enter. Press F and Enter to ready both players. R rematches.'
if($usePackage){& $packagedPath -windowed -ResX=1600 -ResY=900}else{& $editorPath $projectPath -game -windowed -ResX=1600 -ResY=900}
