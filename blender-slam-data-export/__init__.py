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
    "location" : "Sidebar > ExportSLAM",
    "warning" : "",
    "url": "https://github.com/avkudr/blender-slam-data-export",
    "wiki_url": "https://github.com/avkudr/blender-slam-data-export",
    "tracker_url": "https://github.com/avkudr/blender-slam-data-export/issues",
    "category": "Import-Export"
}

from . import addon
from . import render_engine

PROPS = [
    ('slam_export_render_images', bpy.props.BoolProperty(name='Render images', default=True)),
]

class SlamDataExporterPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_slam_data_exporter'
    bl_label = 'Export SLAM data'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ExportSLAM"

    def draw(self, context):
        col = self.layout.column()
        col.label(text='SLAM data exporter tool')
        col.prop(context.scene, "slam_export_render_images")
        col.operator(addon.SlamDataExporter.bl_idname, text='Export')

def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels

def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    bpy.utils.register_class(render_engine.VertexRayCastEngine)
    bpy.utils.register_class(addon.SlamDataExporter)
    bpy.utils.register_class(SlamDataExporterPanel)

def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    bpy.utils.unregister_class(render_engine.VertexRayCastEngine)
    bpy.utils.unregister_class(SlamDataExporterPanel)
    bpy.utils.unregister_class(addon.SlamDataExporter)
