# 📄 Water IO V1.3.7

**Water IO** is a Blender 4.0 add-on for **importing**, **editing**, **color‑coding**, and **exporting** `water.dat` files used in **GTA San Andreas**. It now also includes **Prevent Water Merge**, **Fix Zone**, **Flatten Plane**, **Reset Params**, **Water Speed**, **Enable Logging**, and **Visibility Flags** features, all unified into a single panel in the **3D Viewport → Sidebar → Water IO**.

---

## 🎯 What Water IO Does

- **Load** (`Load water.dat`) water zones from a `water.dat` file into Blender.
- **Display** each zone as its **own separate object** under a `WaterIO` collection (old data cleared on each import).
- **Edit** per‑vertex GTA water parameters (p0–p3) and adjust **Water Speed** in one place.
- **Automatically color-code** zones based on depth (p2) using the **Shallow Threshold** slider.
- **Prevent Water Merge**: export adjacent zones as separate entries to preserve distinct regions.
- **Fix Zone**: remove selected zones below an **area threshold** to avoid crashes.
- **Flatten Plane**: align a selected zone’s vertices to their average height.
- **Reset Params**: restore all per‑vertex parameters to defaults.
- **Visibility Flags**: toggle **Default Visible**, **Default Invisible**, **Shallow Visible**, **Shallow Invisible** states per zone.
- **Export** (`Export water.dat`) selected zones back into a valid `water.dat` file, writing `processed` at the top and honoring merge/fix settings.
- **Enable Logging**: toggle detailed log output for easier issue reporting (users can paste logs).
- **Multi‑selection** support: import or export multiple zones at once.

---

## 📥 Unified Water IO Panel

Located in **3D Viewport → Sidebar → Water IO**. Everything lives in one cohesive panel:

1. **Import / Export**
   - **Load water.dat**: opens file selector and imports zones.
   - **Export water.dat**: saves selected zones to file.

2. **Scene Settings**
   - **Shallow Threshold**: depth cutoff for color‑coding (default **0.5**).
   - **Prevent Water Merge** [✓]: keep adjacent zones separate on export.
   - **Fix Thresh**: area threshold to auto‑remove small zones (default **0.01**).
   - **Water Speed**: global multiplier for zone animation speed.
   - **Enable Logging** [✓]: record detailed operations for debugging.

3. **Utilities**
   - **Fix Zone**: removes selected zones below the **Fix Thresh** area.
   - **Flatten Plane**: flattens active zone to its average height.
   - **Reset Params**: resets all p0–p3 values to defaults for the active zone.

4. **Active Zone Parameters** (when a zone is selected and marked **Is Water Face**)
   - **Vertex 1–4** parameter fields (p0, p1, p2, p3).
   - **Visibility Flags** toggles:
     - **Default Visible** [✓]
     - **Default Invisible** [ ]
     - **Shallow Visible** [✓]
     - **Shallow Invisible** [ ]

---

## 📥 How Import (Load) Works

1. Click **Load water.dat**.
2. Select your `water.dat` file.
3. Each triangle (3‑vertex; 22 tokens) or quad (4‑vertex; 29 tokens) line is parsed, ignoring invalid lines and comments.
4. Creates objects named `Zone_0`, `Zone_1`, … with a custom `water_verts` property group storing per‑vertex parameters.
5. Applies initial **color‑coding** based on the default **Shallow Threshold**.

---

## 📤 How Export (Save) Works

1. Select one or more **Water Face** objects.
2. Click **Export water.dat**.
3. Choose save location.
4. Writes a `processed` header, then one line per zone:
   ```
   x1 y1 z1 p0 p1 p2 p3   x2 y2 z2 p0 p1 p2 p3   x3 y3 z3 p0 p1 p2 p3   (x4 y4 z4 p0 p1 p2 p3)   1
   ```
5. Honors **Prevent Water Merge**, **Fix Zone**, and **Visibility Flags** when exporting.

---

## 🛠️ Additional Notes

- **Undo/Redo Friendly**: all operators support Blender’s undo stack.
- **Triangle & Quad Support**: handles both face types seamlessly.
- **Safe Import**: skips lines with wrong token counts without errors.
- **Legacy Compatibility**: older imports still export correctly.

---

## 📝 Summary Table

| Feature                   | Description                                                                                       |
|---------------------------|---------------------------------------------------------------------------------------------------|
| Import / Export           | Load & save `water.dat` directly within Blender                                                   |
| Unified Panel             | Single sidebar UI for all tools, settings, and parameters                                         |
| Per‑Vertex Editing        | Edit p0–p3 directly for each vertex                                                                |
| Automatic Color Coding    | Depth-based materials via **Shallow Threshold**                                                    |
| Prevent Water Merge       | Export adjacent zones separately                                                                    |
| Fix Zone                  | Remove small zones below **Fix Thresh**                                                          |
| Flatten Plane             | Align zone to average height                                                                       |
| Reset Params              | Reset all parameters to defaults                                                                   |
| Visibility Flags          | Toggle visible/invisible states per zone                                                          |
| Water Speed               | Adjust global water animation speed                                                                |
| Enable Logging            | Detailed log output for debugging                                                                  |
| Multi‑selection Support   | Import or export multiple zones at once                                                          |
| Undo/Redo Support         | Full integration with Blender’s undo system                                                        |

---

![Screenshot 2025-05-04 143927](https://github.com/user-attachments/assets/a9e4eb9f-a4f2-4d78-9f0e-48cf2b4d0db5)

---

## Water.dat File Overview in GTA: San Andreas

### Introduction

In **GTA San Andreas**, the `water.dat` file located in the game's `data` folder defines all the water surfaces within the game world. This plain-text file outlines the geometry and behavior of water planes such as oceans, lakes, pools, and more. Notably, the default game includes up to 307 water planes, with a hard limit of 1021 planes, which can be extended with mods (e.g., **Sacky’s Limit Adjuster**).

### File Format

The `water.dat` file begins with a header (usually the word "processed"), followed by individual entries for each water plane. Each entry specifies the coordinates for the corners of a water plane (either triangular or rectangular), along with additional parameters. The planes can have 3 (triangular) or 4 (rectangular) corner points, and each water plane is defined by a set of world coordinates (x, y) and a common water height (z).

While the planes are not required to align to a grid, adjacent planes may touch, and their continuity depends on matching edge coordinates. Modding tools like **3ds Max water I/O scripts** can be used to import/export this format.

### Plane Parameters (P0–P3)

Each water plane entry contains four additional values, commonly referred to as **P0**, **P1**, **P2**, and **P3**. Although Rockstar has not officially documented these parameters, modder analyses suggest they control the behavior of the water, including:

* **P0**: Likely related to the water's type or depth.
* **P1**: Possibly adjusts wave parameters.
* **P2 & P3**: Further influence wave heights and other dynamic water behaviors.

These values help distinguish between different types of water (e.g., oceans vs. pools) and may also affect wave movement, although the actual wave speed is handled by the engine’s water shader rather than the `water.dat` file itself. Water transparency and color are set globally (e.g., through **TimeCyc**, not in `water.dat`).

### Behavior, Speed, and Edge Merging

The game engine renders each water plane independently. When two planes share an edge at the same height, they merge seamlessly. However, if the edges do not align, the water will break continuity, potentially leading to visible gaps or rendering issues. Incorrect or degenerate entries, such as invalid geometry, can even cause the game to crash (e.g., division-by-zero errors).

If the `water.dat` file is missing or contains errors, water surfaces will fail to render, causing the game to display no water at all. Since `water.dat` essentially controls sea level and water maps, any errors in the file can lead to significant issues with water rendering.

### Known Limits and Tools

By default, **GTA San Andreas** allows up to 1021 water planes, and exceeding this limit can cause issues. The shipped `water1.dat` is ignored by the game. While Rockstar has never provided official documentation for the file format, modders rely on reverse-engineering and community knowledge to understand and edit it.

Several tools and scripts are available to help create and modify `water.dat`, including **Gforce’s** and **Ocram’s 3ds Max water I/O scripts**. These tools have been essential for mods that modify water levels or wave heights.

### Conclusion

The structure of `water.dat` is simple, but its contents are crucial for proper water rendering in GTA San Andreas. Each plane’s corners and parameters must be correct for the game to render water surfaces as intended. Despite the absence of official documentation, the GTA modding community has developed a strong understanding of the file format, allowing for detailed customization of water surfaces within the game.

### Sources:

* [Water.dat - GTAMods Wiki](https://gtamods.com/wiki/Water.dat)
* [Water1.dat | GTA Wiki | Fandom](https://gta.fandom.com/wiki/Water1.dat)

---
