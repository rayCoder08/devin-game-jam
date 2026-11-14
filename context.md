# Cupcake Cannibal — Project Context

Everything decided in planning (2026-11-14). The implementation brief is in `prompt.md`.
**Engine decision (final, 3:32 p.m.): Unreal Engine 5 on Windows.** The earlier browser-game plan is void.

## Event and deadlines
- **Pitch:** two cupcakes chase each other around Cake-Land, land bites and race into a rematch. Story: a recipe-book origin and a first accidental taste, told in one opening line the team will provide (placeholder until then).
- **Chroma Awards track:** Game → Arcade & Party (quick rounds, accessible controls, friendly competition, strong game feel). https://chromaawards.com/prizes/game-arcade-party
- **DevKick demo:** today, 5:00 p.m. Toronto. The winning team advances directly to the semifinals of its category. https://devkick.com/005/#presentations
- **Chroma public deadline:** Jan 7, 2027, 11:45 p.m. Pacific (Jan 8, 2:45 a.m. Toronto). https://chromaawards.com/faq
- **Multiplayer reference:** room-code + WebSocket pattern from King of the Ring. https://devpost.com/software/king-of-the-ring

## Chroma submission checklist (later, not today)
- Submit once, under Arcade & Party.
- Needs a publicly playable build (the team's plan said a browser URL; UE5 can't ship to browsers, so confirm with Chroma that a downloadable Windows build is accepted), a gameplay video, a thumbnail and English text or subtitles.
- Rules require at least one AI tool. Tag Meshy (models) and ElevenLabs (audio); keep screenshots or notes of what each produced. https://chromaawards.com/terms
- Related awards: Meshy Awards https://chromaawards.com/prizes/creative-tools-meshy-awards · ElevenLabs Awards https://chromaawards.com/prizes/creative-tools-elevenlabs-awards · Meshy Game of the Year https://chromaawards.com/prizes/game-meshy-game-of-the-year-award

## Control decision: one game PC + two iPhones
| Option | Difficulty | Verdict |
|---|---|---|
| 1. One computer + 2 phones (tilt) | 5.5/10 (web) → ~7/10 in UE5 | **Chosen.** The game PC runs the whole match; phones only send input. Keyboard fallback on the same screen. |
| 2. Two computers + 2 phones | 8.5/10 | Rejected: networked state sync for two screens, a second machine, doesn't fit 2 hours. |
| 3. Two computers, WASD | 6/10 | Rejected: still needs networked sync and loses the phone hook. |

## Machines
- **Development and demo:** the **Windows PC** running Codex, with Unreal Engine 5 installed. It must also have Visual Studio 2022 with "Game development with C++" (UE needs it to compile the C++ WebSocket code), Node.js 20 and cloudflared (`winget install Cloudflare.cloudflared`).
- **Game PC hardware (Julian's laptop, "JulianSong"):** Intel Core 5 210H (2.2 GHz), 32 GB RAM, NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM) + Intel Graphics, Windows 64-bit x64, ~3.7 TB free, no touchscreen. Enough for a small arena game; 6 GB VRAM is the limit:
  - Scalability Medium/High; Lumen and Nanite off if frames drop; no virtual shadow maps if needed.
  - Run plugged in. In Windows Graphics settings (and NVIDIA Control Panel), set `UnrealEditor.exe` and the packaged game to the NVIDIA GPU, not Intel.
- **Hardware needed for the demo: this one PC + 2 iPhones.** No MacBook. Phones need nothing installed (Safari only). Keep the cloudflared tunnel even on one PC: Safari only grants tilt on HTTPS pages, and venue Wi-Fi often blocks phone-to-laptop traffic.
- **MacBook:** cannot run a UE5 Windows build (packaging for macOS needs a Mac with Xcode, and there is no time). Use it only for screen-sharing or notes. If the demo must be shown on the MacBook, share the Windows PC's screen.
- **Repo:** `rayCoder08/devin-game-jam`. Commit the UE project with Git LFS for binary assets (`*.uasset`, `*.umap`, `*.glb`, `*.png`, `*.wav`, `*.mp3`). Ignore `Binaries/`, `Intermediate/`, `DerivedDataCache/`, `Saved/`, `.vs/`, `*.sln`.

## How phone control works in UE5
- iPhones can only talk WebSockets from Safari, and UE5's built-in `WebSockets` module is a **client**, so a tiny **Node relay** (`relay/`) runs on the Windows PC:
  - serves the phone controller page over HTTP,
  - relays phone input to the UE game, which connects as a WebSocket client to `ws://localhost:3000/ue`.
- `cloudflared tunnel --url http://localhost:3000` gives the relay a public HTTPS URL. iOS requires HTTPS for motion sensors. The UE game shows a QR code of that URL plus a 4-letter room code.
- **iPhones:** no app, Safari only. Scan the QR code with the Camera app → Enable Motion → Allow → Ready (sets neutral tilt). Settings: Auto-Lock Never, Low Power Mode off, charged, held in portrait.

## iOS Safari gotchas (controller page)
- Motion needs HTTPS plus a tap-triggered `DeviceOrientationEvent.requestPermission()`.
- Safari can't lock orientation; show a "rotate to portrait" overlay.
- Keep the screen awake with `navigator.wakeLock` (iOS 16.4+); Auto-Lock Never is the backup.
- `touch-action:none`, no text selection, prevent pinch, double-tap zoom and pull-to-refresh.
- No vibration API; feedback comes from the phone screen and the game audio.
- Reconnect automatically to the same slot (`clientId` in localStorage). Clear held input on disconnect or page hide.
- Use `deviceorientation` beta/gamma (tilt), not raw acceleration.

## Answered design questions
| # | Question | Answer |
|---|---|---|
| 0 | Platform | **Unreal Engine 5** (changed from browser at 3:32 p.m.) |
| 1 | Existing game | Team has a basic working game with the 3D models (not in the repo). Use it as the starting project if it is UE5; otherwise start from the Third Person template |
| 2 | Models | 2 Meshy cupcake GLBs, in the repo root |
| 3 | Audio | Uploaded later → placeholder sounds now; ElevenLabs files later |
| 4 | Bite cooldown / immunity | 0.6 s cooldown, 0.8 s hit immunity; sunlight ignores immunity |
| 5 | Controls | Phone tilt to move; no keys on the phone |
| 6 | Cane drop on hit | No, the holder keeps it. Keep the visible windup (rules require it) |
| 7 | Cane respawn | 6 s after it is used |
| 8 | Knockback | Small knockback on hit; cupcakes are solid and push each other |
| 9 | Round start / result | 3-2-1 countdown each round; result screen auto-continues after ~3 s |
| 10 | Tiebreak limit | After 3 tiebreak restarts, a coin flip decides the round |
| 11 | Rematch | From the game PC or either phone |
| 12 | Tone | Cute bakery brawl |
| 13 | Arena | Round cake plate (2–3 small obstacles) |
| 14 | Players | Strawberry (pink) vs Chocolate (brown) |
| 15 | Opening story line | Team pastes it later (placeholder) |
| 16 | Tilt direction | Tilting forward moves the cupcake up the screen |
| 17 | Phone display | Player color and frosting pips |
| 18 | Hit input | One big **Hit** button on the phone |
| 19 | Deploy | Tunnel-only for today's demo |
| 20 | Cut order if late | Polish → tilt (fall back to a phone touch joystick) → tiebreak cap |
| — | Keyboard fallback | Yes, hidden: P1 WASD + F, P2 arrows + Enter |

## Final combat and scoring rules (replace all earlier proposals)
- **Combat:** both cupcakes can bite at any time, including while holding the cane. 5 frosting pips each. A bite (close range, front arc) takes 1 pip.
- **Candy Cane:** spawns at center; touch to pick up. One longer-reach swing for 1 pip, with a visible windup. Respawns at center 6 s after it is used.
- **Single Hit button:** bites if the opponent is in bite range; otherwise, if holding the cane, swings it.
- **Sunlight:** round lasts up to 60 s. Melts 1 pip from both at **30, 45, 55, 58 s**, gold flash before each tick, 0 Crumbs, ignores immunity.
- **Crumbs:** bite = 2, cane hit = 1. Either hit takes 1 pip. Frosting and Crumbs reset each round.
- **Match:** round win = 1 round point; first to 2 wins. HUD shows pips, round points and the shared timer; Crumbs show on the round result screen.
- **Round end order:** (1) exactly one at 0 pips → other wins; (2) at 60 s, more pips wins; (3) both at 0 on the same update, or equal pips at 60 s → more Crumbs wins; (4) equal Crumbs → **Golden Crumb tiebreak**: 10 s, both on 1 pip at start positions, sunlight paused, cane cleared, first uncontested bite wins; both bite on the same update or time out → restart with no points; after 3 restarts → coin flip.
- **Implementation:** track frosting, Crumbs and round points per player. Process both players' hits and any sunlight tick in the same update, then check the result. Award the round point once.
- **Must-test:** unanswered bite · cane hit · sunlight knockout · untouched round to tiebreak · simultaneous bites in the tiebreak.

## Assets in repo
- `Meshy_AI_Mint_Chocolate_Cupcak_1114201753_image-to-3d-texture.glb` (~25 MB) → **Chocolate**.
- `Meshy_AI_cupcake_character_leg_1114201729_image-to-3d-texture.glb` (~33 MB) → **Strawberry** (tint frosting pink if needed).
- Import via UE's glTF importer (Interchange, UE 5.3+) as Static Meshes. They have no rig: animate in code (bob, squash, lunge, hit shake).

## Schedule (updated 3:32 p.m., ~1h25 left)
- Effort estimate in UE5: project + arena + pawns + rules ~45 min · relay + phone page ~20 min · UE WebSocket client + input ~20 min · polish ~15 min. Fits only with cuts; polish goes first.
- **Feature freeze 4:30.** 4:30–4:50: clean launch, must-test cases, record a clip. 4:50–5:00: buffer.
- **Cut rule:** phones not reliable by 4:15 → demo with the keyboard.
- **Demo script:** one pairing, one bite, one rematch. Demo runs from the Windows PC (PIE in a standalone window or a packaged Win64 build).
