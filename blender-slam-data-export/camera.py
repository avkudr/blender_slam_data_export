import collections
import numpy as np

import bpy
import mathutils
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.object_utils import world_to_camera_view

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

def project_point(scene, vertices, limit=1e-4):
     # Threshold to test if ray cast corresponds to the original vertex
     
     camera = scene.camera

     points = {}

     depsgraph = bpy.context.evaluated_depsgraph_get()
     depsgraph.update()

     resolution_x = bpy.context.scene.render.resolution_x
     resolution_y = bpy.context.scene.render.resolution_y
     
     cnt = 0
     for id, v in vertices.items():     
          # Get the 2D projection of the vertex
          co2D = world_to_camera_view( scene, camera, v )

          # By default, deselect it
          #obj.data.vertices[i].select = False
          
          if not is_in_camera_field_of_view(camera, co2D):
               continue
          
          # Try a ray cast, in order to test the vertex visibility from the camera
          origin = camera.location
          direction = (v - origin).normalized()
          max_distance = (v - origin).length # camera far clip
          
          is_something_hit,location,_,_,_,_ = scene.ray_cast(depsgraph, origin, direction, distance=max_distance )
          
          # if we are hitting nothing or we are hitting the vertex itself
          if is_something_hit == False or (v - location).length < limit:
               # y axis is inverted in blender
               points[id] = ([resolution_x * co2D.x, resolution_y * (1-co2D.y)], cnt)
               cnt = cnt + 1     

          #if cnt % 50 == 0:
          #     print("processing vertex: ", id, len(vertices))
               
     return points