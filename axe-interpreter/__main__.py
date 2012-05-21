#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

#import cProfile
#import pstats

## Project Modules ##
import console
import axe
from meta import *


def main(args=None):
    """
    A wrapper around various parts of this program to take input and run it.
    
    This should be considered the main entry point of the program, and should
    be run from the command line.  You can also pass in arguments via a 
    list of strings.
    
    The two are identical:
    
        $ python __init__.py --test interpreter ~/programs/test.txt
        
    ...and...
    
        >>> import __init__
        >>> __init__.main(['--test', 'interpreter', r'~/program/test.txt'])
    """
    console_parser = console.CommandIo()
    if args:
        options = console_parser.parse(args)
    else:
        options = console_parser.parse()
        
    if options.input_path:
        with open(options.input_path, 'r') as input_file:
            text = input_file.read()
    else:
        text = ''
    
    choice = options.test
    
    if choice == 'lexer':
        axe.lexer.test(text)
    elif choice == 'parser':
        axe.parser.test(text)
    elif choice == 'interpreter':
        axe.interpreter.test(text=text)
    return

# Testing harness below (too lazy to bundle properly)
#
#text1 = """
#.TEST
#
#ClrDraw
#20->X->Y
#
#Repeat getKey(15)
#    X - getKey(2) + getKey(3) -> X
#    Y - getKey(4) + getKey(1) -> Y
#    Rect(X,Y,5,5)^^r
#    DispGraph^^r
#    RectI(X,Y,5,5)^^r
#End
#"""
#
#text = """
#.AA
#
#0->B
#For(A,0,2000):
#    For(C,0,100):
#        A->B
#    End
#End
#Disp B
#"""
#
#interp = None
#ast = None
#
#def setup():
#    global interp
#    global ast
#    interp = axe.Axe()
#    interp.calculator.init()
#    ast = interp.parser.parse(text, lexer=interp.lexer)
#    return
#        
#def quick():
#    global interp
#    global ast
#    interp.interpreter.execute(ast)
#    return
#
#def test():
#    setup()
#    #quick()
#    cProfile.run('quick()', 'results')
#    stats = pstats.Stats('results')
#    stats.sort_stats('calls', 'nfl')
#    stats.print_stats()#

if __name__ == '__main__':
    main()
    #test()
