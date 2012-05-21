#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

## Program Modules ##
import axe.lexer
import axe.parser
import axe.interpreter
import axe.calculator
from meta import *
    
class Axe():
    def __init__(self):
        self.lexer = axe.lexer.build()
        self.parser = axe.parser.build()
        self.calculator = axe.calculator.Calculator()
        self.interpreter = axe.interpreter.Interpreter(self.calculator)
        return
    
    def run(self, text=''):
        self.calculator.init()
        ast = self.parser.parse(text, lexer=self.lexer)
        return self.interpreter.execute(ast)

if __name__ == '__main__':
    axe = Axe()
    axe.run()
    
    
