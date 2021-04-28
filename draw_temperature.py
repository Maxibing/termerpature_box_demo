import sys
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdate
import numpy as np


# 从log中读取温度和时间
def get_temperatures_from_log(file):
    '''
        file            :   log file of temperature box
        np_timestramp   :   array of timestramp
        np_temperatures :   array of temperature
    '''
    np_temperatures = np.array([])
    np_timestramp = np.array([])
    f = open(file)
    _tmp = True
    while _tmp:
        _tmp = f.readline()
        if "temperature_measurement" in _tmp:
            _tmp = _tmp.split(" ")
            _time = datetime.datetime.strptime(
                ("%s %s" % (_tmp[0], _tmp[1][:8])), "%Y-%m-%d %H:%M:%S")
            _temp = float(_tmp[3][:-1]) / 100
            np_timestramp = np.append(np_timestramp, _time)
            np_temperatures = np.append(np_temperatures, _temp)
    f.close()

    return np_timestramp, np_temperatures


# 画图
def draw_temp(times, temps):
    '''
        times   :   array of timestramp
        temps   :   array of temperature
    '''
    fig = plt.figure()
    ax1 = fig.ax1 = fig.add_subplot(211)
    # x轴说明
    plt.xlabel("time")
    # y轴说明
    plt.ylabel("temperature")
    # y轴增加单位°C
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f °C'))
    # 设置x轴格式
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%H:%M:%S'))
    # y轴单位精度
    info = "Start time: %s \nEnd time: %s \nHighest temperature: %.2f °C\nLowest temperature: %.2f °C" % (
        times[0], times[-1], np.max(temps), np.min(temps))
    # 显示11个数字
    # plt.xticks(range(1, len(times), int(len(times)/10)), times[::int(len(times)/10)])
    # 字体倾斜70°
    # plt.xticks(rotation=70)
    ax1.plot(times,
             temps,
             color="red",
             linewidth=1.0,
             linestyle="-",
             label=info)
    # label位置
    plt.legend(loc="upper left")
    # 设置网格样式
    plt.grid(linestyle='-.')

    ax2 = fig.add_subplot(212, sharex=ax1)
    # step = int(len(temps)/1000)
    # temps_step = temps[1::step] - temps[:-1:step]
    temps_step = temps[1:] - temps[:-1]
    # x轴说明
    plt.xlabel("times")
    # y轴说明
    plt.ylabel("change slope")
    # y轴增加单位°C
    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f °C'))
    # 设置x轴格式
    plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%H:%M:%S'))
    temps_step = np.maximum(temps_step, -temps_step)
    temps_step = np.append(temps_step, temps_step[-1])
    # temps_step = np.around(temps_step, decimals=1, out=None)
    ax2.plot(times,
             temps_step,
             "r.",
             color="blue",
             label="The diff of 2 temperature")
    # label位置
    plt.legend(loc="upper left")
    # 设置网格样式
    plt.grid(linestyle='-.')

    # 画图
    plt.show()


if __name__ == "__main__":
    file = sys.argv[1]
    x, y = get_temperatures_from_log(file)
    draw_temp(x, y)