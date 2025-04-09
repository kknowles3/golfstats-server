# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 12:29:04 2022

@author: kknow

Collection of utilities for scripts and operational and maintenance task.

This is experimental and under construction

"""

from abc import ABC


# TOOD Consider renaming to ResultScript
class OpsScript(ABC):
    
    def run(self, *args):
        return NotImplemented
    
    def save_results(self, *args):
        return NotImplemented
    
if __name__ == '__main__':
    
    script = OpsScript()
    script.run()
    
    class Ops2(OpsScript):
        ...
        
    script2 = Ops2()
    script2.run()