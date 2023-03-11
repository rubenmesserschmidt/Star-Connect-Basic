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
    'doc_url': 'https://star-connect.readthedocs.io/en/latest/',
}

bl_info['blender'] = getattr(bpy.app, "version")


import bmesh
import rna_keymap_ui
import webbrowser
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
        kmi = km.keymap_items.new('scb.star_connect', type='S', value='PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))


def del_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()



##### Operators #####


class SCB_OT_OpenLink(Operator):
    bl_idname='scb.open_link'
    bl_label=''

    link: bpy.props.StringProperty()

    def execute(self, context):
        webbrowser.open_new_tab(self.link)
        return {'FINISHED'}



class SCB_OT_StarConnect(Operator):
    bl_idname = 'scb.star_connect'
    bl_label = 'Star Connect'
    bl_options = {'UNDO', 'REGISTER'}


    def invoke(self, context, event):
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

    show_menu: bpy.props.BoolProperty(
        name='Show Menu',
        default=True,
        description='Show operator in edit mode context menu'
    )

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout
        col = layout.column()
        split = col.split()
        sub = split.column()
        sub.label(text='Show Menu')
        sub = split.column()
        sub.prop(self, 'show_menu', text='')
        col.separator()
        row = col.row()
        sub = row.column()
        sub.enabled = False
        sub.label(text='Keybinds')

        col = layout.column()

        # draw keymap
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        old_id_l = []

        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:

                    if not kmi_con.id in old_id_l:
                        kmi = kmi_con
                        old_id_l.append(kmi_con.id)
                        break

            try:
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                col.separator()

            except:
                pass

        layout.separator()
        sub = layout.column()
        sub.enabled = False
        sub.label(text='Upgrade')
        col = layout.column()
        split = col.split()
        sub = split.column()
        sub.scale_y = 1.5
        sub.label(text='Get Star Connect Pro')

        sub = split.column()
        sub.scale_y = 1.5
        sub.operator('scb.open_link', text='Upgrade to Pro').link = 'https://blendermarket.com/products/starconnect'


##### Draw Functions #####


def draw_VIEW3D_MT_edit_mesh_context_menu(self, context):
    if not bpy.context.preferences.addons['Star Connect Basic'].preferences.show_menu:
        return
    
    layout: bpy.types.UILayout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('scb.star_connect')



classes = [
    SCB_OT_StarConnect,
    SCB_AP_AddonPreferences,
    SCB_OT_OpenLink
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

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(draw_VIEW3D_MT_edit_mesh_context_menu)

    init_keymap()


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(draw_VIEW3D_MT_edit_mesh_context_menu)

    for cls in registered_classes:
        bpy.utils.unregister_class(cls)

    registered_classes.clear()

    del_keymap()


if __name__ == "__main__":
    register()