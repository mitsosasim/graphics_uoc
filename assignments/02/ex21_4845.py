#DIMITRIOS ASIMAKOPOULOS CSD4845
import os
import numpy as np
import Elements.pyECSS.math_utilities as util
import OpenGL.GL as gl
import Elements.utils.normals as norm
import imgui
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, Camera, RenderMesh
from Elements.pyECSS.System import TransformSystem, CameraSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.Viewer import RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from OpenGL.GL import GL_LINES
from Elements.utils.obj_to_mesh import obj_to_mesh
from Elements.utils.Shortcuts import displayGUI_text

#the text shown in GUI to describe each assignment
example_description = \
"Assignment 2.1 renders two cubes and a pyramid and also implements a reactive GUI window \n\n\
    where the user can change the color and the lighting of the entities.   \n\n\
        The scene is being lit using the Blinn-Phong algorithm.\n\n\
            csd4845 - Dimitrios Asimakopoulos"

winWidth = 1024
winHeight = 1024
scene = Scene()

#CREATE ENTITIES AND THEIR BASICTRANSFORM/RENDERMESH COMPONENTS
rootEntity = scene.world.createEntity(Entity(name="RooT"))
entityCam1 = scene.world.createEntity(Entity(name="entityCam1"))
entityCam2 = scene.world.createEntity(Entity(name="entityCam2"))
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="trans1", trs=util.identity()))
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="trans2", trs=util.identity()))
scene.world.addEntityChild(rootEntity, entityCam1)
scene.world.addEntityChild(entityCam1, entityCam2)

#CREATE SYSTEMS
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())

#create cube 1 and 2
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
colorCube1 = np.array([
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
colorCube2 = np.array([
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0]
], dtype=np.float32)
indexCube = np.array((1,0,3, 1,3,2,
                  2,3,7, 2,7,6,
                  3,0,4, 3,4,7,
                  6,5,1, 6,1,2,
                  4,5,6, 4,6,7,
                  5,4,0, 5,0,1), np.uint32)

#create pyramid
vertexPyramid = np.array([
    [0.0, 1.25, 0.0, 1.0],
    [-0.5, 0.5, 0.5, 1.0],
    [0.5, 0.5, 0.5, 1.0],
    [0.5, 0.5, -0.5, 1.0],
    [-0.5, 0.5, -0.5, 1.0]
], dtype=np.float32)
colorPyramid = np.array([
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
indexPyramid = np.array([0, 1, 2,
                         0, 2, 3,
                         0, 3, 4,
                         0, 4, 1,
                         1, 2, 3,
                         3, 4, 1],
                        dtype=np.uint32)

#generate flat normals for the cube and pyramid
vertices, indices, _, normals = norm.generateFlatNormalsMesh(vertexCube , indexCube) # use generatesmoothnormalsmesh for smooth shading and better show shininess
verticesP, indicesP, _, normalsP = norm.generateFlatNormalsMesh(vertexPyramid , indexPyramid)

#create entities for the cube, pyramid, and axes
cube1 = scene.world.createEntity(Entity(name="cube1"))
scene.world.addEntityChild(rootEntity, cube1)
cube1_trans = scene.world.addComponent(cube1, BasicTransform(name="cube1_trans", trs=util.identity()))
cube1_mesh = scene.world.addComponent(cube1, RenderMesh(name="cube1_mesh"))
cube1_mesh.vertex_attributes.append(vertices)
cube1_mesh.vertex_attributes.append(normals)
#cube1_mesh.vertex_attributes.append(colors)
cube1_mesh.vertex_index.append(indices)
cube1_vertexArray = scene.world.addComponent(cube1, VertexArray())
cube1_shader = scene.world.addComponent(cube1, ShaderGLDecorator(Shader(vertex_source = Shader.VERT_PHONG_MVP, fragment_source=Shader.FRAG_PHONG_MATERIAL)))

cube2 = scene.world.createEntity(Entity(name="cube2"))
scene.world.addEntityChild(rootEntity, cube2)
cube2_trans = scene.world.addComponent(cube2, BasicTransform(name="cube2_trans", trs=util.identity()))
cube2_mesh = scene.world.addComponent(cube2, RenderMesh(name="cube2_mesh"))
cube2_mesh.vertex_attributes.append(vertices)
cube2_mesh.vertex_attributes.append(normals)
cube2_mesh.vertex_index.append(indices)
cube2_vertexArray = scene.world.addComponent(cube2, VertexArray())
cube2_shader = scene.world.addComponent(cube2, ShaderGLDecorator(Shader(vertex_source = Shader.VERT_PHONG_MVP, fragment_source=Shader.FRAG_PHONG_MATERIAL)))

pyramid = scene.world.createEntity(Entity(name="pyramid"))
scene.world.addEntityChild(rootEntity, pyramid)
pyramid_trans = scene.world.addComponent(pyramid, BasicTransform(name="pyramid_trans", trs=util.identity()))
pyramid_mesh = scene.world.addComponent(pyramid, RenderMesh(name="pyramid_mesh"))
pyramid_mesh.vertex_attributes.append(verticesP)
pyramid_mesh.vertex_attributes.append(normalsP)
pyramid_mesh.vertex_index.append(indicesP)
pyramid_vertexArray = scene.world.addComponent(pyramid, VertexArray())
pyramid_shader = scene.world.addComponent(pyramid, ShaderGLDecorator(Shader(vertex_source=Shader.VERT_PHONG_MVP, fragment_source=Shader.FRAG_PHONG_MATERIAL)))


# #create axes
# vertexAxes = np.array([
#     [0.0, 0.0, 0.0, 1.0],
#     [1.0, 0.0, 0.0, 1.0],
#     [0.0, 0.0, 0.0, 1.0],
#     [0.0, 1.0, 0.0, 1.0],
#     [0.0, 0.0, 0.0, 1.0],
#     [0.0, 0.0, 1.0, 1.0]
# ],dtype=np.float32)
# colorAxes = np.array([
#     [1.0, 0.0, 0.0, 1.0],
#     [1.0, 0.0, 0.0, 1.0],
#     [0.0, 1.0, 0.0, 1.0],
#     [0.0, 1.0, 0.0, 1.0],
#     [0.0, 0.0, 1.0, 1.0],
#     [0.0, 0.0, 1.0, 1.0]
# ], dtype=np.float32)
# indexAxes = np.array((0,1,2,3,4,5), np.uint32) #3 simple colored Axes as R,G,B lines
# axes = scene.world.createEntity(Entity(name="axes"))
# axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.001, 0.0)))
# axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))
# scene.world.addEntityChild(rootEntity, axes)
# axes_mesh.vertex_attributes.append(vertexAxes)
# axes_mesh.vertex_attributes.append(colorAxes)
# axes_mesh.vertex_index.append(indexAxes)
# axes_vArray = scene.world.addComponent(axes, VertexArray(primitive=GL_LINES))
# axes_shader = scene.world.addComponent(axes, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))
# model_axes = axes_trans.trs




#initialize variables for GUI
#light
Lposition = util.vec(1.0, 1.0, 1.0)
Lambientcolor = util.vec(1.0, 1.0, 1.0)
Lambientstr = 0.5
LviewPos = util.vec(3.0, 3.0, 5.0)
Lcolor = util.vec(1.0,1.0,1.0)
Lintensity = 1.0

#material
MshininessCube1 = 1.0
MshininessCube2 = 1.0
MshininessPyramid = 1.0
diffuseStrengthCube1 = 1.0
diffuseStrengthCube2 = 1.0
diffuseStrengthPyramid = 1.0

#color
new_color1 = colorCube1[0][:4].tolist()
new_color2 = colorCube2[0][:4].tolist()
new_color3 = colorPyramid[0][:4].tolist()
McolorCube1 = new_color1
McolorCube2 = new_color2
McolorPyramid = new_color3


# GUI function
def displayGUI():
    global changed1, changed2, changed3, McolorCube1, McolorCube2, McolorPyramid
    global new_color1, new_color2, new_color3, Lposition, Lambientcolor
    global Lambientstr, LviewPos, Lcolor, Lintensity, MshininessCube1, MshininessCube2, MshininessPyramid
    global diffuseStrengthCube1, diffuseStrengthCube2, diffuseStrengthPyramid

    imgui.set_next_window_size(525, 420)
    imgui.begin("Color & Lighting Controls", flags=imgui.WINDOW_NO_RESIZE)

    #colors section
    imgui.text("Object Colors")
    imgui.separator()
    changed1, new_color1 = imgui.color_edit3("Cube 1 Color", *new_color1)
    changed2, new_color2 = imgui.color_edit3("Cube 2 Color", *new_color2)
    changed3, new_color3 = imgui.color_edit3("Pyramid Color", *new_color3)

    if changed1:
        McolorCube1 = new_color1
        cube1_shader.setUniformVariable(key='inputColor', value=[*new_color1], float4=True)
    if changed2:
        McolorCube2 = new_color2
        cube2_shader.setUniformVariable(key='inputColor', value=[*new_color2], float4=True)
    if changed3:
        McolorPyramid = new_color3
        pyramid_shader.setUniformVariable(key='inputColor', value=[*new_color3], float4=True)

    #lighting section
    imgui.separator()
    imgui.text("Lighting Controls")
    _, Lcolor = imgui.color_edit3("Light Color", *Lcolor)
    _, Lposition = imgui.drag_float3("Light Position", *Lposition, change_speed=0.1)
    _, Lintensity = imgui.drag_float("Light Intensity", Lintensity, change_speed=0.01, min_value=0.0, max_value=10.0)
    _, Lambientcolor = imgui.color_edit3("Ambient Color", *Lambientcolor)
    _, Lambientstr = imgui.drag_float("Ambient Intensity", Lambientstr, change_speed=0.01, min_value=0.0, max_value=1.0)

    #material section
    imgui.separator()
    imgui.text("Material Properties")
    _, MshininessCube1 = imgui.drag_float("Cube 1 Shininess", MshininessCube1, change_speed=0.01, min_value=0.1, max_value=10000.0)
    _, MshininessCube2 = imgui.drag_float("Cube 2 Shininess", MshininessCube2, change_speed=0.01, min_value=0.1, max_value=10000.0)
    _, MshininessPyramid = imgui.drag_float("Pyramid Shininess", MshininessPyramid, change_speed=0.01, min_value=0.1, max_value=100.0)

    _, diffuseStrengthCube1 = imgui.drag_float("Cube 1 Diffuse Strength", diffuseStrengthCube1, change_speed=0.01, min_value=0.0, max_value=10000.0)
    _, diffuseStrengthCube2 = imgui.drag_float("Cube 2 Diffuse Strength", diffuseStrengthCube2, change_speed=0.01, min_value=0.0, max_value=10000.0)
    _, diffuseStrengthPyramid = imgui.drag_float("Pyramid Diffuse Strength", diffuseStrengthPyramid, change_speed=0.01, min_value=0.0, max_value=10000.0)
    imgui.end()


#function to update the uniform variables of the phong shader
def set_phong_shader_uniforms(shader, model, matColor):
    shader.setUniformVariable(key='model',value=model,mat4=True)
    shader.setUniformVariable(key='ambientColor', value=Lambientcolor, float3=True)
    shader.setUniformVariable(key='ambientStr', value=Lambientstr, float1=True)
    shader.setUniformVariable(key='viewPos', value=LviewPos, float3=True)
    shader.setUniformVariable(key='lightPos', value=Lposition, float3=True)
    shader.setUniformVariable(key='lightColor', value=Lcolor, float3=True)
    shader.setUniformVariable(key='lightIntensity', value=Lintensity, float1=True)
    #shader.setUniformVariable(key='shininess', value=Mshininess, float1=True)
    shader.setUniformVariable(key='matColor', value=matColor, float3=True)




running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "Assignment 2.1", openGLversion = 4, customImGUIdecorator = ImGUIecssDecorator)

eManager = scene.world.eventManager #this handles events such as user input, mouse movements, key presses, or other triggers within the rendering system.
gWindow = scene.renderWindow #refers to the render window where the scene is displayed.
gGUI = scene.gContext #refers to the GUI context (e.g., ImGui), which handles the graphical user interface (GUI) elements within the rendering window.
renderGLEventActuator = RenderGLStateSystem() #this system will manage OpenGL-related state changes based on events (rendering updates, wireframe-solid modes).

eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator


#CAMERA SETUP
eye = util.vec(2.5, 2.5, 2.5)
target = util.vec(0, 0, 0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
projMat = util.perspective(50.0, 1.0, 0.01, 10.0)
m = np.linalg.inv(projMat @ view)
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))
gWindow._myCamera = view

#MODEL MATRICES
model_cube1 = cube1_trans.trs @ util.translate(-0.6, 0, 0.7) @ util.scale(0.5)
model_cube2 = cube2_trans.trs @ util.translate(1.1, 0, -0.5) @ util.scale(0.5)
model_pyramid = pyramid_trans.trs @ util.translate(0.1, -0.5, -0.3) @ util.scale(0.69)

cube1_shader.setUniformVariable(key='inputColor', value=[*new_color1], float4=True)
cube2_shader.setUniformVariable(key='inputColor', value=[*new_color2], float4=True)
pyramid_shader.setUniformVariable(key='inputColor', value=[*new_color3], float4=True)


#MAIN LOOP
scene.world.traverse_visit(initUpdate, scene.world.root)

while running:
    running = scene.render()
    displayGUI_text(example_description)
    displayGUI()
    scene.world.traverse_visit(transUpdate, scene.world.root)
    scene.world.traverse_visit(renderUpdate, scene.world.root) # triggers the renderUpdate function across all components attached to scene.world.root.
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam) # responsible for performing camera-specific updates before the rendering occurs.
    scene.world.traverse_visit(camUpdate, scene.world.root) # updates the camera parameters to make sure everything is in sync before the next frame is rendered.
    view = gWindow._myCamera # updates view via the imgui ensuring that any user interactions are reflected in the camera's view

    #update the model matrices
    mvp_cube1 = projMat @ view @ model_cube1
    mvp_cube2 = projMat @ view @ model_cube2
    mvp_pyramid = projMat @ view @ model_pyramid
    cube1_shader.setUniformVariable(key='modelViewProj', value=mvp_cube1, mat4=True)
    cube2_shader.setUniformVariable(key='modelViewProj', value=mvp_cube2, mat4=True)
    pyramid_shader.setUniformVariable(key='modelViewProj', value=mvp_pyramid, mat4=True)

    #update the phong shader uniforms
    set_phong_shader_uniforms(cube1_shader, model_cube1, McolorCube1)
    set_phong_shader_uniforms(cube2_shader, model_cube2, McolorCube2)
    set_phong_shader_uniforms(pyramid_shader, model_pyramid, McolorPyramid)

    #update the shininess and diffuse strength
    cube1_shader.setUniformVariable(key='shininess', value=MshininessCube1, float1=True)
    cube2_shader.setUniformVariable(key='shininess', value=MshininessCube2, float1=True)
    pyramid_shader.setUniformVariable(key='shininess', value=MshininessPyramid, float1=True)

    cube1_shader.setUniformVariable(key='diffuseStrength', value=diffuseStrengthCube1, float1=True)
    cube2_shader.setUniformVariable(key='diffuseStrength', value=diffuseStrengthCube2, float1=True)
    pyramid_shader.setUniformVariable(key='diffuseStrength', value=diffuseStrengthPyramid, float1=True)

    # mvp_axes = projMat @ view @ model_axes
    # axes_shader.setUniformVariable(key='modelViewProj', value=mvp_axes, mat4=True)
    scene.render_post()

scene.shutdown()
