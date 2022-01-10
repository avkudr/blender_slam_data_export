import unittest
import bpy
import importlib
import os
import sys

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

addon_dir = os.path.join(os.path.dirname(bpy.data.filepath), '..', "blender-slam-data-export")
if addon_dir not in sys.path:
   sys.path.append(addon_dir)

import common
import camera

class TestCameraIntrinsics(unittest.TestCase):
    def test_camera_30mm(self):
        common.select_scene("Scene1920x1080")
        common.select_camera("Camera_30mm.A")

        self.assertTrue(True)

if __name__ == "__main__":
    TestCameraIntrinsics().test_camera_30mm() 
