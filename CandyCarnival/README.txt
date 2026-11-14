CANDY CARNIVAL — Unreal Engine 5.6 environment

Open CandyCarnival.uproject. The CandyCarnival level is the startup map.
Content location: /Game/CandyCarnival/Maps/CandyCarnival

The environment combines the supplied pink candy-land drawing with the
striped circus tents, popcorn and bitten candy apples of the second reference.

EXPLORE
Press Play for the default Unreal flying explorer: WASD and mouse to look;
E / Q to rise / descend. Shift+F1 releases the mouse. Escape stops play.
This is an environment scene, not a complete game with objectives or enemies.

EDIT
Scenery actors are grouped in the Outliner by asset category. Four CameraActors
provide a hero view, a path view, an apple-grove view and an elevated overview.
All meshes and materials are local to /Game/CandyCarnival and can be migrated
into another UE 5.6 project with the Content Browser's Migrate command.
The original .blend and grouped .fbx files are in SourceArt.

COLLISION
Physical scenery uses fitted convex hulls (up to 42 vertices per hull).
Tents retain their doorways and open interiors; candy cane hooks and individual
props have separate shapes, so collision does not bridge empty space.
The ground, biscuit path and caramel ribbon use separate lightweight surface
meshes, totaling 5,480 triangles. The background sky and marquee lettering do
not block movement; the marquee itself and the clouds do.
In Unreal, Alt+C toggles the collision display in the level viewport.
The authoring workspace keeps a local backup; backups are not committed.

REBUILD
Tools/build_models.py runs in Blender 5.x to regenerate original source meshes.
Tools/build_unreal.py runs in Unreal's editor Python environment to import the
meshes, create materials, lighting and cameras, and save the environment map.
If source geometry changes, run Tools/generate_collision.py in Blender after
build_models.py to regenerate the collision FBXs. The Unreal build script then
applies them automatically. Tools/apply_collision.py updates only collision in
the existing scene. Tools/verify_collision_play.py checks clearances and drives
the explorer into a cane, a wall and through the tent doorway in Play mode.
Rebuilding replaces the generated CandyCarnival map. Save any custom edits to
a different level before rebuilding.

The project uses DX11, dynamic shadows, screen-space reflections and ambient
occlusion. It requires no downloaded asset packs and no C++ compilation.
