# Codex Implementation Prompt: Cupcake Cannibal

Read `context.md` first. It is the source of truth for all rules and decisions. Build exactly what it specifies.

## Environment (important)
- You are on **Windows**. Unreal Engine 5 is installed but **do not use it**. This is a browser game (Vite + Three.js + Node).
- The game will be pulled from GitHub and run on a **MacBook**. Keep everything cross-platform:
  - Add `.gitattributes` with `* text=auto eol=lf`.
  - npm scripts must be plain `node`/`vite` commands: no `set VAR=`, no backslash paths, no PowerShell syntax.
  - Import paths must match filename case exactly.
  - No native npm modules. Commit `package-lock.json`; ignore `node_modules` and `dist`.
- Set `"engines": {"node": ">=20"}` and add a `.nvmrc` containing `20`.
- Time budget: about 1h30. Ship a working round first, then layer features. Commit and push to `main` after every milestone below.

## Stack and layout
- **Dependencies:**
  - runtime: `three`, `ws`, `express`, `qrcode`
  - dev: `vite`
  - nothing else unless essential
- **Scripts:**
  - `npm run dev`: Vite dev server plus the Node server (run both with a tiny Node script; no `concurrently` needed).
  - `npm run build`: `vite build`.
  - `npm start`: `node server/index.js`. Serves `dist/` and WebSockets on **port 3000** (`PORT` env override).
- **Suggested files:**
  ```
  server/index.js          express static + ws rooms
  index.html               host (game) page
  play.html                phone controller page (Vite multi-page input)
  src/host/main.js         boot, renderer, scene, QR + room code lobby
  src/host/net.js          host socket: room create, receive inputs
  src/game/rules.js        PURE match logic, no Three.js (see Rules engine)
  src/game/input.js        merges phone + hidden keyboard into {moveX, moveY, hit} per player
  src/game/world.js        arena, models, cane, VFX, camera
  src/game/hud.js          DOM HUD + result screens
  src/game/audio.js        cue player with placeholder beeps
  src/controller/main.js   phone UI, tilt, Hit button, socket
  public/models/strawberry.glb, chocolate.glb
  public/audio/            (empty; ElevenLabs files arrive later)
  ```
- **Models:** move the two root GLBs into `public/models/` with `git mv`:
  - `Meshy_AI_cupcake_character_leg_...glb` → `strawberry.glb`
  - `Meshy_AI_Mint_Chocolate_Cupcak_...glb` → `chocolate.glb`
  - Load them with `GLTFLoader` and normalize scale to the same height.
  - If a model fails to load, fall back to a primitive cupcake (cylinder + sphere) in the player color.
  - Animate in code (no rig): idle bob, squash/stretch while moving, forward lunge on bite, flash and shake when hit.

## Networking (one MacBook runs the match; phones only send input)
- **Server role:** a dumb relay. Rooms are keyed by a 4-letter code.
- **Messages** (JSON):
  - host → server: `{t:"host"}` → server replies `{t:"room", code}`
  - phone → server: `{t:"join", code, slot?, clientId}` → server replies `{t:"joined", slot}` or `{t:"full"}`
    - `clientId` is kept in `localStorage`, so a reconnect gets back the same slot.
  - phone → host (relayed): `{t:"in", slot, x, y, hit}`, sent at about 30 Hz while connected; `hit` is true for one message per tap.
  - phone → host: `{t:"rematch"}`
  - host → phone (relayed): `{t:"state", slot, color, pips, phase}`, sent only on change.
  - server → host: `{t:"left", slot}` when a phone socket closes.
- **Disconnects:** on `left`, a page hide, or no input for 500 ms, the host zeroes that player's movement.
- **Host lobby:** shows a large QR code of `${location.origin}/play.html?room=CODE` (from `location.origin`, never hard-coded), the room code, and which slots are joined. When both are ready, start the countdown.
- **Hidden keyboard fallback:** always active on the host, never shown in the UI.
  - P1: WASD to move, F to hit. P2: arrow keys to move, Enter to hit.
  - Pressing either hit key in the lobby claims that slot, so the game can run with no phones.
  - Holding a hit key does not auto-repeat; one press = one hit.

## Phone controller (`play.html`, iOS Safari)
- **Screen:** full-screen portrait, background in the player color.
  - Top: player name (Strawberry or Chocolate) and the frosting pips.
  - Center: one huge **HIT** button.
  - Small connection dot.
- **Flow:**
  1. Join screen showing the room code (from the URL) → **Enable Motion** button. On tap, call `DeviceOrientationEvent.requestPermission()` when it exists, then connect.
  2. **Ready** button: records the current `beta`/`gamma` as neutral.
- **Tilt mapping:**
  - `x` comes from `gamma` (left/right); `y` from `beta`, where tilting forward = up on the screen.
  - Subtract the neutral values, apply a 5° dead zone, reach full speed at 25°, then clamp to a unit circle.
- **If motion is denied or unavailable:** show a virtual touch joystick on the left half instead. This is the cut-order fallback.
- **Phone setup:**
  - `touch-action:none`; `user-select:none`; viewport `user-scalable=no`; `overscroll-behavior:none`; prevent `gesturestart`.
  - Request a wake lock with `navigator.wakeLock.request('screen')` when supported, and re-request it on `visibilitychange`.
  - In landscape, show a "Rotate to portrait" overlay.
  - Reconnect with backoff, using the same `clientId`.
- **Feedback** (no vibration on iOS): on each tap, flash the button and play a short local click.
- **Rematch:** on the match-end screen, the phone shows a **Rematch** button.

## Rules engine (`src/game/rules.js`): pure and deterministic, fixed 60 Hz step
- **API:**
  - `createMatch()`
  - `step(match, inputs, dt)`, where `inputs = [{moveX, moveY, hit}, {...}]`
  - It returns events for VFX and audio: `bite`, `caneWindup`, `caneHit`, `pickup`, `sunWarn`, `melt`, `roundEnd`, `matchEnd`, `tiebreakStart`, `countdown`.
- **Tunable constants at the top of the file** (start values):
  - `PIPS=5`, `BITE_RANGE=1.1`, `BITE_ARC_DEG=70`, `BITE_COOLDOWN=0.6`, `IMMUNITY=0.8`
  - `CANE_RANGE=2.4`, `CANE_ARC_DEG=100`, `CANE_WINDUP=0.4`, `CANE_RESPAWN=6`
  - `KNOCKBACK=3`, `SPEED=4.5`, `ROUND_TIME=60`, `SUN_TICKS=[30,45,55,58]`, `SUN_WARN=1.0`
  - `TIEBREAK_TIME=10`, `MAX_TIEBREAK_RESTARTS=3`, `ROUNDS_TO_WIN=2`, `RESULT_DELAY=3`
- **Movement:**
  - Velocity comes from the input vector. Facing = last non-zero movement direction.
  - Circle collision against the plate edge and the 2–3 obstacles.
  - The two cupcakes are solid circles that push each other apart.
- **Hit button** (one edge-triggered action):
  - If the opponent is within `BITE_RANGE` and the front arc → **bite**.
  - Else if holding the cane → start the **cane windup**. After `CANE_WINDUP`, the swing resolves against `CANE_RANGE`/`CANE_ARC`.
  - The cane is consumed whether the swing hits or misses. It respawns at center `CANE_RESPAWN` s after use, and a player picks it up by touching it.
  - Cooldowns:
    - Bite cooldown applies to bites only.
    - Bites are still allowed while holding the cane, and during a windup.
- **Damage:**
  - A bite deals −1 pip and +2 Crumbs to the biter; a cane hit deals −1 pip and +1 Crumb.
  - Each landed hit also gives the target `IMMUNITY` and knockback.
  - Hits on an immune target do nothing.
  - The holder keeps the cane when hit.
- **Sunlight:**
  - At each `SUN_TICKS` time: −1 pip to both, 0 Crumbs, ignores immunity.
  - Emit `sunWarn` `SUN_WARN` s before each tick (gold screen flash).
- **Order within one step:**
  1. Resolve both players' hits (using pre-step state, so simultaneous bites both land).
  2. Apply the sunlight tick.
  3. Then evaluate the round end.
- **Round end:**
  1. If exactly one player has 0 pips, the other wins.
  2. If both are at 0 on the same step → compare Crumbs.
  3. At 60 s, more pips wins; equal pips → compare Crumbs.
  4. Equal Crumbs → **Golden Crumb tiebreak**:
     - 10 s, both on 1 pip, starting positions reset.
     - Sunlight paused, cane cleared.
     - The first uncontested bite wins.
     - Both bite on the same step, or time runs out → restart the tiebreak (no points).
     - After `MAX_TIEBREAK_RESTARTS` restarts → coin flip (`Math.random`), shown as "Sugar rush coin flip!".
- **Scoring:**
  - Award the round point exactly once.
  - First to 2 round points wins the match.
  - Reset pips, Crumbs, positions and the cane every round.
- **Phases:** `lobby → countdown(3-2-1) → playing → (tiebreak) → roundResult(3 s auto) → … → matchEnd`.
  - Rematch from matchEnd via the R key or Enter on the host, a click, or any phone's Rematch button.
  - A rematch resets the match without a page reload and keeps the phones connected.

## Host visuals, HUD, audio
- **Scene:**
  - Fixed, slightly angled overhead camera.
  - Round cake-plate arena: a pastel plate with a frosting rim, 2–3 obstacles (candle, sprinkle jar).
  - Cute bakery-brawl palette: Strawberry pink vs Chocolate brown.
  - A glow under the Candy Cane at center.
- **Effects:**
  - Bite: crumb particle burst at the target.
  - Cane windup: a visible glowing arc telegraph in front of the holder.
  - Sun warning: a gold full-screen flash, with a melt drip effect on both cupcakes.
  - Immunity: the cupcake blinks.
- **HUD** (DOM overlay, large, minimal):
  - Each player's frosting pips and round points.
  - The shared timer, with the next sun tick hinted.
  - Text callouts for big moments, with the same text as the audio cue: "3-2-1", "CHOMP!", "SUN!", "GOLDEN CRUMB!", "STRAWBERRY WINS!".
- **Round result screen:** shows each player's Crumbs, frosting left and the reason (Knockout, More frosting, Crumbs, Golden Crumb, Coin flip).
- **Opening line:** a title card with a placeholder story line in a single config constant (`STORY_LINE`). The team will paste the real line later.
- **Audio:**
  - `audio.js` maps cue names to `public/audio/<cue>.mp3`. If a file is missing, play a WebAudio placeholder beep.
  - Cues: `countdown`, `go`, `bite`, `hit`, `caneSwing`, `sunWarn`, `melt`, `roundWin`, `matchWin`.
  - Unlock audio on the first click or keypress on the host.

## Milestones (commit + push after each)
1. Scaffold, `.gitattributes`, models moved, server that serves `dist/` on port 3000.
2. Keyboard-only full match on the host: movement, bite, cane, sunlight, scoring, tiebreak, results, rematch. Verify all must-test cases from `context.md` (an `npm test` with simple Node assertions on `rules.js` is a plus).
3. Rooms + QR lobby + phone controller with the Hit button (touch joystick first).
4. Tilt + iOS motion permission + calibration + wake lock + disconnect handling.
5. Visuals, HUD and audio polish. **Feature freeze, then bug fixes only.**

## README (short)
- MacBook setup:
  - Node 20, Git, `brew install cloudflared`.
  - Run: `git pull && npm install && npm run build && npm start`, then `cloudflared tunnel --url http://localhost:3000`, and open the tunnel URL.
- iPhone steps: scan the QR code → Enable Motion → Allow → Ready.
- Hidden keyboard keys.

## Acceptance
- On the MacBook, a clean clone runs with only the README commands.
- Two iPhones on Safari join through the tunnel QR code, tilt to move, tap HIT to bite or swing, and play a full best-of-3 match. Rematch works without reloading.
- Losing a phone mid-move stops that cupcake. Reconnecting restores the same slot.
- The keyboard-only match works with no phones.
