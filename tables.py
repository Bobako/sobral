from PyQt5.QtWidgets import QApplication,QInputDialog,QHBoxLayout, QVBoxLayout,QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton,QLineEdit
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtCore
import random
import time

class MainWindow(QMainWindow):
    def __init__(self,display_time = None,display_interval = None,display_interval_borders = None, sygnals = None):

        self.display_time = display_time
        self.display_interval = display_interval
        self.display_interval_borders = display_interval_borders
        self.sygnals = sygnals
        self.table_values_archive = None


        self.default_headers = ["Время","ID KKS","Значение","Единицы измериения","Минимум","Максимум","Описание"]
        ##############################################################
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)
        self.setMinimumSize(QSize(900, 900))  # Устанавливаем размеры
        self.setWindowTitle("Протокол")  # Устанавливаем заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        layout = QVBoxLayout()  #

       
        time_btn = QPushButton("Отбор по времени",self)
        time_btn.setMinimumSize(QSize(80,40))
        time_btn.setMaximumSize(QSize(100,40))
        layout.addWidget(time_btn)
        time_btn.clicked.connect(self.select_btn)


        central_widget.setLayout(layout)  #
        self.table = QTableWidget(self)  # Создаём таблицу

        self.table.setColumnCount(len(self.default_headers))  # Устанавливаем  колонки
        #table.setRowCount(len(a))  # и строк в таблице

        # Устанавливаем заголовки таблицы
        self.table.setHorizontalHeaderLabels(self.default_headers)  # у понятно суюда массивом передаем заголовки
        #a = a[::-1]

        

        layout.addWidget(self.table)
        #table.resizeColumnsToContents()
        ###############################################################

        self.full_values()
        self.reset_values()


        if display_time == 'archive':
            self.time_start = display_interval_borders[0]
            self.time_fin = display_interval_borders[1]
            self.select_by_time()

    def select_btn(self):
        self.full_values()
        self.time_start = str_to_mkt(self.table_values[0][0])
        self.time_fin = str_to_mkt(self.table_values[-1][0])


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
                time_start,time_fin = str_to_mkt(time_start),str_to_mkt(time_fin)

                self.time_start,self.time_fin = time_start+3600*3,time_fin+3600*3

            except Exception:
                labelT = "Неверный формат ввода, повторите:"
                dlg.setTextValue(time_str)
            else:
                break
        self.select_by_time()


    def select_by_time(self):
        
        new = []
        for i in range(len(self.table_values)):
            if str_to_mkt(self.table_values[i][0])<=self.time_fin and str_to_mkt(self.table_values[i][0])>=self.time_start:
                new.append(self.table_values[i])
        self.table_values = new
        self.reset_values()

    def full_values(self):
        if self.table_values_archive!=None:
            self.table_values = self.table_values_archive
            return 0
        sygnals = self.sygnals.copy()
       
        new = []
        while sygnals != []:
            k = 0
            while k <len(sygnals):
                if sygnals[k].x_data == []:
                    t1 = sygnals.pop(k)
                    k-=1
                k+=1

            if sygnals == []:
                break

            min_time = min([sygnal.x_data[0] for sygnal in sygnals])

            for i in range(len(sygnals)):
                if sygnals[i].x_data[0]==min_time:
                    row = [mk_to_str(sygnals[i].x_data[0]),
                           sygnals[i].info['id_'],
                           sygnals[i].y_data[0],
                           sygnals[i].info['units'],
                           sygnals[i].info['min'],
                           sygnals[i].info['max'],
                           sygnals[i].info['desc']
                          ]
                    new.append(row)
                    t1,t2 = sygnals[i].x_data.pop(0),sygnals[i].y_data.pop(0)

        self.table_values_archive = new
        self.table_values = new
        


    def update(self,x,y,sygnal_n):                  #передаем в сигнал под номером sygnal_n новые данные, обновляем
        row = [mk_to_str(x),
               sygnals[sygnal_n].info['id_'],
               y,
               sygnals[sygnal_n].info['units'],
               sygnals[sygnal_n].info['min'],
               sygnals[sygnal_n].info['max'],
               sygnals[sygnal_n].info['desc']
              ]
        self.table_values_archive.append(row)
        self.table_values.append(row)
        self.reset_values()


        
    def reset_values(self):
        a = self.table_values
        self.table.clear()
        self.table.setRowCount(len(a))
        self.table.setHorizontalHeaderLabels(self.default_headers)
        for row in range(len(a)):
            for col in range(len(a[0])):
                self.table.setItem(row, col, QTableWidgetItem(str(a[row][col])))

        self.table.resizeColumnsToContents()



def mk_to_str(value):
    t = time.gmtime(value)

    s = time.strftime("%Y-%m-%d-%H:%M:%S",t)

    return s

def str_to_mkt(s):
    
    struct = time.strptime(s,"%Y-%m-%d-%H:%M:%S")
    mkt = time.mktime(struct)
        
    return mkt




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = MainWindow(a, mas)
    mw.show()
    sys.exit(app.exec())
