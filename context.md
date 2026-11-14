# Cupcake Cannibal — Project Context

Everything decided in planning (2026-11-14). The implementation brief is in `prompt.md`.

## Event and deadlines
- **Pitch:** two cupcakes chase each other around Cake-Land, land bites and race into a rematch. Story: a recipe-book origin and a first accidental taste, told in one opening line that the team will provide (use a placeholder until then).
- **Chroma Awards track:** Game → Arcade & Party (quick rounds, accessible controls, friendly competition, strong game feel). https://chromaawards.com/prizes/game-arcade-party
- **DevKick demo:** today at 5:00 p.m. Toronto. The winning team advances directly to the semifinals of its chosen category. https://devkick.com/005/#presentations
- **Chroma public deadline:** Jan 7, 2027, 11:45 p.m. Pacific (Jan 8, 2:45 a.m. Toronto). https://chromaawards.com/faq
- **Multiplayer reference:** the room-code + WebSocket pattern from King of the Ring. https://devpost.com/software/king-of-the-ring

## Chroma submission checklist (later, not today)
- Submit once, under Arcade & Party.
- Needs a public browser URL, a downloadable gameplay video, a thumbnail and English text or subtitles.
- The rules require at least one AI tool. Tag Meshy (models) and ElevenLabs (audio), and keep screenshots or notes on what each produced. https://chromaawards.com/terms
- Related awards:
  - Meshy Awards: https://chromaawards.com/prizes/creative-tools-meshy-awards
  - ElevenLabs Awards: https://chromaawards.com/prizes/creative-tools-elevenlabs-awards
  - Meshy Game of the Year: https://chromaawards.com/prizes/game-meshy-game-of-the-year-award
- The permanent public URL needs a WebSocket-capable host (e.g. Render or Fly). Netlify and Vercel static hosting can't run the server.

## Control decision: one MacBook + two iPhones
Three options were considered:

| Option | Difficulty | Verdict |
|---|---|---|
| 1. One laptop + 2 phones (tilt) | 5.5/10 | **Chosen.** The laptop runs the whole match and the phones only send input. Keyboard fallback on the same screen. |
| 2. Two laptops + 2 phones (tilt) | 8.5/10 | Rejected. Needs networked state sync for two screens and a second laptop, and doesn't fit 2 hours. |
| 3. Two laptops, WASD | 6/10 | Rejected. Still needs networked sync and loses the phone hook. |

## Hardware and software
- **Development:** Codex on a Windows PC. Unreal Engine 5 is installed there but **is not used**: a UE5 build made on Windows can't be packaged for the Mac without Apple's build tools, and the team chose a browser game. All code goes to GitHub (`rayCoder08/devin-game-jam`). **Demo machine:** a MacBook that pulls from GitHub and runs the game.
- **MacBook installs:**
  - Node.js 20 LTS
  - Git (`xcode-select --install`)
  - cloudflared (`brew install cloudflared`)
  - Chrome or Safari
- **MacBook run commands:**
  ```
  git pull && npm install && npm run build && npm start
  cloudflared tunnel --url http://localhost:3000
  ```
  Open the tunnel URL on the MacBook. The QR code it shows points the phones at the same URL.
- **iPhones:** no app, Safari only.
  - Scan the QR code with the Camera app.
  - Tap Enable Motion, then Allow. iOS requires a tap before motion access (`DeviceOrientationEvent.requestPermission()`), and HTTPS.
  - Pick or auto-claim P1/P2, then tap Ready to set the neutral tilt.
  - Settings: Auto-Lock to Never, Low Power Mode off, phone charged, held in portrait.
- **Cross-platform rules (Windows to Mac):**
  - `.gitattributes` with `* text=auto eol=lf`.
  - Commit `package-lock.json`; never commit `node_modules`.
  - No Windows-only commands in npm scripts.
  - Import paths must match filename case exactly.
  - No native npm modules.
- **Tunnel URL:** changes each run, so generate the QR code at runtime from `location.origin`.
- **Testing without the Mac:** cloudflared also runs on Windows, so phones can be tested during development.

## iOS Safari gotchas
- Motion needs HTTPS plus the permission tap.
- Safari can't lock the screen orientation, so show a "rotate to portrait" overlay.
- Keep the screen awake with Wake Lock (`navigator.wakeLock`, iOS 16.4+), with Auto-Lock Never as backup.
- Use `touch-action: none` and no text selection, and prevent pinch, double-tap zoom and pull-to-refresh.
- No vibration API, so feedback comes from the phone screen and MacBook audio.
- Reconnect automatically to the same player slot when Safari returns from the background (`visibilitychange`). Clear held input on disconnect or page hide.
- Use `deviceorientation` (beta/gamma) for tilt, not raw acceleration, which is too noisy.

## Answered design questions

| # | Question | Answer |
|---|---|---|
| 0 | Platform | Browser game (Vite + Three.js), built fresh |
| 1 | Existing game | Not used; whatever is best → fresh build |
| 2 | Models | 2 Meshy cupcake GLBs, already on GitHub (repo root) |
| 3 | Audio | Uploaded later → placeholder sounds now, ElevenLabs files later in `public/audio/` |
| 4 | Bite cooldown / immunity | 0.6 s cooldown, 0.8 s hit immunity; sunlight ignores immunity |
| 5 | Controls | Phone tilt to move, no keys on the phone |
| 6 | Cane drop on hit | No. The holder keeps it. Keep the visible windup, which the rules require |
| 7 | Cane respawn | 6 s after it's used ("the end after it dies") |
| 8 | Knockback | Small knockback on hit; cupcakes push each other (solid) |
| 9 | Round start / result | 3-2-1 countdown each round; results auto-continue after ~3 s |
| 10 | Tiebreak limit | After 3 tiebreak restarts, a coin flip decides the round |
| 11 | Rematch | From the MacBook or either phone |
| 12 | Tone | Cute bakery brawl |
| 13 | Arena | Round cake plate (2–3 small obstacles, e.g. a candle and a sprinkle jar) |
| 14 | Players | Strawberry (pink) vs Chocolate (brown) |
| 15 | Opening story line | Team will paste it later (placeholder for now) |
| 16 | Tilt direction | Tilting forward moves the cupcake up the screen |
| 17 | Phone display | Shows the player's color and frosting pips |
| 18 | Hit input | One big **Hit** button on the phone |
| 19 | Deploy | Tunnel-only for today's demo |
| 20 | Cut order if late | Polish → tilt falls back to a touch joystick → tiebreak cap |
| — | Keyboard fallback | Yes, hidden (not shown in UI): P1 WASD + F, P2 arrows + Enter |

## Final combat and scoring rules (these replace all earlier proposals)
- **Combat:**
  - Both cupcakes can bite at any time, including while holding the cane.
  - Each starts with **5 frosting pips**. A bite (close range, front arc) takes 1 pip.
- **Candy Cane:**
  - Spawns at arena center; touch it to pick it up.
  - Gives **one** longer-reach swing for 1 pip, with a visible windup the other player can dodge.
  - Respawns at center **6 s after it's used**.
- **Single Hit button:** bites if the opponent is in bite range; otherwise, if holding the cane, swings it.
- **Sunlight:**
  - The round lasts up to 60 s. Sunlight melts 1 pip from **both** cupcakes at **30, 45, 55 and 58 s**.
  - A brief gold flash comes before each tick.
  - Sunlight earns 0 Crumbs. Equal frosting stays equal, so the round needs a tiebreak.
- **Crumbs:** a landed bite earns **2**, a cane hit earns **1**. Either hit takes 1 pip. Frosting and Crumbs reset each round.
- **Match:** a round win is worth 1 round point; first to **2** wins the match.
- **HUD:** each player's frosting pips, round points and the shared timer. Crumb totals appear on the round result screen.
- **Round end:**
  1. If exactly one cupcake reaches 0 frosting, the other wins.
  2. At 60 s, more frosting wins.
  3. If both reach 0 on the same update, or frosting is equal at 60 s, more Crumbs wins.
  4. If Crumbs are also tied, start the **Golden Crumb tiebreak**:
     - 10 s long, both players on 1 pip at their starting positions.
     - Sunlight paused and cane cleared.
     - The first uncontested bite wins.
     - If both bite on the same update, or nobody bites, restart with no points. After 3 restarts, a coin flip decides.
- **Implementation:**
  - Track frosting, Crumbs and round points separately per player.
  - Process both players' hits and any sunlight tick in the same simulation update, *then* check the result.
  - Award the round point exactly once.
- **Must-test cases:**
  - an unanswered bite
  - a cane hit
  - a sunlight knockout
  - an untouched round that goes to the tiebreak
  - simultaneous bites in the tiebreak

## Assets in repo
- `Meshy_AI_Mint_Chocolate_Cupcak_1114201753_image-to-3d-texture.glb` (~25 MB) → **Chocolate** player.
- `Meshy_AI_cupcake_character_leg_1114201729_image-to-3d-texture.glb` (~33 MB) → **Strawberry** player (tint pink frosting if needed).
- Only the MacBook loads the models, from localhost, so their size doesn't affect the phones. Compressing them is optional (`npx @gltf-transform/cli optimize in.glb out.glb --texture-compress webp`).
- These are image-to-3D meshes and probably have no rig. Animate them in code: bob, squash and stretch, a lunge on bite.

## Build schedule (as planned at 2:55 p.m.)
- **Estimated effort:**
  - Game core: ~40 min
  - Visuals, HUD and audio: ~25 min
  - Phone control: ~45 min
  - Integration and testing: ~20 min
- **Feature freeze at 4:30.** 4:30–4:50: clean pull and run on the MacBook, edge-case tests, record a clip. 4:50–5:00: buffer.
- **Cut rule:** if the phones aren't reliable by 4:15, demo with the hidden keyboard mode.
- **Demo script:** one pairing, one bite, one rematch.
