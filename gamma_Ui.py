import numpy as np
import argparse
import cv2
import glob
import os
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication , QMainWindow, QFileDialog, QAction, QLabel, QSizePolicy, QMessageBox
from PyQt5.QtGui import *
import sys
from PyQt5.QtCore import QMetaObject, Qt,QPoint, QCoreApplication, QObject, pyqtSignal, QEvent, QRect, QThread
import time

class Thread1(QThread):
	sig = pyqtSignal(int)
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.index=0
	def run(self):
		try:
			# for i in range(len(self.parent.path_li)):
				# self.sig.emit(i)
				# self.parent.progressBar.setValue(i+1)
				# QThread.sleep(1)
			for li in self.parent.path_li:
				self.sig.emit(self.index)
				filename = li.split('\\')
				img_array = np.fromfile(li, np.uint8)
				curImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
				#에러발생
				img_gamma = adjust_gamma(curImg, 2.0) # 감마값 적용
				dst = img_gamma + (img_gamma-255)*0.6 ## 콘트라스트 적용
				newPath = f'./{self.parent.path_li}/{filename[len(filename)-1]}_.jpg'
				msg = f'\r진행 수량 : {self.index+1}/{len(self.parent.path_li)}(완료/총계)'
				self.index+=1
				print(msg, end='')
				cv2.imwrite(newPath, dst)
			if self.index == len(self.parent.path_li):
				print("작업이 완료 되었습니다.")
				QMessageBox.information(self.parent,"Image Load","이미지 저장완료")

		except Exception as E:
			print(E)	

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
		self.index = 0
		self.objName_Li = [self.pic_1,self.pic_2,self.pic_3,self.pic_4,self.pic_5,self.pic_6,self.pic_7]
		self.obj = []
		self.filters = []
		self.path_li = []
		self.thread = Thread1(self)
		self.btn_save.clicked.connect(lambda: self.thread.start())
		self.thread.sig.connect(self.progressBar_SetValue)
		#UI업데이트 :  pyrcc5 -o rc_rc.py rc.qrc

			#이미지 파일도 받아와서 클릭하면 크게 보여줄 수 있게 수정.
		self.isMaximized = 0
		self.btn_settings.clicked.connect(self.progressBar_SetValue)

		# self.btn_save.clicked.connect(self.actionFunction1)

	def progressBar_SetValue(self, t):
		self.progressBar.setValue(t)

	def clickable(self,widget,objlist,filters):
		class Filter(QObject):
			clicked = pyqtSignal()	#pyside2 사용자는 pyqtSignal() -> Signal()로 변경
			def eventFilter(self, obj, event):
				if obj == widget:
					if event.type() == QEvent.MouseButtonPress:
						if obj.rect().contains(event.pos()):
							self.clicked.emit()
							# for objName in objlist:
							# 	if objName == obj:
							# 		print("dfdd")
							return True
				return False
		filter = Filter(widget)
		widget.installEventFilter(filter)
		#Filters List에 Filter리스트 저장. Filter의 순서가 Label이미지 순서와 동일.
		filters.append(filter)
		return filter.clicked
	
	def zoom_Image(self):
		# Self.sender와 Filters 리스트의 index 필터링함.
		index = 0
		# self.pathes.append('D:\\개인_프로그래밍 개발\\OpenCV_Source\\1.jpg')
		for filter in self.filters:
			if self.sender() == filter:
				pixmap = QPixmap(self.path_li[index])
				pixmap = pixmap.scaled(500,300)
				self.pic_Zoom.setPixmap(pixmap)
				self.pic_Zoom.setAlignment(Qt.AlignVCenter)
				print(self.objName_Li[index])
			index += 1
		# if self.clickedList.count > 0:
		# 	print(sender.findChild(self.clickedList[0]))
		# if len(self.clickedList) > 0:
		# 	print(self.clickedList[len(self.clickedList)])
	
	def change_page(self):
		print(self.stackedWidget.currentIndex())
		if(self.stackedWidget.currentIndex()==0):
			self.stackedWidget.setCurrentIndex(1)
		elif(self.stackedWidget.currentIndex()==1):
			self.stackedWidget.setCurrentIndex(0)

	def dialog_fileOpen(self):
		fname = QFileDialog.getExistingDirectory(self, '폴더선택', '')
		if fname:
			self.path_label.setText(fname)
			path = fname + '/*.jpg'
			file_list = glob.glob(path)
			self.path_li = file_list
			self.show_imgae()
			#ProgressBar 최대값 조정.
			self.progressBar.setRange(0, len(self.path_li))

	def show_imgae(self):
		self.label_total_count.setText(str(len(self.path_li))+" 개")
		for i in range(0,7):
			self.imageLabel = self.objName_Li[i]
			self.pixmap = QPixmap()
			# self.pathes.append('D:\\개인_프로그래밍 개발\\OpenCV_Source\\1.jpg')
			self.pixmap.load(self.path_li[i])
			self.pixmap = self.pixmap.scaled(100,80)
			self.imageLabel.setPixmap(self.pixmap)
			self.imageLabel.setAlignment(Qt.AlignVCenter)
			# self.layout_ImagePreview.addWidget(self.imageLabel, i)
			self.obj.append(self.imageLabel)
			self.clickable(self.imageLabel,self.obj,self.filters).connect(self.zoom_Image)
		QMessageBox.information(self,"Image Load","이미지 로드완료")
	
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

	