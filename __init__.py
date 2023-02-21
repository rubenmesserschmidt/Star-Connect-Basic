# This file is part of Star Connect Basic
# Copyright (C) 2023  Ruben Messerschmidt

import bpy


bl_info = {
    "name": "Star Connect Basic",
    "description": "",
    "blender": (2, 93, 0),
    "version": (1, 0, 0),
    "category": "",
    "author": "Ruben Messerschmidt",
    "location": "",
}

bl_info['blender'] = getattr(bpy.app, "version")


import bmesh
import rna_keymap_ui
from bpy.types import Operator, AddonPreferences


##### Functions #####


def get_active_vert(bm):
        if bm.select_history:
            elem = bm.select_history[-1]
            if isinstance(elem, bmesh.types.BMVert):
                return elem
        return None


##### Operators #####


class SCB_OT_StarConnect(Operator):
    bl_idname = 'scb.star_connect'
    bl_label = 'Star Connect'
    bl_options = {'UNDO'}

    def execute(self, context):
        mode = context.mode
        if mode != 'EDIT_MESH':
            self.report({'WARNING'}, message='Star Connect works only in Edit Mode!')

        objs = context.objects_in_mode
        for obj in objs:
            mesh = obj.data
            bm = bmesh.from_edit_mesh(mesh)
            active_vert = get_active_vert(bm)
            for v in [v for v in bm.verts if v.select and v is not active_vert]:
                bmesh.ops.connect_vert_pair(bm, verts=[v, active_vert])
            
            bmesh.update_edit_mesh(mesh)

        return {'FINISHED'}


##### Addon Preferences #####


class SCB_AP_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        row = layout.row()
        row.enabled = False
        row.label(text='Keybinds')

        col = layout.column()
        kc = context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col.separator()



classes = [
    SCB_OT_StarConnect,
    SCB_AP_AddonPreferences
]

registered_classes = []

addon_keymaps = []


##### Registration #####


def register():
    if bpy.app.version < (2, 93, 0):
        print('Star Connect Basic is not compatible with your current Blender version!')
        print('Upgrade to Blender 2.93.0 or later.')
        return

    for cls in classes:
        bpy.utils.register_class(cls)
        registered_classes.append(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs
    if kc:
        km = kc.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(idname='scb.star_connect', type='S', value='PRESS', ctrl=True, alt=True)

    addon_keymaps.append((km, kmi))


def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            continue

    addon_keymaps.clear()


if __name__ == "__main__":
    register()