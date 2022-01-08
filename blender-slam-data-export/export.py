import os
import collections

# see
# 1. http://colmap.github.io/format.html#text-format
# 2. https://github.com/colmap/colmap/blob/dev/scripts/python/read_write_model.py
#
from . import colmap_io as colmap


def export_points_3d(all_data, path):
    """
    3D point list with one line of data per point:
        POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)
    """
    points_3d = {}

    rgb = [255, 0, 0]
    error = 0

    id_to_idx = all_data["id_to_idx"]

    for id, pt3d in all_data["points_3d"].items():

        image_ids = []
        point2D_idxs = []
        for frame_idx, frame_data in all_data["frames"].items():
            assert "points_2d" in frame_data
            if id in frame_data["points_2d"]:
                image_ids.append(frame_idx)
                point2D_idxs.append(frame_data["points_2d"][id][1])

        if len(image_ids) == 0:
            continue

        points_3d[id_to_idx[id]] = colmap.Point3D(
            id_to_idx[id], pt3d[:], rgb, error, image_ids, point2D_idxs
        )

    colmap.write_points3D_text(points_3d, os.path.join(path, "points3D.txt"))


def export_images(all_data, path):
    """
    Image list with two lines of data per image:
       IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME
       POINTS2D[] as (X, Y, POINT3D_ID)
    """
    images = {}

    id_to_idx = all_data["id_to_idx"]

    for frame_idx, frame_data in all_data["frames"].items():
        q = frame_data["pose"].q
        t = frame_data["pose"].t

        camera_id = frame_idx
        name = frame_data["image_name"]

        xys = []
        point3D_ids = []
        for id, pt2d in frame_data["points_2d"].items():
            xys.append(pt2d[0])
            point3D_ids.append(id_to_idx[id])

        c = colmap.BaseImage(
            frame_idx, [q.w, q.x, q.y, q.z], t[:], camera_id, name, xys, point3D_ids
        )
        images[frame_idx] = c

    colmap.write_images_text(images, os.path.join(path, "images.txt"))


def export_cameras(all_data, path):
    """
    Camera list with one line of data per camera:
       CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]
    """
    cameras = {}
    for frame_idx, frame_data in all_data["frames"].items():
        camera_model = colmap.CAMERA_MODEL_NAMES["OPENCV"].model_name
        intrinsics = frame_data["intrinsics"]
        # distortion is not supported :(
        K = intrinsics.K
        fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
        params = [fx, fy, cx, cy, *intrinsics.dist]
        c = colmap.Camera(
            frame_idx,
            camera_model,
            int(intrinsics.width),
            int(intrinsics.height),
            params,
        )
        cameras[frame_idx] = c

    colmap.write_cameras_text(cameras, os.path.join(path, "cameras.txt"))


def export_data(all_data, path):
    export_points_3d(all_data, path)
    export_images(all_data, path)
    export_cameras(all_data, path)
