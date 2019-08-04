import bge
import math, random
from time import sleep
import itertools
import mathutils
import math
from pathlib import Path
import os

def fibonacci_sphere(samples=1, randomize=False):
    rnd = 1.
    if randomize:
        rnd = random.random() * samples
    points = []
    offset = 2 / samples
    increment = math.pi * (3. - math.sqrt(5))
    for i in range(samples):
        y = i * offset - 1 + offset / 2
        r = math.sqrt(1 - pow(y,2))
        phi = ((i + rnd) % samples) * increment
        x = math.cos(phi) * r
        z = math.sin(phi) * r
        points.append((x, y, z))
    return points

# get_min_angle(fibonacci_sphere(100))
def get_min_angle(points):
    min_angle = float("inf")
    for p1, p2 in itertools.combinations(points, 2):
        cos_angle = mathutils.Vector(p1).normalized().dot(mathutils.Vector(p2).normalized())
        if abs(cos_angle) > 1:
            continue
        angle = math.acos(cos_angle)
        min_angle = min(min_angle, angle)
    return math.degrees(min_angle)

def delete_all_objects():
    for object in bpy.data.objects:
        bpy.data.objects.remove(object)

def set_camera():
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"])
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "Camera"
    set_camera_pos((5, -5, 5))
    set_camera_lookat((0, 0, 0))
    bpy.context.scene.camera = cam

def set_object():
    if "Object" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Object"])
    bpy.ops.mesh.primitive_monkey_add()
    bpy.data.objects["Suzanne"].name = "Object"
    bpy.data.objects["Object"].location = (0, 0, 0)

def set_light():
    if "Light" in bpy.data.collections:
        for object in bpy.data.collections["Light"].objects:
            bpy.data.objects.remove(object)
        bpy.data.collections.remove(bpy.data.collections["Light"])
    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_object = bpy.data.objects.new(name="Sun", object_data=sun_data)
    bpy.context.collection.objects.link(sun_object)
    sun_object.location = (5, 5, 5)
    # group lights
    # TODO: fix groups
    #bpy.ops.object.select_all(action='DESELECT')
    #bpy.context.collection.objects["Sun"].select_set(True)
    #bpy.ops.group.create(name="Light")
    #bpy.ops.object.group_link(group="Light")
    # environment light
    #bpy.context.collection.world.light_settings.use_environment_light = True
    #bpy.context.collection.world.light_settings.environment_energy = 0.5

def set_renderer():
    bpy.data.scenes["Scene"].render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    # I guess these two attributes are set by default
    #bpy.data.scenes["Scene"].view_layers["View Layer"].use_pass_combined = True
    #bpy.data.scenes["Scene"].view_layers["View Layer"].use_pass_z = True

def set_camera_pos(pos):
    cam = bpy.data.objects["Camera"]
    cam.location.x = pos[0]
    cam.location.y = pos[1]
    cam.location.z = pos[2]

def set_camera_lookat(look_at):
    if type(look_at) == tuple:
        look_at = mathutils.Vector(look_at)
    cam = bpy.data.objects["Camera"]
    cam_pos = cam.location
    direction = look_at - cam_pos
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

def render(group, name):
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    for n in tree.nodes:
        tree.nodes.remove(n)
    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.location = 185, 285
    v = tree.nodes.new("CompositorNodeComposite")
    v.location = 750, 210
    v.use_alpha = False
    links.new(rl.outputs[0], v.inputs[0])
    path = str(Path.home()) + "/Blender/" + group + "/"
    os.mkdir(path)
    bpy.context.scene.render.filepath = path + name + ".exr"
    #bpy.context.scene.render.resolution_x = 1920
    #bpy.context.scene.render.resolution_y = 1080
    bpy.ops.render.render(write_still = True, use_viewport = True)

'''
def renderDepth():
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    for n in tree.nodes:
        tree.nodes.remove(n)
    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.location = 185, 285
    v = tree.nodes.new("CompositorNodeViewer")
    v.location = 750, 110
    v.use_alpha = True
    links.new(rl.outputs[0], v.inputs[0])
    links.new(rl.outputs[2], v.inputs[1])
    c = tree.nodes.new("CompositorNodeComposite")
    c.location = 750, 310
    c.use_alpha = True
    links.new(rl.outputs[0], c.inputs[0])
    links.new(rl.outputs[2], c.inputs[1])
    bpy.ops.render.render()
    pixels = bpy.data.images["Viewer Node"].pixels
    return np.array(pixels[:])
'''

def images():
    # TODO: make object variable
    # TODO: multiple distances
    # TODO: multiple camera origin position and camera lookat positions/roll/up vertices
    delete_all_objects()
    set_camera()
    set_object()
    set_light()
    set_renderer()
    i = 0
    for pos in fibonacci_sphere(100):
        factor = 5.0
        pos = (pos[0] * factor, pos[1] * factor, pos[2] * factor)
        set_camera_pos(pos)
        set_camera_lookat(bpy.data.objects["Object"].location)
        render(str(i), "1")
        i += 1

def viewpoints():
    for pos in fibonacci_sphere(100):
        factor = 5.0
        pos = (pos[0] * factor, pos[1] * factor, pos[2] * factor)
        bpy.ops.mesh.primitive_uv_sphere_add(location = pos, size = 0.05)

def ray(x, y):
    cam = bpy.data.objects["Camera"]

