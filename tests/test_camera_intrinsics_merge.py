from blender_slam_data_export import camera
import unittest
import importlib
import os
import sys
import numpy as np

git_root_dir = os.path.join(os.path.dirname(__file__), "..")
if git_root_dir not in sys.path:
    sys.path.append(git_root_dir)


class TestCameraIntrinsicsMerge(unittest.TestCase):
    # an impossible matrix of camera parameters
    # that is good enough for the tests
    K = np.random.random((3, 3))
    k1 = camera.CameraIntrinsics(K, 1920, 1080)
    k2 = camera.CameraIntrinsics(K * 2, 1920, 1080)
    k3 = camera.CameraIntrinsics(K, 1920, 512)
    k4 = camera.CameraIntrinsics(K, 512, 1080)

    def all_same_intrinsics(self):
        data = [self.k1 for i in range(4)]
        container = camera.CameraIntrinsicsContainer()
        container.add_intrinsic_list(data)
        self.assertEqual(len(container.dict), 1)
        self.assertEqual(container.map_idx_id, [0, 0, 0, 0])

    def all_different_intrinsics(self):
        data = [self.k1, self.k2, self.k3, self.k4]
        container = camera.CameraIntrinsicsContainer()
        container.add_intrinsic_list(data)
        self.assertEqual(len(container.dict), 4)
        self.assertEqual(container.map_idx_id, [0, 1, 2, 3])

    def add_one_by_one(self):
        data = [self.k1, self.k2, self.k3, self.k4]
        container = camera.CameraIntrinsicsContainer()

        id = container.add_intrinsic(self.k1)
        self.assertEqual(container.map_idx_id, [0])
        self.assertEqual(len(container.dict), 1)
        self.assertEqual(id, 0)

        id = container.add_intrinsic(self.k1)
        self.assertEqual(container.map_idx_id, [0, 0])
        self.assertEqual(len(container.dict), 1)
        self.assertEqual(id, 0)

        id = container.add_intrinsic(self.k2)
        self.assertEqual(container.map_idx_id, [0, 0, 1])
        self.assertEqual(len(container.dict), 2)
        self.assertEqual(id, 1)

        id = container.add_intrinsic(self.k3)
        self.assertEqual(container.map_idx_id, [0, 0, 1, 2])
        self.assertEqual(len(container.dict), 3)
        self.assertEqual(id, 2)

        id = container.add_intrinsic(self.k1)
        self.assertEqual(container.map_idx_id, [0, 0, 1, 2, 0])
        self.assertEqual(len(container.dict), 3)
        self.assertEqual(id, 0)


if __name__ == "__main__":
    TestCameraIntrinsicsMerge().all_same_intrinsics()
    TestCameraIntrinsicsMerge().all_different_intrinsics()
    TestCameraIntrinsicsMerge().add_one_by_one()
