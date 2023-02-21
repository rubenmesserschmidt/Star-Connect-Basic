# Star Connect Basic  Copyright (C) 2023  Ruben Messerschmidt

# Star Connect Basic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Star Connect Basic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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


##### Keymap #####


def init_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs
    if kc:
        km = kc.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(idname='scb.star_connect', type='S', value='PRESS', ctrl=True, alt=True)

    addon_keymaps.append((km, kmi))


def del_keymap():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            continue

    addon_keymaps.clear()


##### Operators #####


class SCB_OT_ResetKeymap(Operator):
    bl_idname = 'scb.reset_keymap'
    bl_label = 'Reset'

    def execute(self, context):
        del_keymap()
        init_keymap()
        return {'FINISHED'}



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
        col = layout.column()
        row = col.row()
        sub = row.column()
        sub.enabled = False
        sub.label(text='Keybinds')
        row.operator('scb.reset_keymap')

        col = layout.column()
        kc = context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col.separator()



classes = [
    SCB_OT_StarConnect,
    SCB_AP_AddonPreferences,
    SCB_OT_ResetKeymap
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

    init_keymap()


def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)

    del_keymap()


if __name__ == "__main__":
    register()