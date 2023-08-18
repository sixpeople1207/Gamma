import numpy as np
import argparse
import cv2
import glob
import os
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication , QMainWindow, QFileDialog, QAction, QLabel, QSizePolicy
from PyQt5.QtGui import *
import sys
from PyQt5.QtCore import Qt, QPoint, QCoreApplication, QObject, pyqtSignal, QEvent

form_class = uic.loadUiType('./main.ui')[0]

class MainWindows(QMainWindow, form_class):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
		self.btn_close.clicked.connect(QCoreApplication.instance().quit)
		self.btn_minimize.clicked.connect(self.window_minimized)
		self.btn_maximize_restore.clicked.connect(self.window_maximized)
		self.btn_open_file.clicked.connect(self.dialog_fileOpen)
		self.btn_Left_1.clicked.connect(self.change_page)
		self.btn_Left_2.clicked.connect(self.change_page)
		self.btn_Right_1.clicked.connect(self.change_page)
		self.btn_Right_2.clicked.connect(self.change_page)
		self.obj = []
		#UI업데이트 :  pyrcc5 -o rc_rc.py rc.qrc
		for i in range(0,6):
			self.imageLabel = QLabel()
			self.pixmap = QPixmap()
			self.pixmap.load('D:\\개인_프로그래밍 개발\\OpenCV_Source\\1.jpg')
			self.pixmap = self.pixmap.scaled(100,80)
			self.imageLabel.setPixmap(self.pixmap)
			self.layout_ImagePreview.addWidget(self.imageLabel, i)
			self.clickable(self.imageLabel).connect(self.zoom_Image)
			self.obj.append(self.imageLabel)
			#이미지 파일도 받아와서 클릭하면 크게 보여줄 수 있게 수정.
		self.isMaximized = 0
		self.btn_settings.clicked.connect(self.change_page)

	# Label에 클릭 이벤트를 연결.
	def clickable(self,widget):
		class Filter(QObject):
			clicked = pyqtSignal()	#pyside2 사용자는 pyqtSignal() -> Signal()로 변경
			def eventFilter(self, obj, event):
				if obj == widget:
					if event.type() == QEvent.MouseButtonPress:
						if obj.rect().contains(event.pos()):
							self.clicked.emit()
							print(obj)
							# The developer can opt for .emit(obj) to get the object within the slot.
							return True
				return False
		filter = Filter(widget)
		widget.installEventFilter(filter)
		return filter.clicked
	
	def zoom_Image(self):
		print(self.obj)

	def change_page(self):
		print(self.stackedWidget.currentIndex())
		if(self.stackedWidget.currentIndex()==0):
			self.stackedWidget.setCurrentIndex(1)
		elif(self.stackedWidget.currentIndex()==1):
			self.stackedWidget.setCurrentIndex(0)


	def dialog_fileOpen(self):
		fname = QFileDialog.getExistingDirectory(self, '폴더선택', '')
		if fname:
			print(fname)
			self.path_label.setText(fname)
			path = fname + '/*.jpg'
			file_list = glob.glob(path)
			print(f"\n  {len(file_list)}개의 이미지가 검색되었습니다.")
			# f = open(fname[0], 'r')
			# with f:
			# 	data = f.read()
			# 	self.path_label.setText(fname[0])

	def window_maximized(self):
		if(self.isMaximized == 0):
			self.setFixedSize(2400, 2400)
			self.isMaximized = 1
		elif(self.isMaximized == 1):
			self.setFixedSize(500, 500)
			self.isMaximized = 0

	def window_minimized(self):
		print(int(self.isMinimized()))
		self.showMinimized()
		print(int(self.isMinimized()))

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__press_pos = event.pos()  
			print(event.pos())

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.__press_pos = QPoint()

	def mouseMoveEvent(self, event):
		if not self.__press_pos.isNull():  
			self.move(self.pos() + (event.pos() - self.__press_pos))
			
def ui_auto_complete(ui_dir, ui_to_py_dir):
    encoding = 'utf-8'

    # UI 파일이 존재하지 않으면 아무 작업도 수행하지 않는다.
    if not os.path.isfile(ui_dir):
        print("The required file does not exist.")
        return
 
def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def check_lowImage():
	folder_name = "raw_image"
	current= os.getcwd() +f"\\{folder_name}"
	if not os.path.exists(current):	
		print("raw_image폴더가 없습니다.")
		return False
	else:
		print("raw_image확인!.")
		return True

if __name__ == '__main__': 
	app = QApplication(sys.argv)
	myWindow = MainWindows()
	myWindow.show()
	sys.exit(app.exec_())

	# if(isRaw):
	# 	folder_name = "new_images"
	# 	current= os.getcwd() +f"\\{folder_name}"
	# 	if not os.path.exists(current):
	# 		os.makedirs(current)
		
	# 	for li in file_list:
	# 		image = cv2.imread(li)
	# 		filename = li.split('\\')
	# 		img_gamma = adjust_gamma(image, 2.0) # 감마값 적용
	# 		dst = img_gamma + (img_gamma-255)*0.6 ## 콘트라스트 적용
	# 		newPath = f'./{folder_name}/{filename[len(filename)-1]}_.jpg'
	# 		msg = f'\r진행 수량 : {index+1}/{len(file_list)}(완료/총계)'
	# 		index+=1
	# 		print(msg, end='')
	# 		cv2.imwrite(newPath, dst)

	# 	if index == len(file_list):
	# 		print("작업이 완료 되었습니다.")
	# else:
	# 	print("폴더 확인 필요합니다.")