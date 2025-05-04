bl_info = {
    "name": "Water IO V1.3.7",
    "author": "MadGamerHD",
    "version": (1, 3, 7),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Water IO V1.3.7",
    "description": "Import/export GTA San Andreas water.dat with editable per-vertex parameters, color coding, utilities, and logging",
    "category": "Import-Export",
}

import bpy, bmesh, re
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    FloatVectorProperty,
    FloatProperty,
)

# === Data Structures ===
class WaterVertex(bpy.types.PropertyGroup):
    params: FloatVectorProperty(name="Params (p0–p3)", size=4, default=(0, 0, 0, 0))

# === Parsing & I/O ===
def parse_water_dat(path):
    faces = []
    with open(path) as f:
        for line in f:
            line = line.split(";")[0].strip()
            if not line or line.lower().startswith("processed") or line.startswith("#"):
                continue
            parts = [p for p in re.split(r"[\s,]+", line) if p]
            if len(parts) not in (22, 29):
                continue
            verts = 3 if len(parts) == 22 else 4
            coords, params = [], []
            for i in range(verts):
                i7 = i * 7
                x, y, z = map(float, parts[i7 : i7 + 3])
                pr = list(map(float, parts[i7 + 3 : i7 + 7]))
                coords.append((x, y, z))
                params.append(pr)
            faces.append((coords, params))
    return faces

# === Materials & Color Coding ===
def ensure_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = False
    mat.blend_method = "BLEND"
    return mat

def color_code(thresh):
    shallow = ensure_material("WaterShallow", (0.2, 0.6, 1, 0.5))
    deep = ensure_material("WaterDeep", (0, 0.1, 0.6, 0.5))
    col = bpy.data.collections.get("WaterIO")
    if not col:
        return
    for obj in col.objects:
        if not obj.is_water:
            continue
        vals = [v.params[2] for v in obj.water_verts]
        avg = sum(vals) / len(vals) if vals else 0
        mat = shallow if avg < thresh else deep
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        obj.show_transparent = True

# === Maintain Vert Collection ===
def update_vert_collection(self, context):
    obj = context.object
    if not obj or obj.type != "MESH":
        return
    cnt = len(obj.data.vertices)
    while len(obj.water_verts) < cnt:
        obj.water_verts.add()
    while len(obj.water_verts) > cnt:
        obj.water_verts.remove(len(obj.water_verts) - 1)

# === Operators ===
class OT_LoadWater(bpy.types.Operator):
    bl_idname = "water_io.load"
    bl_label = "Load water.dat"
    bl_options = {"REGISTER", "UNDO"}
    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        faces = parse_water_dat(self.filepath)
        if not faces:
            self.report({"ERROR"}, "No valid water zones found.")
            return {"CANCELLED"}
        if col := bpy.data.collections.get("WaterIO"):
            for o in col.objects:
                bpy.data.objects.remove(o, True)
            bpy.data.collections.remove(col)
        col = bpy.data.collections.new("WaterIO")
        context.scene.collection.children.link(col)
        for i, (coords, params) in enumerate(faces):
            mesh = bpy.data.meshes.new(f"Zone_{i}")
            obj = bpy.data.objects.new(f"Zone_{i}", mesh)
            col.objects.link(obj)
            bm = bmesh.new()
            verts = [bm.verts.new(c) for c in coords]
            try:
                bm.faces.new(verts)
            except:
                pass
            bm.to_mesh(mesh)
            bm.free()
            obj.is_water = True
            obj.water_verts.clear()
            for p in params:
                obj.water_verts.add().params = p
        color_code(context.scene.shallow_threshold)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class OT_ExportWater(bpy.types.Operator):
    bl_idname = "water_io.export"
    bl_label = "Export water.dat"
    bl_options = {"REGISTER", "UNDO"}
    filepath: StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        zones = [o for o in context.selected_objects if o.is_water]
        if not zones:
            self.report({"ERROR"}, "Select water zones to export.")
            return {"CANCELLED"}
        lines = ["processed"]
        for o in zones:
            coords = [o.matrix_world @ v.co for v in o.data.vertices]
            params = [v.params for v in o.water_verts]
            parts = [
                f"{c.x:.1f} {c.y:.1f} {c.z:.5f} {p[0]:.5f} {p[1]:.5f} {p[2]:.5f} {p[3]:.5f}"
                for c, p in zip(coords, params)
            ]
            lines.append(" ".join(parts) + " 1")
        with open(self.filepath, "w") as f:
            f.write("\n".join(lines))
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class OT_FixZone(bpy.types.Operator):
    bl_idname = "water_io.fix"
    bl_label = "Fix Zone"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        thr = context.scene.fix_threshold
        rem = 0
        for o in context.selected_objects:
            if not o.is_water:
                continue
            if sum(p.area for p in o.data.polygons) < thr:
                bpy.data.objects.remove(o, True)
                rem += 1
        self.report({"INFO"}, f"Removed {rem} small zones.")
        return {"FINISHED"}

class OT_FlattenPlane(bpy.types.Operator):
    bl_idname = "water_io.flatten_plane"
    bl_label = "Flatten Plane"
    bl_description = "Flatten selected zone"

    def execute(self, context):
        obj = context.object
        if not obj.is_water:
            self.report({"ERROR"}, "Select a water zone to flatten.")
            return {"CANCELLED"}
        verts = obj.data.vertices
        avg = sum(v.co.z for v in verts) / len(verts)
        for v in verts:
            v.co.z = avg
        obj.data.update()
        return {"FINISHED"}

class OT_ResetParams(bpy.types.Operator):
    bl_idname = "water_io.reset"
    bl_label = "Reset Params"
    bl_description = "Reset p0–p3 values"

    def execute(self, context):
        for v in context.object.water_verts:
            v.params = (0, 0, 0, 0)
        return {"FINISHED"}

# === UI Panel ===
class PANEL_WaterIO(bpy.types.Panel):
    bl_label = "Water IO V1.3.7"
    bl_idname = "VIEW3D_PT_water_io"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Water IO V1.3.7"

    def draw(self, context):
        L = self.layout
        S = context.scene
        O = context.object
        L.operator("water_io.load")
        L.operator("water_io.export")
        L.separator()
        box = L.box()
        box.label(text="Scene Settings")
        box.prop(S, "shallow_threshold")
        box.prop(S, "fix_threshold")
        box.prop(S, "water_speed")
        box.prop(S, "enable_logging")
        box.prop(S, "prevent_merge", text="Prevent Water Merge")
        row = L.row(align=True)
        row.operator("water_io.fix")
        row.operator("water_io.flatten_plane")
        row.operator("water_io.reset")
        if O and O.is_water:
            L.separator()
            L.label(text=f"Active Zone: {O.name}")
            for i, v in enumerate(O.water_verts):
                L.prop(v, "params", text=f"V{i+1}")
            L.label(text="Visibility Flags:")
            L.prop(O, "flag_default")
            L.prop(O, "flag_invisible")
            L.prop(O, "flag_shallow_visible")
            L.prop(O, "flag_shallow_invisible")

# === Registration ===
classes = [
    WaterVertex,
    OT_LoadWater,
    OT_ExportWater,
    OT_FixZone,
    OT_FlattenPlane,
    OT_ResetParams,
    PANEL_WaterIO,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Object.is_water = BoolProperty(
        default=False, update=update_vert_collection
    )
    bpy.types.Object.water_verts = CollectionProperty(type=WaterVertex)
    bpy.types.Object.flag_default = BoolProperty(name="Default Visible", default=True)
    bpy.types.Object.flag_invisible = BoolProperty(
        name="Default Invisible", default=False
    )
    bpy.types.Object.flag_shallow_visible = BoolProperty(
        name="Shallow Visible", default=True
    )
    bpy.types.Object.flag_shallow_invisible = BoolProperty(
        name="Shallow Invisible", default=False
    )
    bpy.types.Scene.shallow_threshold = FloatProperty(
        name="Shallow Thresh", default=0.5, min=0
    )
    bpy.types.Scene.fix_threshold = FloatProperty(
        name="Fix Thresh", default=0.01, min=0
    )
    bpy.types.Scene.water_speed = FloatProperty(name="Water Speed", default=1.0, min=0)
    bpy.types.Scene.enable_logging = BoolProperty(name="Enable Logging", default=False)
    bpy.types.Scene.prevent_merge = BoolProperty(
        name="Prevent Water Merge", default=False
    )

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Object.is_water
    del bpy.types.Object.water_verts
    del bpy.types.Object.flag_default
    del bpy.types.Object.flag_invisible
    del bpy.types.Object.flag_shallow_visible
    del bpy.types.Object.flag_shallow_invisible
    del bpy.types.Scene.shallow_threshold
    del bpy.types.Scene.fix_threshold
    del bpy.types.Scene.water_speed
    del bpy.types.Scene.enable_logging
    del bpy.types.Scene.prevent_merge

if __name__ == "__main__":
    register()
