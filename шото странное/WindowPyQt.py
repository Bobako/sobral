import sys
import importlib
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QDesktopWidget, QMainWindow, QGridLayout, QSizePolicy, QVBoxLayout
from PyQt5.QtCore import QCoreApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib import pyplot as plt
import numpy as np
import math

class DrowToCanvas(FigureCanvas):
    def __init__(self, fig):
        self.fig = fig
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class DrowGraficMatPlot():
    
    def __init__(self, max_x, max_y, pirp_P, pirp_Q, I, U, sin_fi):
        self.max_x = max_x # Максимальное значение модуля активной мощности
        self.max_y = max_y # Максимальное значение модуля реактивной можности
        self.pirp_P = pirp_P # Фиолетовая граница активной мощности
        self.pirp_Q = pirp_Q # Фиолетовая грпница реактивной мозности
        self.I = I # Значения силы тока за промежуток времени
        self.U = U # Значения напряжения за промежуток времни
        self.sin_fi = sin_fi # Синус фи, где фи - это фаза
        
    def Start(self):
        max_x = self.max_x
        max_y = self.max_y
        pirp_P = self.pirp_P
        pirp_Q = self.pirp_Q
        I = self.I
        U = self.U
        sin_fi = self.sin_fi

        #Blue graph
        fig, axes = plt.subplots()
        for fi in [0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            X = [0, max_x]
            Y = [x * (fi/math.sqrt(1 - fi*fi)) for x in X]
            plt.annotate(str(fi), xy=(X[-1], Y[-1]))
            plt.annotate(str(fi), xy=(-X[-1], Y[-1]))
            plt.plot(X, Y, color='blue', marker=',', linestyle='solid')
            plt.plot([-t for t in X], Y, color='blue', marker=',', linestyle='solid')
        for fi in [0.85, 0.9]:
            Y = [0, max_y]
            X = [y * (math.sqrt(1 - fi*fi)/fi) for y in Y]
            plt.annotate(str(fi), xy=(X[-1], Y[-1]))
            plt.annotate(str(fi), xy=(-X[-1], Y[-1]))
            plt.plot(X, Y, color='blue', marker=',', linestyle='solid')
            plt.plot([-t for t in X], Y, color='blue', marker=',', linestyle='solid')
        ####################

        #Red graph
        S = [i*u for i,u in zip(I, U)]
        Q = [sin_fi * s for s in S]
        P = [(1 - sin_fi*sin_fi) * s for s in S]
        plt.plot(P, Q, color='red', marker='+', linestyle='solid')
        ####################

        #Purple graph
        plt.plot(pirp_P, pirp_Q, color='magenta', marker=',', linestyle='solid')
        ####################

        #Orange lines
        row = [[-max_x, max_x], [Q[-1], Q[-1]]]
        plt.plot(row[0], row[1], '--', color='orange', marker=',')
        col = [[P[-1], P[-1]], [0, max_y]]
        plt.plot(col[0], col[1], '--', color='orange', marker=',')
        plt.scatter(P[-1], Q[-1], color='red', zorder = 10)
        ####################

        #Axis style
        plt.style.use('ggplot')
        ax = plt.gca()
        ax.spines['left'].set_position('center')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid()
        ####################

        return fig
        

class WindowGrafic(QMainWindow):
    def __init__(self, max_x = 800, max_y = 1200, pirp_P = [-500, -400, -300, -150, 0, 150, 300, 400, 500], pirp_Q = [0, 500, 700, 800, 850, 800, 700, 500, 0], I = [10, 20, 30, 40], U = [10, 15, 20, 25], sin_fi = 0.9):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)
        self.grid = QGridLayout(self.centralwidget)

        self.graphGrid = QVBoxLayout(self.GraphWidget)
        graph = DrowGraficMatPlot(max_x, max_y, pirp_P, pirp_Q, I, U, sin_fi)
        self.fig = graph.Start()
        
        self.canvas = DrowToCanvas(self.fig)
        self.graphGrid.addWidget(self.canvas)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WindowGrafic()
    main.show()
    sys.exit(app.exec_())