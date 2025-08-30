import sys
import os

from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction


# 小狗动作管理类

class PuppyAnimator:
   def __init__(self, parent, resource_dir, width=150, height=150):
      self.parent = parent
      self.label = QLabel(parent)
      self.fixed_width = width
      self.fixed_height = height
      self.label.setGeometry(0, 0, self.fixed_width, self.fixed_height)
      self.dance_gif_path = os.path.join(resource_dir, 'dance.gif')
      self.pickup_gif_path = os.path.join(resource_dir, 'pick_up.gif')
      self.rua_gif_path = os.path.join(resource_dir, 'rua.gif')
      self.appear_gif_path = os.path.join(resource_dir, 'appear1.gif')
      self._custom_width = None
      self._custom_height = None
      self._custom_x = None
      self._custom_y = None
      self.movie = None
      self.label.setAttribute(Qt.WA_TransparentForMouseEvents, False)

      # 交互状态
      self._drag_active = False
      self._drag_position = None
      self._press_timer = None
      self._press_time = None
      self._pick_up_mode = False
      self._is_rua_playing = False

   def set_puppy(self, gif_path, width=None, height=None, x=None, y=None):
      if self.movie:
         self.movie.stop()
      self.movie = QMovie(gif_path)
      self.label.setMovie(self.movie)
      self._custom_width = width
      self._custom_height = height
      self._custom_x = x
      self._custom_y = y
      self.movie.frameChanged.connect(self._resize_frame)
      self.movie.start()

   def _resize_frame(self):
      pixmap = self.movie.currentPixmap()
      if not pixmap.isNull():
         w = self._custom_width if self._custom_width else self.fixed_width
         h = self._custom_height if self._custom_height else self.fixed_height
         x = self._custom_x if self._custom_x is not None else 0
         y = self._custom_y if self._custom_y is not None else 0
         scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
         self.label.setPixmap(scaled)
         self.label.setGeometry(x, y, w, h)

   # 鼠标事件处理
   def mousePressEvent(self, event):
      if event.button() == Qt.LeftButton and self.label.geometry().contains(event.pos()):
         self._drag_active = True
         self._drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
         self._press_time = QTime.currentTime()
         self._pick_up_mode = False
         if self._press_timer:
            self._press_timer.stop()
         self._press_timer = QTimer(self.parent)
         self._press_timer.setSingleShot(True)
         self._press_timer.timeout.connect(self._on_press_timeout)
         self._press_timer.start(100)
         event.accept()
         return True
      return False

   def mouseReleaseEvent(self, event):
      if self._drag_active and event.button() == Qt.LeftButton:
         self._drag_active = False
         if self._press_timer:
            self._press_timer.stop()
         elapsed = self._press_time.msecsTo(QTime.currentTime()) if self._press_time else 0
         if not self._pick_up_mode and elapsed < 100:
            self.play_rua_once()
         else:
            self.set_puppy(self.dance_gif_path,100,100,25,25)
         self._pick_up_mode = False
         event.accept()
         return True
      return False

   def mouseMoveEvent(self, event):
      if self._drag_active and event.buttons() & Qt.LeftButton:
         self.parent.move(event.globalPos() - self._drag_position)
         event.accept()
         return True
      return False

   def _on_press_timeout(self):
      if self._drag_active:
         self._pick_up_mode = True
         self.set_puppy(self.pickup_gif_path)

   def play_rua_once(self):
      if self._is_rua_playing:
         return
      self._is_rua_playing = True
      self.set_puppy(self.rua_gif_path)
      def restore():
         self.set_puppy(self.dance_gif_path,100,100,25,25)
         self._is_rua_playing = False
      timer = QTimer(self.parent)
      timer.setSingleShot(True)
      timer.timeout.connect(restore)
      timer.start(1000)


# 图标管理类
class IconManager:
   def __init__(self, parent):
      self.parent = parent
      self.icons = []  # [(QLabel, x, y, w, h)]

   def add_icon(self, image_path, x, y, w, h):
      label = QLabel(self.parent)
      pixmap = QPixmap(image_path)
      pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
      label.setPixmap(pixmap)
      label.setGeometry(x, y, w, h)
      label.setAttribute(Qt.WA_TransparentForMouseEvents)
      label.show()
      self.icons.append(label)

class GifWindow(QWidget):
   def contextMenuEvent(self, event):
      # from PyQt5.QtWidgets import QMenu, QAction
      menu = QMenu(self)
      exit_action = QAction('退出', self)
      exit_action.triggered.connect(self.close)
      menu.addAction(exit_action)
      # 可在此添加更多菜单项
      # other_action = QAction('其他功能', self)
      # menu.addAction(other_action)
      menu.exec_(event.globalPos())

   def __init__(self, parent=None):
      super().__init__(parent)
      self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
      self.setAttribute(Qt.WA_TranslucentBackground)

      self.source_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/'))
      self.fixed_width = 150
      self.fixed_height = 150
      self.setFixedSize(self.fixed_width, self.fixed_height)

      # 小狗动画管理
      self.puppy = PuppyAnimator(self, self.source_dir_path, self.fixed_width, self.fixed_height)
      # 图标管理
      self.icon_manager = IconManager(self)
      # 添加网球图标
      tennis_png_path = os.path.join(self.source_dir_path, 'tennis.png')
      self.icon_manager.add_icon(tennis_png_path, 0, 0, 30, 30)

      self._drag_active = False
      self._drag_position = None
      self._press_timer = None
      self._press_time = None
      self._pick_up_mode = False
      self._is_rua_playing = False

      self._startup_appear()

   def _startup_appear(self):
      self.puppy.set_puppy(self.puppy.appear_gif_path)
      timer = QTimer(self)
      timer.setSingleShot(True)
      def show_dance():
         self.puppy.set_puppy(self.puppy.dance_gif_path,100,100,25,25)
      timer.timeout.connect(show_dance)
      timer.start(3000)

   def set_puppy(self, gif_path, width=None, height=None, x=None, y=None):
      self.puppy.set_puppy(gif_path, width, height, x, y)
   
   # def set_button(self, gif_path, width=None, height=None):

   # _resize_frame 由 PuppyAnimator 管理

   def mousePressEvent(self, event):
      # 优先分发给 puppy
      if self.puppy.mousePressEvent(event):
         return
      # 预留：icon交互
      # for icon in self.icon_manager.icons:
      #     if icon.geometry().contains(event.pos()):
      #         # 这里可实现 icon 的鼠标交互
      #         event.accept()
      #         return
      super().mousePressEvent(event)

   def mouseMoveEvent(self, event):
      if self.puppy.mouseMoveEvent(event):
         return
      # 预留：icon交互
      super().mouseMoveEvent(event)

   def mouseReleaseEvent(self, event):
      if self.puppy.mouseReleaseEvent(event):
         return
      # 预留：icon交互
      super().mouseReleaseEvent(event)

   def _on_press_timeout(self):
      if self._drag_active:
         self._pick_up_mode = True
         self.puppy.set_puppy(self.puppy.pickup_gif_path)

   def play_rua_once(self):
      if self._is_rua_playing:
         return
      self._is_rua_playing = True
      self.puppy.set_puppy(self.puppy.rua_gif_path)
      def restore():
         self.puppy.set_puppy(self.puppy.dance_gif_path,100,100,25,25)
         self._is_rua_playing = False
      timer = QTimer(self)
      timer.setSingleShot(True)
      timer.timeout.connect(restore)
      timer.start(1000)

def main():
   app = QApplication(sys.argv)
   window = GifWindow()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
