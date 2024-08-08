import bpy
import os

# Path to the downloaded .zip file
addon_zip = "/git/io_mesh_stl.zip"

# Install the add-on
bpy.ops.preferences.addon_install(filepath=addon_zip)

# Enable the add-on
bpy.ops.preferences.addon_enable(module="io_mesh_stl")

# Save preferences
bpy.ops.wm.save_userpref()