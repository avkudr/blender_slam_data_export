
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
import test_camera_intrinsics_merge

def suite():
    suite = unittest.TestSuite()
    suite.addTest(test_camera_intrinsics.TestCameraIntrinsics('test_camera_30mm'))
    suite.addTest(test_camera_intrinsics.TestCameraIntrinsics('test_camera_50mm'))
    suite.addTest(test_camera_intrinsics_merge.TestCameraIntrinsicsMerge('all_same_intrinsics'))
    suite.addTest(test_camera_intrinsics_merge.TestCameraIntrinsicsMerge('all_different_intrinsics'))
    suite.addTest(test_camera_intrinsics_merge.TestCameraIntrinsicsMerge('add_one_by_one'))

    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())