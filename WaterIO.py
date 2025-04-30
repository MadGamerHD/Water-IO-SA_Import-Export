bl_info = {
    "name": "Water IO Version 1.1.0",
    "author": "MadGamerHD",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Water IO / Object Properties > Water Face Parameters",
    "description": "Import/export GTA San Andreas water.dat with editable per-vertex parameters",
    "category": "Import-Export",
}

import bpy
import bmesh
import re
from bpy.props import (
    StringProperty, BoolProperty, CollectionProperty,
    FloatVectorProperty
)

# --------------------------------------
# Property Group: holds 4 water parameters per vertex
# --------------------------------------
class WaterVertexProps(bpy.types.PropertyGroup):
    params: FloatVectorProperty(
        name="Params (p0,p1,p2,p3)",
        description="GTA water parameters for this vertex",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0)
    )

# --------------------------------------
# Helpers: parse and write water.dat
# --------------------------------------
def parse_water_dat(filepath):
    faces = []  # list of (coords, params)
    with open(filepath, 'r') as f:
        for raw in f:
            line = raw.split(';', 1)[0].strip()
            if not line or line.lower().startswith('processed') or line.startswith('#'):
                continue
            parts = [p for p in re.split(r'[\s,]+', line) if p]
            if len(parts) not in (22, 29):
                continue
            verts = 3 if len(parts) == 22 else 4
            coords = []
            params = []
            for i in range(verts):
                base = i * 7
                x, y, z = map(float, parts[base:base+3])
                pr = list(map(float, parts[base+3:base+7]))
                coords.append((x, y, z))
                params.append(pr)
            faces.append((coords, params))
    return faces

# --------------------------------------
# Operators: Import & Export
# --------------------------------------
class IMPORT_OT_water_dat(bpy.types.Operator):
    bl_idname = "import_scene.water_dat"
    bl_label = "Load water.dat"
    bl_description = "Load GTA water.dat faces with parameters"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        faces = parse_water_dat(self.filepath)
        if not faces:
            self.report({'ERROR'}, "No valid entries found.")
            return {'CANCELLED'}
        # clear previous collection
        colname = "WaterIO"
        if colname in bpy.data.collections:
            old = bpy.data.collections[colname]
            for obj in list(old.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old)
        col = bpy.data.collections.new(colname)
        context.scene.collection.children.link(col)

        for idx, (coords, params) in enumerate(faces):
            mesh = bpy.data.meshes.new(f"Zone_{idx}")
            obj = bpy.data.objects.new(f"Zone_{idx}", mesh)
            col.objects.link(obj)
            bm = bmesh.new()
            verts = [bm.verts.new(co) for co in coords]
            try:
                bm.faces.new(verts)
            except ValueError:
                pass
            bm.to_mesh(mesh)
            bm.free()

            # mark as water and assign per-vertex props
            obj.is_water = True
            obj.water_verts.clear()
            for pr in params:
                item = obj.water_verts.add()
                item.params = pr
        self.report({'INFO'}, f"Loaded {len(faces)} zones into '{colname}'.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class EXPORT_OT_water_dat(bpy.types.Operator):
    bl_idname = "export_scene.water_dat"
    bl_label = "Export water.dat"
    bl_description = "Export selected zones back to water.dat"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        zones = [o for o in context.selected_objects if getattr(o, 'is_water', False)]
        if not zones:
            self.report({'ERROR'}, "Select imported water zone objects to export.")
            return {'CANCELLED'}

        prevent = context.scene.prevent_water_merge
        # TODO: implement merging behavior if prevent is False

        lines = ["processed"]
        for obj in zones:
            # choose source of params: updated props or legacy stored
            params_list = []
            if obj.water_verts:
                params_list = [v.params for v in obj.water_verts]
            else:
                params_list = obj.get("water_params", [])

            coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
            parts = []
            for co, pr in zip(coords, params_list):
                parts.append(f"{co.x:.1f} {co.y:.1f} {co.z:.5f} {pr[0]:.5f} {pr[1]:.5f} {pr[2]:.5f} {pr[3]:.5f}")
            line = "    ".join(parts) + "    1"
            lines.append(line)

        with open(self.filepath, 'w') as f:
            for l in lines:
                f.write(l + "\n")
        self.report({'INFO'}, f"Exported {len(zones)} zones to '{self.filepath}'.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --------------------------------------
# UI Panels
# --------------------------------------
class VIEW3D_PT_water_io(bpy.types.Panel):
    bl_label = "Water IO"
    bl_idname = "VIEW3D_PT_water_io"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Water IO'

    def draw(self, context):
        layout = self.layout
        layout.operator("import_scene.water_dat", text="Load water.dat")
        layout.operator("export_scene.water_dat", text="Export water.dat")

class OBJECT_PT_water_params(bpy.types.Panel):
    bl_idname = "OBJECT_PT_water_params"
    bl_label = "Water Face Parameters"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH' and getattr(obj, 'is_water', False))

    def draw(self, context):
        layout = self.layout
        obj = context.object
        for i, v in enumerate(obj.water_verts):
            box = layout.box()
            box.label(text=f"Vertex {i+1} Params:")
            box.prop(v, "params", text="")

class SCENE_PT_water_export_options(bpy.types.Panel):
    bl_idname = "SCENE_PT_water_export_options"
    bl_label = "Water Export Options"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "prevent_water_merge")

# --------------------------------------
# Registration
# --------------------------------------
def update_is_water(self, context):
    # ensure water_verts matches vertex count
    obj = context.object
    if not obj or not obj.data:
        return
    n = len(obj.data.vertices)
    col = obj.water_verts
    while len(col) < n:
        col.add()
    while len(col) > n:
        col.remove(len(col)-1)

classes = [WaterVertexProps,
           IMPORT_OT_water_dat, EXPORT_OT_water_dat,
           VIEW3D_PT_water_io, OBJECT_PT_water_params,
           SCENE_PT_water_export_options]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.is_water = BoolProperty(
        name="Is Water Face",
        description="Mark this object as a GTA water face",
        default=False,
        update=update_is_water
    )
    bpy.types.Object.water_verts = CollectionProperty(type=WaterVertexProps)
    bpy.types.Scene.prevent_water_merge = BoolProperty(
        name="Prevent Water Merge",
        description="Keep water faces separate on export",
        default=False
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Object.is_water
    del bpy.types.Object.water_verts
    del bpy.types.Scene.prevent_water_merge

if __name__ == "__main__":
    register()
