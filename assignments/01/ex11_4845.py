## DIMITRIOS ASIMAKOPOULOS CSD4845 ##

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
from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE


# the text shown in GUI to describe each assignment
example_description = \
"Assignement 1 first creates a scene with a sphere only showing vertices and indeces.\n"
"Then we add some color transitioning from red to orange as we move vertically.\n"
"Then we color every vertex to its correspoding RGB values.\n"
"Finally, we render 5 different spheres in the scene"\

# window size
winWidth = 768
winHeight = 768

# scene object is created
scene = Scene()


### ENTITIES/COMPONENTS ###
# This serves as the root node of the entire scenegraph. All other entities
# (like cameras, meshes, etc.) will be children or descendants of this root node.
# The purpose of having a root is to organize the scenegraph.
# Since rootEntity is the parent, transformations or changes applied to the root can affect all its children.
rootEntity = scene.world.createEntity(Entity(name="RooT"))

# entityCam1 is created as a camera entity, which means it will define a view into the scene.
# It gets a transformation component trans1 initialized with an identity matrix (meaning no transformations are applied initially).
entityCam1 = scene.world.createEntity(Entity(name="entityCam1"))
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="trans1", trs=util.identity()))

# entityCam2 is created as a second camera with its own transformation component trans2, also initialized with an identity matrix.
# The Camera component added later to entityCam2 (orthoCam) defines it as an orthogonal projection camera.
# This type of camera uses parallel projection (unlike a perspective camera), often used for 2D or technical views.
# entityCam1 might represent a perspective camera (like a typical view of a 3D scene),
# while entityCam2 represents an orthographic camera (which could be used for a different rendering style or a technical view).
entityCam2 = scene.world.createEntity(Entity(name="entityCam2"))
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="trans2", trs=util.identity()))


# node4 entity is where the 3D geometry for the sphere will be attached.
node4 = scene.world.createEntity(Entity(name="node4"))

# trans4 is a component (BasicTransform) of node4 and defines the position, rotation, and scale of node4 in the scene.
# The BasicTransform component holds a transformation matrix (trs), which is used by the rendering system to position the sphere in the 3D scene.
# Initially, it's translated by (0, 0.5, 0), which moves the sphere slightly upwards.
trans4 = scene.world.addComponent(node4, BasicTransform(name="trans4", trs=util.translate(0,0.5,0)))

# mesh4 is a component (RenderMesh) of node4 which holds the geometry of the sphere (vertices, indices, color, material information etc).
# The RenderMesh component is responsible for defining the geometric information that can later be sent to the GPU for rendering.
mesh4 = scene.world.addComponent(node4, RenderMesh(name="mesh4"))


# These lines create parent-child relationships between the entities,
# building a scenegraph where the transformations and properties of child entities inherit from their parents.
# As we can see all entitites are children of rootEntity.
scene.world.addEntityChild(rootEntity, entityCam1)
scene.world.addEntityChild(entityCam1, entityCam2)
scene.world.addEntityChild(rootEntity, node4)


def generate_sphere(radius=1.0, sectors=36, stacks=18):
    vertices = []
    indices = []
    colors = []

    # Define spherical coordinates
    for i in range(stacks + 1):
        stack_angle = np.pi / 2 - i * np.pi / stacks  # from pi/2 to -pi/2
        xy = radius * np.cos(stack_angle)  # r * cos(phi)
        z = radius * np.sin(stack_angle)   # r * sin(phi)

        normalized_z = (z + radius) / (2 * radius)  # 1.2) z goes from -radius to +radius, normalize it to [0, 1]

        for j in range(sectors + 1):
            sector_angle = j * 2 * np.pi / sectors  # from 0 to 2pi
            x = xy * np.cos(sector_angle)
            y = xy * np.sin(sector_angle)

            vertices.append([x, y, z, 1.0])

            #1.1) standard white color
            color = [1.0, 1.0, 1.0, 1.0]

            #1.2) range between red (1, 0, 0) and yellow (1, 1, 0) based on height
            #color = [1.0, normalized_z, 0.0, 1.0]

            #1.3) Normal vector is the normalized position vector on the sphere
            # nx = x / radius
            # ny = y / radius
            # nz = z / radius
            # color = [(nx + 1) / 2, (ny + 1) / 2, (nz + 1) / 2, 1.0] # Map the normal vector components (nx, ny, nz) to color values [0, 1]

            colors.append(color)


    # Generate indices to connect the vertices
    for i in range(stacks):
        for j in range(sectors):
            first = (i * (sectors + 1)) + j
            second = first + sectors + 1

            # Create the two triangles for the current quad
            indices.append([first, second, first + 1])
            indices.append([second, second + 1, first + 1])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32), np.array(colors, dtype=np.float32)

# Generate sphere data
vertexSphere, indexSphere, colorSphere = generate_sphere()


# The TransformSystem is responsible for updating the transformations of all entities that have a BasicTransform component attached to them.
# This system calculates the transformation matrices (like translation, rotation, and scaling) and applies them to the relevant entities.
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))

# The CameraSystem is in charge of updating the view and projection matrices for all entities that have a Camera component attached.
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))

# The RenderGLShaderSystem is responsible for rendering objects using OpenGL shaders.
# Every entity that has a ShaderGLDecorator attached to it will use this system to render itself.
# It binds shaders, updates the necessary uniforms (e.g., modelViewProjection matrices), and draws the geometry.
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())

# The InitGLShaderSystem initializes all the OpenGL resources, ensuring shaders are ready.
initUpdate = scene.world.createSystem(InitGLShaderSystem())


### ADD SPHERE TO THE SCENE ###
# attach all attributes of a sphere (vertices, indeces, color) in a RenderMesh (mesh4) so that VertexArray can pick it up
mesh4.vertex_attributes.append(vertexSphere)
mesh4.vertex_attributes.append(colorSphere)
mesh4.vertex_index.append(indexSphere)
# adds a VertexArray component to the node4 entity.
# a VertexArray is an OpenGL structure that stores all the vertex attribute data (like position, color, normals) needed to render an object.
vArray4 = scene.world.addComponent(node4, VertexArray())
# applies a shader program to the entity to control how it is rendered visually (like coloring, lighting, etc.).
shaderDec4 = scene.world.addComponent(node4, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))


# initializes the OpenGL rendering context, setting up the window and GUI.
running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "ASSIGNMENT 1.1", customImGUIdecorator = ImGUIecssDecorator, openGLversion = 4)

### EVENT MANAGER ###
# This section of code sets up an event management system for handling user input and updates to the scene (such as wireframe view toggling and camera updates),
# and it configures the camera view and transformation matrices for objects like the sphere, terrain, and axes.
eManager = scene.world.eventManager # this handles events such as user input, mouse movements, key presses, or other triggers within the rendering system.
gWindow = scene.renderWindow # refers to the render window where the scene is displayed.
gGUI = scene.gContext # refers to the GUI context (e.g., ImGui), which handles the graphical user interface (GUI) elements within the rendering window.
renderGLEventActuator = RenderGLStateSystem() # this system will manage OpenGL-related state changes based on events (rendering updates, wireframe-solid modes).

# subscribes the render window (gWindow) to the OnUpdateWireframe event.
# This means that when the OnUpdateWireframe event is triggered, the window will be notified and respond accordingly.
eManager._subscribers['OnUpdateWireframe'] = gWindow

# renderGLEventActuator is set as the actuator for the OnUpdateWireframe event,
# meaning it will be responsible for handling the rendering state changes (like toggling between wireframe and solid rendering modes).
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator

# Similarly, the render window (gWindow) is also subscribed to the OnUpdateCamera event,
# and renderGLEventActuator will handle the camera updates when this event is triggered (e.g., moving the camera, zooming in/out).
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator


### CAMERA SETUP ###
# This block defines the camera view and projection using lookat() for the view matrix
# and perspective() for the projection matrix. The Camera component is added to entityCam2.
eye = util.vec(2.5, 2.5, 2.5) # located 2.5 inits away from each axe
target = util.vec(0.0, 0.0, 0.0) # the origin
up = util.vec(0.0, 1.0, 0.0) # meaning the y-axis is the up direction.
view = util.lookat(eye, target, up) # this matrix describes the camera's position, orientation, and the direction it's looking in.

# This matrix is responsible for converting 3D points in the scene to 2D points on the screen, taking into account depth and perspective.
# FOV: 50.0 degrees,  width/height ratio (aspect): 1.0, near clipping plane: 0.01, far clipping plane: 10.0
projMat = util.perspective(50.0, 1.0, 0.01, 10.0)
m = np.linalg.inv(projMat @ view)
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))

# sets the camera view matrix (view) to the window's camera property (_myCamera).
# otherwise, an imgui slider must be moved to properly update
gWindow._myCamera = view

# This retrieves the transformation matrix (trs) of the cube (represented by node4) and stores it in model_cube.
# This matrix includes translation, rotation, and scaling for the cube.
model_sphere4 = trans4.trs @ util.translate(0.0, 0.0, 0.0) @ util.rotate((1.0,0.0,0.0), 90) @ util.scale(1.0) # TAMPER WITH OBJECT's TRS

#1.4) ADD 4 MORE SPHERES
# node5 = scene.world.createEntity(Entity(name="node5"))
# node6 = scene.world.createEntity(Entity(name="node6"))
# node7 = scene.world.createEntity(Entity(name="node7"))
# node8 = scene.world.createEntity(Entity(name="node8"))

# trans5 = scene.world.addComponent(node5, BasicTransform(name="trans5", trs=util.translate(0, 0.5, 0)))
# trans6 = scene.world.addComponent(node6, BasicTransform(name="trans6", trs=util.translate(0, 0.5, 0)))
# trans7 = scene.world.addComponent(node7, BasicTransform(name="trans7", trs=util.translate(0, 0.5, 0)))
# trans8 = scene.world.addComponent(node8, BasicTransform(name="trans8", trs=util.translate(0, 0.5, 0)))

# mesh5 = scene.world.addComponent(node5, RenderMesh(name="mesh5"))
# mesh6 = scene.world.addComponent(node6, RenderMesh(name="mesh6"))
# mesh7 = scene.world.addComponent(node7, RenderMesh(name="mesh7"))
# mesh8 = scene.world.addComponent(node8, RenderMesh(name="mesh8"))

# mesh5.vertex_attributes.append(vertexSphere)
# mesh5.vertex_attributes.append(colorSphere)
# mesh5.vertex_index.append(indexSphere)

# mesh6.vertex_attributes.append(vertexSphere)
# mesh6.vertex_attributes.append(colorSphere)
# mesh6.vertex_index.append(indexSphere)

# mesh7.vertex_attributes.append(vertexSphere)
# mesh7.vertex_attributes.append(colorSphere)
# mesh7.vertex_index.append(indexSphere)

# mesh8.vertex_attributes.append(vertexSphere)
# mesh8.vertex_attributes.append(colorSphere)
# mesh8.vertex_index.append(indexSphere)

# scene.world.addEntityChild(rootEntity, node5)
# scene.world.addEntityChild(rootEntity, node6)
# scene.world.addEntityChild(rootEntity, node7)
# scene.world.addEntityChild(rootEntity, node8)

# vArray5 = scene.world.addComponent(node5, VertexArray())
# vArray6 = scene.world.addComponent(node6, VertexArray())
# vArray7 = scene.world.addComponent(node7, VertexArray())
# vArray8 = scene.world.addComponent(node8, VertexArray())

# shaderDec5 = scene.world.addComponent(node5, ShaderGLDecorator(Shader(vertex_source=Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))
# shaderDec6 = scene.world.addComponent(node6, ShaderGLDecorator(Shader(vertex_source=Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))
# shaderDec7 = scene.world.addComponent(node7, ShaderGLDecorator(Shader(vertex_source=Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))
# shaderDec8 = scene.world.addComponent(node8, ShaderGLDecorator(Shader(vertex_source=Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))

# model_sphere5 = trans5.trs @ util.translate(0.5, 0.5, 0.5)  @ util.scale(0.25)
# model_sphere6 = trans6.trs @ util.translate(-0.3, -0.7, 0.2) @ util.scale(0.22)
# model_sphere7 = trans7.trs @ util.translate(0.6, -1.8, 1.0)  @ util.scale(0.18)
# model_sphere8 = trans8.trs @ util.translate(-1.0, -0.4, 0.5) @ util.scale(0.3)


### MAIN LOOP ###
# is used to traverse through the scene's entity-component system starting from root (traverse_visit)
# and apply a specific system (initUpdate) to each relevant entity and component.
scene.world.traverse_visit(initUpdate, scene.world.root)

while running:
    running = scene.render() # calls the scene.render() method, which performs rendering for the current frame.
    displayGUI_text(example_description) # responsible for rendering a text description in the GUI
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) #1.1) set to wireframe mode by default
    scene.world.traverse_visit(renderUpdate, scene.world.root) # triggers the renderUpdate function across all components attached to scene.world.root.
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam) # responsible for performing camera-specific updates before the rendering occurs.
    scene.world.traverse_visit(camUpdate, scene.world.root) # updates the camera parameters to make sure everything is in sync before the next frame is rendered.
    view =  gWindow._myCamera # updates view via the imgui ensuring that any user interactions are reflected in the camera's view

    mvp_sphere4 = projMat @ view @ model_sphere4 # MVP matrix for the sphere
    shaderDec4.setUniformVariable(key='modelViewProj', value=mvp_sphere4, mat4=True) # passes the MVP matrix to the shader responsible for rendering the sphere

    #1.4) render 5 different spheres with some translation ans scaling done to them
    # mvp_sphere5 = projMat @ view @ model_sphere5
    # mvp_sphere6 = projMat @ view @ model_sphere6
    # mvp_sphere7 = projMat @ view @ model_sphere7
    # mvp_sphere8 = projMat @ view @ model_sphere8

    # shaderDec5.setUniformVariable(key='modelViewProj', value=mvp_sphere5, mat4=True)
    # shaderDec6.setUniformVariable(key='modelViewProj', value=mvp_sphere6, mat4=True)
    # shaderDec7.setUniformVariable(key='modelViewProj', value=mvp_sphere7, mat4=True)
    # shaderDec8.setUniformVariable(key='modelViewProj', value=mvp_sphere8, mat4=True)

    scene.render_post() # handles any post-processing tasks or cleanup required after rendering

scene.shutdown()
