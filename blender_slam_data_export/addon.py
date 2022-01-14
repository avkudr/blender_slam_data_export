import bpy
import collections
import os

from . import export
from . import camera

ADDON_GLOBAL_DATA = {"points_2d": {}, "points_3d": {}}


class SlamDataExporter(bpy.types.Operator):
    """Export SLAM data (projected vertices, camera intrinsics and extrinsics, 3D points)"""

    bl_idname = "render.save_slam_data"
    bl_label = "Save SLAM data"
    bl_icon = "EXPORT"

    def ensure_object_mode(self):
        if bpy.context.mode == "OBJECT":
            return

        if not bpy.ops.object.mode_set.poll():
            raise Exception("Can't switch to object mode")
            
        bpy.ops.object.mode_set(mode="OBJECT")

    def get_frame_indices(self):
        """
        Frame indices of the playback/rendering range
        """
        scene = bpy.context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end  # included in animation
        frame_step = scene.frame_step

        return [*range(frame_start, frame_end + 1, frame_step)]

    def get_render_output_path(self):
        output_dir = bpy.context.scene.render.filepath
        if not os.path.exists(output_dir):
            raise Exception(
                (
                    "Output Properties > Output Path must be a directory."
                    "Actual: %s" % output_dir
                )
            )

        return output_dir

    def go_to_frame(self, frame):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()

    def render_image(self, output_dir, image_name):
        old_format = bpy.context.scene.render.image_settings.file_format
        old_path = bpy.context.scene.render.filepath

        new_path = os.path.join(output_dir, image_name)
        bpy.context.scene.render.filepath = new_path
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(write_still=True)

        bpy.context.scene.render.filepath = old_path
        bpy.context.scene.render.image_settings.file_format = old_format

        return new_path

    def set_render_engine(self, engine):
        bpy.context.scene.render.engine = engine

    def set_export_render_engine(self):
        bpy.context.scene.render.engine = "CUSTOM_SLAM_data_exporter"

    def execute(self, context):
        self.report({'INFO'}, "SLAM data export... started")

        scene = bpy.context.scene
        self.ensure_object_mode()

        frame_indices = self.get_frame_indices()

        original_render_engine = bpy.context.scene.render.engine

        try:
            all_data = {}
            all_data["points_3d"] = {}
            all_data["frames"] = {}
            all_data["cameras"] = camera.CameraIntrinsicsContainer()

            output_dir = self.get_render_output_path()
            output_image_dir = "images"
            if scene.slam_export_render_images:
                os.makedirs(os.path.join(output_dir, output_image_dir), exist_ok=True)


            for frame_idx in frame_indices:
                self.go_to_frame(frame_idx)

                image_name = output_image_dir + ("/image_%d.png" % frame_idx)
                intr = camera.get_camera_intrinsics(scene.camera, scene)
                pose = camera.get_camera_pose(scene.camera)

                self.set_export_render_engine()
                bpy.ops.render.render(write_still=False)

                points_2d = ADDON_GLOBAL_DATA["points_2d"]
                points_3d = ADDON_GLOBAL_DATA["points_3d"]

                # points_2d = camera.project_point(scene, all_data["points_3d"])

                all_data["points_3d"] = {**all_data["points_3d"], **points_3d}
                camera_id = all_data["cameras"].add_intrinsic(intr)
                all_data["frames"][frame_idx] = {
                    "image_name": image_name,
                    "camera_id": camera_id,
                    "pose": pose,
                    "points_2d": points_2d,
                }

                if scene.slam_export_render_images:
                    self.set_render_engine(original_render_engine)
                    self.render_image(output_dir, image_name)

            all_data["id_to_idx"] = {
                id: idx for idx, (id, v) in enumerate(all_data["points_3d"].items())
            }
            export.export_data(all_data, path=self.get_render_output_path())

        except Exception as e: 
            self.set_render_engine(original_render_engine)
            self.report({'ERROR'}, "SLAM data export... failed:\n %s" % e)
            return {"CANCELLED"}

        self.report({'INFO'}, "SLAM data export... done")
        return {"FINISHED"}
