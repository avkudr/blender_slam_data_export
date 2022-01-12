[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](https://img.shields.io/badge/blender-2.8+-green)](https://www.blender.org/download/)

Export SLAM data 3D data from a blender scene in COLMAP format. This data can be used as the reference or ground truth for a variety of computer vision applications: 3d reconstruction, structure-from-motion, SLAM, tracking and many more. The add-on supports the export of **3d vertices**, **2d projections**, **camera poses**, and **camera intrinsic** parameters.

Evaluating the performance of 3d reconstruction or SLAM is not an easy task. The ground truch is often collected using special motion capture systems or LiDARs and it still not perfect. Using a rendering software, such as Blender, allows creating pefrect data for an arbitrary scene, for an arbitrary camera or a set of cameras, and for an arbitrary camera motion. For free!

### Example


## Install

### 1. Download the add-on

### 2. Install the add-on

## Usage


## Output format

The calibration is provided in the [format](http://colmap.github.io/format.html) of the [COLMAP](http://colmap.github.io/) Structure-from-Motion program. Camera intrinsics are given in a text file [cameras.txt](http://colmap.github.io/format.html#cameras-txt), while image extrinsics are given in a text file [images.txt](http://colmap.github.io/format.html#images-txt).

Keypoints and matches (projections of mesh vertices) are given in [images.txt](http://colmap.github.io/format.html#images-txt). 3d points, that correspond to the mesh vertices themselves, are given in [points3D.txt](http://colmap.github.io/format.html#points3d-txt) file.

Note that COLMAP format can be used in [MATLAB](https://github.com/colmap/colmap/blob/master/scripts/matlab/read_model.m), [Python](https://github.com/colmap/colmap/blob/dev/scripts/python/read_write_model.py), and [c++](https://github.com/colmap/colmap/blob/dev/src/base/reconstruction.h). In addition to that, this format can be used in [openMVG](https://github.com/openMVG/openMVG/blob/develop/src/software/SfM/import/io_readGTETH3D.hpp)

Example forder structure:
```
/output/dir/
   images/
      image_0.png
      image_1.png
      ...
   cameras.txt
   images.txt
   points3D.txt
```