import sys
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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
        self.renderer.load_obj('D:\\Project\\MockBoost\\Frame\\rp_mei_posed_001_30k.obj')  # 指定您的 OBJ 文件路径

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

    sys.exit(app.exec())
