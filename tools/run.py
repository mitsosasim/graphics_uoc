"""Run an original Elements exercise, optionally capture its OpenGL framebuffer."""
import argparse, os, runpy, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXERCISES={'1.1':'01/ex11_4845.py','1.2':'01/ex12_4845.py','1.3':'01/ex13_4845.py','2.1':'02/ex21_4845.py','2.2':'02/ex22_4845.py','3.1':'03/ex31_4845.py'}
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('exercise',choices=EXERCISES)
p.add_argument('--elements',type=Path,default=ROOT/'vendor/Elements')
p.add_argument('--capture',type=Path)
p.add_argument('--frames',type=int,default=60)
a=p.parse_args()
sys.path.insert(0,str(a.elements.resolve()))
from Elements.pyGLV.GL.Scene import Scene
if os.environ.get('LIBGL_ALWAYS_SOFTWARE') == '1':
 import sdl2
 original_attribute=sdl2.SDL_GL_SetAttribute
 def software_attribute(attribute,value):
  if attribute in (sdl2.SDL_GL_ACCELERATED_VISUAL,sdl2.SDL_GL_MULTISAMPLEBUFFERS):value=0
  return original_attribute(attribute,value)
 sdl2.SDL_GL_SetAttribute=software_attribute
 original_window=sdl2.SDL_CreateWindow
 def create_window(*args):
  window=original_window(*args)
  if not window: raise RuntimeError(sdl2.SDL_GetError().decode())
  return window
 sdl2.SDL_CreateWindow=create_window
# The supplied assignment-2 Shader.py is an extension of the teaching framework.
# Load it as that module, without editing the external installation.
if a.exercise.startswith('2.'):
 import importlib.util
 name='Elements.pyGLV.GL.Shader'
 spec=importlib.util.spec_from_file_location(name,ROOT/'assignments/02/Shader.py')
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
if a.capture:
 from OpenGL.GL import glReadPixels,glGetIntegerv,GL_VIEWPORT,GL_RGB,GL_UNSIGNED_BYTE,glPixelStorei,GL_PACK_ALIGNMENT
 from PIL import Image
 import sdl2
 original=Scene.render_post
 count=0
 def post(scene):
  global count
  count+=1
  if a.exercise=="1.2":
   import Elements.pyECSS.math_utilities as util
   scene.renderWindow._myCamera=util.lookat(util.vec(5,4,7),util.vec(0,0,0),util.vec(0,1,0))
  if count>=a.frames:
   x,y,w,h=glGetIntegerv(GL_VIEWPORT)
   glPixelStorei(GL_PACK_ALIGNMENT,1)
   image=Image.frombytes('RGB',(int(w),int(h)),glReadPixels(0,0,w,h,GL_RGB,GL_UNSIGNED_BYTE))
   a.capture.parent.mkdir(parents=True,exist_ok=True)
   image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(a.capture)
   print('CAPTURED',a.exercise,flush=True)
   raise SystemExit(0)
  original(scene)
 Scene.render_post=post
runpy.run_path(str(ROOT/'assignments'/EXERCISES[a.exercise]),run_name='__main__')
