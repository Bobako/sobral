from PyQt5.QtCore import QSize, Qt
import pyqtgraph as pg
import numpy as np
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QInputDialog, QSlider, QLabel,QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton,QLineEdit,QVBoxLayout,QHBoxLayout
from random import randint
from PyQt5.QtCore import QTimer

def mk_to_str(value):
    t = time.gmtime(value)

    s = time.strftime("%Y-%m-%d-%H:%M:%S",t)

    return s

def str_to_mkt(values):
    res = []
    for s in values:    
        struct = time.strptime(s,"%Y-%m-%d-%H:%M:%S")
        mkt = time.mktime(struct)
        res.append(mkt)
    return res

class Sygnal():
    info = {"id_" : None,
            "color" : None,
            "desc" : None,
            "units" : None,
            "min": None,
            "max" : None,
            "current" : None,
            "curs" : None}

    x_data = []
    y_data = []#архивные икс игрек
    st_x = []#отображаемые икс игрек
    st_y = []
    def __init__(self, id_, desc, units, min, max,data):
        self.info["id_"] = id_
        self.info["desc"] = desc
        self.info["units"] = units
        self.info["min"] = min
        self.info["max"] = max
        

        self.x_data = data[0]
        self.y_data = data[1]



class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        
        
        return ''


class Window(QMainWindow):


    #весь визуал
    def __init__(self,display_time = None,display_interval = None,display_interval_borders = None, sygnals = None):
        super().__init__()

        self.setMinimumSize(QSize(1000, 800))  # Устанавливаем размеры
        self.setWindowTitle("Гистограмма")  # Устанавливаем заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет



        layout = QVBoxLayout(self)
        central_widget.setLayout(layout)
        

        ##########################
        
     #   layout.addWidget(nav)


        #########################################


        plots = QtWidgets.QWidget(self)
        nav_layout = QHBoxLayout(self)
        plots.setLayout(nav_layout)


       
       
        self.plot = pg.PlotWidget(title='', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        nav_layout.addWidget(self.plot)
        nav_layout.addStretch(1)

        self.plot.setMinimumSize(QSize(1000, 400))
        layout.addWidget(plots)
        
        
        #########################################
        time_chooseLayout = QHBoxLayout(self)
        time_chooseLayout.addWidget(QLabel("Выбранное время:"))
        self.time_choose_field = QLineEdit()
        time_chooseLayout.addWidget(self.time_choose_field)
        self.time_choose_btn = QPushButton("Изменить")
        self.time_choose_btn.clicked.connect(self.read_time)
        self.error_label = QLabel('')
        time_chooseLayout.addWidget(self.error_label)
        time_chooseLayout.addWidget(self.time_choose_btn)
        time_chooseLayout.addStretch(1)
        layout.addLayout(time_chooseLayout)
        #########################################
        #легенда

        legend_table = QTableWidget(self)
        legend_table.setColumnCount(7)
        legend_table.setRowCount(4)
        legend_table.setHorizontalHeaderLabels(["Сигнал","Цвет","Описание","Ед.измерения","Минимум","Максимум","Значение"])
        legend_table.setVerticalHeaderLabels([""]*4)

        self.legend_table = legend_table

        layout.addWidget(legend_table)
        self.legend_table.setMinimumSize(QSize(1500, 200))
        self.layout = layout

        
        ########################################

        self.display_interval = display_interval
        self.display_interval_borders = display_interval_borders

        self.curves = []
        self.sygnals = []
        if len(sygnals)>4:
            sygnals = sygnals[0:4]
        for sygnal in sygnals:
            self.add_sygnal(sygnal)
        
        if display_time == "current":
            self.chosen_time = self.sygnals[0].x_data[-1]

        else:
            self.chosen_time = display_interval_borders[1]

        self.time_choose_field.setText(mk_to_str(self.chosen_time))

        self.change() 

       
    def add_sygnal(self,sygnal):
        sygnal_n = len(self.sygnals)
        self.sygnals.append(sygnal)
        color_si,color_s = self.define_color(sygnal_n)             

        self.curves.append(self.plot.plot(pen=color_si,fillBrush=pg.mkBrush(color_si), fillLevel = 0))
        #self.curves[-1].setData(sygnal.st_x,sygnal.st_y)
     

        self.legend_table.setItem(sygnal_n,0,QTableWidgetItem(sygnal.info["id_"]))
        self.legend_table.setItem(sygnal_n,1,QTableWidgetItem(color_s))
        self.legend_table.setItem(sygnal_n,2,QTableWidgetItem(sygnal.info["desc"]))
        self.legend_table.setItem(sygnal_n,3,QTableWidgetItem(sygnal.info["units"]))
        self.legend_table.setItem(sygnal_n,4,QTableWidgetItem(str(sygnal.info["min"])))
        self.legend_table.setItem(sygnal_n,5,QTableWidgetItem(str(sygnal.info["max"])))
        self.legend_table.setItem(sygnal_n,6,QTableWidgetItem(str(sygnal.y_data[-1])))
        self.legend_table.resizeColumnsToContents()
     
    def update(self,sygnal_n,x,y):
        self.sygnals[sygnal_n].x_data.append(x)
        self.sygnals[sygnal_n].y_data.append(y)
        self.change()

    def trianggered(self,a,n):
            masy=[0,a,a,0]
            k=1.5
            masx=[0+k*n,0+k*n,1+k*n,1+k*n]
            
            self.sygnals[n].st_x = masx
            self.sygnals[n].st_y = masy
            self.reset_sygnals()

    def change(self,last = True):

        for i in range(len(self.sygnals)):

            if last:
                self.trianggered(self.sygnals[i].y_data[-1],i)
                self.chosen_time = self.sygnals[i].x_data[-1]
                self.time_choose_field.setText(mk_to_str(self.chosen_time))
                self.legend_table.setItem(i,6,QTableWidgetItem(str(self.sygnals[i].y_data[-1])))
            else:

                sygnal = self.sygnals[i]
                try:
                    time_value_i = sygnal.x_data.index(self.chosen_time+3600*3)
                    self.trianggered(sygnal.y_data[time_value_i],i)
                    
                    self.legend_table.setItem(i,6,QTableWidgetItem(str(sygnal.y_data[time_value_i])))
                except Exception:
                    k = 1
                    self.legend_table.setItem(i,6,QTableWidgetItem('Значение для этого момента времени не заданы'))
                    while k < (len(sygnal.x_data)) and self.chosen_time+3600*3<sygnal.x_data[k]:
                        k+=1
                    time_value_i = k-1
                    self.trianggered(0,i)
                
                

                #self.chosen_time = sygnal.x_data[time_value_i]
                #self.time_choose_field.setText(mk_to_str(self.chosen_time))

               

    def reset_sygnals(self):
        for i in range(len(self.curves)):
            self.curves[i].clear()
            self.curves[i].setData([],[])

            self.curves[i].setData(self.sygnals[i].st_x,self.sygnals[i].st_y)

    def read_time(self):
        try:
            self.chosen_time = str_to_mkt([self.time_choose_field.text()])[0]
        except Exception:
            self.error_label.setText("Неверный формат ввода, повторите!")
        else:
            self.error_label.setText("")
            self.change(False)



    def define_color(self,n):
        sygnal_colors = ['g','r','c','m']
        sygnal_colors_names = ['Зеленый','Красный','Голубой','Фиолетовый']

        return (sygnal_colors[n],sygnal_colors_names[n])

       



def get_time(l=7):
    t = [(time.mktime(time.localtime())-i+3600*3) for i in range(l)][::-1]
    return t




if __name__ == "__main__":
    app = QApplication([])
    w = Window()

    for i in range(4):
        example_data = [get_time(7),[randint(1800,2200) for i in range(7)]]

        sygnal = Sygnal('00MOT01CS001','Скорость вращения №1','обороты в минуту',0,3500,example_data)
        try:
            w.add_sygnal(sygnal)
        except Exception:
            pass

    w.show()

    timer = QTimer()
    timer.timeout.connect(w.update_all)
    timer.start(1000)


    app.exec()