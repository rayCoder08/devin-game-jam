# Codex Implementation Prompt: Cupcake Cannibal (Unreal Engine 5)

Read `context.md` first; it is the source of truth for rules and decisions. Build exactly what it specifies. Time budget: about 1h20. Get a keyboard-only match working first, then phones, then polish. Commit and push to `main` after every milestone.

## Environment
- Windows PC with Unreal Engine 5 (use the installed 5.x; prefer 5.3+ for the glTF importer). The game is **developed and demoed on this PC**. Do not target macOS.
- C++ project (the WebSocket client needs C++). Requires Visual Studio 2022 with "Game development with C++". If the C++ toolchain is missing, say so immediately and fall back to a Blueprint-only project plus a marketplace-free alternative: run the relay's UDP bridge (see Relay) and read it with the built-in `Sockets`/`Networking` modules in C++… if even that is impossible, deliver keyboard-only.
- Also needs Node.js 20 and cloudflared (`winget install Cloudflare.cloudflared`).
- Repo hygiene: `.gitignore` for UE (`Binaries/`, `Intermediate/`, `DerivedDataCache/`, `Saved/`, `.vs/`, `*.sln`), `.gitattributes` with Git LFS for `*.uasset *.umap *.glb *.png *.wav *.mp3`, and `* text=auto eol=lf` for text.

## Project layout
```
CupcakeCannibal.uproject
Source/CupcakeCannibal/
  CupcakeGameMode.{h,cpp}        match state machine + rules (see Rules)
  CupcakePawn.{h,cpp}            movement, facing, bite/cane, pips, crumbs, VFX hooks
  CandyCanePickup.{h,cpp}        pickup actor, respawn timer
  PhoneInputSubsystem.{h,cpp}    UGameInstanceSubsystem: WebSocket client to the relay
  CupcakeHUD.{h,cpp}             AHUD or UMG host: pips, round points, timer, callouts, QR
Content/
  Maps/CakeLand.umap             round cake-plate arena, fixed camera
  Models/SM_Strawberry, SM_Chocolate (imported GLBs), cane, plate, 2–3 obstacles
  UI/WBP_HUD, WBP_RoundResult, WBP_Lobby (QR + room code), WBP_Title (story line)
  Audio/ (placeholders now; ElevenLabs files later)
relay/
  package.json  server.js  public/play.html  public/play.js
README.md
```
- Enable plugins: `WebSockets` module (add `"WebSockets", "Json", "JsonUtilities"` to `Build.cs`), `Interchange`/glTF importer, `EnhancedInput`.
- Import the two root GLBs as Static Meshes into `Content/Models`, normalize to the same height, and set simple capsule collision. Strawberry = `Meshy_AI_cupcake_character_leg_*`, Chocolate = `Meshy_AI_Mint_Chocolate_Cupcak_*`. If an import fails, use a cylinder + sphere placeholder in the player color.

## Relay (`relay/`, Node 20, deps: `express`, `ws`, `qrcode`)
- `npm start` → `node server.js`, port 3000 (`PORT` override). Serves `public/` and two WebSocket paths:
  - `/ue` — the game connects here (exactly one client). On connect, server sends `{t:"room", code}` with a 4-letter room code it generates.
  - `/phone` — phones connect here.
- Messages (JSON):
  - phone → server: `{t:"join", code, clientId, slot?}` → `{t:"joined", slot}` or `{t:"full"}`; same `clientId` reclaims the same slot.
  - phone → UE (relayed): `{t:"in", slot, x, y, hit}` at ~30 Hz; `hit` true once per tap. `{t:"rematch"}`.
  - UE → phone (relayed): `{t:"state", slot, color, pips, phase}` on change.
  - server → UE: `{t:"left", slot}` when a phone disconnects.
- Also serves `GET /qr.png` returning a QR of `${PUBLIC_URL}/play.html?room=CODE`; `PUBLIC_URL` comes from the `PUBLIC_URL` env var or the first `--url` argument (paste the cloudflared URL). UE downloads this PNG with `HttpModule` and shows it in `WBP_Lobby`. If the download fails, show the URL and room code as text.
- Provide `relay/start.cmd`: starts the server and prints instructions to run `cloudflared tunnel --url http://localhost:3000`, then set `PUBLIC_URL`.

## Phone controller (`relay/public/play.html`, iOS Safari)
- Portrait, full-screen, background in the player color; top: player name + frosting pips; center: one huge **HIT** button; small connection dot.
- Flow: Join screen (room code from URL) → **Enable Motion** (tap → `DeviceOrientationEvent.requestPermission()` if present → connect) → **Ready** (records current beta/gamma as neutral).
- Tilt: `x` from gamma, `y` from beta (tilt forward = up on screen). Subtract neutral, 5° dead zone, full speed at 25°, clamp to unit circle. If motion is denied/unavailable, show a touch joystick on the left half.
- `touch-action:none`, `user-select:none`, `user-scalable=no`, `overscroll-behavior:none`, prevent `gesturestart`. Wake lock on connect and on `visibilitychange`. Landscape → "Rotate to portrait" overlay. Reconnect with backoff using the stored `clientId`.
- Feedback (no vibration on iOS): flash the button and play a short local click on tap. On `phase==="matchEnd"`, show a **Rematch** button.

## UE: PhoneInputSubsystem
- On game start, connect to `ws://localhost:3000/ue` with `FWebSocketsModule::Get().CreateWebSocket`. Reconnect every 2 s on failure. Parse JSON with `FJsonSerializer`.
- Expose Blueprint-assignable delegates: `OnRoomCode(FString)`, `OnPhoneInput(int32 Slot, FVector2D Move, bool Hit)`, `OnPhoneRematch()`, `OnPhoneLeft(int32 Slot)`.
- Keep per-slot `LastInputTime`; if no input for 0.5 s, treat movement as zero. Send `state` messages when pips/phase change.

## UE: input merge (hidden keyboard fallback, always active, never shown in UI)
- Enhanced Input: P1 = WASD move, F hit; P2 = arrow keys move, Enter hit. Each hit key fires once per press (no repeat).
- Rematch on the PC: R or Enter on the match-end screen.
- Pressing a slot's hit key in the lobby claims that slot, so the game runs with no phones.
- Each pawn reads `Move = phone input if fresh else keyboard`, `Hit = either`.

## Rules (implement in `CupcakeGameMode`; fixed-step logic in `Tick` with accumulated 1/60 s steps)
Tunable `UPROPERTY(EditAnywhere)` constants with these defaults: `Pips=5`, `BiteRange=110` cm, `BiteArcDeg=70`, `BiteCooldown=0.6`, `Immunity=0.8`, `CaneRange=240`, `CaneArcDeg=100`, `CaneWindup=0.4`, `CaneRespawn=6`, `Knockback=300` cm/s, `Speed=450` cm/s, `RoundTime=60`, `SunTicks={30,45,55,58}`, `SunWarn=1.0`, `TiebreakTime=10`, `MaxTiebreakRestarts=3`, `RoundsToWin=2`, `ResultDelay=3`.
- **Movement:** velocity from input vector; facing = last non-zero move direction. Pawn collision vs plate edge (invisible ring of blocking volumes or a radius clamp) and obstacles; the two pawns are solid and push each other apart.
- **Hit (edge-triggered):** if the opponent is within `BiteRange` and the front arc → bite; else if holding the cane → start windup; after `CaneWindup` the swing resolves against `CaneRange`/`CaneArcDeg`. The cane is consumed on swing (hit or miss) and respawns at center `CaneRespawn` s later; pick up by overlap. Bite cooldown applies to bites only; bites are allowed while holding the cane and during the windup.
- **Damage:** bite = −1 pip, +2 Crumbs; cane hit = −1 pip, +1 Crumb. Each hit gives the target `Immunity` and knockback. Immune targets take nothing. The holder keeps the cane when hit.
- **Sunlight:** at each `SunTicks` time, −1 pip to both, 0 Crumbs, ignores immunity. Emit `SunWarn` warning `SunWarn` s before (gold flash).
- **Step order:** (1) resolve both players' hits against pre-step state so simultaneous bites both land; (2) apply sunlight tick; (3) evaluate round end.
- **Round end:** exactly one at 0 → other wins; both at 0 same step → Crumbs; at 60 s more pips wins, equal → Crumbs; equal Crumbs → **Golden Crumb tiebreak** (10 s, both 1 pip, start positions, sunlight paused, cane cleared; first uncontested bite wins; both bite same step or timeout → restart, no points; after `MaxTiebreakRestarts` → coin flip, shown as "Sugar rush coin flip!").
- **Scoring:** award the round point exactly once; first to `RoundsToWin` wins the match; reset pips, Crumbs, positions and cane each round.
- **Phases:** `Lobby → Countdown(3-2-1) → Playing → (Tiebreak) → RoundResult(auto 3 s) → … → MatchEnd`. Rematch resets without reloading the level (or reload the level with phones staying connected, since the subsystem lives in the GameInstance).
- Events for VFX/audio: `Bite, CaneWindup, CaneHit, Pickup, SunWarn, Melt, RoundEnd, MatchEnd, TiebreakStart, Countdown`.

## Visuals, HUD, audio
- Fixed, slightly angled overhead camera actor (`CameraActor`, set as view target). Round cake-plate arena, pastel plate with frosting rim, 2–3 obstacles (candle, sprinkle jar). Cute bakery-brawl palette, Strawberry pink vs Chocolate brown, glow under the cane.
- Effects: crumb Niagara burst on bite; glowing arc telegraph during cane windup; gold full-screen flash on sun warning and a melt drip material pulse; blinking while immune. Procedural animation on the static meshes: idle bob, squash/stretch when moving, lunge on bite, shake on hit.
- HUD (UMG, large, minimal): each player's pips and round points, the shared timer with the next sun tick hinted, text callouts matching the audio cues ("3-2-1", "CHOMP!", "SUN!", "GOLDEN CRUMB!", "STRAWBERRY WINS!"). Round result screen: Crumbs, frosting left, reason (Knockout / More frosting / Crumbs / Golden Crumb / Coin flip).
- Title card with the story line in one `UPROPERTY` string `StoryLine` (placeholder text; the team pastes the real line later).
- Audio: `UPROPERTY` map from cue name → `USoundBase`. Cues: `countdown, go, bite, hit, caneSwing, sunWarn, melt, roundWin, matchWin`. Use simple generated/placeholder WAVs now; the team drops ElevenLabs files into `Content/Audio` later and assigns them in the map.

## Milestones (commit + push after each)
1. Project compiles; repo hygiene (ignore, LFS); GLBs imported; arena map with fixed camera.
2. Keyboard-only full match: movement, bite, cane, sunlight, scoring, tiebreak, results, rematch. Verify the must-test cases from `context.md`.
3. Relay + phone page (touch joystick + HIT) + `PhoneInputSubsystem` + lobby QR.
4. Tilt + iOS motion permission + calibration + wake lock + disconnect handling.
5. Visuals, HUD, audio polish. Then **feature freeze; bug fixes only.**

## README (short)
- PC setup: UE5, VS2022 C++, Node 20, cloudflared.
- Run: `cd relay && npm install && npm start`; in another terminal `cloudflared tunnel --url http://localhost:3000`; set `PUBLIC_URL` to the tunnel URL (restart relay); open the project and Play in a standalone window (or launch the packaged Win64 build).
- iPhone steps: scan QR → Enable Motion → Allow → Ready. Hidden keyboard keys.

## Acceptance
- Fresh clone + README steps compiles and plays on the Windows PC.
- Two iPhones on Safari join through the tunnel QR, tilt to move, tap HIT to bite/swing, and finish a best-of-3 match; rematch works without restarting the game.
- Losing a phone mid-move stops that cupcake; reconnecting restores the same slot.
- The keyboard-only match works with no phones.
