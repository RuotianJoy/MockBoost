import sys
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import torch
from pytorch3d.io import load_objs_as_meshes
from pytorch3d.renderer import (
    look_at_view_transform,
    FoVPerspectiveCameras,
    PointLights,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
)
from pytorch3d.structures import Meshes
import matplotlib.pyplot as plt

class ObjRenderer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vertices = []
        self.faces = []

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def load_obj(self, file_name):
        with open(file_name, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == 'v':
                    self.vertices.append(list(map(float, parts[1:])))
                elif parts[0] == 'f':
                    self.faces.append([int(i.split('/')[0]) - 1 for i in parts[1:]])
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.update()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)

        if self.vertices.size > 0 and self.faces:
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex_idx in face:
                    glVertex3fv(self.vertices[vertex_idx])
            glEnd()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQt6 OBJ Renderer')

        self.renderer = ObjRenderer(self)
        self.renderer.load_obj('D:\\Project\\MockBoost\\Frame\\objmodel\\rp_mei_posed_001_30k.obj')  # 指定您的 OBJ 文件路径

        layout = QVBoxLayout()
        layout.addWidget(self.renderer)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置 OpenGL 表面格式
    format = QSurfaceFormat()
    format.setVersion(3, 3)
    format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    window = MainWindow()
    window.resize(800, 600)
    window.show()

    # Set the device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Load the 3D model
    obj_filename = "D:\\Project\\MockBoost\\Frame\\objmodel\\rp_mei_posed_001_30k.obj"
    mesh = load_objs_as_meshes([obj_filename], device=device)

    # Initialize a camera
    R, T = look_at_view_transform(2.7, 0, 180)  # distance, elevation, azimuth
    cameras = FoVPerspectiveCameras(device=device, R=R, T=T)

    # Define the settings for rasterization and shading
    raster_settings = RasterizationSettings(
        image_size=512,
        blur_radius=0.0,
        faces_per_pixel=1,
    )

    # Place a point light in front of the object
    lights = PointLights(device=device, location=[[2.0, 2.0, -2.0]])

    # Create a phong renderer by composing a rasterizer and a shader
    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(
            cameras=cameras,
            raster_settings=raster_settings
        ),
        shader=SoftPhongShader(
            device=device,
            cameras=cameras,
            lights=lights
        )
    )

    # Render the image
    images = renderer(mesh)
    plt.figure(figsize=(10, 10))
    plt.imshow(images[0, ..., :3].cpu().numpy())
    plt.axis("off")
    plt.show()

    sys.exit(app.exec())
