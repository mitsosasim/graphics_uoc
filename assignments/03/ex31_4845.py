#CSD4845 DIMITRIOS ASIMAKOPOULOS
#ASSIGNMENT 3.1
import imgui
import numpy as np
import math
import time
import OpenGL.GL as gl;
import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.System import  TransformSystem, CameraSystem
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform,  RenderMesh
from Elements.pyECSS.Event import Event
from Elements.pyECSS.math_utilities import vec

from Elements.pyGLV.GUI.Viewer import  RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator2
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
from Elements.pyGLV.GL.Scene import Scene
from Elements.definitions import ROOT_DIR
from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE

#function to calculate the length of a vector
def len(vector):
    """Calculate the length of a vector."""
    return sum(x**2 for x in vector) ** 0.5

#vertex and fragment shaders
manos_animation_vertexShader = """
    #version 410
    layout (location=0) in vec4 vPosition;
    layout (location=1) in vec4 vColor;
    layout (location=2) in vec3 weights;
    out vec4 color;

    uniform mat4 M0;
    uniform mat4 M1;
    uniform mat4 M2;

    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;

    void main()
    {

        mat4 M = (weights[0] * M0) + (weights[1] * M1) + (weights[2] * M2);
        gl_Position = projection * view * model *  M  * vPosition;
        color = vColor;
    }

    """

fragmentShader = """
    #version 410
    in vec4 color;
    out vec4 outputColour;
    void main()
    {
        outputColour = color;
    }
    """

#vertex data for the object
object_vertex = np.array([
    [-0.5, 0, -0.5, 1.0],
    [-0.5, 0, 0.5, 1.0],
    [0.5, 0, 0.5, 1.0],
    [0.5, 0, -0.5, 1.0],
    [-0.5, 1, -0.5, 1.0],
    [-0.5, 1, 0.5, 1.0],
    [0.5, 1, 0.5, 1.0],
    [0.5, 1, -0.5, 1.0],
    [-0.5, 2, -0.5, 1.0],
    [-0.5, 2, 0.5, 1.0],
    [0.5, 2, 0.5, 1.0],
    [0.5, 2, -0.5, 1.0],
    [-0.5, 3, -0.5, 1.0],
    [-0.5, 3, 0.5, 1.0],
    [0.5, 3, 0.5, 1.0],
    [0.5, 3, -0.5, 1.0],
    [-0.5, 4, -0.5, 1.0],
    [-0.5, 4, 0.5, 1.0],
    [0.5, 4, 0.5, 1.0],
    [0.5, 4, -0.5, 1.0]
],dtype=np.float32)

#color data for the object
object_color = np.array([
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 0.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 0.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 1.0, 1.0]
], dtype=np.float32)

#index data for the object
object_index = np.array([

    #bottom face of the first cube
    0, 1, 2,
    0, 2, 3,
    #top face of the first cube
    4, 5, 6,
    4, 6, 7,
    #side faces of the first cube
    0, 1, 5,
    0, 5, 4,
    1, 2, 6,
    1, 6, 5,
    2, 3, 7,
    2, 7, 6,
    3, 0, 4,
    3, 4, 7,

    #bottom face of the second cube
    4, 5, 6,
    4, 6, 7,
    #top face of the second cube
    8, 9, 10,
    8, 10, 11,
    #side faces of the second cube
    4, 5, 9,
    4, 9, 8,
    5, 6, 10,
    5, 10, 9,
    6, 7, 11,
    6, 11, 10,
    7, 4, 8,
    7, 8, 11,

    #bottom face of the third cube
    8, 9, 10,
    8, 10, 11,
    #top face of the third cube
    12, 13, 14,
    12, 14, 15,
    #side faces of the third cube
    8, 9, 13,
    8, 13, 12,
    9, 10, 14,
    9, 14, 13,
    10, 11, 15,
    10, 15, 14,
    11, 8, 12,
    11, 12, 15,

    #bottom face of the fourth cube
    12, 13, 14,
    12, 14, 15,
    #top face of the fourth cube
    16, 17, 18,
    16, 18, 19,
    #side faces of the fourth cube
    12, 13, 17,
    12, 17, 16,
    13, 14, 18,
    13, 18, 17,
    14, 15, 19,
    14, 19, 18,
    15, 12, 16,
    15, 16, 19
], dtype=np.uint32)

#joint positions
joints = [vec(0, 0, 0), vec(0, 1, 0), vec(0, 2, 0)]

#function to calculate the weights of the joints
def calculate_weights(point):
    distances = np.array([len(point - joint) for joint in joints])
    weights = 1 / distances
    weights /= weights.sum()
    return weights

joint_weights = np.array([calculate_weights(vec(vertex[0], vertex[1], vertex[2])) for vertex in object_vertex])



#initialize the scene and systems
winWidth = 1000
winHeight = 800
scene = Scene()
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())

#create the entities and components
rootEntity = scene.world.createEntity(Entity(name="Root"))
object = scene.world.createEntity(Entity(name="object"))
scene.world.addEntityChild(rootEntity, object)
object_trans = scene.world.addComponent(object, BasicTransform(name="object_trans", trs=util.identity()))
object_mesh = scene.world.addComponent(object, RenderMesh(name="object_mesh"))
scene.world.addComponent(object, VertexArray())
object_shader = scene.world.addComponent(object, ShaderGLDecorator(Shader(vertex_source=manos_animation_vertexShader, fragment_source=fragmentShader)))

object_mesh.vertex_attributes.append(object_vertex)
object_mesh.vertex_attributes.append(object_color)
object_mesh.vertex_attributes.append(joint_weights)
object_mesh.vertex_index.append(object_index)



#animation variables
play_animation = False
previous_time = time.time()
animation_time = 0.0
animation_duration = 5.0

#keyframes
keyframe_1 = {"angle_joint1": -30.0, "angle_joint2": -45.0}
keyframe_2 = {"angle_joint1": 60.0, "angle_joint2": 360.0}

angle_joint1 = keyframe_1["angle_joint1"]
angle_joint2 = keyframe_1["angle_joint2"]

current_angle_joint1 = keyframe_1["angle_joint1"]
current_angle_joint2 = keyframe_1["angle_joint2"]

#function to display the GUI
def displayGUI():
    global angle_joint1, angle_joint2, play_animation

    imgui.begin("ANIMATION")
    clicked, play_animation = imgui.checkbox("Play Animation", play_animation)

    #show sliders only when animation is off
    if not play_animation:
        _, angle_joint1 = imgui.drag_float("Joint 1 Angle", angle_joint1, change_speed=0.1)
        _, angle_joint2 = imgui.drag_float("Joint 2 Angle", angle_joint2, change_speed=0.1)

    imgui.end()


#function to interpolate between keyframes
def interpolate_keyframes(t):
    """
    Interpolates between keyframe_1 and keyframe_2 based on the parameter t (0 to 1).
    """
    global keyframe_1, keyframe_2
    angle_joint1 = (1 - t) * keyframe_1["angle_joint1"] + t * keyframe_2["angle_joint1"]
    angle_joint2 = (1 - t) * keyframe_1["angle_joint2"] + t * keyframe_2["angle_joint2"]
    return angle_joint1, angle_joint2


#function to display the object
def display_object(object_shader, angle_joint1, angle_joint2):
    global view, projMat

    M0 = util.identity()
    M1 = util.translate(0.5)
    M2 = util.translate(0.5)

    B0 = M0
    B1 = M0 @ M1
    B2 = M0 @ M1 @ M2

    B0_inv = np.linalg.inv(B0)
    B1_inv = np.linalg.inv(B1)
    B2_inv = np.linalg.inv(B2)

    M0_prime = util.identity()
    M1_prime = util.translate(0.5) @ util.rotate(axis=util.vec(1, 0, 1), angle=angle_joint1)
    M2_prime = util.translate(0.5) @ util.rotate(axis=util.vec(0, 1, 0), angle=angle_joint2)

    B0_prime = M0_prime
    B1_prime = M0_prime @ M1_prime
    B2_prime = M0_prime @ M1_prime @ M2_prime

    model = util.translate(0.0, -0.4, 0.0) @ util.scale(0.4)

    object_shader.setUniformVariable(key='M0', value=B0_prime @ B0_inv, mat4=True)
    object_shader.setUniformVariable(key='M1', value=B1_prime @ B1_inv, mat4=True)
    object_shader.setUniformVariable(key='M2', value=B2_prime @ B2_inv, mat4=True)
    object_shader.setUniformVariable(key='model', value=model, mat4=True)
    object_shader.setUniformVariable(key='view', value=view, mat4=True)
    object_shader.setUniformVariable(key='projection', value=projMat, mat4=True)


#main loop
running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "Elements: A CameraSystem Example", customImGUIdecorator = ImGUIecssDecorator2)
scene.world.traverse_visit(initUpdate, rootEntity)
eManager = scene.world.eventManager
gWindow = scene.renderWindow
gGUI = scene.gContext
renderGLEventActuator = RenderGLStateSystem()


#setup Events and add them to the EventManager
updateTRS = Event(name="OnUpdateTRS", id=100, value=None)
updateBackground = Event(name="OnUpdateBackground", id=200, value=None)
eManager._events[updateTRS.name] = updateTRS
eManager._events[updateBackground.name] = updateBackground
eManager._subscribers[updateTRS.name] = gGUI
eManager._subscribers[updateBackground.name] = gGUI
eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator
eManager._publishers[updateBackground.name] = gGUI
scene.world.traverse_visit(transUpdate, scene.world.root)


#initialize the camera
projMat = util.perspective(50.0, 1.0, 0.01, 100.0)
eye = util.vec(2.5, 2.5, 2.5)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
gWindow._myCamera = view # otherwise, an imgui slider must be moved to properly update


model_object = util.identity()

while running:
    view =  gWindow._myCamera
    scene.world.traverse_visit(transUpdate, scene.world.root)
    running = scene.render()
    #wireframe mode
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    current_time = time.time()
    dt = current_time - previous_time  #time difference between frames
    previous_time = current_time

    if play_animation:
        animation_time += dt
        if animation_time > animation_duration:
            animation_time = 0.0  # Loop the animation

        #calculate interpolation factor (t ranges from 0 to 1)
        t = (animation_time % animation_duration) / animation_duration
        current_angle_joint1, current_angle_joint2 = interpolate_keyframes(t)

    else:
        #when animation is off, use manual angles
        current_angle_joint1 = angle_joint1
        current_angle_joint2 = angle_joint2

    displayGUI()
    display_object(object_shader, current_angle_joint1, current_angle_joint2)

    view =  gWindow._myCamera
    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.render_post()

scene.shutdown()
