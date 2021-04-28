import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp
from global_value import *


class ModBus(object):
    '''
        ModBus to control Temperature box
    '''
    def __init__(self):
        self.master = ""

    def init_master(self, address, port=502):
        self.master = modbus_tcp.TcpServer(address=address, port=port)
        self.master.set_timeout(5.0)
        self.master.set_verbose(True)

    def close_master(self):
        self.master._do_close()

    def read_holding_registers(self, quantity_of_x=100):
        registers = {}
        try:
            result = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0,
                                         quantity_of_x)
            registers["temperature_measurement"] = result[
                TEMPERATURE_MEASUREMENT_ADRESS] if result[
                    TEMPERATURE_MEASUREMENT_ADRESS] < 40000 else result[
                        TEMPERATURE_MEASUREMENT_ADRESS] - 65536
            registers["temperature_set_final"] = result[
                TEMPERATURE_SET_VALUE_FINAL_ADRESS] if result[
                    TEMPERATURE_SET_VALUE_FINAL_ADRESS] < 40000 else result[
                        TEMPERATURE_SET_VALUE_FINAL_ADRESS] - 65536
            registers["temperature_set_current"] = result[
                TEMPERATURE_SET_VALUE_CURRENT_ADRESS] if result[
                    TEMPERATURE_SET_VALUE_CURRENT_ADRESS] < 40000 else result[
                        TEMPERATURE_SET_VALUE_CURRENT_ADRESS] - 65536
            registers["temperature_slope"] = result[
                TEMPERATURE_SLOPE_ADRESS] if result[
                    TEMPERATURE_SLOPE_ADRESS] < 40000 else result[
                        TEMPERATURE_SLOPE_ADRESS] - 65536
            registers["run_switch"] = result[RUN_SWITCH_ADRESS]

            return registers

        except Exception as e:
            print(str(e))

    def write_single_register(self, address, value):
        try:
            return self.master.execute(1,
                                       cst.WRITE_SINGLE_REGISTER,
                                       address,
                                       output_value=value)

        except Exception as e:
            print(str(e))

    def switch_temperature_box_on(self):
        result = list(self.write_single_register(RUN_SWITCH_ADRESS, SWITCH_ON))

        return result[-1]

    def switch_tempreature_box_off(self):
        result = self.write_single_register(RUN_SWITCH_ADRESS, SWITCH_OFF)

        return result[-1]

    def set_temperature(self, temperature):
        if temperature < LOW_TEMPERATURE or temperature > HIGH_TEMPERATURE:
            return False

        temperature = int(temperature * 100)
        result = self.write_single_register(TEMPERATURE_SET_VALUE_FINAL_ADRESS,
                                            temperature)

        return result[-1]

    def set_temperature_slope(self, slope):
        if slope < LOW_SLOPE or slope > HIGHT_SLOPE:
            return False

        slope = int(slope * 100)
        result = self.write_single_register(TEMPERATURE_SLOPE_ADRESS, slope)

        return result[-1]


if __name__ == "__main__":
    m = ModBus("192.168.111.200")
    print(m.read_holding_registers())
