import bpy


def select_scene(scene_name):
    if scene_name not in bpy.data.scenes:
        raise Exception("No scene with the name %s" % scene_name)

    bpy.context.window.scene = bpy.data.scenes[scene_name]


def select_camera(camera_name):
    if camera_name not in bpy.data.objects:
        raise Exception("No camera with the name %s" % camera_name)

    camera = bpy.data.objects[camera_name]
    if not isinstance(camera.data, bpy.types.Camera):
        raise Exception(
            "Object with name %s is not a camera (%s)" % (camera_name, type(camera.data))
        )

    bpy.context.scene.camera = camera
