from PyQt5.QtCore import QSize, Qt
import pyqtgraph as pg
import numpy as np
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QInputDialog, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton,QLineEdit,QVBoxLayout,QHBoxLayout
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

    x_data = []  #отображаемые икс игрек
    y_data = []

    st_x = []   #архивные икс игрек
    st_y = []


    def __init__(self, id_, desc, units, min, max,data):
        self.info["id_"] = id_
        self.info["desc"] = desc
        self.info["units"] = units
        self.info["min"] = min
        self.info["max"] = max
        

        self.x_data = data[0]
        self.y_data = data[1]

        self.st_x = data[0]
        self.st_y = data[1]



class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        
        return [mk_to_str(value) for value in values]


class Window(QMainWindow):
    
    def __init__(self,display_time = None,display_interval = None,display_interval_borders = None, sygnals = None):
        super().__init__()
        self.triangualated = False
        self.dots_enabled = False

        if True: #визуал 

            self.setMinimumSize(QSize(1000, 800))  # Устанавливаем размеры
            self.setWindowTitle("Тренды")  # Устанавливаем заголовок окна
            self.central_widget = QWidget(self)  # Создаём центральный виджет
            self.setCentralWidget(self.central_widget)  # Устанавливаем центральный виджет

            layout = QVBoxLayout(self)
            self.central_widget.setLayout(layout)
          

            ##########################
            #верхняя панель        
            nav = QtWidgets.QWidget(self)
            nav.setMinimumSize(QSize(800, 40))
            nav_layout = QHBoxLayout(self)
            nav.setLayout(nav_layout)
            
            nav_btns = []
            for i in range(4):
                nav_btns.append(QPushButton(str(i),self))
                nav_btns[i].setMinimumSize(QSize(80,40))
                #nav_btns[i].setMaximumSize(QSize(80,40))
                nav_layout.addWidget(nav_btns[i])
            nav_layout.addStretch(1)
            

            nav_btns[0].setText('Отображение точек')
            nav_btns[0].clicked.connect(self.dots)

            #nav_btns[1].setText('update')
            #nav_btns[1].clicked.connect(self.update_c)

            nav_btns[1].setText('Линейная интерполяция')
            nav_btns[1].clicked.connect(self.triang)

            nav_btns[2].setText('Отбор по времени')
            nav_btns[2].clicked.connect(self.read_time)

            nav_btns[3].setText('Установить курсор')
            nav_btns[3].clicked.connect(self.set_cursor)

            
            layout.addWidget(nav)


            #########################################
            #график


            self.plot = pg.PlotWidget(title='', axisItems={'bottom': TimeAxisItem(orientation='bottom')})   
            layout.addWidget(self.plot)
            
            
            

            

            #########################################
            #легенда

            legend_table = QTableWidget(self)
            legend_table.setColumnCount(8)
            legend_table.setRowCount(4)
            legend_table.setHorizontalHeaderLabels(["Сигнал","Цвет","Описание","Ед.измерения","Минимум","Максимум","Последнее значение","Значение в точке курсора"])
            legend_table.setVerticalHeaderLabels([""]*4)

            self.legend_table = legend_table

            layout.addWidget(legend_table)

            self.layout = layout 



        self.display_interval = display_interval
        self.display_interval_borders = display_interval_borders

        self.curves = []
        self.sygnals = []
        if len(sygnals)>4:
            sygnals = sygnals[0:4]
        for sygnal in sygnals:
            self.add_sygnal(sygnal)
        self.reset_sygnals()
        if display_time == "archive":
            self.selection_by_time(display_interval_borders[0],display_interval_borders[1])   


        


    def set_cursor(self):
        time_str = mk_to_str(max([self.sygnals[i].x_data[-1] for i in range(len(self.sygnals))]))
        labelT = "Выберите время для установки курсора:"
        while True:
            dlg = QInputDialog(self)
            dlg = QInputDialog(self)
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setWindowTitle("Установка курсора")
            dlg.setLabelText(labelT)
            dlg.resize(500,200)
            dlg.setTextValue(time_str)
            ok = dlg.exec_()
            if not(ok):
                break
            else:
                cursor_time_str = dlg.textValue()
                try:
                    cursor_time = str_to_mkt([cursor_time_str])[0]+3600*3
                except Exception:
                    labelT = "Неверный формат ввода, повторите:"
                    dlg.setTextValue(time_str)
                else:
                    self.cursor = self.cursor_by_value(cursor_time)
                    break

        for i in range(len(self.sygnals)):
            sygnal = self.sygnals[i]
            try:
                cursor_value_i = sygnal.x_data.index(cursor_time+3600*3)
            except Exception:
                k=1
                while k < (len(sygnal.x_data)) and cursor_time+3600*3<sygnal.x_data[k]:
                    k+=1
                cursor_value_i = k-1

            cursor_value = sygnal.y_data[cursor_value_i]
            self.legend_table.setItem(i,7,QTableWidgetItem(str(cursor_value)))

    def cursor_by_value(self,value):
        self.cursor_curve = self.plot.plot()
        self.cursor_curve.setData([value,value],[min([min(s.y_data) for s in self.sygnals]),max([max(s.y_data) for s in self.sygnals])])

    def update(self,x,y,sygnal_n):       #передаем в сигнал под номером sygnal_n новые данные, обновляем
        if self.triangualated:
            self.triang()
            self.sygnals[sygnal_n].x_data.append(x)
            self.sygnals[sygnal_n].y_data.append(y)
            self.sygnals[sygnal_n].st_x.append(x)
            self.sygnals[sygnal_n].st_y.append(y)
            self.triang()
        else:
            self.sygnals[sygnal_n].x_data.append(x)
            self.sygnals[sygnal_n].y_data.append(y)
            self.sygnals[sygnal_n].st_x.append(x)
            self.sygnals[sygnal_n].st_y.append(y)

        if self.sygnals[sygnal_n].x_data[-1] - self.sygnals[sygnal_n].x_data[0] > self.display_interval:
            trash1,trash2 = self.sygnals[sygnal_n].x_data.pop(0),self.sygnals[sygnal_n].y_data.pop(0)

    def read_time(self):


        self.time_start = min([self.sygnals[i].x_data[0] for i in range(len(self.sygnals))])
        self.time_fin = max([self.sygnals[i].x_data[-1] for i in range(len(self.sygnals))])

        


        time_str = 'от '+ mk_to_str(self.time_start) + ' до ' + mk_to_str(self.time_fin)
        labelT = "Введите интервал для отбора по времени:"
        while True:
            dlg = QInputDialog(self)
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setWindowTitle("Установка времени отбора")
            dlg.setLabelText(labelT)
            dlg.resize(500,200)
            dlg.setTextValue(time_str)
            ok = dlg.exec_()
            if not(ok):
                break
            time_str2 = dlg.textValue()
            try:
                time_start,time_fin = time_str2.split(' ')[1],time_str2.split(' ')[3]
                time_start,time_fin = str_to_mkt([time_start,time_fin])

                time_start,time_fin = time_start+3600*3,time_fin+3600*3

            except Exception:
                labelT = "Неверный формат ввода, повторите:"
                dlg.setTextValue(time_str)
            else:
                break
        
        self.selection_by_time(time_start,time_fin)

    def selection_by_time(self,time_start,time_fin):
        for i in range (len(self.sygnals)):
            y_new = []
            x_new = []
            for k in range(len(self.sygnals[i].st_x)):
                if (self.sygnals[i].st_x[k]>=time_start and self.sygnals[i].st_x[k]<=time_fin):
                    x_new.append(self.sygnals[i].st_x[k])
                    y_new.append(self.sygnals[i].st_y[k])
            self.sygnals[i].x_data = x_new
            self.sygnals[i].y_data = y_new

        if self.triangualated:
            self.triang()    
            self.reset_sygnals()
            self.triang()
        else:
            self.reset_sygnals()

       
    def add_sygnal(self,sygnal):
        sygnal_n = len(self.sygnals)
        self.sygnals.append(sygnal)
        color_si,color_s = self.define_color(sygnal_n)        

        self.curves.append(self.plot.plot(pen=color_si))
        self.curves[-1].setData(sygnal.x_data,sygnal.y_data)

        self.legend_table.setItem(sygnal_n,0,QTableWidgetItem(sygnal.info["id_"]))
        self.legend_table.setItem(sygnal_n,1,QTableWidgetItem(color_s))
        self.legend_table.setItem(sygnal_n,2,QTableWidgetItem(sygnal.info["desc"]))
        self.legend_table.setItem(sygnal_n,3,QTableWidgetItem(sygnal.info["units"]))
        self.legend_table.setItem(sygnal_n,4,QTableWidgetItem(str(sygnal.info["min"])))
        self.legend_table.setItem(sygnal_n,5,QTableWidgetItem(str(sygnal.info["max"])))
        self.legend_table.setItem(sygnal_n,6,QTableWidgetItem(str(sygnal.y_data[-1])))
        self.legend_table.resizeColumnsToContents()

    def triang(self):
        for i in range(len(self.sygnals)):
            x_new = []
            y_new = []
            x_old = self.sygnals[i].x_data
            y_old = self.sygnals[i].y_data
            if self.triangualated:
                x_new = x_old[::2]   
                y_new = y_old[::2]
            else:  
                for l in range(len(x_old)-1):
                    x_new.append(x_old[l])
                    y_new.append(y_old[l])
                    x_new.append(x_old[l+1])
                    y_new.append(y_old[l])
                x_new.append(x_old[-1])
                y_new.append(y_old[-1])


            self.sygnals[i].x_data = x_new
            self.sygnals[i].y_data = y_new
        self.triangualated = not(self.triangualated)

        self.reset_sygnals()
    
    def reset_sygnals(self):
        for i in range(len(self.curves)):
            self.curves[i].clear()
            self.curves[i].setData([],[])

            self.curves[i].setData(self.sygnals[i].x_data,self.sygnals[i].y_data)

    def dots(self):
        for i in range(len(self.curves)):
            color_si = self.define_color(i)[0]
            self.curves[i].clear()
            self.curves[i].setData([],[])
            if self.dots_enabled:
                self.curves[i] = self.plot.plot(pen=color_si)
            else:
                self.curves[i] = self.plot.plot(pen=color_si,
                                                name="BEP",
                                                symbol='o',
                                                symbolPen=pg.mkPen(color=color_si, width=0),                                      
                                                symbolBrush=pg.mkBrush(0, 0, 0, 255),
                                                symbolSize=7)   
            self.curves[i].setData(self.sygnals[i].x_data,self.sygnals[i].y_data)

        self.dots_enabled = not(self.dots_enabled)
        #print("dots")

    def define_color(self,n):
        sygnal_colors = ['g','r','c','m']
        sygnal_colors_names = ['Зеленый','Красный','Голубой','Фиолетовый']
        return (sygnal_colors[n],sygnal_colors_names[n])

def main():
    app = QApplication([])
    w = Window()

    for i in range(4):
        example_data = [[(time.mktime(time.localtime())-i+3600*3) for i in range(7)][::-1],[randint(1800,2200) for i in range(7)]]

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
    print('shown')


if __name__ == "__main__":
    #main()
    pass




    

    
