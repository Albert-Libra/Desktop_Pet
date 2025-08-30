import sys
import os

from PyQt5.QtCore import Qt, QTimer, QTime

from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction
from Puppy import PuppyAnimator
from Icons import IconManager

class GifWindow(QWidget):
   def puppy_context_menu(self, event):
      # 右键puppy时，icon飞出
      puppy_rect = self.puppy.label.geometry()
      center_x = puppy_rect.center().x()
      center_y = puppy_rect.center().y()
      self.icon_manager.show_icons(center_x, center_y)

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
      self.icon_manager.add_icon(tennis_png_path, -70, -70, 30, 30)  # 左上角

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
      print(f"Mouse press at: {event.pos()}, button: {event.button()}")
      
      # 优先icon点击
      if self.icon_manager.center_pos is not None:
         icon = self.icon_manager.icon_at_pos(event.pos())
         if icon:
            # tennis图标左键单击时退出
            if event.button() == Qt.LeftButton:
               print("Tennis icon clicked - exiting")
               QApplication.quit()
               return
            # 其它icon点击可扩展
            return
         else:
            # 点击空白，icon回收
            print("Clicked empty space - hiding icons")
            self.icon_manager.hide_icons()
            return
      
      # 右键puppy弹出icon
      if event.button() == Qt.RightButton and self.puppy.label.geometry().contains(event.pos()):
         print("Right clicking puppy - showing icons")
         self.puppy_context_menu(event)
         return
      
      # 其它交互
      handled = False
      if hasattr(self, 'puppy'):
         handled = self.puppy.mousePressEvent(event) or handled
      if not handled:
         super().mousePressEvent(event)

   def mouseMoveEvent(self, event):
      handled = False
      if hasattr(self, 'puppy'):
         handled = self.puppy.mouseMoveEvent(event) or handled
      if hasattr(self, 'icon_manager'):
         for icon in self.icon_manager.icons:
            if hasattr(icon, 'mouseMoveEvent'):
               handled = icon.mouseMoveEvent(event) or handled
      if not handled:
         super().mouseMoveEvent(event)

   def mouseReleaseEvent(self, event):
      handled = False
      if hasattr(self, 'puppy'):
         handled = self.puppy.mouseReleaseEvent(event) or handled
      if hasattr(self, 'icon_manager'):
         for icon in self.icon_manager.icons:
            if hasattr(icon, 'mouseReleaseEvent'):
               handled = icon.mouseReleaseEvent(event) or handled
      if not handled:
         super().mouseReleaseEvent(event)

   def _on_press_timeout(self):
      if self._drag_active:
         self._pick_up_mode = True
         self.puppy.set_puppy(self.puppy.pickup_gif_path)

def main():
   app = QApplication(sys.argv)
   window = GifWindow()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
