import sys
import bpy

def select_scene(scene_name):
    if scene_name not in bpy.data.scenes:
        raise Exception("No scene with the name %s" % scene_name)

    scene = bpy.data.scenes[scene_name]
    bpy.context.window.scene = scene
    return scene


def select_camera(camera_name):
    if camera_name not in bpy.data.objects:
        raise Exception("No camera with the name %s" % camera_name)

    camera = bpy.data.objects[camera_name]
    if not isinstance(camera.data, bpy.types.Camera):
        raise Exception(
            "Object with name %s is not a camera (%s)" % (camera_name, type(camera.data))
        )

    bpy.context.scene.camera = camera
    return camera

class ProgressBar:
    def __init__(self, total, suffix="", every=1):
        self.total = total
        self.suffix = suffix
        self.every = every

    def draw(self, count):
        if count % self.every or count == self.total - 1 or count == 0:
            bar_len = 60
            filled_len = int(round(bar_len * count / float(self.total)))

            percents = round(100.0 * count / float(self.total), 1)
            bar = "=" * filled_len + "-" * (bar_len - filled_len)

            sys.stdout.write("[%s] %s%s ...%s\r" % (bar, percents, "%", self.suffix))
            sys.stdout.flush()

    def __del__(self):
        print("\r")
