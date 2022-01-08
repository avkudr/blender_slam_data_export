import collections
import numpy as np
import sys

import bpy
import mathutils
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.object_utils import world_to_camera_view

from . import utils

CameraIntrinsics = collections.namedtuple(
     "CameraIntrinsics", ["K", "dist", "width", "height"])

CameraPose = collections.namedtuple(
     "CameraPose", ["q", "t"])

def get_camera_pose(scene):
     """
     Extract camera pose from the current scene for the current frame
     """
     camera = scene.camera

     cTw = camera.matrix_world.inverted()

     ctw = cTw.to_translation()
     cqw = cTw.to_quaternion().normalized()

     # for some reason, this rotation has to be applied for 
     # the correct visualization inside colmap gui
     qy = mathutils.Quaternion([0,0,1,0])

     t = qy.inverted() @ cTw.to_translation()
     q = qy @ cTw.to_quaternion().normalized()

     return CameraPose(q, t)


def get_camera_intrinsics(scene):
     """
     Extract camera intrinsic parameters from the current scene for the current frame
     """
     cam = scene.camera.data

     # assume angles describe the horizontal field of view
     assert cam.sensor_fit != 'VERTICAL'

     f_in_mm = cam.lens
     sensor_width_in_mm = cam.sensor_width

     scale = scene.render.resolution_percentage / 100
     w = scene.render.resolution_x * scale # px
     h = scene.render.resolution_y * scale # px

     pixel_aspect = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x

     f_x = f_in_mm / sensor_width_in_mm * w
     f_y = f_x * pixel_aspect

     # yes, shift_x is inverted. WTF blender?
     c_x = w * (0.5 - cam.shift_x)
     # and shift_y is still a percentage of width..
     c_y = h * 0.5 + w * cam.shift_y
          
     K = np.array([[f_x, 0, c_x],
          [0, f_y, c_y],
          [0,   0,   1]], dtype=np.float32)
          
     dist = np.array([0,0,0,0])
     return CameraIntrinsics(K, dist, w, h)


def is_in_camera_field_of_view(camera, pt_in_camera_frame):
     x,y,z = pt_in_camera_frame.x, pt_in_camera_frame.y, pt_in_camera_frame.z

     # If inside the camera view
     if  x < 0 or y < 0 or x > 1 or y > 1:
          return False

     if z < camera.data.clip_start or z > camera.data.clip_end:
          return False

     return True

def project_point(scene, depsgraph, vertices, limit=1e-4):
     # Threshold to test if ray cast corresponds to the original vertex
     
     camera = scene.camera

     points = {}

     resolution_x = bpy.context.scene.render.resolution_x
     resolution_y = bpy.context.scene.render.resolution_y
     
     camera_origin = camera.matrix_world.to_translation()

     cnt = 0
     
     suffix =' Frame %i/%i (%i verts)' % (scene.frame_current, scene.frame_end, len(vertices))
     progress_bar = utils.ProgressBar(len(vertices),suffix=suffix,every=200)

     count_processed = 0
     for id, v in vertices.items():     
          # Get the 2D projection of the vertex
          co2D = world_to_camera_view(scene, camera, v )

          # By default, deselect it
          #obj.data.vertices[i].select = False
          
          if is_in_camera_field_of_view(camera, co2D):          
               # Try a ray cast, in order to test the vertex visibility from the camera
               direction = (camera_origin - v).normalized()
               max_distance = (camera_origin - v).length # camera far clip
               
               # To avoid hitting the vertex itself we start the cast from some very
               # small offset towards the camera
               offset = 1e-4
               is_something_hit,_,_,_,_,_ = scene.ray_cast(depsgraph, v + offset * direction, direction, distance=max_distance )
               
               # if we are hitting nothing
               if is_something_hit == False:
                    # y axis is inverted in blender
                    points[id] = ([resolution_x * co2D.x, resolution_y * (1-co2D.y)], cnt)
                    cnt = cnt + 1     

          #if count_processed % 1 or count_processed == len(vertices) - 1:
          count_processed = count_processed + 1
          progress_bar.draw(count_processed)

     return points