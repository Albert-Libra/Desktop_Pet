import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

class GifWindow(QWidget):
   def contextMenuEvent(self, event):
      from PyQt5.QtWidgets import QMenu, QAction
      menu = QMenu(self)
      exit_action = QAction('退出', self)
      exit_action.triggered.connect(self.close)
      menu.addAction(exit_action)
      # 可在此添加更多菜单项
      # other_action = QAction('其他功能', self)
      # menu.addAction(other_action)
      menu.exec_(event.globalPos())
   def __init__(self, gif_path, parent=None):
      super().__init__(parent)
      self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
      self.setAttribute(Qt.WA_TranslucentBackground)
      self.label = QLabel(self)
      self.label.setStyleSheet("background: transparent;")
      self.dance_gif_path = gif_path
      self.pickup_gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/pick_up.gif'))
      self.rua_gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/rua.gif'))
      # 固定窗口大小
      self.fixed_width = 150
      self.fixed_height = 150
      self.setFixedSize(self.fixed_width, self.fixed_height)
      self.label.setGeometry(0, 0, self.fixed_width, self.fixed_height)
      self._drag_active = False
      self._drag_position = None
      self._press_timer = None
      self._press_time = None
      self._pick_up_mode = False
      self._is_rua_playing = False
      self.appear_gif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/appear1.gif'))
      self._startup_appear()

   def _startup_appear(self):
      from PyQt5.QtCore import QTimer
      self.set_gif(self.appear_gif_path)
      timer = QTimer(self)
      timer.setSingleShot(True)
      def show_dance():
         self.set_gif(self.dance_gif_path)
      timer.timeout.connect(show_dance)
      timer.start(3000)

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
         from PyQt5.QtCore import QTimer, QTime
         self._drag_active = True
         self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
         self._press_time = QTime.currentTime()
         self._pick_up_mode = False
         if self._press_timer:
            self._press_timer.stop()
         self._press_timer = QTimer(self)
         self._press_timer.setSingleShot(True)
         self._press_timer.timeout.connect(self._on_press_timeout)
         self._press_timer.start(100)  # 0.1秒
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
         if self._press_timer:
            self._press_timer.stop()
         from PyQt5.QtCore import QTime
         elapsed = self._press_time.msecsTo(QTime.currentTime()) if self._press_time else 0
         if not self._pick_up_mode and elapsed < 100:
            self.play_rua_once()
         else:
            self.set_gif(self.dance_gif_path)
         self._pick_up_mode = False
         event.accept()
      else:
         super().mouseReleaseEvent(event)

   def _on_press_timeout(self):
      # 0.1秒后还未松开，切换为pick_up
      if self._drag_active:
         self._pick_up_mode = True
         self.set_gif(self.pickup_gif_path)

   def play_rua_once(self):
      if self._is_rua_playing:
         return
      self._is_rua_playing = True
      self.set_gif(self.rua_gif_path)
      from PyQt5.QtCore import QTimer
      def restore():
         self.set_gif(self.dance_gif_path)
         self._is_rua_playing = False
      timer = QTimer(self)
      timer.setSingleShot(True)
      timer.timeout.connect(restore)
      timer.start(1000)  # 1秒

def main():
   app = QApplication(sys.argv)
   gif_path = os.path.join(os.path.dirname(__file__), '../resources/dance.gif')
   gif_path = os.path.abspath(gif_path)
   window = GifWindow(gif_path)
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
