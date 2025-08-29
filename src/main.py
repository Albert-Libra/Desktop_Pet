import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

class GifWindow(QWidget):
   def __init__(self, gif_path, parent=None):
      super().__init__(parent)
      self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
      self.setAttribute(Qt.WA_TranslucentBackground)
      self.label = QLabel(self)
      self.label.setStyleSheet("background: transparent;")
      self.default_gif_path = gif_path
      self.pickup_gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/pick_up.gif'))
      # 固定窗口大小
      self.fixed_width = 150
      self.fixed_height = 150
      self.setFixedSize(self.fixed_width, self.fixed_height)
      self.label.setGeometry(0, 0, self.fixed_width, self.fixed_height)
      self._drag_active = False
      self._drag_position = None
      self.set_gif(self.default_gif_path)

   def set_gif(self, gif_path):
      if hasattr(self, 'movie'):
         self.movie.stop()
      self.movie = QMovie(gif_path)
      self.label.setMovie(self.movie)
      self.movie.frameChanged.connect(self._resize_frame)
      self.movie.start()

   def _resize_frame(self):
      # 获取当前帧并缩放到窗口大小，保持长宽比
      pixmap = self.movie.currentPixmap()
      if not pixmap.isNull():
         scaled = pixmap.scaled(self.fixed_width, self.fixed_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
         self.label.setPixmap(scaled)

   def mousePressEvent(self, event):
      if event.button() == Qt.LeftButton:
         self._drag_active = True
         self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
         self.set_gif(self.pickup_gif_path)
         event.accept()
      else:
         super().mousePressEvent(event)

   def mouseMoveEvent(self, event):
      if self._drag_active and event.buttons() & Qt.LeftButton:
         self.move(event.globalPos() - self._drag_position)
         event.accept()
      else:
         super().mouseMoveEvent(event)

   def mouseReleaseEvent(self, event):
      if self._drag_active and event.button() == Qt.LeftButton:
         self._drag_active = False
         self.set_gif(self.default_gif_path)
         event.accept()
      else:
         super().mouseReleaseEvent(event)

def main():
   app = QApplication(sys.argv)
   gif_path = os.path.join(os.path.dirname(__file__), '../resources/dance.gif')
   gif_path = os.path.abspath(gif_path)
   window = GifWindow(gif_path)
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
