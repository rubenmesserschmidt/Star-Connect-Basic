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


classes = [

]

registered_classes = []


##### Registration #####


def register():
    if bpy.app.version < (2, 93, 0):
        print('Star Connect Basic is not compatible with your current Blender version!')
        print('Upgrade to Blender 2.93.0 or later.')
        return

    for cls in classes:
        bpy.utils.register_class(cls)
        registered_classes.append(cls)


def unregister():
    for cls in registered_classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()