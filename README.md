# Cupcake Cannibal

UE 5.6 Windows demo in development. Rules and priorities are in [context.md](context.md); the implementation brief is [prompt.md](prompt.md).

## Current environment milestone

Open `CandyCarnival/CandyCarnival.uproject` in Unreal Engine 5.6. The startup map is `/Game/CandyCarnival/Maps/CandyCarnival`. Press Play to explore with WASD and mouse; Q/E descend and rise. Escape ends Play.

The environment includes a grand striped circus pavilion, four smaller stalls, six peppermint gates, ten candy apples, five popcorn buckets, gumdrop gardens, sugar flowers, sprinkles, bunting, a decorative cupcake trio, marshmallow clouds and a winding biscuit path beside a caramel stream. Lighting, 23 base materials, four camera views and source art are included.

Physical scenery has fitted lightweight collision: 39 collidable actors, 1,279 convex hulls across grouped props, and 5,480 triangles in separate ground/path collision surfaces. Tent entrances and curved cane openings remain clear. The backdrop sky and marquee lettering do not block movement. Alt+C toggles collision visualization.

Validation: 48 saved-scene collision checks plus three real explorer movement checks passed. Reports are in `CandyCarnival/Tools/`. See [PROGRESS.md](PROGRESS.md) for scope and integration status.

![CandyCarnival environment](CandyCarnival/Previews/CandyCarnival_Hero.png)

## Checkout and requirements

Install Git LFS, then run `git lfs install` and `git lfs pull` after cloning. Unreal assets, source models and preview images use LFS. Generated caches, logs and local backups are excluded.

The environment project uses built-in editor Python tools and requires no C++ compilation. Its render setup uses DX11, dynamic shadows and screen-space reflections, with Lumen and virtual shadow maps disabled. Run the laptop plugged in and set UnrealEditor.exe and the eventual packaged game to High performance (NVIDIA GPU) in Windows Graphics settings.

Blender 5.x is needed only to regenerate geometry; the saved Unreal content can be opened directly. Build and collision scripts use paths relative to their project. The environment's [README](CandyCarnival/README.txt) describes editing and rebuilding.

## Gameplay integration priorities

Reuse CandyCarnival assets while keeping the demo arena compact. The two Meshy GLBs in the repository root take priority for the playable Strawberry and Chocolate characters. The decorative environment cupcake trio is not a replacement for those models. Voice lines and final sound effects will be supplied later; keep assignable audio hooks ready.

The first gameplay target is a complete keyboard match, followed by phone controls if time permits. Combat, scoring, sunlight and tiebreak rules follow context.md.
