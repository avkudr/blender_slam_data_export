import bpy

from . import addon
from . import camera

class VertexRayCastEngine(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = "CUSTOM_SLAM_data_exporter"
    bl_label = "SLAM data exporter"
    bl_use_preview = False

    # Init is called whenever a new render engine instance is created. Multiple
    # instances may exist at the same time, for example for a viewport and final
    # render.
    def __init__(self):
        self.scene_data = None
        self.draw_data = None
        self.points_2d = {}
        self.count = 0

    # When the render engine instance is destroy, this is called. Clean up any
    # render engine data here, for example stopping running render threads.
    def __del__(self):
        pass

    # This is the method called by Blender for both final renders (F12) and
    # small preview for materials, world and lights.
    def render(self, depsgraph):
        scene = depsgraph.scene
        
        points_3d = {}
        for object_instance in depsgraph.object_instances:
            obj = object_instance.object

            if obj.type != "MESH":
                continue
            obj_eval = obj.evaluated_get(depsgraph)

            vertices_dict = {obj.name + '.' + str(v.index): obj.matrix_world @ v.co for v in obj_eval.data.vertices}
            points_3d = {**points_3d, **vertices_dict}

        points_2d = camera.project_point(scene, depsgraph, points_3d)

        addon.ADDON_GLOBAL_DATA['points_2d'] = points_2d
        addon.ADDON_GLOBAL_DATA['points_3d'] = points_3d

        
    def view_update(self, context, depsgraph):
        pass

    def get_projected_vertices(self):
        return self.count

    def view_draw(self, context, depsgraph):
        pass