#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

## 3rd party modules ##
import ply.lex

a = """
Takes a string and returns a string of tokens.

This is the first step in the process of executing a program -- this class
will return a stream of tokens which should then be fed to a Parser object
(see 'axe/parser.py').
"""


    
## Define tokens ##

# Reserved keywords:
# Doesn't require a regex.
reserved = {
    'If' : 'IF',
    'Else' : 'ELSE',
    'End' : 'END',
    'Lbl' : 'LBL',
    'Goto' : 'GOTO',
    'Disp' : 'DISP',
    'For' : 'FOR',
    'While': 'WHILE',
    'Repeat': 'REPEAT',
    'Rect': 'RECT',
    'RectI': 'RECTI',
    'Circle': 'CIRCLE',
    'DispGraph': 'DISPGRAPH',
    'ClrDraw': 'CLRDRAW',
    'Line': 'LINE',
    'Pause': 'PAUSE',
    'rand': 'RAND',
    'Horizontal' : 'HORIZONTAL',
    'Vertical' : 'VERTICAL',
    'DiagnosticOn' : 'DIAGNOSTICON',
    'DiagnosticOff' : 'DIAGNOSTICOFF'
}

# Tokens:
# Requires a regex
tokens = [
    'DEBUG',
    'EXIT',
    'HELP',
    'ABOUT',
    'VAR',
    'CONST',
    'NUMBER',
    'COLON',
    'COMMA',
    'GETKEY',
    'DEREFERENCE',
    'RMODIFIER',
    'LMODIFIER',
    'TWOMODIFIER',
    'NEWLINE',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'ASSIGN',
    'PXL_ON',
    'PXL_OFF',
    'PXL_TEST',
    'PXL_CHANGE',
    'INCREMENT',
    'DECREMENT',
    'ADD',
    'SUB',
    'MUL',
    'DIV',
    'MOD',
    'LT',
    'LE',
    'EQ',
    'NE',
    'GE',
    'GT',
    'ID',
    'NAME'
] + list(reserved.values())


## Define rules ##

# Note: the docstring is used for regex matching.


t_DEBUG = r'\@DEBUG'
t_EXIT = r'\@EXIT'
#t_STATE = r'\@STATE'
#t_DRAW = r'\@DRAW'
t_HELP = r'\@HELP'
t_ABOUT = r'\@ABOUT'
#t_OPEN = r'\@OPEN'

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_NEWLINE(t):
    r'(\n)+'
    t.lexer.lineno += len(t.value)
    t.value = 'NEWLINE'
    return t

def t_COLON(t):
    r'(:)+'
    t.value = 'NEWLINE'
    return t

def t_COMMA(t):
    r'(\,)'
    t.value = 'COMMA'
    return t

def t_GETKEY(t):
    r'(getKey)|(GetKey)'
    t.value = 'GETKEY'
    return t

def t_DEREFERENCE(t):
    r'(o\^\^)'
    t.value = 'DEREFERENCE'
    return t

def t_RMODIFIER(t):
    r'(\^\^r)'
    t.value = 'RMODIFIER'
    return t

def t_LMODIFIER(t):
    r'(l\^\^)|(L\^\^)'
    t.value = 'LMODIFIER'
    return t

def t_TWOMODIFIER(t):
    r'(\^\^2)'
    t.value = 'TWOMODIFIER'
    return t

def t_LPAREN(t):
    r'(\()'
    t.value = 'LPAREN'
    return t

def t_RPAREN(t):
    r'(\))'
    t.value = 'RPAREN'
    return t

def t_LBRACK(t):
    r'(\{)'
    t.value = 'LBRACK'
    return t

def t_RBRACK(t):
    r'(\})'
    t.value = 'RBRACK'
    return t

def t_ASSIGN(t):
    r'(\-\>)'
    t.value = 'ASSIGN'
    return t

def t_PXL_ON(t):
    r'Pxl\-On'
    t.value = 'PXL_ON'
    return t 

def t_PXL_OFF(t):
    r'Pxl\-Off'
    t.value = 'PXL_OFF'
    return t

def t_PXL_TEST(t):
    r'(Pxl\-Test)|(pxl\-Test)'
    t.value = 'PXL_TEST'
    return t

def t_PXL_CHANGE(t):
    r'Pxl\-Change'
    t.value = 'PXL_CHANGE'
    return t

def t_VAR(t):
    r'\b[A-Z]\b'
    t.value = 'VAR_' + t.value
    return t

def t_CONST(t):
    r'L1|L2|L3|L4|L5|L6'
    t.value = 'CONST_' + t.value
    return t

def t_INCREMENT(t):
    r'\+\+'
    t.value = 'INCREMENT'
    return t

def t_DECREMENT(t):
    r'\-\-'
    t.value = 'DECREMENT'
    return t

def t_ADD(t):
    r'\+'
    t.value = 'ADD'
    return t
    
def t_SUB(t):
    r'\-'
    t.value = 'SUB'
    return t
    
def t_MUL(t):
    r'\*'
    t.value = 'MUL'
    return t
    
def t_DIV(t):
    r'\/'
    t.value = 'DIV'
    return t

def t_MOD(t):
    r'\^'
    t.value = 'MOD'
    return t
        
def t_LE(t):
    r'(\<\=){1}'
    t.value = 'LE'
    return t

def t_LT(t):
    r'\<'
    t.value = 'LT'
    return t
    
def t_EQ(t):
    r'(\=)'
    t.value = 'EQ'
    return t
    
def t_NE(t):
    r'(\!\=)'
    t.value = 'NE'
    return t
    
def t_GE(t):
    r'(\>\=){1}'
    t.value = 'GE'
    return t
    
def t_GT(t):
    r'(\>){1}'
    t.value = 'GT'
    return t

def t_ID(t):
    r'[A-Za-z][a-zA-Z_0-9]*'
    # Check for reserved keywords
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'ID':
        if len(t.value) <= 8:
            t.type = 'NAME'
    return t

def t_COMMENT(t):
    r'(\..*)|(\.\.\.\n.*\n\.\.\.)'
    pass    # No return value.

def t_error(t):
    error_str = "! > Unrecognized token.  Lineno {lineno}, column {column}.  Token: '{token}'"
    info = {'lineno': t.lexer.lineno,
            'column': find_column(t.value, t),
            'token':  t.value}
    print error_str.format(**info)
    t.lexer.skip(1)
    pass

t_ignore = ' \t'

## Misc. functions ##
def find_column(input_str, token):
    last_cr = input_str.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr) + 1
    return column


    
    
    
def build(**kwargs):
    return ply.lex.lex(debug=0, **kwargs)
    

def test(text):
    """
    Tests the lexer and prints the stream of tokens.
    
    Specifically, this allows the user to repeatedly enter text in via the
    console to see exactly how they are lexed.
    """
    lexer = build()
    while True:
        if text:
            lexer.input(text)
            while True:
                tok = lexer.token()
                if not tok:
                    break
                print tok
        try:
            text = raw_input('lexer > ')
        except KeyboardInterrupt:
            print ''
            break
    return

if __name__ == '__main__':
    test()
    
