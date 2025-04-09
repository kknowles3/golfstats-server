# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:17:57 2021

@author: kknow

These are generic execption handlers and function timers.

TODO Need to fix an issue where a valid function wrapped with the exception
handler returns an empty result, even though result within function (and
without the decorator) is valid.

"""

from timeit import default_timer as timer

def gen_handler(e, msg=None):
    print(msg)
    print(e)

# https://stackoverflow.com/questions/129144/generic-exception-handling-in-python-the-right-way
def handle_exception(handler=gen_handler, msg=None):
    def decorate(func):
        def call_function(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                handler(e, msg)
        return call_function
    return decorate

def calc_function_time(func):
    # def decorate(func):
    def call_function(*args, **kwargs):
        start = timer()        
        res = func(*args, **kwargs)
        end = timer()
        print("Completed {} in {:.2f} seconds".format(func.__name__, end-start))
        return res
    return call_function
    # return decorate


# *** Sample code ***
if __name__ == '__main__':
    
    import time
    import math
    
    @calc_function_time
    def factorial(num):
     
        # sleep 2 seconds because it takes very less time
        # so that you can see the actual difference
        time.sleep(2)
        print(math.factorial(num))
     
    # calling the function.
    factorial(10)