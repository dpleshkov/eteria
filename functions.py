import threading
import math

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def distance(x1, y1, x2, y2):
    return math.hypot(abs(x1-x2), abs(y1-y2))
