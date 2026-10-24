## DIMITRIOS ASIMAKOPOULOS CSD4845 ##

import imgui
import numpy as np
import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, Camera, RenderMesh
from Elements.pyECSS.System import  TransformSystem, CameraSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.Viewer import RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator, ImGUIDecorator
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.utils.terrain import generateTerrain
from Elements.utils.Shortcuts import displayGUI_text
from OpenGL.GL import GL_LINES
from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE
from OpenGL.GL import *


example_description = \
"Assignment 1.3 first renders a triangle, two lines and three points\n"

winWidth = 1024
winHeight = 1024
scene = Scene()

# CREATE ENTITIES AND THEIR BASICTRANSFIRM/RENDERMESH COMPONENTS
rootEntity = scene.world.createEntity(Entity(name="RooT"))

entityCam1 = scene.world.createEntity(Entity(name="entityCam1"))
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="trans1", trs=util.identity()))

entityCam2 = scene.world.createEntity(Entity(name="entityCam2"))
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="trans2", trs=util.identity()))

triangleEntity = scene.world.createEntity(Entity(name="Triangle"))
triangleTransform = scene.world.addComponent(triangleEntity, BasicTransform(name="triangleTransform", trs=util.identity()))
triangleMesh = scene.world.addComponent(triangleEntity, RenderMesh(name="triangleMesh"))

lineEntity = scene.world.createEntity(Entity(name="Line"))
lineTransform = scene.world.addComponent(lineEntity, BasicTransform(name="lineTransform", trs=util.identity()))
lineMesh = scene.world.addComponent(lineEntity, RenderMesh(name="lineMesh"))

pointEntity = scene.world.createEntity(Entity(name="Point"))
pointTransform = scene.world.addComponent(pointEntity, BasicTransform(name="pointTransform", trs=util.identity()))
pointMesh = scene.world.addComponent(pointEntity, RenderMesh(name="pointMesh"))

axes = scene.world.createEntity(Entity(name="axes"))
axes_trans = scene.world.addComponent(axes, BasicTransform(name="axes_trans", trs=util.translate(0.0, 0.001, 0.0)))
axes_mesh = scene.world.addComponent(axes, RenderMesh(name="axes_mesh"))

terrain = scene.world.createEntity(Entity(name="terrain"))
terrain_trans = scene.world.addComponent(terrain, BasicTransform(name="terrain_trans", trs=util.identity()))
terrain_mesh = scene.world.addComponent(terrain, RenderMesh(name="terrain_mesh"))


# ADD THE ENTITITIES AS CHILDREN OF ROOT
scene.world.addEntityChild(rootEntity, entityCam1)
scene.world.addEntityChild(entityCam1, entityCam2)
scene.world.addEntityChild(rootEntity, triangleEntity)
scene.world.addEntityChild(rootEntity, lineEntity)
scene.world.addEntityChild(rootEntity, pointEntity)
scene.world.addEntityChild(rootEntity, axes)
scene.world.addEntityChild(rootEntity, terrain)


# CREATE THE GEOMETRY AND COLOR FOR THE ENTITIES
triangleVertices = np.array([
    [0.0, 0.5, 0.0, 1.0],
    [-0.5, -0.5, 0.0, 1.0],
    [0.5, -0.5, 0.0, 1.0]
], dtype=np.float32)
triangleColor = np.array([
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0]
], dtype=np.float32)
triangleIndex = np.array([
    [0,1,2]
], dtype=np.uint32)


lineVertices = np.array([
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
lineColor = np.array([
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0, 1.0]
], dtype=np.float32)
lineIndex = np.array([
    [0,1],
    [2,3]
], dtype=np.uint32)


pointVertices = np.array([
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 1.0, 0.0, 1.0]
],dtype=np.float32)
pointColor = np.array([
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0]
],dtype=np.float32)


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
],dtype=np.float32)
indexAxes = np.array((0,1,2,3,4,5), np.uint32)

vertexTerrain, indexTerrain, colorTerrain= generateTerrain(size=4,N=20)

# ADD THE VERTICES, COLOR AND INDICES TO THE MESH OF EVERY ENTITY
triangleMesh.vertex_attributes.append(triangleVertices)
triangleMesh.vertex_attributes.append(triangleColor)
triangleMesh.vertex_index.append(triangleIndex)
vArrayTriangle = scene.world.addComponent(triangleEntity, VertexArray())
shaderDecTriangle = scene.world.addComponent(triangleEntity, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

lineMesh.vertex_attributes.append(lineVertices)
lineMesh.vertex_attributes.append(lineColor)
lineMesh.vertex_index.append(lineIndex)
vArrayLine = scene.world.addComponent(lineEntity, VertexArray(primitive=GL_LINES))
shaderDecLine = scene.world.addComponent(lineEntity, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

pointMesh.vertex_attributes.append(pointVertices)
pointMesh.vertex_attributes.append(pointColor)
vArrayPoint = scene.world.addComponent(pointEntity, VertexArray(primitive=GL_POINTS))
shaderDecPoint = scene.world.addComponent(pointEntity, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

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

# SYSTEMS
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())

running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "Elements: A Working Event Manager", customImGUIdecorator = ImGUIecssDecorator, openGLversion = 4)

# EVENT MANAGER
eManager = scene.world.eventManager
gWindow = scene.renderWindow
gGUI = scene.gContext
renderGLEventActuator = RenderGLStateSystem()

eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator


# CAMERA SETUP
eye = util.vec(2.5, 2.5, 2.5)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
projMat = util.perspective(50.0, 1.0, 0.01, 50.0)
m = np.linalg.inv(projMat @ view)
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))
gWindow._myCamera = view

# MODEL MATRIX OF EACH ENTITY
model_triangle = triangleTransform.trs @ util.translate(0.2, 0.4, 0.2) @ util.rotate((1 ,0, 0), 45)
model_line = lineTransform.trs @ util.translate(0.5, 0.4, 0.2) @ util.rotate((1 ,0, 0), 30)
model_point = pointTransform.trs  @ util.translate(0.2, 0.3, 0.6)
model_terrain = terrain.getChild(0).trs
model_axes = axes_trans.trs


# MAIN LOOP
scene.world.traverse_visit(initUpdate, scene.world.root)

while running:
    running = scene.render()
    displayGUI_text(example_description)
    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam)
    scene.world.traverse_visit(camUpdate, scene.world.root)
    view =  gWindow._myCamera

    mvp_triangle = projMat @ view @ model_triangle
    mvp_line = projMat @ view @ model_line
    mvp_point = projMat @ view @ model_point
    mvp_axes = projMat @ view @ model_axes
    mvp_terrain = projMat @ view @ model_terrain

    shaderDecTriangle.setUniformVariable(key='modelViewProj', value=mvp_triangle, mat4=True)
    shaderDecLine.setUniformVariable(key='modelViewProj', value=mvp_line, mat4=True)
    shaderDecPoint.setUniformVariable(key='modelViewProj', value=mvp_point, mat4=True)
    axes_shader.setUniformVariable(key='modelViewProj', value=mvp_axes, mat4=True)
    terrain_shader.setUniformVariable(key='modelViewProj', value=mvp_terrain, mat4=True)

    scene.render_post()

scene.shutdown()
