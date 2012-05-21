#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

## System Modules ##
import argparse

## Program Modules ##
import meta

class CommandIo():
    """
    Reads and interprets arguments from the console/command line.
    
    This is the main method of obtaining input to run the program.  It uses
    argparse, a module from the standard library.
    """
    def __init__(self):
        """
        Initializes the class and creates the parser and its arguments.
        """
        self._parser = argparse.ArgumentParser(
            description=meta.__description__,
            add_help=True,
            prog=meta.__program_name__
        )
        self._add_arguments()
        return
    
    def _add_arguments(self):
        """
        Adds arguments to the parser.
        
        This method should only by called by self.__init__
        """
        self._add_mandatory_arguments()
        self._add_optional_arguments()
        return
    
    def _add_mandatory_arguments(self):
        """
        Adds mandatory arguments to the parser.
        
        This method should only be called by self._add_arguments
        """
        self._parser.add_argument(
            'input_path',
            nargs='?',
            type=str,
            help='The path to the file to execute.'
        )
        return
    
    def _add_optional_arguments(self):
        """
        Adds optional arguments to the parser.
        
        This method should only be called by self._add_arguments
        """
        self._parser.add_argument(
            '-v', '--version',
            action='version',
            version='Version ' + meta.__version__ + '; released ' + \
                meta.__release__,
            help='Display the version and release date.'
        )
        self._parser.add_argument(
            '-t', '--test',
            action='store',
            nargs='?',
            const=None,
            default='interpreter',
            type=str,
            choices=['lexer', 'parser', 'interpreter'],
            help='Test specific components of this program.',
            dest='test'
        )
        return
    
    def parse(self, arguments=None):
        """
        Parses input from the command line.
        
        Calling this without any arguments gets values directly from the 
        console.  Alternatively, you can call this function and pass a list of
        strings.  The two are equivalent:
        
    
            $ python console.py --test interpreter ~/programs/test.txt
        
        ...and...
    
            >>> import console
            >>> console.main(['--test', 'interpreter', r'~/program/test.txt'])
        """
        if arguments == None:
            options = self._parser.parse_args()
        else:
            options = self._parser.parse_args(arguments)
        return options



if __name__ == '__main__':
    pass
    
