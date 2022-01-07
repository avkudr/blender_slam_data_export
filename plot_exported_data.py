import cv2
import sys
import os
import importlib
import numpy as np

module_path = os.path.join(os.path.abspath(os.getcwd()),"blender-slam-data-export/colmap_io.py")

import importlib.util
spec = importlib.util.spec_from_file_location("*", module_path)
colmap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colmap)

path = "/tmp/blender_addon/"
cameras, images, points3D = colmap.read_model(path, ".txt")

for image_id, image_data in images.items():
    image_file = os.path.join(path, image_data.name)

    image = np.zeros((1080,1920,3), np.uint8) #cv2.imread(image_file)
    
    points_2d = image_data.xys
    for pt in points_2d:
        cv2.circle(image,(int(pt[0]),int(pt[1])), 2, (0,0,255), -1)

    cv2.namedWindow("image")
    cv2.imshow("image", image)
    cv2.waitKeyEx()