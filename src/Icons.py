from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel


class IconManager:
	def __init__(self, parent):
		self.parent = parent
		self.icons = []  # [(QLabel, x, y, w, h)]
		self.icon_targets = []  # 目标位置 (x, y, w, h)
		self.center_pos = None

	def add_icon(self, image_path, x, y, w, h):
		label = QLabel(self.parent)
		pixmap = QPixmap(image_path)
		pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		label.setPixmap(pixmap)
		label.setGeometry(0, 0, w, h)  # 初始在中心
		label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
		label.lower()  # 保证icon在puppy下方
		label.setVisible(False)  # 初始隐藏
		self.icons.append(label)
		self.icon_targets.append((x, y, w, h))

	def show_icons(self, center_x, center_y):
		self.center_pos = (center_x, center_y)
		print(f"Showing icons at center: {center_x}, {center_y}")
		for i, label in enumerate(self.icons):
			x, y, w, h = self.icon_targets[i]
			# 直接移动到目标位置，先不用动画
			target_x = center_x + x
			target_y = center_y + y
			label.setGeometry(target_x, target_y, w, h)
			label.setVisible(True)
			label.raise_()  # 确保icon在最上层
			print(f"Icon {i} moved to: {target_x}, {target_y}")

	def hide_icons(self):
		if self.center_pos is None:
			return
		cx, cy = self.center_pos
		for i, label in enumerate(self.icons):
			w = label.width()
			h = label.height()
			label.move(cx, cy)
			label.setVisible(False)
		self.center_pos = None

	def icon_at_pos(self, pos):
		for label in self.icons:
			if label.isVisible() and label.geometry().contains(pos):
				return label
		return None
