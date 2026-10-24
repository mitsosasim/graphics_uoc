## DIMITRIOS ASIMAKOPOULOS CSD4845 ##
import os
import numpy as np
import imgui
import Elements.pyECSS.math_utilities as util
from Elements.pyECSS.Entity import Entity
from Elements.pyECSS.Component import BasicTransform, Camera, RenderMesh
from Elements.pyECSS.System import  TransformSystem, CameraSystem
from Elements.pyGLV.GL.Scene import Scene
from Elements.pyGLV.GUI.Viewer import RenderGLStateSystem
from Elements.pyGLV.GUI.ImguiDecorator import ImGUIecssDecorator
from Elements.pyGLV.GL.Shader import InitGLShaderSystem, Shader, ShaderGLDecorator, RenderGLShaderSystem
from Elements.pyGLV.GL.VertexArray import VertexArray
import Elements.utils.normals as norm
from Elements.pyGLV.GL.Textures import Texture
from Elements.utils.terrain import generateTerrain
from Elements.utils.obj_to_mesh import obj_to_mesh
from Elements.pyGLV.GL.Textures import get_texture_faces
from Elements.definitions import TEXTURE_DIR
from Elements.utils.terrain import generateTerrain
from Elements.utils.Shortcuts import displayGUI_text
from OpenGL.GL import glPolygonMode, GL_FRONT_AND_BACK, GL_LINE


example_description = \
"Assignement 2.2 first creates a scene with a sphere and a texture resembling the earth.\n\
Then we add some lighting using Blinn-Phong algorithm resembling the sun.\n\
Then we encapsulate the scene into a huge cube and apply texture to them creating the illusion of a scenery.\n\
Finally, we add a second source of light and also move the sun around the earth.\n"

#resize description window
def displayGUI_text(example_description):
    imgui.set_next_window_size(800, 100)
    imgui.begin("Example Description", flags=imgui.WINDOW_NO_RESIZE)
    imgui.text(example_description)
    imgui.end()

winWidth = 1024
winHeight = 1024
scene = Scene()

#create root entity and camera entities
rootEntity = scene.world.createEntity(Entity(name="RooT"))
entityCam1 = scene.world.createEntity(Entity(name="entityCam1"))
entityCam2 = scene.world.createEntity(Entity(name="entityCam2"))
trans1 = scene.world.addComponent(entityCam1, BasicTransform(name="trans1", trs=util.identity()))
trans2 = scene.world.addComponent(entityCam2, BasicTransform(name="trans2", trs=util.identity()))
scene.world.addEntityChild(rootEntity, entityCam1)
scene.world.addEntityChild(entityCam1, entityCam2)

#create the entities for the sphere, sun and skybox and their components
earth = scene.world.createEntity(Entity(name="earth"))
earth_trans = scene.world.addComponent(earth, BasicTransform(name="earth_trans", trs=util.identity()))
earth_mesh = scene.world.addComponent(earth, RenderMesh(name="earth_mesh"))
scene.world.addEntityChild(rootEntity, earth)

sun = scene.world.createEntity(Entity(name="sun"))
sun_trans = scene.world.addComponent(sun, BasicTransform(name="sun_trans", trs=util.identity()))
sun_mesh = scene.world.addComponent(sun, RenderMesh(name="sun_mesh"))
scene.world.addEntityChild(rootEntity, sun)

skybox = scene.world.createEntity(Entity(name="skybox"))
skybox_trans = scene.world.addComponent(skybox, BasicTransform(name="skybox_trans", trs=util.identity()))
skybox_mesh = scene.world.addComponent(skybox, RenderMesh(name="skybox_mesh"))
scene.world.addEntityChild(rootEntity, skybox)

#create the mesh for the skybox
minbox = -30
maxbox = 30
vertexSkybox = np.array([
    [minbox, minbox, maxbox, 1.0],
    [minbox, maxbox, maxbox, 1.0],
    [maxbox, maxbox, maxbox, 1.0],
    [maxbox, minbox, maxbox, 1.0],
    [minbox, minbox, minbox, 1.0],
    [minbox, maxbox, minbox, 1.0],
    [maxbox, maxbox, minbox, 1.0],
    [maxbox, minbox, minbox, 1.0]
],dtype=np.float32)
indexSkybox = np.array((1,0,3, 1,3,2,
                  2,3,7, 2,7,6,
                  3,0,4, 3,4,7,
                  6,5,1, 6,1,2,
                  4,5,6, 4,6,7,
                  5,4,0, 5,0,1), np.uint32)


#create the mesh for the spheres (earth and sun)
def generate_sphere(radius=1.0, sectors=36, stacks=18):
    vertices = []
    indices = []
    normals = []
    uv_coords = []

    for i in range(stacks + 1):
        stack_angle = np.pi / 2 - i * np.pi / stacks  #from pi/2 to -pi/2
        xy = radius * np.cos(stack_angle)  #r * cos(phi)
        z = radius * np.sin(stack_angle)   #r * sin(phi)

        for j in range(sectors + 1):
            sector_angle = j * 2 * np.pi / sectors  #from 0 to 2pi

            x = xy * np.cos(sector_angle)
            y = xy * np.sin(sector_angle)

            vertices.append([x, y, z, 1.0])
            normals.append([x / radius, y / radius, z / radius])

            #spherical texture coordinates (u, v)
            u = j / sectors            #longitude mapping
            v = i / stacks             #latitude mapping
            uv_coords.append([u, v])

    #generate indices
    for i in range(stacks):
        for j in range(sectors):
            first = (i * (sectors + 1)) + j
            second = first + sectors + 1

            #create the two triangles for the current quad
            indices.append([first, second, first + 1])
            indices.append([second, second + 1, first + 1])

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32).flatten()
    normals = np.array(normals, dtype=np.float32)
    uv_coords = np.array(uv_coords, dtype=np.float32)

    return vertices, indices, normals, uv_coords

vertexSphere, indexSphere, normalSphere, uv_coords = generate_sphere()

#ensure vertexSphere and indexSphere have the same number of dimensions for generateSmoothNormalsMesh
vertexSphere = vertexSphere.reshape(-1, 4)
indexSphere = indexSphere.flatten()

vertices, indices, _, normals = norm.generateSmoothNormalsMesh(vertexSphere , indexSphere)

#DEBUGGING
print("uv_coords", uv_coords)
print("normals", normals)
print("normalSphere", normalSphere)

#append the vertex attributes to the mesh and create the VertexArray and Shader
earth_mesh.vertex_attributes.append(vertices)
earth_mesh.vertex_attributes.append(normalSphere)
earth_mesh.vertex_attributes.append(uv_coords)
earth_mesh.vertex_index.append(indices)

earth_vArray = scene.world.addComponent(earth, VertexArray())
earth_shader = scene.world.addComponent(earth, ShaderGLDecorator(Shader(vertex_source = Shader.SIMPLE_TEXTURE_PHONG_VERT, fragment_source=Shader.SIMPLE_TEXTURE_PHONG_FRAG)))

#load the texture for the earth and pass it to the shader
texturePath = TEXTURE_DIR / "earth.jpg"
if not os.path.exists(texturePath):
    print("Texture file not found at:", texturePath)
else:
    print("Texture file found.")



#append the vertex attributes to the mesh and create the VertexArray and Shader for the sun
#sun_color = util.vec(1.0, 1.0, 0.0, 1.0)
sun_mesh.vertex_attributes.append(vertexSphere)
#sun_mesh.vertex_attributes.append(sun_color) #not needed because its hardcoded in the shader
sun_mesh.vertex_index.append(indexSphere)
sun_vArray = scene.world.addComponent(sun, VertexArray())
sun_shader = scene.world.addComponent(sun, ShaderGLDecorator(Shader(vertex_source = Shader.COLOR_VERT_MVP, fragment_source=Shader.COLOR_FRAG)))


#append the vertex attributes to the mesh and create the VertexArray and Shader for the skybox
vertexSkybox, indexSkybox, _ = norm.generateUniqueVertices(vertexSkybox,indexSkybox)
skybox_mesh.vertex_attributes.append(vertexSkybox)
skybox_mesh.vertex_index.append(indexSkybox)
vArraySkybox = scene.world.addComponent(skybox, VertexArray())
shaderSkybox = scene.world.addComponent(skybox, ShaderGLDecorator(Shader(vertex_source = Shader.STATIC_SKYBOX_VERT, fragment_source=Shader.STATIC_SKYBOX_FRAG)))


#add the systems to the scene and eventmanager
transUpdate = scene.world.createSystem(TransformSystem("transUpdate", "TransformSystem", "001"))
camUpdate = scene.world.createSystem(CameraSystem("camUpdate", "CameraUpdate", "200"))
renderUpdate = scene.world.createSystem(RenderGLShaderSystem())
initUpdate = scene.world.createSystem(InitGLShaderSystem())
running = True
scene.init(imgui=True, windowWidth = winWidth, windowHeight = winHeight, windowTitle = "ASSIGNMENT 1.1", customImGUIdecorator = ImGUIecssDecorator, openGLversion = 4)
scene.world.traverse_visit(initUpdate, scene.world.root)
texture = Texture(texturePath)
earth_shader.setUniformVariable(key='ImageTexture', value=texture, texture=True)
eManager = scene.world.eventManager
gWindow = scene.renderWindow
gGUI = scene.gContext
renderGLEventActuator = RenderGLStateSystem()
eManager._subscribers['OnUpdateWireframe'] = gWindow
eManager._actuators['OnUpdateWireframe'] = renderGLEventActuator
eManager._subscribers['OnUpdateCamera'] = gWindow
eManager._actuators['OnUpdateCamera'] = renderGLEventActuator


#camera settings
eye = util.vec(2.5, 2.5, 2.5)
target = util.vec(0.0, 0.0, 0.0)
up = util.vec(0.0, 1.0, 0.0)
view = util.lookat(eye, target, up)
projMat = util.perspective(50.0, 1.0, 1.0, 100.0)
m = np.linalg.inv(projMat @ view)
orthoCam = scene.world.addComponent(entityCam2, Camera(m, "orthoCam","Camera","500"))
gWindow._myCamera = view


#skybox texture
skybox_texture_locations = TEXTURE_DIR / "Skyboxes" / "Cloudy"
front_img = skybox_texture_locations / "front.jpg"
right_img = skybox_texture_locations / "right.jpg"
left_img = skybox_texture_locations / "left.jpg"
back_img = skybox_texture_locations / "back.jpg"
bottom_img = skybox_texture_locations / "bottom.jpg"
top_img = skybox_texture_locations / "top.jpg"
face_data = get_texture_faces(front_img,back_img,top_img,bottom_img,left_img,right_img)
shaderSkybox.setUniformVariable(key='cubemap', value=face_data, texture3D=True)

#gui function for lighting settings
def displayGUI():
    global Lposition, Lambientcolor, Lambientstr, LviewPos, Lcolor, Lintensity, Lposition2, Lcolor2, Lintensity2
    imgui.set_next_window_size(480, 250)
    imgui.begin("Lighting Settings", flags=imgui.WINDOW_NO_RESIZE)

    imgui.text("Lighting Controls")
    _, Lcolor = imgui.color_edit3("Sun Color", *Lcolor)
    _, Lposition = imgui.drag_float3("Sun Position", *Lposition, change_speed=0.1)
    _, Lintensity = imgui.drag_float("Sun Intensity", Lintensity, change_speed=0.01, min_value=0.0, max_value=10.0)
    _, Lcolor2 = imgui.color_edit3("2nd Light Color", *Lcolor2)
    _, Lposition2 = imgui.drag_float3("2nd Light Position", *Lposition2, change_speed=0.1)
    _, Lintensity2 = imgui.drag_float("2nd Light Intensity", Lintensity2, change_speed=0.01, min_value=0.0, max_value=10.0)
    _, Lambientcolor = imgui.color_edit3("Ambient Color", *Lambientcolor)
    _, Lambientstr = imgui.drag_float("Ambient Intensity", Lambientstr, change_speed=0.01, min_value=0.0, max_value=1.0)

    imgui.end()


#sun initial settings
Lposition = util.vec(5.0, 1.0, 2.0)
Lcolor = util.vec(1.0,1.0,1.0)
Lintensity = 1.0

# 2nd light initial settings
Lposition2 = util.vec(-5.0, 1.0, 2.0)
Lcolor2 = util.vec(1.0, 1.0, 1.0)
Lintensity2 = 1.0

#ambient light settings
Lambientcolor = util.vec(1.0, 1.0, 1.0)
Lambientstr = 0.5
LviewPos = util.vec(3.0, 3.0, 5.0)

#material settings
Mshininess = 0.4
Mcolor = util.vec(0.8, 0.0, 0.8)

#model transformations
model_sphere4 = earth_trans.trs @ util.translate(0.0, 0.0, 0.0) @ util.rotate((1.0,0.0,0.0), 90) @ util.scale(0.5)
model_sun = sun_trans.trs @ util.translate(5.0, 1.0, 2.0) @ util.scale(0.3)

#initial sun position
angle = 0.0

while running:
    running = scene.render()
    displayGUI_text(example_description)
    displayGUI()
    scene.world.traverse_visit(renderUpdate, scene.world.root)
    scene.world.traverse_visit_pre_camera(camUpdate, orthoCam)
    scene.world.traverse_visit(camUpdate, scene.world.root)
    view =  gWindow._myCamera

    #rotating the sun around the Y-axis
    angle += 0.001  #control rotation speed
    sun_x = 5.0 * np.cos(angle)
    sun_z = 5.0 * np.sin(angle)
    Lposition = util.vec(sun_x, 1.0, sun_z)

    #update the model transformation for the sun
    model_sun = sun_trans.trs @ util.translate(sun_x, 1.0, sun_z) @ util.scale(0.3)
    mvp_sun = projMat @ view @ model_sun
    sun_shader.setUniformVariable(key='modelViewProj', value=mvp_sun, mat4=True)

    #update the model transformation and uniform variables for the earth
    mvp_sphere4 = projMat @ view @ model_sphere4
    earth_shader.setUniformVariable(key='model', value=model_sphere4, mat4=True)
    earth_shader.setUniformVariable(key='View', value=view, mat4=True)
    earth_shader.setUniformVariable(key='Proj', value=projMat, mat4=True)
    earth_shader.setUniformVariable(key='ambientColor',value=Lambientcolor,float3=True)
    earth_shader.setUniformVariable(key='ambientStr',value=Lambientstr,float1=True)
    earth_shader.setUniformVariable(key='viewPos',value=LviewPos,float3=True)
    earth_shader.setUniformVariable(key='lightPos',value=Lposition,float3=True)
    earth_shader.setUniformVariable(key='lightColor',value=Lcolor,float3=True)
    earth_shader.setUniformVariable(key='lightIntensity',value=Lintensity,float1=True)
    earth_shader.setUniformVariable(key='shininess',value=Mshininess,float1=True)

    earth_shader.setUniformVariable(key='lightPos2',value=Lposition2,float3=True)
    earth_shader.setUniformVariable(key='lightColor2',value=Lcolor2,float3=True)
    earth_shader.setUniformVariable(key='lightIntensity2',value=Lintensity2,float1=True)

    #update the proj and view matrix for the skybox
    shaderSkybox.setUniformVariable(key='Proj', value=projMat, mat4=True)
    shaderSkybox.setUniformVariable(key='View', value=view, mat4=True)

    earth_shader.setUniformVariable(key='ImageTexture', value=texture, texture=True)


    scene.render_post()

scene.shutdown()
