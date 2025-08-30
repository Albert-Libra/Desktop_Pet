from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
import math


class IconManager:
	def __init__(self, parent):
		self.parent = parent
		self.icons = []  # QLabel对象列表
		self.icon_targets = []  # 目标位置 (x, y, w, h)
		self.center_pos = None
		self.animation_timer = QTimer()
		self.animation_timer.timeout.connect(self._update_animation)
		self.animation_duration = 300  # 动画持续时间（毫秒）
		self.animation_start_time = 0
		self.is_showing = False  # 是否正在显示动画
		self.is_hiding = False   # 是否正在隐藏动画
		self.start_positions = []  # 动画开始位置
		self.end_positions = []    # 动画结束位置

	def add_icon(self, image_path, x, y, w, h):
		label = QLabel(self.parent)
		pixmap = QPixmap(image_path)
		pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		label.setPixmap(pixmap)
		label.setGeometry(0, 0, w, h)  # 初始在中心
		label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
		label.lower()  # 保证icon在puppy下方，不遮挡puppy
		label.setVisible(False)  # 初始隐藏
		self.icons.append(label)
		self.icon_targets.append((x, y, w, h))

	def _smoothstep(self, t):
		"""平滑插值函数"""
		return t * t * (3.0 - 2.0 * t)

	def _update_animation(self):
		"""更新动画帧"""
		elapsed = self.animation_timer.interval() * (self.animation_start_time)
		self.animation_start_time += 1
		
		if elapsed >= self.animation_duration:
			# 动画结束
			self.animation_timer.stop()
			if self.is_showing:
				self._finish_show_animation()
			elif self.is_hiding:
				self._finish_hide_animation()
			return
			
		# 计算动画进度 (0.0 到 1.0)
		progress = elapsed / self.animation_duration
		smooth_progress = self._smoothstep(progress)
		
		# 更新每个图标的位置
		for i, label in enumerate(self.icons):
			if not label.isVisible() and self.is_showing:
				label.setVisible(True)
				label.lower()  # 确保在puppy下方
				
			start_x, start_y = self.start_positions[i]
			end_x, end_y = self.end_positions[i]
			
			current_x = start_x + (end_x - start_x) * smooth_progress
			current_y = start_y + (end_y - start_y) * smooth_progress
			
			label.move(int(current_x), int(current_y))

	def _finish_show_animation(self):
		"""完成显示动画"""
		self.is_showing = False
		for i, label in enumerate(self.icons):
			end_x, end_y = self.end_positions[i]
			label.move(int(end_x), int(end_y))
			label.lower()  # 确保在puppy下方

	def _finish_hide_animation(self):
		"""完成隐藏动画"""
		self.is_hiding = False
		for label in self.icons:
			label.setVisible(False)
		self.center_pos = None

	def show_icons(self, center_x, center_y):
		"""从中心位置动画显示图标到目标位置"""
		if self.is_showing or self.is_hiding:
			return  # 如果正在动画中，忽略新的请求
			
		self.center_pos = (center_x, center_y)
		self.is_showing = True
		
		# 准备动画数据
		self.start_positions = []
		self.end_positions = []
		
		for i, label in enumerate(self.icons):
			x, y, w, h = self.icon_targets[i]
			target_x = center_x + x
			target_y = center_y + y
			
			# 起始位置是窗口中心
			window_center_x = self.parent.width() // 2
			window_center_y = self.parent.height() // 2
			
			self.start_positions.append((window_center_x, window_center_y))
			self.end_positions.append((target_x, target_y))
			
			# 设置初始位置和可见性
			label.setGeometry(window_center_x, window_center_y, w, h)
			label.setVisible(True)
			label.lower()  # 确保在puppy下方，不遮挡puppy
		
		# 开始动画
		self.animation_start_time = 0
		self.animation_timer.start(16)  # 约60fps

	def hide_icons(self):
		"""动画隐藏图标回到窗口中心"""
		if self.center_pos is None or self.is_hiding or self.is_showing:
			return
			
		self.is_hiding = True
		
		# 准备动画数据
		self.start_positions = []
		self.end_positions = []
		
		window_center_x = self.parent.width() // 2
		window_center_y = self.parent.height() // 2
		
		for label in self.icons:
			if label.isVisible():
				current_rect = label.geometry()
				self.start_positions.append((current_rect.x(), current_rect.y()))
				self.end_positions.append((window_center_x, window_center_y))
			else:
				self.start_positions.append((window_center_x, window_center_y))
				self.end_positions.append((window_center_x, window_center_y))
		
		# 开始动画
		self.animation_start_time = 0
		self.animation_timer.start(16)  # 约60fps

	def icon_at_pos(self, pos):
		"""检查指定位置是否有图标"""
		if self.is_showing or self.is_hiding:
			return None  # 动画期间不响应点击
		for label in self.icons:
			if label.isVisible() and label.geometry().contains(pos):
				return label
		return None
