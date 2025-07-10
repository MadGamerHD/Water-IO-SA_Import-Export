bl_info = {
    "name": "Water IO V1.4.0",
    "author": "MadGamerHD",
    "version": (1, 4, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Water IO",
    "description": "Import/export GTA San Andreas water.dat with editable water zones, color-coded shallow/deep, and manual zone creation",
    "category": "Import-Export",
}

import bpy
import bmesh
import re
from mathutils import Vector
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    FloatVectorProperty,
    FloatProperty,
)
from bpy.types import Operator, Panel, PropertyGroup

# -------------------------------------------------------------------------
# Property Group for per-vertex parameters
# -------------------------------------------------------------------------
class WaterVertex(PropertyGroup):
    params: FloatVectorProperty(
        name="Params (p0–p3)",
        size=4,
        default=(0.0, 0.0, 0.0, 0.0),
        precision=4,
        description="Vertex-specific parameters"
    )

# -------------------------------------------------------------------------
# Utilities: Material creation & color coding
# -------------------------------------------------------------------------
def ensure_material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Alpha'].default_value = color[3]
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'NONE'
    return mat


def color_code_zone(obj, threshold):
    depths = [v.params[2] for v in obj.water_verts]
    avg_depth = sum(depths) / len(depths) if depths else 0
    name = 'WaterShallow' if avg_depth < threshold else 'WaterDeep'
    color = (0.2, 0.6, 1.0, 0.5) if name == 'WaterShallow' else (0.0, 0.1, 0.6, 0.5)
    mat = ensure_material(name, color)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.show_transparent = True

# Ensure vertex collection matches mesh

def update_vert_collection(self, context):
    obj = context.object
    if obj and obj.type == 'MESH':
        cnt = len(obj.data.vertices)
        while len(obj.water_verts) < cnt:
            obj.water_verts.add()
        while len(obj.water_verts) > cnt:
            obj.water_verts.remove(len(obj.water_verts)-1)

# -------------------------------------------------------------------------
# Parsing water.dat
# -------------------------------------------------------------------------
def parse_water_dat(path):
    zones = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.split(';')[0].strip()
            if not line or line.startswith('#') or line.lower().startswith('processed'):
                continue
            parts = [p for p in re.split(r"[\s,]+", line) if p]
            if len(parts) not in (22, 29):
                continue
            verts = 3 if len(parts) == 22 else 4
            coords, params = [], []
            for i in range(verts):
                base = i*7
                x,y,z = map(float, parts[base:base+3])
                p = list(map(float, parts[base+3:base+7]))
                coords.append((x,y,z))
                params.append(p)
            zones.append((coords, params))
    return zones

# -------------------------------------------------------------------------
# Operators: Load, Export, Create, Fix, Flatten, Reset
# -------------------------------------------------------------------------
class WATER_OT_Load(Operator):
    bl_idname = 'water_io.load'
    bl_label = 'Load water.dat'
    bl_options = {'REGISTER','UNDO'}
    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        zones = parse_water_dat(self.filepath)
        if not zones:
            self.report({'ERROR'}, 'No zones found.')
            return {'CANCELLED'}
        # clear existing
        if col := bpy.data.collections.get('WaterIO'):
            for o in col.objects: bpy.data.objects.remove(o, do_unlink=True)
            bpy.data.collections.remove(col)
        col = bpy.data.collections.new('WaterIO')
        context.scene.collection.children.link(col)
        for i,(coords,params) in enumerate(zones):
            mesh = bpy.data.meshes.new(f'Zone_{i:03d}')
            mesh.from_pydata(coords, [], [list(range(len(coords)))])
            mesh.update()
            obj = bpy.data.objects.new(f'Zone_{i:03d}', mesh)
            col.objects.link(obj)
            obj.is_water = True
            obj.water_verts.clear()
            for p in params: obj.water_verts.add().params = p
            color_code_zone(obj, context.scene.shallow_threshold)
        self.report({'INFO'}, f'Loaded {len(zones)} zones.')
        return {'FINISHED'}

    def invoke(self, context,event): context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}


class WATER_OT_Export(Operator):
    bl_idname = 'water_io.export'
    bl_label = 'Export water.dat'
    bl_options = {'REGISTER','UNDO'}
    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        zones = [o for o in context.selected_objects if o.is_water]
        if not zones:
            self.report({'ERROR'}, 'No zones selected.')
            return {'CANCELLED'}
        lines=['processed']
        for o in zones:
            for co,vert in zip((o.matrix_world @ v.co for v in o.data.vertices), o.water_verts):
                p=vert.params
                lines.append(f"{co.x:.1f} {co.y:.1f} {co.z:.5f} {p[0]:.5f} {p[1]:.5f} {p[2]:.5f} {p[3]:.5f} 1")
        open(self.filepath,'w',encoding='utf-8').write("\n".join(lines))
        self.report({'INFO'}, f'Exported {len(zones)} zones.')
        return {'FINISHED'}
    def invoke(self, context,event): context.window_manager.fileselect_add(self); return {'RUNNING_MODAL'}


class WATER_OT_CreateZone(Operator):
    bl_idname = 'water_io.create_zone'
    bl_label = 'Create New Zone'
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        mesh=bpy.data.meshes.new('NewZone')
        bm=bmesh.new()
        bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=5)
        bm.to_mesh(mesh); bm.free()
        obj=bpy.data.objects.new('WaterZone',mesh)
        context.collection.objects.link(obj)
        obj.is_water=True; obj.water_verts.clear()
        for v in obj.data.vertices: obj.water_verts.add().params = (0,0,0,0)
        color_code_zone(obj,context.scene.shallow_threshold)
        self.report({'INFO'},'Zone created.')
        return {'FINISHED'}


class WATER_OT_Fix(Operator):
    bl_idname = 'water_io.fix'
    bl_label = 'Remove Small Zones'
    bl_options = {'REGISTER','UNDO'}
    def execute(self,context):
        rem=0;thr=context.scene.fix_threshold
        for o in list(context.selected_objects):
            if o.is_water and sum(p.area for p in o.data.polygons)<thr:
                bpy.data.objects.remove(o,do_unlink=True); rem+=1
        self.report({'INFO'},f'Removed {rem} zones.')
        return {'FINISHED'}


class WATER_OT_Flatten(Operator):
    bl_idname='water_io.flatten'
    bl_label='Flatten Zone'
    bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        o=context.object
        if not getattr(o,'is_water',False): self.report({'ERROR'},'No zone'); return {'CANCELLED'}
        avg=sum(v.co.z for v in o.data.vertices)/len(o.data.vertices)
        for v in o.data.vertices: v.co.z=avg
        o.data.update()
        self.report({'INFO'},f'Flattened {o.name}')
        return {'FINISHED'}


class WATER_OT_Reset(Operator):
    bl_idname='water_io.reset'
    bl_label='Reset Params'
    bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        o=context.object
        if getattr(o,'is_water',False):
            for v in o.water_verts: v.params=(0,0,0,0)
            self.report({'INFO'},f'Reset {o.name}')
            return {'FINISHED'}
        return {'CANCELLED'}

# -------------------------------------------------------------------------
# UI Panel
# -------------------------------------------------------------------------
class WATER_PT_Panel(Panel):
    bl_label='Water IO'
    bl_idname='VIEW3D_PT_water_io'
    bl_space_type='VIEW_3D'
    bl_region_type='UI'
    bl_category='Water IO'
    def draw(self,context):
        L=self.layout;S=context.scene
        L.operator('water_io.load',icon='IMPORT')
        L.operator('water_io.export',icon='EXPORT')
        L.operator('water_io.create_zone',icon='MESH_GRID')
        L.separator()
        box=L.box();box.label(text='Settings')
        box.prop(S,'shallow_threshold')
        box.prop(S,'fix_threshold')
        L.separator()
        row=L.row(align=True)
        row.operator('water_io.fix')
        row.operator('water_io.flatten')
        row.operator('water_io.reset')

# -------------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------------
classes=[WaterVertex,
         WATER_OT_Load,WATER_OT_Export,WATER_OT_CreateZone,
         WATER_OT_Fix,WATER_OT_Flatten,WATER_OT_Reset,
         WATER_PT_Panel]

def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.Object.is_water=BoolProperty(default=False,update=update_vert_collection)
    bpy.types.Object.water_verts=CollectionProperty(type=WaterVertex)
    bpy.types.Scene.shallow_threshold=FloatProperty(name='Shallow Threshold',default=0.5,min=0)
    bpy.types.Scene.fix_threshold=FloatProperty(name='Fix Threshold',default=0.01,min=0)

def unregister():
    for c in reversed(classes): bpy.utils.unregister_class(c)
    del bpy.types.Object.is_water
    del bpy.types.Object.water_verts
    del bpy.types.Scene.shallow_threshold
    del bpy.types.Scene.fix_threshold

if __name__=='__main__': register()
