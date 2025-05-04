# 📄 Water IO V1.3.6

**Water IO** is a Blender 4.0 add-on for **importing**, **editing**, **color‑coding**, and **exporting** `water.dat` files used in **GTA San Andreas**. It now also includes **Prevent Water Merge**, **Fix Zone**, **Reset Params**, **Water Speed**, and **Enable Logging** features, all unified into a single panel in the **3D Viewport → Sidebar → Water IO**.

---

## 🎯 What Water IO Does

- **Load** (`Load water.dat`) water zones from a `water.dat` file into Blender.
- **Display** each zone as its **own separate object** under a `WaterIO` collection (old data cleared on each import).
- **Edit** per‑vertex GTA water parameters (p0–p3) and adjust **Water Speed** in one place.
- **Automatically color-code** zones based on depth (p2) using the **Shallow Threshold** slider.
- **Prevent Water Merge**: export adjacent zones as separate entries to preserve distinct regions.
- **Fix Zone**: remove selected zones below an **area threshold** to avoid crashes.
- **Reset Params**: restore all per‑vertex parameters to defaults.
- **Export** (`Export water.dat`) selected zones back into a valid `water.dat` file, writing `processed` at the top.
- **Enable Logging**: toggle detailed log output for easier issue reporting (paste log for debugging).
- **Multi‑selection** support: import or export multiple zones at once.

---

## 📥 Unified Water IO Panel

Located in **3D Viewport → Sidebar → Water IO**. Everything lives in one cohesive panel:

1. **Import / Export**
   - **Load water.dat**: opens file selector and imports zones.
   - **Export water.dat**: saves selected zones to file, honoring merge and fix settings.

2. **Scene Settings**
   - **Shallow Threshold**: depth cutoff for color‑coding (default **0.5**).
   - **Prevent Water Merge** [✓]: keep adjacent zones separate on export.
   - **Fix Thresh**: area threshold to auto‑remove small zones (default **0.01**).
   - **Water Speed**: global multiplier for zone animations (reads from file by default).
   - **Enable Logging** [✓]: record detailed operations for debugging.

3. **Utilities**
   - **Fix Zone**: removes all selected zones below the **Fix Thresh** area.
   - **Reset Params**: resets all p0–p3 values to defaults for the active zone.

4. **Active Zone Parameters** (when a zone is selected and marked **Is Water Face**)
   - Displays **Vertex 1–4** parameter fields (p0, p1, p2, p3).
   - **Visibility Flags**:
     - **Default Visible** [✓]
     - **Default Invisible** [ ]
     - **Shallow Visible** [✓]
     - **Shallow Invisible** [ ]

---

## 📥 How Import (Load) Works

1. Click **Load water.dat**.
2. Select your `water.dat` file.
3. Each triangle (3‑vert; 22 tokens) or quad (4‑vert; 29 tokens) line is read, ignoring invalid lines and comments.
4. Creates objects named `Zone_0`, `Zone_1`, … with custom `water_verts` storing per‑vertex parameters.
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
5. Honors **Prevent Water Merge** (zones kept separate) and **Fix Zone** removals.

---

## 🛠️ Additional Notes

- **Undo/Redo Friendly**: all operators use Blender’s undo stack.
- **Triangle & Quad Support**: handles both face types seamlessly.
- **Safe Import**: skips lines with wrong token counts without errors.
- **Legacy Compatibility**: older imports still export correctly.

---

## 📝 Summary Table

| Feature                   | Description                                                                                       |
|---------------------------|---------------------------------------------------------------------------------------------------|
| Import / Export           | Load & save `water.dat` from within Blender                                                       |
| Unified Panel             | All settings, utilities, and parameters in one sidebar UI                                          |
| Per‑Vertex Editing        | Edit p0–p3 directly for each vertex                                                                |
| Automatic Color Coding    | Shallow vs deep depth coloring via **Shallow Threshold**                                          |
| Prevent Water Merge       | Toggle to export adjacent zones separately                                                       |
| Fix Zone                  | Remove small zones below **Fix Thresh**                                                          |
| Reset Params              | Reset all custom parameters back to defaults                                                      |
| Water Speed               | Adjust global zone animation speed                                                                |
| Enable Logging            | Record detailed logs for issue diagnostics                                                         |
| Multi‑selection Support   | Import or export multiple zones in one operation                                                  |
| Undo/Redo Support         | Full Blender undo/redo integration                                                                 |

---
![Screenshot 2025-05-04 122207](https://github.com/user-attachments/assets/602d7f8b-36ff-47e7-bef7-36dd17fb1cd4)
