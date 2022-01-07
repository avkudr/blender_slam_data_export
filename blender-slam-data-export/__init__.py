# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

bl_info = {
    "name" : "SLAM data exporter",
    "author" : "Andrey Kudryavtsev",
    "description" : "Export SLAM data in ETH3D format: 3d vertices, 2d projections, camera poses, etc.",
    "blender" : (3, 0, 0),
    "version" : (0, 0, 1),
    "location" : "Render > Save SLAM data",
    "warning" : "",
    "url": "https://github.com/avkudr/blender_slam_export",
    "wiki_url": "https://github.com/avkudr/blender_slam_export",
    "tracker_url": "https://github.com/avkudr/blender_slam_export/issues",
    "category": "Import-Export"
}

from . import addon

def menu_func(self, context):
    self.layout.operator(addon.SlamDataExporter.bl_idname)

def register():
    print("Addon registration")
    bpy.utils.register_class(addon.SlamDataExporter)
    bpy.types.TOPBAR_MT_render.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    print("Addon deregistration")
    bpy.types.TOPBAR_MT_render.remove(menu_func)
    bpy.utils.unregister_class(addon.SlamDataExporter)