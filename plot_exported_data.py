import cv2
import sys
import os
import importlib
import numpy as np

blend_dir = os.path.join(os.path.dirname(__file__),"blender_slam_data_export")
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

import colmap_io as colmap

path = "/tmp/"
cameras, images, points_3d = colmap.read_model(path, ".txt")


def qvec2rotmat(qvec):
    return np.array(
        [
            [
                1 - 2 * qvec[2] ** 2 - 2 * qvec[3] ** 2,
                2 * qvec[1] * qvec[2] - 2 * qvec[0] * qvec[3],
                2 * qvec[3] * qvec[1] + 2 * qvec[0] * qvec[2],
            ],
            [
                2 * qvec[1] * qvec[2] + 2 * qvec[0] * qvec[3],
                1 - 2 * qvec[1] ** 2 - 2 * qvec[3] ** 2,
                2 * qvec[2] * qvec[3] - 2 * qvec[0] * qvec[1],
            ],
            [
                2 * qvec[3] * qvec[1] - 2 * qvec[0] * qvec[2],
                2 * qvec[2] * qvec[3] + 2 * qvec[0] * qvec[1],
                1 - 2 * qvec[1] ** 2 - 2 * qvec[2] ** 2,
            ],
        ]
    )


for image_id, image_data in images.items():

    camera = cameras[image_data.camera_id]

    # --- get the image

    image_file = os.path.join(path, image_data.name)
    image = None
    if os.path.exists(image_file):
        image = cv2.imread(image_file)
    else:
        w, h = camera.width, camera.height
        image = np.zeros((h, w, 3), np.uint8)

    # --- get intrinsics matrix

    params = camera.params
    fx, fy, cx, cy = params
    K = np.matrix([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)

    # --- get extrinsics matrix

    R = qvec2rotmat(image_data.qvec)
    t = np.array(image_data.tvec[:, None])
    T = np.hstack((R, t))

    # --- get camera matrix

    P = K.dot(T)

    # --- get reprojection error (in px)

    errors = []
    points_2d = []
    points_2d_projected = []

    for pt, pt_3d_idx in zip(image_data.xys, image_data.point3D_ids):
        x, y, z = points_3d[pt_3d_idx].xyz
        pt_estimated = P.dot(np.array([x, y, z, 1]).T)

        q = np.array(pt[:, None]).T
        q_est = pt_estimated[0, 0:2] / pt_estimated[0, 2]

        reproj_error = np.linalg.norm(q - q_est)
        errors.append(reproj_error)

        points_2d.append((int(q[0, 0]), int(q[0, 1])))
        points_2d_projected.append((int(q_est[0, 0]), int(q_est[0, 1])))

    print("Reprojection error (%i pts):" % len(errors))
    print(" - mean: %d (px)" % np.mean(errors))
    print(" - std: %d (px)" % np.std(errors))

    # --- plot the image with points

    for pt, projection in zip(points_2d, points_2d_projected):
        # plot keypoints and projected 3d points
        cv2.circle(image, pt, 3, (0, 0, 255), -1)
        cv2.circle(image, projection, 2, (255, 0, 0), -1)

    cv2.namedWindow("image")
    cv2.imshow("image", image)
    cv2.waitKeyEx()
