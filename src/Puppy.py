import os

from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

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