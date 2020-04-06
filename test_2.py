import time, threading

i = 0
def foo():
    print(time.ctime(), i)
    threading.Timer(1, foo).start()

foo()
while True:
    i += 1

