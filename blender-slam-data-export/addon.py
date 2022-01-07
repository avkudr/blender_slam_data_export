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
        if bpy.context.mode == 'OBJECT':
            return

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
        bpy.context.view_layer.update()

    def get_all_vertices(self):
        """
        Returns a dictionary with objects and their respective vertices
        in world coordinates
        """
        points_3d = {}
        depsgraph = bpy.context.evaluated_depsgraph_get()

        for obj in bpy.context.scene.objects:
            if obj.type != "MESH":
                continue
            if obj.hide_viewport or obj.hide_render:
                continue

            obj_eval = obj.evaluated_get(depsgraph)
            vertices_dict = {obj.name + '.' + str(v.index): obj.matrix_world @ v.co for v in obj_eval.data.vertices}
            points_3d = {**points_3d, **vertices_dict} # merge dictionaries vertices_dict

        return points_3d


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

        all_data = {}
        all_data["points_3d"] = self.get_all_vertices()
        all_data["frames"] = {}

        output_dir = self.get_render_output_path()
        output_image_dir = "images"
        if scene.slam_export_render_images:
            os.makedirs(os.path.join(output_dir, output_image_dir), exist_ok = True)

        for frame_idx in frame_indices:
            print('Processing frame ', frame_idx)
            self.go_to_frame(frame_idx)

            camera_id = frame_idx
            image_name = output_image_dir + ("/image_%d.png" % camera_id)
            intr = camera.get_camera_intrinsics(scene)
            pose = camera.get_camera_pose(scene)

            points_2d = camera.project_point(scene, all_data["points_3d"])

            all_data["frames"][camera_id] = {
                "image_name": image_name,
                "intrinsics": intr,
                "pose": pose,
                "points_2d": points_2d
            }

            if scene.slam_export_render_images:
                self.render_image(output_dir, image_name)


        all_data["id_to_idx"] = {id: idx for idx,(id,v) in enumerate(all_data["points_3d"].items())}
        export.export_data(all_data, path=self.get_render_output_path())

        print('Done')
        return {'FINISHED'}
