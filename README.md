# 📄 Water IO V1.3.5  

**Water IO** is a Blender 4.0 add-on for **importing**, **editing**, **color-coding**, and **exporting** `water.dat` files used in **GTA San Andreas**. It now also includes a **Prevent Water Merge** option and a **Fix Zone** utility.  

---

## 🎯 What Water IO Does

- **Load** (Import) water zones from a `water.dat` file into Blender.  
- **Display** each water zone as its **own separate object** (easy to select and edit).  
- **Mark** objects as **Water Faces** and store per-vertex GTA water parameters (p0–p3).  
- **Edit** all four parameters for each vertex directly in the **Object Properties** panel.  
- **Automatically color-code** water faces based on depth parameter (p2) using configurable **Shallow Threshold**.  
- **Prevent Water Merge**: Optionally export adjacent zones as separate entries to preserve distinct regions.  
- **Fix Zone**: Remove selected zones whose area falls below a user-defined threshold to avoid small-crash issues.  
- **Export** (Save) the selected water zones back into a correctly formatted `water.dat` file.  
- **Automatically adds** the line `processed` at the top of exported files.  
- **Fully supports multi-selection**: you can export multiple water zones at once.  

---

## 📥 How Import (Load) Works

1. Click **Load water.dat** in the **3D Viewport → Sidebar → Water IO** tab.  
2. Select your `water.dat` file.  
3. The add-on **reads** each face (triangle or quad) with **7 values** per vertex: X, Y, Z, plus the four GTA water params (p0, p1, p2, p3).  
4. It **creates one Blender object per water face**, grouping them under a collection named **WaterIO** (old data is cleared each import to avoid duplicates).  
5. Each imported object is automatically marked **Is Water Face** and its per-vertex parameters populate the new **water_verts** property group.  

✅ Objects are named `Zone_0`, `Zone_1`, etc., in load order.  

---

## 🎨 Automatic Color Coding

After import (or whenever parameters change), Water IO assigns a material based on each face's average **depth** (p2):  

- **Shallow Water** (p2 < Shallow Threshold): Light-blue transparent material (`WaterShallow`).  
- **Deep Water** (p2 ≥ Shallow Threshold): Dark-blue transparent material (`WaterDeep`).  

The **Shallow Threshold** slider in **Scene Properties → Water Options** controls the cutoff depth (default: **0.5**).  

Color coding updates automatically on import and when you adjust the threshold or per-vertex parameters.  

---

## 💧 Water Face Parameters Panel

When you select an object marked **Is Water Face**, a new panel appears in **Object Properties → Water Face Parameters**:  

- A toggle **Is Water Face** marks or unmarks any mesh object as a water zone.  
- One **boxed section per vertex**, with editable fields for the four parameters **(p0, p1, p2, p3)**.  
- Edits immediately update the internal data and will reflect in color coding on export or manual recolor.  

---

## 🔧 Scene Options

Located in **Scene Properties → Water Options**:

- **Shallow Threshold**: Depth cutoff for differentiating shallow vs. deep water (default **0.5**).  
- **Prevent Water Merge**: When enabled, adjacent zones export as separate entries, preserving distinct regions (default **Off**).  
- **Fix Thresh**: Area threshold below which zones are considered too small; select a zone and click **Fix Zone** to remove (default **0.01**).  

---

## 📤 How Export (Save) Works

1. Select one or more objects marked **Is Water Face** (e.g., `Zone_0`, `Zone_1`, etc.).  
2. Click **Export water.dat** in the **Water IO** tab.  
3. Choose the save location.  
4. The export routine:  
   - Writes **`processed`** as the first line.  
   - Reads the **per-vertex parameters** from each object’s **water_verts**.  
   - Assembles each face into lines of the form:  
     ```  
     x1 y1 z1 p0 p1 p2 p3   x2 y2 z2 p0 p1 p2 p3   x3 y3 z3 p0 p1 p2 p3   (optional fourth vertex)   1  
     ```  
   - Honors **Prevent Water Merge** and **Fix Zone** settings when exporting.  

---

## 🛠️ Additional Features & Notes

- **Undo/Redo Friendly**: All operations support Blender’s undo stack.  
- **Triangle & Quad Support**: Works seamlessly with both 3- and 4-vertex faces.  
- **Safe Import**: Lines in `water.dat` with invalid token counts are skipped without crashing.  
- **Legacy Compatibility**: Objects imported with older versions still export correctly.  

---

## 📝 Summary Table

| Feature                   | Description                                                                        |
|---------------------------|------------------------------------------------------------------------------------|
| Import                    | Loads `water.dat` into separate Blender objects                                    |
| Is Water Face Toggle      | Marks/unmarks mesh objects as GTA water zones                                      |
| Per-Vertex Editing        | Edit all four GTA parameters (p0–p3) in UI                                         |
| Automatic Color Coding    | Depth-based material assignment with configurable threshold                        |
| Prevent Water Merge       | Toggle merging behavior on export                                                  |
| Fix Zone                  | Remove small zones below area threshold                                            |
| Export                    | Saves selected zones back to `water.dat`                                           |
| Scene Options             | Shallow Threshold, Prevent Water Merge & Fix Thresh settings in Scene Properties    |
| Collection Management     | Auto-clears old data in **WaterIO** collection                                     |
| Triangle & Quad Support   | Fully supports 3- and 4-vertex water faces                                         |
| Undo/Redo Support         | All actions are undoable and redoable                                               |

---

_Previews_:  
![Screenshot 2025-04-30 171417](https://github.com/user-attachments/assets/ba0509f7-af82-4f3b-bf83-b387152bd999)
