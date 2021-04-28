import queue
import threading
import time
import os

import serial.tools.list_ports

from modbus import *
from gui import *
from draw_temperature import *


class Main(Temp_box_gui, ModBus):
    def __init__(self):
        super().__init__()
        self.add_coms()
        self.cmd_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.cmd_lock = threading.Lock()
        self.bind_ui_func()
        self.listen_thread = ""
        self.log_file = ""
        self.cyclic_temp_run_flag = False
        self.cyclic_low_temp = None
        self.cyclic_high_temp = None

    def bind_ui_func(self):
        self.btn_serial_open.clicked.connect(self.open_serial)
        self.btn_serial_close.clicked.connect(self.close_serial)
        self.btn_temp_set.clicked.connect(self.set_temperature_by_btn)
        self.btn_slope_set.clicked.connect(self.set_temperature_slope_by_btn)
        self.btn_open.clicked.connect(self.switch_temperature_box_on_by_btn)
        self.btn_stop.clicked.connect(self.switch_temperature_box_off_by_btn)
        self.chk_box_log.stateChanged.connect(self.open_close_log_record)
        self.btn_cyclic_temp_start.clicked.connect(self.start_cyclic_run)
        self.btn_cyclic_temp_stop.clicked.connect(self.stop_cyclic_run)
        self.btn_draw_temperature.clicked.connect(self.draw_temperature)

    def add_coms(self):
        port_list = list(serial.tools.list_ports.comports())
        for each_port in port_list:
            self.cbx_serial.addItem(each_port[0])

    def listen_modbus(self):
        while True:
            _start = time.time()
            self.cmd_lock.acquire()
            self.display_temperature()
            self.cmd_lock.release()
            _sleep = 1 - (time.time() - _start)
            if _sleep > 0:
                time.sleep(_sleep)

    def display_temperature(self):
        result = self.read_holding_registers()
        try:
            self.le_current_temp.setText(
                str(result["temperature_measurement"] / 100))
            self.le_final_temp.setText(
                str(result["temperature_set_final"] / 100))
            self.le_temp_slope.setText(str(result["temperature_slope"] / 100))
            if result["run_switch"] == SWITCH_ON:
                self.le_currnet_switch.setText("ON")
            elif result["run_switch"] == SWITCH_OFF:
                self.le_currnet_switch.setText("OFF")
            else:
                self.le_currnet_switch.setText("ERROR")
            self.record_log(str(result))

            if self.cyclic_temp_run_flag:
                if result["temperature_measurement"] / 100 <= self.cyclic_low_temp and result[
                        "temperature_set_final"] / 100 != self.cyclic_high_temp:
                    self.set_temperature(self.cyclic_high_temp)
                    self.record_log("Set temperature: %d" %
                                    self.cyclic_high_temp)
                if result["temperature_measurement"] / 100 >= self.cyclic_high_temp and result[
                        "temperature_set_final"] / 100 != self.cyclic_low_temp:
                    self.set_temperature(self.cyclic_low_temp)
                    self.record_log("Set temperature: %d" %
                                    self.cyclic_low_temp)

        except Exception as e:
            self.le_current_temp.setText("None")
            self.le_final_temp.setText("None")
            self.le_temp_slope.setText("None")
            self.le_currnet_switch.setText("None")
            self.record_log("Read temperature failed: %s" % str(e))

    def enable_temp_control_btn(self, switch):
        if switch == True or switch == False:
            self.btn_slope_set.setEnabled(switch)
            self.btn_temp_set.setEnabled(switch)
            self.btn_open.setEnabled(switch)
            self.btn_stop.setEnabled(switch)
            self.btn_cyclic_temp_start.setEnabled(switch)
            self.btn_cyclic_temp_stop.setEnabled(False)

    def open_serial(self):
        com = self.cbx_serial.currentText()
        try:
            self.init_master(com)
            self.listen_thread = threading.Thread(target=self.listen_modbus,
                                                  daemon=True)
            self.listen_thread.start()
            self.btn_serial_close.setEnabled(True)
            self.btn_serial_open.setEnabled(False)
            self.cbx_serial.setEnabled(False)
            self.enable_temp_control_btn(True)
            self.record_log("Open Serial")
        except Exception as e:
            self.record_log("Open Seerial failed: %s" % e)
            self.close_serial()

    def close_serial(self):
        try:
            self.stop_thread(self.listen_thread)
            self.close_master()
            self.btn_serial_close.setEnabled(False)
            self.btn_serial_open.setEnabled(True)
            self.cbx_serial.setEnabled(True)
            self.enable_temp_control_btn(False)
            self.record_log("Close Serial")
        except Exception as e:
            self.record_log("Close Serial failed: %s" % e)

    def set_temperature_by_btn(self):
        temp = self.le_temp_set.displayText()
        try:
            temp = float(temp)
            if temp < LOW_TEMPERATURE or temp > HIGH_TEMPERATURE:
                self.record_log("Set temperature failed: %d" % temp)
                return
            else:
                self.cmd_lock.acquire()
                self.set_temperature(temp)
                self.cmd_lock.release()
                self.record_log("Set temgperature: %d" % temp)
        except Exception as e:
            self.record_log("Set temgperature failed: %s" % e)

    def set_temperature_slope_by_btn(self):
        slope = self.le_slope_set.displayText()
        try:
            slope = float(slope)
            if slope < LOW_SLOPE or slope > HIGHT_SLOPE:
                self.record_log("Set temperature slope failed: %d" % slope)
                return
            else:
                self.cmd_lock.acquire()
                self.set_temperature_slope(slope)
                self.cmd_lock.release()
                self.record_log("Set temperature slope: %d" % slope)
        except Exception as e:
            self.record_log("Set temperature slope failed: %s" % e)

    def switch_temperature_box_on_by_btn(self):
        self.cmd_lock.acquire()
        self.switch_temperature_box_on()
        self.cmd_lock.release()
        self.record_log("Switch box on")

    def switch_temperature_box_off_by_btn(self):
        self.cmd_lock.acquire()
        self.switch_tempreature_box_off()
        self.cmd_lock.release()
        self.record_log("Switch box off")

    def record_log(self, log):
        # 添加时间戳
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time()))
        log = cur_time + ": " + log + "\n"
        # 加入队列
        if self.chk_box_log.isChecked():
            self.log_queue.put(log)

    def save_log_to_file(self):
        while True:
            with open(self.log_file, "a+") as f:
                # 读取队列消息
                log = self.log_queue.get()
                print(log)
                # 写入文件
                f.write(log)
                # 如果文件大于19M，则新建LOG文件
                if os.path.getsize(self.log_file) > 20000000:
                    self.create()

    def open_close_log_record(self):
        if self.chk_box_log.isChecked():
            self.create_log_file()
            self._save_log = threading.Thread(target=self.save_log_to_file,
                                              daemon=True)
            self._save_log.start()
            self.btn_draw_temperature.setEnabled(True)

        else:
            self.stop_thread(self._save_log)

    def create_log_file(self):
        self.log_file = "Temperature_box_%s.log" % str(
            time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())))
        f = open(self.log_file, "w", encoding="utf-8")
        f.close()

    def start_cyclic_run(self):
        temp_low = self.le_cyclic_start_temp.displayText()
        temp_high = self.le_cyclic_stop_temp.displayText()
        try:
            temp_low = float(temp_low)
            temp_high = float(temp_high)
            if temp_low < LOW_TEMPERATURE or temp_high > HIGH_TEMPERATURE:
                self.record_log("Set temperature failed: %d ~ %d" %
                                (temp_low, temp_high))
                return
            else:
                self.cmd_lock.acquire()
                self.set_temperature(temp_low)
                self.cmd_lock.release()
                self.record_log("Set temgperature: %d" % temp_low)
                self.cyclic_temp_run_flag = True
                self.cyclic_low_temp = temp_low
                self.cyclic_high_temp = temp_high
                self.btn_cyclic_temp_start.setEnabled(False)
                self.btn_cyclic_temp_stop.setEnabled(True)
        except Exception as e:
            self.record_log("Set temperature failed: %s" % e)

    def draw_temperature(self):
        if self.log_file != "":
            try:
                x, y = get_temperatures_from_log(self.log_file)
                draw_temp(x, y)
            except Exception as e:
                self.record_log("Draw temperature failed: %s" % e)

    def stop_cyclic_run(self):
        self.cyclic_temp_run_flag = False
        self.btn_cyclic_temp_start.setEnabled(True)
        self.btn_cyclic_temp_stop.setEnabled(False)

    # 定义raise
    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)

        if not inspect.isclass(exctype):
            exctype = type(exctype)

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            tid, ctypes.py_object(exctype))

        if res == 0:
            raise ValueError("invalid thread id")

        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    # 定义杀掉线程的方法
    def stop_thread(self, thread):
        try:
            self._async_raise(thread.ident, SystemExit)
        except Exception as e:
            print("NOTE: stop thread raise a Exception: " + e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())