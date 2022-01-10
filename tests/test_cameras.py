
import unittest
import os
import bpy
import sys

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

git_root_dir = os.path.join(os.path.dirname(bpy.data.filepath), "..")
if git_root_dir not in sys.path:
    sys.path.append(git_root_dir)

import test_camera_intrinsics

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_camera_intrinsics.TestCameraIntrinsics('test_camera_30mm'))
    suite.addTest(test_camera_intrinsics.TestCameraIntrinsics('test_camera_50mm'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())