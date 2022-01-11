import unittest
import bpy
import importlib
import os
import sys
import numpy as np

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

git_root_dir = os.path.join(os.path.dirname(bpy.data.filepath), "..")
if git_root_dir not in sys.path:
    sys.path.append(git_root_dir)

import blender_slam_data_export


class TestCameraIntrinsics(unittest.TestCase):
    def test_camera_30mm(self):
        scene = blender_slam_data_export.utils.select_scene("Scene1920x1080")
        camera = blender_slam_data_export.utils.select_camera("Camera_30mm.A")

        self.assertEqual(camera.data.lens, 30)
        self.assertEqual(camera.data.sensor_width, 36)

        K, w, h = blender_slam_data_export.camera.get_camera_intrinsics(camera, scene)

        K_expected = np.matrix(
            [
                [1600, 0.0, w / 2],
                [0.0, 1600, h / 2],
                [0.0, 0.0, 1.0],
            ]
        )

        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)
        np.testing.assert_array_almost_equal(K, K_expected, decimal=3)

    def test_camera_50mm(self):
        scene = blender_slam_data_export.utils.select_scene("Scene1920x1080")
        camera = blender_slam_data_export.utils.select_camera("Camera_50mm.A")

        self.assertEqual(camera.data.lens, 50)
        self.assertEqual(camera.data.sensor_width, 36)

        K, w, h = blender_slam_data_export.camera.get_camera_intrinsics(camera, scene)

        K_expected = np.matrix(
            [
                [2666.6667, 0.0, w / 2],
                [0.0, 2666.6667, h / 2],
                [0.0, 0.0, 1.0],
            ]
        )

        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)
        np.testing.assert_array_almost_equal(K, K_expected, decimal=3)


if __name__ == "__main__":
    TestCameraIntrinsics().test_camera_30mm()
    TestCameraIntrinsics().test_camera_50mm()
