import unittest
import bpy
import importlib
import os
import sys
import numpy as np

np.set_printoptions(precision=5)

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

git_root_dir = os.path.join(os.path.dirname(bpy.data.filepath), "..")
if git_root_dir not in sys.path:
    sys.path.append(git_root_dir)

import common
import blender_slam_data_export


class TestCameraIntrinsics(unittest.TestCase):
    def test_camera_30mm(self):
        scene = common.select_scene("Scene1920x1080")
        camera = common.select_camera("Camera_30mm.A")

        self.assertEqual(camera.data.lens, 30)

        K, w, h = blender_slam_data_export.camera.get_camera_intrinsics(camera, scene)

        K_expected = np.matrix(
            [
                [1.6e03, 0.0e00, 9.6e02],
                [0.0e00, 1.6e03, 5.4e02],
                [0.0e00, 0.0e00, 1.0e00],
            ]
        )

        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)
        np.testing.assert_array_almost_equal(K, K_expected, decimal=3)

    def test_camera_50mm(self):
        scene = common.select_scene("Scene1920x1080")
        camera = common.select_camera("Camera_50mm.A")

        self.assertEqual(camera.data.lens, 50)

        K, w, h = blender_slam_data_export.camera.get_camera_intrinsics(camera, scene)

        K_expected = np.matrix(
            [
                [2.666667e03, 0.000000e00, 9.600000e02],
                [0.000000e00, 2.666667e03, 5.400000e02],
                [0.000000e00, 0.000000e00, 1.000000e00],
            ]
        )

        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)
        np.testing.assert_array_almost_equal(K, K_expected, decimal=3)


if __name__ == "__main__":
    TestCameraIntrinsics().test_camera_30mm()
    TestCameraIntrinsics().test_camera_50mm()
