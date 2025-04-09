# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 10:27:44 2021

@author: kknow
"""

# https://stackoverflow.com/questions/5114292/break-interrupt-a-time-sleep-in-python
from threading import Event

exit = Event()

def main():
    i = 0
    while not exit.is_set():
        print("Running loop number {}".format(i))
        i += 1
        # do_my_thing()
        exit.wait(5)

    print("All done!")
    # perform any cleanup here

def quit(signo, _frame):
    print("Interrupted by %d, shutting down" % signo)
    exit.set()

if __name__ == '__main__':

    import signal
    import platform
    
    if platform.system() != 'Linux':
        signal.SIGHUP = 1
        
    for sig in ('TERM', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit)

    main()