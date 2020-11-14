from PyQt5.QtWidgets import QApplication,QInputDialog,QLabel,QHBoxLayout, QVBoxLayout,QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton,QLineEdit
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
        self.setWindowTitle("Сравнение")  # Устанавливаем заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        layout = QVBoxLayout()  #

       
        time_btn = QPushButton("Отбор по времени",self)
        time_btn.setMinimumSize(QSize(80,40))
        time_btn.setMaximumSize(QSize(100,40))
        layout.addWidget(time_btn)
        time_btn.clicked.connect(self.select_btn)
        central_widget.setLayout(layout)  #

        self.legend_table = QTableWidget(self)
        layout.addWidget(QLabel('Сигналы:'))
        layout.addWidget(self.legend_table)







        self.table = QTableWidget(self)  # Создаём таблицу

        #self.table.setColumnCount(len(self.default_headers))  # Устанавливаем  колонки
        #table.setRowCount(len(a))  # и строк в таблице

        # Устанавливаем заголовки таблицы
        #self.table.setHorizontalHeaderLabels(self.default_headers)  # у понятно суюда массивом передаем заголовки
        #a = a[::-1]

        
        layout.addWidget(QLabel('Значения:'))
        layout.addWidget(self.table)
        #table.resizeColumnsToContents()
        ###############################################################
        self.full_legend()
        self.full_values()  
        self.reset_values()

        if display_time == 'archive':
            self.time_start = display_interval_borders[0]
            self.time_fin = display_interval_borders[1]
            self.select_by_time()
        


    def full_legend(self):
        self.legend_headers = ["ID KKS","Описание","Минимум","Максимум","Единицы измерения"]
        self.legend_values  = []
        for sygnal in self.sygnals:
            row = [sygnal.info['id_'],
                   sygnal.info['desc'],
                   sygnal.info['min'],
                   sygnal.info['max'],
                   sygnal.info['units']
                  ]
            self.legend_values.append(row)
        self.legend_table.setRowCount(len(self.legend_values))
        self.legend_table.setColumnCount(len(self.legend_values[0]))
        self.legend_table.setHorizontalHeaderLabels(self.legend_headers)


        for row in range(len(self.legend_values)):
            for col in range (len(self.legend_values[0])):
                self.legend_table.setItem(row,col,QTableWidgetItem(str(self.legend_values[row][col])))

        self.legend_table.resizeColumnsToContents()

    def select_btn(self):
        self.full_values()
        self.time_start = self.vertical_headers[0]
        self.time_fin = self.vertical_headers[-1]


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
        new_v_headers = []
        
        for i in range(len(self.vertical_headers)):
            if self.vertical_headers[i]<=self.time_fin and self.vertical_headers[i]>=self.time_start:
                new.append(self.table_values[i])
                new_v_headers.append(self.vertical_headers[i])


        self.table_values = new
        self.vertical_headers = new_v_headers
        self.reset_values()

    def full_values(self):
        new = []
        vertical_headers = []
        for sygnal in self.sygnals:
            for x in sygnal.x_data:
                if not(x in vertical_headers):
                    vertical_headers.append(x)
        vertical_headers.sort() 
        for x in vertical_headers:
            row = []
            for sygnal in self.sygnals:
                appended = False
                for i in range (len(sygnal.x_data)):

                    if sygnal.x_data[i] == x:
                        row.append(sygnal.y_data[i])
                        appended = True
                        break
                if not(appended):
                    row.append('')
            new.append(row)

        self.table_values = new
        self.table_values_archive = new
        self.vertical_headers = vertical_headers
        self.horisontal_headers = []
        for sygnal in self.sygnals:
            self.horisontal_headers.append(sygnal.info['id_'])

    def update(self,x,y,sygnal_n):                  #передаем в сигнал под номером sygnal_n новые данные, обновляем
        self.sygnals[sygnal_n].x_data.append(x)
        self.sygnals[sygnal_n].y_data.append(y)
        self.full_values()
        self.reset_values()
        
    def reset_values(self):
        a = self.table_values
        self.table.clear()
        self.table.setRowCount(len(a))
        self.table.setColumnCount(len(a[0]))
        self.table.setHorizontalHeaderLabels(self.horisontal_headers)
        self.table.setVerticalHeaderLabels([mk_to_str(header) for header in self.vertical_headers])
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
