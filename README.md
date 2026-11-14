# Cupcake Cannibal

Playable UE 5.6 Windows bakery brawl: Strawberry versus Chocolate, phone tilt or keyboard movement, bites, a candy cane, melting sunlight and first-to-two rounds. Rules are in [context.md](context.md); the original implementation brief is [prompt.md](prompt.md).

![Playable cake arena](Previews/Cupcake_Gameplay.png)

## Run the demo

Prerequisites for a source checkout: Unreal Engine 5.6, Visual Studio 2022 with Game development with C++, Git LFS, and Node.js 20+ for phones. This workstation was tested with Node 24. Run plugged in and select the NVIDIA GPU for Unreal/the game in Windows Graphics settings.

```powershell
git lfs install
git lfs pull
.\Build.ps1
.\Play.cmd
```

`Play.cmd` launches the packaged game when present, otherwise the Unreal game window. Use `Start-Demo.ps1 -Editor` to force the editor executable. In the lobby, press **F** for Strawberry and **Enter** for Chocolate to ready both players. Keyboard fallback: P1 **WASD + F**, P2 **arrows + Enter**. **R** or a click rematches after a match ends. Movement follows screen directions. Keyboard hints stay in this README rather than the game UI.

The local packaged build is `Builds/Windows/CupcakeCannibal.exe`; the entire `Builds/Windows` folder must stay together. Packaged output is excluded from Git. Use `Tools/Package-Demo.ps1` to produce it from a fresh checkout. The environment-only project remains available separately under CandyCarnival.

## Two iPhones

Install cloudflared (`winget install Cloudflare.cloudflared`) and run `Play-Phones.cmd`, or `Start-Demo.ps1 -Phones`. The launcher starts the relay and a temporary HTTPS tunnel, or reuses the relay already running. To use an existing tunnel, pass `-Phones -PublicUrl https://your-tunnel.trycloudflare.com`. A local portable cloudflared binary under Tools/Local is also supported and is not committed.

Scan the game lobby QR on each iPhone → Enable Motion → Allow → hold comfortably in portrait → Ready. Tilt forward moves up the screen. Tap HIT to bite in range, or swing the held cane otherwise. If motion is unavailable or denied, the controller shows a touch joystick. Recenter tilt from the phone when needed. Turn Auto-Lock off for the demo and keep phones charged.

The temporary URL changes when the tunnel is restarted; the QR and four-letter room code come from the relay. The UE game uses `ws://127.0.0.1:3000/ue`; only phone input crosses the tunnel. A stale/disconnected phone stops supplying movement, and its client ID reclaims the slot on reconnect. Keep the relay and cloudflared processes running during play.

Manual relay setup:

```powershell
cd relay
npm ci
npm start -- --url https://your-tunnel.trycloudflare.com
```

Run `cloudflared tunnel --url http://localhost:3000` in another terminal to obtain that URL. Cloudflared use for this demo was explicitly approved. [Cloudflare Quick Tunnel documentation](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Implemented gameplay

- Five frosting pips each. Bites have a 0.6 s cooldown and award two Crumbs; cane hits award one. Hits remove one pip and grant 0.8 s immunity with small knockback.
- The center cane has a visible 0.4 s windup, is consumed on swing and respawns after six seconds. Biting remains available while carrying it or during windup.
- Sunlight melts both players at 30, 45, 55 and 58 seconds, ignores immunity and awards no Crumbs. Rounds last up to 60 seconds.
- Simultaneous hits resolve together. Round results use knockout, remaining frosting and then Crumbs. Ties enter a ten-second Golden Crumb round; simultaneous bites restart it, with a coin flip after three restarts.
- Countdown, results, first-to-two scoring and rematch are implemented. Solid player separation, a bounded plate and three obstacles keep play compact.

The root GLBs are the playable characters: the legged cupcake is Strawberry; the mint/chocolate cupcake is Chocolate. Per the video update, the full CandyCarnival world surrounds the arena, including tents, pink hills, clouds, candy gates and the winding biscuit path. Players are 1.6 times their initial height (208 cm), with matching 64 cm collision radii and adjusted bite/cane reach (165/300 cm). The supplied otter GLB is a decorative mascot beside the plate with a simple capsule collider. Imported texture maximums are 2K.

## Audio and story

Pulled the team's `audio/` folder from GitHub. The game now uses the supplied countdown voice, GO, cane hit/pickup, sun warning, player hurt, round/match victory and tiebreak sounds, plus a quiet looping `cupcake_brawl` music track. Runtime loads named SoundWaves from `/Game/Audio/Cues`. `Tools/update_candy_world.py` imports the team WAVs and records their mapping in `Tests/scene-update.json`. Only bite-hit, cane-windup and sun-melt cues remain synthesized placeholders because those files are still missing in `audio/README.md`; the unlabeled sound is left unassigned.

The opening story line is a placeholder in `ACupcakeGameMode::StoryLine`. Procedural bobbing, hit blinking and cane telegraphing are present; full character rigs and final Niagara polish are outside this demo milestone.

## Validation

Unreal's `Cupcake.Rules` suite passed the required bite, cane, sunlight, untouched-round and simultaneous-tiebreak cases plus cooldown, scoring, rematch and boundary checks. `npm test` in relay passed pairing, slot authority, input clamping, disconnect/reconnect, state forwarding and QR generation.

Two simulated controllers completed a real Unreal match and rematch; `Tests/live-demo.json` records the states. The user also confirmed both physical phone controllers' movement and HIT work. See `Tests/validation-summary.json` and [PROGRESS.md](PROGRESS.md) for the final validation scope.

## Reusable environment project

Open `CandyCarnival/CandyCarnival.uproject` in Unreal Engine 5.6. The startup map is `/Game/CandyCarnival/Maps/CandyCarnival`. Press Play to explore with WASD and mouse; Q/E descend and rise. Escape ends Play.

The environment includes a grand striped circus pavilion, four smaller stalls, six peppermint gates, ten candy apples, five popcorn buckets, gumdrop gardens, sugar flowers, sprinkles, bunting, a decorative cupcake trio, marshmallow clouds and a winding biscuit path beside a caramel stream. Lighting, 23 base materials, four camera views and source art are included.

Physical scenery has fitted lightweight collision: 39 collidable actors, 1,279 convex hulls across grouped props, and 5,480 triangles in separate ground/path collision surfaces. Tent entrances and curved cane openings remain clear. The backdrop sky and marquee lettering do not block movement. Alt+C toggles collision visualization.

Validation: 48 saved-scene collision checks plus three real explorer movement checks passed. Reports are in `CandyCarnival/Tools/`. See [PROGRESS.md](PROGRESS.md) for scope and integration status.

![CandyCarnival environment](CandyCarnival/Previews/CandyCarnival_Hero.png)

## Checkout and requirements

Install Git LFS, then run `git lfs install` and `git lfs pull` after cloning. Unreal assets, source models and preview images use LFS. Generated caches, logs and local backups are excluded.

The environment project uses built-in editor Python tools and requires no C++ compilation. Its render setup uses DX11, dynamic shadows and screen-space reflections, with Lumen and virtual shadow maps disabled. Run the laptop plugged in and set UnrealEditor.exe and the eventual packaged game to High performance (NVIDIA GPU) in Windows Graphics settings.

Blender 5.x is needed only to regenerate geometry; the saved Unreal content can be opened directly. Build and collision scripts use paths relative to their project. The environment's [README](CandyCarnival/README.txt) describes editing and rebuilding.
