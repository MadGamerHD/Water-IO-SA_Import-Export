Water IO V1.4.0 is a Blender add‑on that lets you work seamlessly with GTA SA’s water.dat format. You can import existing water zones, tweak per‑vertex parameters, color‑code zones by depth, create new water patches from scratch, and then export back to a valid water.dat. Everything is integrated into the 3D View sidebar for a smooth, non‑destructive workflow.

Key Features
Import & Export

Load any standard GTA SA water.dat file into Blender

Export selected water zones back to water.dat with full precision

Color‑Coded Depth Visualization

Zones automatically receive “shallow” or “deep” materials based on a configurable depth threshold

Transparent shaders let you preview overlaps

Per‑Vertex Parameter Editing

Each zone’s vertices store four custom floats (p0–p3) directly editable in the UI

Real‑time updates propagate to material assignments

Manual Zone Creation

Create a new square water patch at the origin with one click

Auto‑populates its vertex parameters so you can place and shape custom zones

Zone Utilities

Remove Small Zones: Automatically delete water patches below a minimum area

Flatten Zone: Level all vertices to an average height

Reset Parameters: Zero out all per‑vertex values

Clean, Modern UI

Operators grouped logically in the sidebar

Clear icons for import, export, create, and utilities

Adjustable thresholds for shallow coloring and minimum zone size

Installation
Open Blender 4.0

Go to Edit → Preferences → Add‑ons → Install…

Select the waterio.py file

Enable “Water IO” in your add‑ons list

Usage
Import

In the 3D View sidebar → Water IO, click Load water.dat

Choose your water.dat; zones appear as mesh planes

Edit & Visualize

Select any zone to see its per‑vertex p0–p3 parameters in the panel

Adjust the Shallow Threshold to recolor zones

Use Remove Small Zones, Flatten Zone, or Reset Params on selected zones

Create New Zone

Click Create New Zone to spawn a 5×5 square at the scene origin

Move, scale, or edit it just like imported zones

Export

Select the zones you want in the viewport

Click Export water.dat, choose a save location

A new water.dat is written with your modified data

Contributing & Feedback
Report bugs or suggest enhancements via GitHub Issues

Pull requests welcome for new features, optimizations, or UI improvements
