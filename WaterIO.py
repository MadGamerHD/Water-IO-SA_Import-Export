bl_info = {
    "name": "Water IO",
    "author": "MadGamerHD",
    "version": (1, 0, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Water IO",
    "description": "Import/export GTA San Andreas water.dat with full parameters",
    "category": "Import-Export",
}

import bpy
import bmesh
import re
from bpy.props import StringProperty

# --------------------------------------
# Utility: parse face entries (coords + 4 params per vertex)
# --------------------------------------
def parse_water_dat(filepath):
    faces = []  # list of (coords, params)
    with open(filepath, 'r') as f:
        for raw in f:
            line = raw.split(';', 1)[0].strip()
            if not line or line.lower().startswith('processed') or line.startswith('#'):
                continue
            parts = [p for p in re.split(r'[\s,]+', line) if p]
            # must be 22 tokens for tri or 29 for quad
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
# Import operator
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
        # clear old
        colname = "WaterIO"
        if colname in bpy.data.collections:
            old = bpy.data.collections[colname]
            for obj in list(old.objects): bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old)
        col = bpy.data.collections.new(colname)
        context.scene.collection.children.link(col)
        # create objects
        for idx, (coords, params) in enumerate(faces):
            mesh = bpy.data.meshes.new(f"Zone_{idx}")
            obj = bpy.data.objects.new(f"Zone_{idx}", mesh)
            col.objects.link(obj)
            bm = bmesh.new()
            vlist = [bm.verts.new(co) for co in coords]
            try:
                bm.faces.new(vlist)
            except ValueError:
                pass
            bm.to_mesh(mesh)
            bm.free()
            # store parameters on object
            obj["water_params"] = params
        self.report({'INFO'}, f"Loaded {len(faces)} zones into '{colname}'.")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# --------------------------------------
# Export operator
# --------------------------------------
class EXPORT_OT_water_dat(bpy.types.Operator):
    bl_idname = "export_scene.water_dat"
    bl_label = "Export water.dat"
    bl_description = "Export selected zones back to water.dat"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        # collect selected zone objects
        zones = [o for o in context.selected_objects if o.get("water_params")]
        if not zones:
            self.report({'ERROR'}, "Select imported water zone objects to export.")
            return {'CANCELLED'}
        lines = ["processed"]
        for obj in zones:
            params = obj["water_params"]
            # world coords of verts
            coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
            parts = []
            for co, pr in zip(coords, params):
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
# Panel
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

# --------------------------------------
# Registration
# --------------------------------------
def register():
    bpy.utils.register_class(IMPORT_OT_water_dat)
    bpy.utils.register_class(EXPORT_OT_water_dat)
    bpy.utils.register_class(VIEW3D_PT_water_io)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_water_io)
    bpy.utils.unregister_class(EXPORT_OT_water_dat)
    bpy.utils.unregister_class(IMPORT_OT_water_dat)

if __name__ == "__main__":
    register()
