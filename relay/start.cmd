@echo off
cd /d "%~dp0"
echo In a second terminal, run: cloudflared tunnel --url http://localhost:3000
echo Then set PUBLIC_URL to the HTTPS URL and restart this relay.
echo Example in PowerShell: $env:PUBLIC_URL='https://your-tunnel.trycloudflare.com'; npm start
call npm start
