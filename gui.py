import sys
import time
import re
import socket
import threading
import ctypes
import inspect

from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QGroupBox, QFormLayout, \
     QLabel, QPushButton, QGridLayout, QLineEdit, QTextEdit, QFormLayout, QComboBox, QCheckBox
from PyQt5.QtCore import pyqtSignal, QRect, QRegExp, Qt
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.Qt import QRegExpValidator, QIntValidator


class Temp_box_gui(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化界面
        self.initUI()
        # 界面显示
        self.show()

    # 初始化界面
    def initUI(self):
        # 窗口大小及居中
        self.setGeometry(400, 400, 800, 550)
        self.center()
        # 标题
        self.setWindowTitle("温箱控制")
        # 各UI元素
        self.initButton()
        self.initLabel()
        self.initLineEdit()
        self.initcombox()
        self.initchkbox()
        self.group_display()
        self.group_option()
        self.group_serial()
        self.group_temp_switch()
        self.group_cyclic_and_log_switch()

    # 窗口居中
    def center(self):
        # 得到了主窗口的大小
        qr = self.frameGeometry()
        # 获取屏幕的分辨率
        cp = QDesktopWidget().availableGeometry().center()
        # 得到中间点的位置
        qr.moveCenter(cp)
        # 把自己窗口的中心点放到qr的中心点
        self.move(qr.topLeft())

    # 初始化Label
    def initLabel(self):
        dis = []
        self.lab_current_temp = QLabel(self)
        self.lab_current_temp.setText("当前温度")
        dis.append(self.lab_current_temp)
        # self.lab_current_set_temp = QLabel(self)
        # self.lab_current_set_temp.setText("当前设定温度")
        # dis.append(self.lab_current_set_temp)
        self.lab_final_temp = QLabel(self)
        self.lab_final_temp.setText("目标温度")
        dis.append(self.lab_final_temp)
        self.lab_temp_slope = QLabel(self)
        self.lab_temp_slope.setText("转换时间")
        dis.append(self.lab_temp_slope)
        self.lab_current_switch = QLabel(self)
        self.lab_current_switch.setText("运行状态")
        dis.append(self.lab_current_switch)

        for lab in dis:
            lab.setFont(QFont("Roman times", 20, QFont.Bold))
            lab.setAlignment(Qt.AlignCenter)

        dis = []
        self.le_current_temp = QLabel(self)
        dis.append(self.le_current_temp)
        # self.le_current_set_temp = QLabel(self)
        # dis.append(self.le_current_set_temp)
        self.le_final_temp = QLabel(self)
        dis.append(self.le_final_temp)
        self.le_temp_slope = QLabel(self)
        dis.append(self.le_temp_slope)
        self.le_currnet_switch = QLabel(self)
        dis.append(self.le_currnet_switch)

        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.blue)

        for le in dis:
            le.setEnabled(False)
            le.setFixedWidth(180)
            le.setFixedHeight(150)
            # le.setText("-88.88")
            le.setFont(QFont("Roman times", 40, QFont.Bold))
            le.setAlignment(Qt.AlignCenter)
            le.setStyleSheet("border:2px solid gray;")
            le.setPalette(pe)

        # self.le_currnet_switch.setText("OFF")

        # cyclic = []

        # self.lab_cyclic_start_temp = QLabel(self)
        # self.lab_cyclic_start_temp.setText("开始温度")
        # cyclic.append(self.lab_cyclic_start_temp)
        # self.lab_cyclic_stop_temp = QLabel(self)
        # self.lab_cyclic_stop_temp.setText("结束温度")
        # cyclic.append(self.lab_cyclic_stop_temp)

        # for lab in cyclic:
        #     lab.setFont(QFont("Roman times",20,QFont.Bold))
        #     lab.setAlignment(Qt.AlignCenter)

    # 初始化LineEdit
    def initLineEdit(self):
        data_reg = QRegExp('[-\.0-9]+')
        data_validator = QRegExpValidator(self)
        data_validator.setRegExp(data_reg)

        temp_control = []
        self.le_temp_set = QLineEdit(self)
        temp_control.append(self.le_temp_set)
        self.le_slope_set = QLineEdit(self)
        temp_control.append(self.le_slope_set)

        for le in temp_control:
            le.setFixedWidth(150)
            le.setFixedHeight(60)
            le.setFont(QFont("Roman times", 20, QFont.Bold))
            le.setAlignment(Qt.AlignCenter)
            le.setValidator(data_validator)

        cyclic = []
        self.le_cyclic_start_temp = QLineEdit(self)
        self.le_cyclic_start_temp.setPlaceholderText("最低温度")
        cyclic.append(self.le_cyclic_start_temp)
        self.le_cyclic_stop_temp = QLineEdit(self)
        self.le_cyclic_stop_temp.setPlaceholderText("最高温度")
        cyclic.append(self.le_cyclic_stop_temp)

        for le in cyclic:
            le.setFixedWidth(150)
            le.setFixedHeight(60)
            le.setFont(QFont("Roman times", 20, QFont.Bold))
            le.setAlignment(Qt.AlignCenter)
            le.setValidator(data_validator)

    # 初始化按钮
    def initButton(self):
        temp_control = []
        self.btn_stop = QPushButton('停止温控', self)
        temp_control.append(self.btn_stop)
        self.btn_stop.setFixedWidth(150)
        self.btn_stop.setFixedHeight(75)
        self.btn_open = QPushButton("开始温控", self)
        temp_control.append(self.btn_open)
        self.btn_open.setFixedWidth(150)
        self.btn_open.setFixedHeight(110)
        self.btn_temp_set = QPushButton("温度设置", self)
        temp_control.append(self.btn_temp_set)
        self.btn_slope_set = QPushButton("时间设置", self)
        temp_control.append(self.btn_slope_set)
        self.btn_serial_open = QPushButton("打开", self)
        temp_control.append(self.btn_serial_open)
        self.btn_serial_open.setFixedHeight(80)
        self.btn_serial_close = QPushButton("关闭", self)
        temp_control.append(self.btn_serial_close)
        self.btn_serial_close.setFixedHeight(80)
        self.btn_cyclic_temp_start = QPushButton("开始循环", self)
        temp_control.append(self.btn_cyclic_temp_start)
        self.btn_cyclic_temp_stop = QPushButton("结束循环", self)
        temp_control.append(self.btn_cyclic_temp_stop)

        self.btn_draw_temperature = QPushButton('绘制温度曲线', self)
        self.btn_draw_temperature.setFont(QFont("Roman times", 15, QFont.Bold))
        self.btn_draw_temperature.setEnabled(False)

        for btn in temp_control:
            btn.setFont(QFont("Roman times", 20, QFont.Bold))
            btn.setEnabled(False)

        self.btn_serial_open.setEnabled(True)

    # 初始化下拉选择框
    def initcombox(self):
        self.cbx_serial = QComboBox(self)
        self.cbx_serial.setFixedWidth(140)
        self.cbx_serial.setFixedHeight(70)
        # self.cbx_serial.addItems(["COM1", "COM2"])
        self.cbx_serial.setFont(QFont("Roman times", 25, QFont.Bold))

    # 初始化单选框
    def initchkbox(self):
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.gray)

        self.chk_box_log = QCheckBox()
        self.chk_box_log.setText("是否记录LOG")
        # self.chk_box_log.setFixedWidth(140)
        # self.chk_box_log.setFixedHeight(70)
        self.chk_box_log.setFont(QFont("Roman times", 15, QFont.Bold))
        self.chk_box_log.setPalette(pe)
        self.chk_box_log.setStyleSheet("border:2px solid gray;")

    # 显示框
    def group_display(self):
        # 定义及title
        group = QGroupBox(self)
        group.setGeometry(QRect(10, 10, 780, 230))
        # group.setTitle("显示框")
        self.group_display_layout = QGridLayout(group)

        self.group_display_layout.addWidget(self.lab_current_temp, 0, 0)
        self.group_display_layout.addWidget(self.le_current_temp, 1, 0)
        # self.group_display_layout.addWidget(self.lab_current_set_temp, 0, 1)
        # self.group_display_layout.addWidget(self.le_current_set_temp, 1, 1)
        self.group_display_layout.addWidget(self.lab_final_temp, 0, 2)
        self.group_display_layout.addWidget(self.le_final_temp, 1, 2)
        self.group_display_layout.addWidget(self.lab_temp_slope, 0, 3)
        self.group_display_layout.addWidget(self.le_temp_slope, 1, 3)
        self.group_display_layout.addWidget(self.lab_current_switch, 0, 4)
        self.group_display_layout.addWidget(self.le_currnet_switch, 1, 4)

    # 温箱控制框
    def group_option(self):
        # 定义及title
        group = QGroupBox(self)
        group.setGeometry(QRect(210, 250, 380, 130))
        # group.setTitle("温箱控制框")
        self.group_option_layout = QGridLayout(group)
        self.group_option_layout.setHorizontalSpacing(30)
        # self.group_option_layout.setVerticalSpacing(30)

        self.group_option_layout.addWidget(self.le_temp_set, 0, 0)
        self.group_option_layout.addWidget(self.btn_temp_set, 1, 0)
        self.group_option_layout.addWidget(self.le_slope_set, 0, 1)
        self.group_option_layout.addWidget(self.btn_slope_set, 1, 1)
        # self.group_option_layout.addWidget(self.btn_open, 0, 2)
        # self.group_option_layout.addWidget(self.btn_stop, 1, 2)

    # 温箱开关框
    def group_temp_switch(self):
        # 定义及title
        group = QGroupBox(self)
        group.setGeometry(QRect(600, 250, 190, 290))
        # group.setTitle("温箱开关框")
        self.group_switch_layout = QGridLayout(group)
        self.group_switch_layout.setHorizontalSpacing(30)
        # self.group_option_layout.setVerticalSpacing(30)

        self.group_switch_layout.addWidget(self.btn_open, 0, 0)
        self.group_switch_layout.addWidget(self.btn_stop, 1, 0)
        self.group_switch_layout.addWidget(self.btn_draw_temperature, 2, 0)
        self.group_switch_layout.addWidget(self.chk_box_log, 3, 0)

    # 温箱温度循环
    def group_cyclic_and_log_switch(self):
        # 定义及title
        group = QGroupBox(self)
        group.setGeometry(QRect(210, 385, 380, 155))
        # group.setTitle("循环及LOG框")
        self.group_cyclic_layout = QGridLayout(group)
        self.group_cyclic_layout.setHorizontalSpacing(30)
        # self.group_option_layout.setVerticalSpacing(30)

        # self.group_cyclic_layout.addWidget(self.lab_cyclic_start_temp, 0, 0)
        # self.group_cyclic_layout.addWidget(self.lab_cyclic_stop_temp, 0, 1)
        self.group_cyclic_layout.addWidget(self.le_cyclic_start_temp, 0, 0)
        self.group_cyclic_layout.addWidget(self.le_cyclic_stop_temp, 0, 1)
        self.group_cyclic_layout.addWidget(self.btn_cyclic_temp_start, 1, 0)
        self.group_cyclic_layout.addWidget(self.btn_cyclic_temp_stop, 1, 1)

    # 串口选择框
    def group_serial(self):
        # 定义及title
        group = QGroupBox(self)
        group.setGeometry(QRect(10, 250, 190, 290))
        # group.setTitle("串口选择")
        self.group_serial_layout = QGridLayout(group)
        self.group_serial_layout.setContentsMargins(10, 10, 10, 10)

        self.group_serial_layout.addWidget(self.cbx_serial, 0, 0)
        self.group_serial_layout.addWidget(self.btn_serial_open, 1, 0)
        self.group_serial_layout.addWidget(self.btn_serial_close, 2, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Temp_box_gui()
    sys.exit(app.exec_())