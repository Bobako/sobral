БД я не приделал, получается, да оно мне и нахуй не надо.

Запускается все через user_interface.py
нужны библиотеки pyqt5, pyqtgraph, numpy и чето там по бд, но я не ебу

необходимо сформировать из бд все выбранные в конфигураторе сигналы в список объектов класса сигнал,
он кстати в самом низу представлен, и засунуть их в переменную sygnals функции form_sygnals в user_interface.py на 537 строке, и все магическим образом заработает, хотя оно
сейчас и так работает, правда на сулчайных данных

и еще надо научить окошки обращаться к бд и проверять ее на наличие там новых сигналов для обновления показаний в текущем времени



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
