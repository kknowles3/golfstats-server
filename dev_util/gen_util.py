# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:17:57 2021

@author: kknow

These are generic utilities, including execption handlers and function timers.

TODO Need to fix an issue where a valid function wrapped with the exception
handler returns an empty result, even though result within function (and
without the decorator) is valid.

"""

from timeit import default_timer as timer

from typing import Dict, List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor

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

class MethodRunner():
    '''
    Utility class for executing a list of methods in parallel.  This is useful for reducing 
    the time to executing a set of independent methods, particularly in cases where
    multiple processors are available and/or the methods are remote calls to external
    services (e.g., url request).
    
    '''

    # TODO Consider adding support for method name as a string
    def run_method(self, method_args: Tuple[Callable, Dict]):
        '''
        Method for executing a single method call.  This is the worker method
        used by the run_multi_methods method.

        Parameters
        ----------
        method_args : Tuple[Callable, Dict]
            Two-item tuple that includes a callable method and a dictionary
            of named arguments for that method.

        Returns
        -------
        result : TYPE
            The result of method called with the input args.

        '''
        
        method, args = method_args
        result = method(**args)
        
        return result

    def run_multi_methods(self, method_args_list: List, max_workers: int = 10, filter_none=True):
        '''
        Method for executing a list of methods in parallel.  This is convenient
        for enhancing performance of a set of methods, particularly in cases
        where the methods are time-intensive and/or have higher latency.

        Parameters
        ----------
        method_args_list : List
            DESCRIPTION.
        max_workers : int, optional
            DESCRIPTION. The default is 10.
        filter_none : boolean, optional
            Exclude 'None' results from output. The default is True.

        Returns
        -------
        results : TYPE
            DESCRIPTION.

        '''
        
        max_workers = len(method_args_list) if len(method_args_list) < max_workers else max_workers

        # https://python-tutorials.in/python-threadpoolexecutor/
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = [result for result in executor.map(self.run_method, method_args_list)]

        if filter_none:
            results = [result for result in results if result is not None]
            
        return results

# Moved to data_util
# def get_nested_item(d, keys):
#     '''
#     Gets a nested item within a dictionary by traversing a list of keys

#     Parameters
#     ----------
#     d : dict
#         DESCRIPTION.
#     keys : list
#         DESCRIPTION.

#     Returns
#     -------
#     dn : TYPE
#         Nested item within dictionary.

#     '''
#     dn = d
#     for key in keys:
#         dn = dn.get(key)
#         if dn is None:
#             # TODO Covert to logger
#             # TODO Consider implementing exception
#             print("Unable to find key: {} in keys: {}".format(key, ":".join(keys)))
#             return None
        
#     return dn

# *******************
# *** Sample code ***
# *******************

if __name__ == '__main__':
    
    import time
    import math
    
    @calc_function_time
    def factorial(num):
     
        # sleep 2 seconds because it takes very less time
        # so that you can see the actual difference
        time.sleep(2)
        print(math.factorial(num))
     
    # Call the decorated function.
    factorial(10)
    
