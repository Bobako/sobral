import random
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from db import *

class Dplot(object):
    def __init__(self, npoints: int, x_label: str, y_label: str, title: str, data: list):
        self.npoints = npoints

        if (type(data) == list and len(data) > 0):
            self.x = deque([x for x in range(len(data))], maxlen=npoints)
            self.y = deque(data, maxlen=npoints)
        else:
            self.x = deque([0], maxlen=npoints)
            self.y = deque([0], maxlen=npoints)
        
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.set_title(title)
        [self.line] = self.ax.step(self.x, self.y, 'k', label = 'Value of sumething')

        self.legend = self.ax.legend(loc='lower right', fontsize='medium')
        self.legend.get_frame().set_facecolor('C0')

    def update(self, dy):
        self.x.append(self.x[-1] + 1)  # update data
        self.y.append(dy)

        self.line.set_xdata(self.x)  # update plot data
        self.line.set_ydata(self.y)

        self.ax.relim()  # update axes limits
        self.ax.autoscale_view(True, True, True)
        return self.line, self.ax

    def data_gen(self):
        while True:
            yield float(random.randint(-10,10)) # вместо рандома вставить функцию, возвращающую новые значения

    def draw(self):
        ani = animation.FuncAnimation(self.fig, self.update, self.data_gen)
        plt.show()

if __name__ == '__main__':
    a = [float(random.randint(-10,10)) for x in range(10)] # Archive.select_column('value', False, False, 10)
    my_plot = Dplot(20, 'time', 'y', 'Plot', a)
    my_plot.draw()