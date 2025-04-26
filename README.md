# 📄 Water IO - Tool Description

**Water IO** is a Blender 4.0 add-on for **importing**, **editing**, and **exporting** `water.dat` files used in **GTA San Andreas**.

---

## 🎯 What Water IO Does

- **Load** (Import) water zones from a `water.dat` file into Blender.
- **Display** each water zone as its **own separate object** (easy to select and edit).
- **Store** all water parameters (like currents or properties) inside each object.
- **Export** (Save) the selected water zones back into a correctly formatted `water.dat` file.
- **Automatically adds** the line `processed` at the top of exported files.
- **Fully supports multi-selection**: you can export multiple water zones at once.

---

## 📥 How Import (Load) Works

- Click **Load water.dat**.
- Select your `water.dat` file.
- The add-on **reads** each face (triangle or quad) with **7 parameters** per vertex (X, Y, Z, and 4 parameters like water height, wave, etc.).
- It **creates one Blender object per water face**, grouping them under a collection called **WaterIO**.
- Each water object stores its **original parameters** in Blender's object data (`water_params` property).

✅ Faces are **color coded** by Blender’s default material viewport shading (for easy visualizing). / Note Patching ColorCoding Soon
✅ Objects are **named** `Zone_0`, `Zone_1`, etc. based on their load order.

---

## 📤 How Export (Save) Works

- Select one or more water zone objects (e.g., `Zone_0`, `Zone_1`, etc.).
- Click **Export water.dat**.
- Choose the location to save the file.
- The export:
  - Writes a **`processed`** line at the very top (required by GTA).
  - Saves each zone in **correct format**:
    ```
    x y z p0 p1 p2 p3   x y z p0 p1 p2 p3   x y z p0 p1 p2 p3   (optional 4th vertex)   1
    ```
  - Each water face writes the vertex positions + its 4 stored parameters, just like the original water.dat.
- Export supports **multiple zones** at once.

---

## 🔧 Additional Features

- **Auto-Clear Old Data**: When loading a new file, the old `WaterIO` collection is cleared automatically to avoid duplicate data.
- **Simple Panel Interface**: You can find the tool in:
  > **3D Viewport** → **Sidebar (N panel)** → **Water IO Tab**.
- **Safe for Undo/Redo**: Operations are Blender Undo-friendly.

---

## 📌 Things to Keep In Mind

- Always **select** the water zones you want to export before clicking **Export**.
- Only zones loaded through **Water IO** are recognized for export (they store special parameters).
- It works with both **triangles** (3 vertices) and **quads** (4 vertices) automatically.
- If the `.dat` file format is wrong (missing numbers, etc.), import will skip that line safely.

![Screenshot 2025-04-26 205745](https://github.com/user-attachments/assets/5c929e8e-bb5a-478b-91e1-d1778aac194f)

---

## 🛠️ Summary

| Feature             | Description                              |
|---------------------|------------------------------------------|
| Import              | Loads `water.dat` into Blender zones     |
| Export              | Saves selected Blender zones back        |
| Grouping            | Everything organized under WaterIO collection |
| Format Matching     | Exactly matches GTA SA expected format  |
| Easy Editing        | Edit, move, scale water zones freely     |
| Full Parameters     | Saves all 4 parameters per vertex        |
| Multi-Export        | Export many zones at once                |
| Safe Handling       | Clear old data when loading new file     |
