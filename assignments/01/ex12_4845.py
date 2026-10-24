# DIMITRIOS ASIMAKOPOULOS CSD4845

import numpy as np
import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, Camera, RenderMesh
from Elements.pyECSS.System import  TransformSystem, CameraSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.Viewer import RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.utils.terrain import generateTerrain
from Elements.utils.Shortcuts import displayGUI_text
from OpenGL.GL import GL_LINES
from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE
from OpenGL.GL import *
import imgui


# the text shown in GUI to describe each assignment
example_description = \
"Assignment 1.2 renders two cubes, a pyramid , axes and terrain and also implements a reactive GUI window where the user can transform the entitities\n"

winWidth = 1024
winHeight = 1024
scene = Scene()

# CREATE ENTITIES AND THEIR BASICTRANSFIRM/RENDERMESH COMPONENTS
rootEntity = scene.world.createEntity(Entity(name="RooT"))

entityCam1 = scene.world.createEntity(Entity(name="entityCam1"))
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="trans1", trs=util.identity()))

entityCam2 = scene.world.createEntity(Entity(name="entityCam2"))
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="trans2", trs=util.identity()))

# node4 entity is where the 3D geometry for the cube1 will be attached, node5 is for cube2 and node6 is for the pyramid
node4 = scene.world.createEntity(Entity(name="node4"))
node5 = scene.world.createEntity(Entity(name="node5"))
node6 = scene.world.createEntity(Entity(name="node6"))

trans4 = scene.world.addComponent(node4, BasicTransform(name="trans4", trs=util.identity()))
trans5 = scene.world.addComponent(node5, BasicTransform(name="trans5", trs=util.identity()))
trans6 = scene.world.addComponent(node6, BasicTransform(name="trans6", trs=util.identity()))

mesh4 = scene.world.addComponent(node4, RenderMesh(name="mesh4"))
mesh5 = scene.world.addComponent(node5, RenderMesh(name="mesh5"))
mesh6 = scene.world.addComponent(node6, RenderMesh(name="mesh6"))

axes = scene.world.createEntity(Entity(name="axes"))
axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.001, 0.0)))
axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))

terrain = scene.world.createEntity(Entity(name="terrain"))
terrain_trans = scene.world.addComponent(terrain, BasicTransform(name="terrain_trans", trs=util.identity()))
terrain_mesh = scene.world.addComponent(terrain, RenderMesh(name="terrain_mesh"))

# These lines create parent-child relationships between the entities,
# building a scenegraph where the transformations and properties of child entities inherit from their parents.
# As we can see all entitites are children of rootEntity.
scene.world.addEntityChild(rootEntity, entityCam1)
scene.world.addEntityChild(entityCam1, entityCam2)
scene.world.addEntityChild(rootEntity, node4)
scene.world.addEntityChild(rootEntity, node5)
scene.world.addEntityChild(rootEntity, node6)
scene.world.addEntityChild(rootEntity, axes)
scene.world.addEntityChild(rootEntity, terrain)

# create cube
vertexCube = np.array([
    [-0.5, -0.5, 0.5, 1.0],
    [-0.5, 0.5, 0.5, 1.0],
    [0.5, 0.5, 0.5, 1.0],
    [0.5, -0.5, 0.5, 1.0],
    [-0.5, -0.5, -0.5, 1.0],
    [-0.5, 0.5, -0.5, 1.0],
    [0.5, 0.5, -0.5, 1.0],
    [0.5, -0.5, -0.5, 1.0]
],dtype=np.float32)
colorCube = np.array([
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0]
], dtype=np.float32)
indexCube = np.array([
    [1, 0, 3], [1, 3, 2],
    [2, 3, 7], [2, 7, 6],
    [3, 0, 4], [3, 4, 7],
    [6, 5, 1], [6, 1, 2],
    [4, 5, 6], [4, 6, 7],
    [5, 4, 0], [5, 0, 1]
], dtype=np.uint32)

# create pyramid
vertexPyramid = np.array([
    [0.0, 1.25, 0.0, 1.0],
    [-0.5, 0.5, 0.5, 1.0],
    [0.5, 0.5, 0.5, 1.0],
    [0.5, 0.5, -0.5, 1.0],
    [-0.5, 0.5, -0.5, 1.0]
], dtype=np.float32)
colorPyramid = np.array([
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
indexPyramid = np.array([
    [0, 1, 2],
    [0, 2, 3],
    [0, 3, 4],
    [0, 4, 1],
    [1, 2, 3],
    [3, 4, 1]
], dtype=np.uint32)

# create axes
vertexAxes = np.array([
    [0.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
],dtype=np.float32)
colorAxes = np.array([
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)

indexAxes = np.array((0,1,2,3,4,5), np.uint32) #3 simple colored Axes as R,G,B lines

# create terrain
vertexTerrain, indexTerrain, colorTerrain= generateTerrain(size=4,N=20)


transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())


mesh4.vertex_attributes.append(vertexCube)
mesh4.vertex_attributes.append(colorCube)
mesh4.vertex_index.append(indexCube)
vArray4 = scene.world.addComponent(node4, VertexArray())
shaderDec4 = scene.world.addComponent(node4, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

mesh5.vertex_attributes.append(vertexCube)
mesh5.vertex_attributes.append(colorCube)
mesh5.vertex_index.append(indexCube)
vArray5 = scene.world.addComponent(node5, VertexArray())
shaderDec5 = scene.world.addComponent(node5, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

mesh6.vertex_attributes.append(vertexPyramid)
mesh6.vertex_attributes.append(colorPyramid)
mesh6.vertex_index.append(indexPyramid)
vArray6 = scene.world.addComponent(node6, VertexArray())
shaderDec6 = scene.world.addComponent(node6, ShaderGLDecorator(Shader(vertex_source=Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

axes_mesh.vertex_attributes.append(vertexAxes)
axes_mesh.vertex_attributes.append(colorAxes)
axes_mesh.vertex_index.append(indexAxes)
axes_vArray = scene.world.addComponent(axes, VertexArray(primitive=GL_LINES))
axes_shader = scene.world.addComponent(axes, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

terrain_mesh.vertex_attributes.append(vertexTerrain)
terrain_mesh.vertex_attributes.append(colorTerrain)
terrain_mesh.vertex_index.append(indexTerrain)
terrain_vArray = scene.world.addComponent(terrain, VertexArray(primitive=GL_LINES))
terrain_shader = scene.world.addComponent(terrain, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

# first positions for very entity
c1_trans = [2.0, 0.0, 0.0]
c1_rot = [0.0, 0.0, 0.0]
c1_scale = [1.0, 1.0, 1.0]

c2_trans = [-1.0, 0.0, 0.0]
c2_rot = [0.0, 0.0, 0.0]
c2_scale = [1.0, 1.0, 1.0]

pyramid_trans = [-1.0, 0.0, 0.0]
pyramid_rot = [0.0, 0.0, 0.0]
pyramid_scale = [1.0, 1.0, 1.0]

house_trans = [-1.0, 0.0, 0.0]
house_rot = [0.0, 0.0, 0.0]
house_scale = [1.0, 1.0, 1.0]

showAxes = True
showGrid = True
showCube1 = True
showCube2 = True
showPyramid = True

def displayGUI():
    global c1_trans, c1_rot, c1_scale
    global c2_trans, c2_rot, c2_scale
    global pyramid_trans, pyramid_rot, pyramid_scale
    global house_trans, house_rot, house_scale
    global showAxes, showGrid, showCube1, showCube2, showPyramid

    imgui.set_next_window_size(500, 500)
    imgui.begin("TRS Controls")

    # cube1 transformations
    imgui.text("Cube 1 Transformations")
    changed_c1_trans, c1_trans = imgui.drag_float3("Cube 1 Translation", *c1_trans, change_speed=0.1)
    changed_c1_rot, c1_rot = imgui.drag_float3("Cube 1 Rotation", *c1_rot, change_speed=1.0)
    changed_c1_scale, c1_scale = imgui.drag_float3("Cube 1 Scaling", *c1_scale, change_speed=0.1)

    # cube2 transformations
    imgui.text("Cube 2 Transformations")
    changed_c2_trans, c2_trans = imgui.drag_float3("Cube 2 Translation", *c2_trans, change_speed=0.1)
    changed_c2_rot, c2_rot = imgui.drag_float3("Cube 2 Rotation", *c2_rot, change_speed=1.0)
    changed_c2_scale, c2_scale = imgui.drag_float3("Cube 2 Scaling", *c2_scale, change_speed=0.1)

    # pyramid transformations
    imgui.text("Pyramid Transformations")
    changed_pyramid_trans, pyramid_trans = imgui.drag_float3("Pyramid Translation", *pyramid_trans, change_speed=0.1)
    changed_pyramid_rot, pyramid_rot = imgui.drag_float3("Pyramid Rotation", *pyramid_rot, change_speed=1.0)
    changed_pyramid_scale, pyramid_scale = imgui.drag_float3("Pyramid Scaling", *pyramid_scale, change_speed=0.1)

    # house transformations
    imgui.text("House Transformations")
    changed_house_trans, house_trans = imgui.drag_float3("House Translation", *house_trans, change_speed=0.1)
    changed_house_rot, house_rot = imgui.drag_float3("House Rotation", *house_rot, change_speed=1.0)
    changed_house_scale, house_scale = imgui.drag_float3("House Scaling", *house_scale, change_speed=0.1)

    # Toggles for visibility
    clicked, showAxes = imgui.checkbox("Show Axes", showAxes)
    clicked, showGrid = imgui.checkbox("Show Floor Grid", showGrid)
    clicked, showCube1 = imgui.checkbox("Show Cube 1", showCube1)
    clicked, showCube2 = imgui.checkbox("Show Cube 2", showCube2)
    clicked, showPyramid = imgui.checkbox("Show Pyramid", showPyramid)

    imgui.end()


# initializes the OpenGL rendering context, setting up the window and GUI.
running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "Elements: A Working Event Manager", customImGUIdecorator = ImGUIecssDecorator, openGLversion = 4)

### EVENT MANAGER ###
# This section of code sets up an event management system for handling user input and updates to the scene (such as wireframe view toggling and camera updates),
# and it configures the camera view and transformation matrices for objects like the cube1, terrain, and axes.
eManager = scene.world.eventManager # this handles events such as user input, mouse movements, key presses, or other triggers within the rendering system.
gWindow = scene.renderWindow # refers to the render window where the scene is displayed.
gGUI = scene.gContext # refers to the GUI context (e.g., ImGui), which handles the graphical user interface (GUI) elements within the rendering window.
renderGLEventActuator = RenderGLStateSystem() # this system will manage OpenGL-related state changes based on events (rendering updates, wireframe-solid modes).

eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator



### CAMERA SETUP ###
eye = util.vec(2.5, 2.5, 2.5) # located 2.5 inits away from each axe
target = util.vec(0.0, 0.0, 0.0) # the origin
up = util.vec(0.0, 1.0, 0.0) # meaning the y-axis is the up direction.
view = util.lookat(eye, target, up)
projMat = util.perspective(50.0, 1.0, 0.01, 10.0)
m = np.linalg.inv(projMat @ view)
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))
gWindow._myCamera = view

model_terrain = terrain.getChild(0).trs
model_axes = axes_trans.trs


### MAIN LOOP ###
scene.world.traverse_visit(initUpdate, scene.world.root)

while running:
    running = scene.render() # calls the scene.render() method, which performs rendering for the current frame.
    displayGUI_text(example_description) # responsible for rendering a text description in the GUI
    displayGUI() # TRS GUI
    scene.world.traverse_visit(renderUpdate, scene.world.root) # triggers the renderUpdate function across all components attached to scene.world.root.
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam) # responsible for performing camera-specific updates before the rendering occurs.
    scene.world.traverse_visit(camUpdate, scene.world.root) # updates the camera parameters to make sure everything is in sync before the next frame is rendered.
    view =  gWindow._myCamera # updates view via the imgui ensuring that any user interactions are reflected in the camera's view

    # transformations for House entity
    model_house = util.translate(*house_trans) @ \
              util.rotate((1.0, 0.0, 0.0), house_rot[0]) @ \
              util.rotate((0.0, 1.0, 0.0), house_rot[1]) @ \
              util.rotate((0.0, 0.0, 1.0), house_rot[2]) @ \
              util.scale(*house_scale)

    # transformations for Cube1
    model_cube1 = util.translate(*c1_trans) @ \
               util.rotate((1.0, 0.0, 0.0), c1_rot[0]) @ \
               util.rotate((0.0, 1.0, 0.0), c1_rot[1]) @ \
               util.rotate((0.0, 0.0, 1.0), c1_rot[2]) @ \
               util.scale(*c1_scale)

    # transformations for Cube2
    model_cube2 = util.translate(c2_trans[0], c2_trans[1], c2_trans[2]) @ \
               util.rotate((1.0, 0.0, 0.0), c2_rot[0]) @ \
               util.rotate((0.0, 1.0, 0.0), c2_rot[1]) @ \
               util.rotate((0.0, 0.0, 1.0), c2_rot[2]) @ \
               util.scale(*c2_scale)

    # combine Cube2 transformation with House transformation
    model_cube2 = model_house @ model_cube2

    # transformations for Pyramid
    model_pyramid = util.translate(pyramid_trans[0], pyramid_trans[1], pyramid_trans[2]) @ \
                 util.rotate((1.0, 0.0, 0.0), pyramid_rot[0]) @ \
                 util.rotate((0.0, 1.0, 0.0), pyramid_rot[1]) @ \
                 util.rotate((0.0, 0.0, 1.0), pyramid_rot[2]) @ \
                 util.scale(*pyramid_scale)

    # combine Pyramid transformation with House transformation
    model_pyramid = model_house @ model_pyramid

    # set MVP matrices based on transformations and visibility
    if showCube1:
        mvp_cube1 = projMat @ view @ model_cube1
        shaderDec4.setUniformVariable(key='modelViewProj', value=mvp_cube1, mat4=True)
        scene.world.traverse_visit(renderUpdate, node4)
    if showCube2:
        mvp_cube2 = projMat @ view @ model_cube2
        shaderDec5.setUniformVariable(key='modelViewProj', value=mvp_cube2, mat4=True)
        scene.world.traverse_visit(renderUpdate, node5)
    if showPyramid:
        mvp_pyramid = projMat @ view @ model_pyramid
        shaderDec6.setUniformVariable(key='modelViewProj', value=mvp_pyramid, mat4=True)
        scene.world.traverse_visit(renderUpdate, node6)
    if showAxes:
        mvp_axes = projMat @ view @ model_axes
        axes_shader.setUniformVariable(key='modelViewProj', value=mvp_axes, mat4=True)
        scene.world.traverse_visit(renderUpdate, axes)
    if showGrid:
        mvp_terrain = projMat @ view @ model_terrain
        terrain_shader.setUniformVariable(key='modelViewProj', value=mvp_terrain, mat4=True)
        scene.world.traverse_visit(renderUpdate, terrain)

    scene.render_post() # handles any post-processing tasks or cleanup required after rendering

scene.shutdown()
