import bpy
import collections
import os

from . import export
from . import camera


class SlamDataExporter(bpy.types.Operator):
    """Export SLAM data (projected vertices, camera intrinsics and extrinsics, 3D points)"""
    bl_idname = "render.save_slam_data"
    bl_label = "Save SLAM data"
    bl_icon = 'EXPORT'

    def ensure_object_mode(self):
        assert bpy.ops.object.mode_set.poll()
        bpy.ops.object.mode_set(mode='OBJECT')


    def get_frame_indices(self):
        """
        Frame indices of the playback/rendering range
        """
        scene = bpy.context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end      #included in animation
        frame_step = scene.frame_step

        return [*range(frame_start, frame_end+1, frame_step)]


    def get_render_output_path(self):
        output_dir = bpy.context.scene.render.filepath
        if not os.path.exists(output_dir):
            raise Exception((
                "Output Properties > Output Path must be a directory."
                "Actual: %s" % output_dir
            ))

        return output_dir


    def go_to_frame(self, frame):
        bpy.context.scene.frame_set(frame)


    def build_depsgraphs(self):
        """
        Returns a dictionary with objects and their respective vertices
        in world coordinates

        More about dependency graphs: https://wiki.blender.org/wiki/Source/Depsgraph
        """
        points_3d = {}
        depsgraph = bpy.context.evaluated_depsgraph_get()

        # each vertex (3d point) gets a unique id (integer)
        # .. this works only if, during animation, there are no new objects entering
        # the scene. \todo the approach has to be revised
        cnt = 0

        for obj in bpy.context.scene.objects:
            if obj.type != "MESH":
                continue
            if obj.hide_render:
                continue

            obj_eval = obj.evaluated_get(depsgraph)
            verts = [obj.matrix_world @ v.co for v in obj_eval.data.vertices]
            vertices_dict = {int(i + cnt): v  for i, v in enumerate(verts)}
            points_3d = {**points_3d, **vertices_dict} # merge dictionaries vertices_dict
            cnt = cnt + len(vertices_dict)


        return points_3d, depsgraph


    def render_image(self, output_dir, image_name):
        old_format = bpy.context.scene.render.image_settings.file_format
        old_path = bpy.context.scene.render.filepath

        new_path = os.path.join(output_dir, image_name)
        bpy.context.scene.render.filepath = new_path
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.ops.render.render(write_still = True)

        bpy.context.scene.render.filepath = old_path
        bpy.context.scene.render.image_settings.file_format = old_format

        return new_path


    def execute(self, context):
        scene = bpy.context.scene
        self.ensure_object_mode()

        frame_indices = self.get_frame_indices()

        # all meshes with all their vertices
        # the graph is needed for visibility check based on ray casting
        # And, it allows having vertices as if all the modifiers were applied
        points_3d, depsgraph = self.build_depsgraphs()

        all_data = {}
        all_data["points_3d"] = points_3d
        all_data["frames"] = {}

        output_dir = self.get_render_output_path()

        for frame_idx in frame_indices:
            print('Processing frame ', frame_idx)
            self.go_to_frame(frame_idx)

            camera_id = frame_idx
            image_name = ("image_%d.png" % camera_id)
            intr = camera.get_camera_intrinsics(scene)
            pose = camera.get_camera_pose(scene)

            points_2d = camera.project_point(scene, depsgraph, points_3d)

            all_data["frames"][camera_id] = {
                "image_name": image_name,
                "intrinsics": intr,
                "pose": pose,
                "points_2d": points_2d
            }

            if scene.slam_export_render_images:
                self.render_image(output_dir, image_name)

        export.export_data(all_data, path=self.get_render_output_path())

        print('Done')
        return {'FINISHED'}
