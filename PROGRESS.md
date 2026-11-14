# Progress — 2026-11-14

## Completed: playable Cupcake Cannibal demo

- Created the root UE 5.6 C++ project, preserving CandyCarnival as a separate environment project.
- Imported the two repository Meshy GLBs as the player models and capped textures at 2K. Reused CandyCarnival materials, three obstacle props, background tents and the candy cane silhouette around a bounded cake plate.
- Implemented a shared fixed-step match model: movement, solid player separation, facing/front-arc bites, cooldown/immunity, cane pickup/windup/respawn, simultaneous damage, sunlight, Crumbs, first-to-two scoring, tiebreak restart cap, results and rematch.
- Added the fixed arena camera, pips/points/timer HUD, round callouts, placeholder story line, procedural bobbing/hit blinking and a visible cane windup arc.
- Added the Node relay and iPhone controller: room pairing, server-assigned slots, tilt permission/calibration, joystick fallback, HIT, reconnect, page-hide input clearing, wake lock and phone rematch. The game downloads the QR and uses a localhost-only UE WebSocket endpoint.
- Added launch/build/package scripts. Pulled the team's audio folder, connected countdown voice, music and available SFX; bite-hit, cane-windup and sun-melt remain temporary pending delivery.
- Created CandyWorld from the complete original CandyCarnival scenery shown in the supplied video. Enlarged both players 1.6x and adjusted collision/reach. Imported the supplied otter GLB as a scene mascot with simple capsule collision.
- Built the standalone Win64 package successfully. Packaged output is local under Builds/Windows and excluded from Git.

## Gameplay validation

- The Unreal Cupcake.Rules suite passed, including all five must-test cases from context.md and additional cooldown, respawn, scoring, rematch and arena-boundary checks.
- Relay integration tests passed room pairing, slot authority, bounded inputs, disconnect/reconnect, state forwarding and QR generation.
- Two live WebSocket phone clients completed a full first-to-two match in the actual Unreal game and rematched with scores reset. See Tests/live-demo.json.
- The user confirmed that both physical phone controllers' tilt movement and HIT work.
- Final packaged keyboard verification passed after the scene and player-size update; Tests/keyboard-demo.json records the result. The complete arena and otter placement were visually checked in the packaged build.

## Remaining beyond this demo

The team's opening story line and three missing SFX (bite-hit, cane-windup, sun-melt) remain pending. Niagara crumb bursts, elaborate character animation, broader device testing and production hosting remain follow-up work. The temporary HTTPS tunnel depends on the local relay/cloudflared processes staying open. No claim is made that the later Chroma submission checklist is complete.

## Completed: CandyCarnival environment and fitted collision

- Added an editable Unreal Engine 5.6 environment based on the supplied candy-land and carnival drawings.
- Included 37 original scenery meshes, 23 base materials, a saved startup map, four camera compositions and four preview images.
- Included the Blender scene, original mesh FBXs, collision FBXs and relative-path generation/import scripts.
- Added collision to 39 physical scenery actors using 1,279 convex hulls. Most hulls have at most 42 vertices. Separate low-resolution meadow, biscuit path and caramel surfaces total 5,480 triangles.
- Split tents, candy cane curves and disconnected decorations into separate shapes to preserve entrances and gaps. Added collision to clouds and the marquee oval; left the distant sky nonblocking.
- Verified the saved map with 48 blocking/clearance checks. In Play mode the explorer stopped at a cane and tent wall and traveled through the main tent doorway. Validation reports are committed under CandyCarnival/Tools.
- Added Git LFS tracking for Unreal assets, GLBs, source FBXs/Blender files and media. Ignored engine caches, logs, backups and IDE outputs.

## Scope at the earlier environment milestone

CandyCarnival remains an explorable environment project. The playable match is now in the repository-root CupcakeCannibal project described above.

Read context.md and prompt.md before gameplay work. Their rules remain authoritative. Reuse the environment, prioritize the two root Meshy models for players, and keep the playable arena small. Final voice lines and sound effects are pending delivery.
