bl_info = {
    "name": "Water IO",
    "author": "MadGamerHD",
    "version": (1, 3, 5),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Water IO",
    "description": "Import/export GTA San Andreas water.dat with editable per-vertex parameters, color coding, and a zone fix utility",
    "category": "Import-Export",
}

import bpy
import bmesh
import re
from bpy.props import StringProperty, BoolProperty, CollectionProperty, FloatVectorProperty, FloatProperty

class WaterVertex(bpy.types.PropertyGroup):
    params: FloatVectorProperty(name="Params", size=4, default=(0,0,0,0))

def parse_water_dat(path):
    faces = []
    with open(path) as f:
        for line in f:
            line = line.split(';')[0].strip()
            if not line or line.lower().startswith('processed') or line.startswith('#'):
                continue
            parts = re.split(r'[\s,]+', line)
            parts = [p for p in parts if p]
            if len(parts) not in (22, 29):
                continue
            verts = 3 if len(parts) == 22 else 4
            coords, params = [], []
            for i in range(verts):
                base = i*7
                x, y, z = map(float, parts[base:base+3])
                pr = list(map(float, parts[base+3:base+7]))
                coords.append((x, y, z))
                params.append(pr)
            faces.append((coords, params))
    return faces

def ensure_material(name, color):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color
        mat.use_nodes = False
        mat.blend_method = 'BLEND'
    return mat

def color_code_collection(collection, threshold):
    deep = ensure_material('WaterDeep', (0, 0.1, 0.6, 0.5))
    shallow = ensure_material('WaterShallow', (0.2, 0.6, 1, 0.5))
    for obj in collection.objects:
        if not getattr(obj, 'is_water', False):
            continue
        vals = [v.params[2] for v in obj.water_verts]
        avg = sum(vals)/len(vals) if vals else 0
        mat = shallow if avg < threshold else deep
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        obj.show_transparent = True

class IMPORT_OT_water_dat(bpy.types.Operator):
    bl_idname = "import_scene.water_dat"
    bl_label = "Load water.dat"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        faces = parse_water_dat(self.filepath)
        if not faces:
            self.report({'ERROR'}, "No water zones found in file.")
            return {'CANCELLED'}
        colname = 'WaterIO'
        if colname in bpy.data.collections:
            old = bpy.data.collections[colname]
            for o in old.objects:
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(old)
        col = bpy.data.collections.new(colname)
        context.scene.collection.children.link(col)
        for i, (coords, params) in enumerate(faces):
            mesh = bpy.data.meshes.new(f'Zone_{i}')
            obj = bpy.data.objects.new(f'Zone_{i}', mesh)
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
                v = obj.water_verts.add()
                v.params = p
        color_code_collection(col, context.scene.shallow_threshold)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class EXPORT_OT_water_dat(bpy.types.Operator):
    bl_idname = "export_scene.water_dat"
    bl_label = "Export water.dat"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        zones = [o for o in context.selected_objects if getattr(o, 'is_water', False)]
        if not zones:
            self.report({'ERROR'}, "Select water zone objects to export.")
            return {'CANCELLED'}
        lines = ['processed']
        for o in zones:
            coords = [o.matrix_world @ v.co for v in o.data.vertices]
            params = [v.params for v in o.water_verts]
            parts = [f"{c.x:.1f} {c.y:.1f} {c.z:.5f} {p[0]:.5f} {p[1]:.5f} {p[2]:.5f} {p[3]:.5f}" for c, p in zip(coords, params)]
            lines.append('    '.join(parts) + '    1')
        with open(self.filepath, 'w') as f:
            for l in lines:
                f.write(l + "\n")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class FIX_OT_water_zone(bpy.types.Operator):
    bl_idname = "water_io.fix_zone"
    bl_label = "Fix Zone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        fixed_count = 0
        threshold = context.scene.fix_threshold
        for o in context.selected_objects:
            if not getattr(o, 'is_water', False):
                continue
            area = sum(p.area for p in o.data.polygons)
            if area < threshold:
                bpy.data.objects.remove(o, do_unlink=True)
                fixed_count += 1
        self.report({'INFO'}, f"Fixed {fixed_count} zone(s) (removed small zones below threshold)")
        return {'FINISHED'}

class VIEW3D_PT_water_io(bpy.types.Panel):
    bl_label = "Water IO"
    bl_idname = "VIEW3D_PT_water_io"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Water IO'

    def draw(self, context):
        layout = self.layout
        layout.operator(IMPORT_OT_water_dat.bl_idname)
        layout.operator(EXPORT_OT_water_dat.bl_idname)
        layout.operator(FIX_OT_water_zone.bl_idname)

class OBJECT_PT_water_params(bpy.types.Panel):
    bl_label = "Water Params"
    bl_idname = "OBJECT_PT_water_params"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return getattr(context.object, 'is_water', False)

    def draw(self, context):
        obj = context.object
        layout = self.layout
        layout.prop(obj, 'is_water')
        for i, v in enumerate(obj.water_verts):
            layout.prop(v, 'params', text=f"V{i+1}")

class SCENE_PT_water_opts(bpy.types.Panel):
    bl_label = "Water Options"
    bl_idname = "SCENE_PT_water_opts"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'shallow_threshold')
        layout.prop(context.scene, 'fix_threshold')

def update_is_water(self, context):
    obj = context.object
    if not obj or obj.type != 'MESH':
        return
    cnt = len(obj.data.vertices)
    while len(obj.water_verts) < cnt:
        obj.water_verts.add()
    while len(obj.water_verts) > cnt:
        obj.water_verts.remove(len(obj.water_verts) - 1)

classes = [
    WaterVertex,
    IMPORT_OT_water_dat,
    EXPORT_OT_water_dat,
    FIX_OT_water_zone,
    VIEW3D_PT_water_io,
    OBJECT_PT_water_params,
    SCENE_PT_water_opts
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Object.is_water = BoolProperty(default=False, update=update_is_water)
    bpy.types.Object.water_verts = CollectionProperty(type=WaterVertex)
    bpy.types.Scene.shallow_threshold = FloatProperty(
        name="Shallow Thresh", default=0.5, min=0, max=2)
    bpy.types.Scene.fix_threshold = FloatProperty(
        name="Fix Thresh", default=0.01, min=0, description="Remove zones below this area threshold")


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Object.is_water
    del bpy.types.Object.water_verts
    del bpy.types.Scene.shallow_threshold
    del bpy.types.Scene.fix_threshold

if __name__ == '__main__':
    register()
