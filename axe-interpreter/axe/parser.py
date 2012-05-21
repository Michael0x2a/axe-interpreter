#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

## System modules ##
import operator

## 3rd party modules ##
import ply.yacc

## Program modules ##
import lexer
from lexer import tokens

a = """
Takes a lexer object and returns an abstract syntax tree.

This module is an intermediary step in the process.  It requires a Lexer
object (see 'axe/lexer.py'), and returns an abstract syntax tree which is
then used by an Interpreter object (see 'axe/interpreter.py') to actually
run the program.
"""



class Node(object):
    """A generic node for the ast."""
    def __init__(self, name, *args):
        assert(isinstance(name, basestring))
        self.name = name
        self.children = list(args)
        return
    
    def __repr__(self, indent=0):
        output = self._wrap(indent, self.name, self.children)
        return '\n'.join(output)
    
    def __str__(self, indent=0):
        return self.__repr__(indent)
    
    def add_children(self, *args):
        args = list(args)
        if len(args) == 1 and type(args[0]) == list:
            args = args[0]
        self.children.extend(args)
        return
    
    def _tab(self, indent):
        tab = '  '
        return tab * indent
    
    def _wrap(self, indent, name, args):
        output = []
        output.append(self._tab(indent) + name + ': {')
        if not isinstance(args, list):
            args = [args]
        for arg in args:
            if isinstance(arg, Node):
                output.append(arg.__repr__(indent + 1))
            else:
                output.append(self._tab(indent + 1) + arg)
        if output[-1].endswith(','):
            output[-1] = output[-1][:-1]
        output.append(self._tab(indent) + '},')
        return output
    
    def _wrap_named(self, indent, name, **kwargs):
        output = []
        output.append(self._tab(indent) + name + ': {')
        for name, item in kwargs.items():
            output.extend(self._wrap(indent + 1, name, item))
        if output[-1].endswith(','):
            output[-1] = output[-1][:-1]
        output.append(self._tab(indent) + '},')
        return output


class Line(Node):
    def __init__(self, *args):
        super(Line, self).__init__('line', *args)
        return


class Control(Node):
    def __init__(self, name, **kwargs):
        self.name = name
        self.children = kwargs
        return
    
    def __repr__(self, indent=0):
        output = self._wrap_named(indent, self.name, **self.children)
        return '\n'.join(output)

class Expression(Node):
    """Nearly everything resolves to an expression of some kind.  An expression
    must have a 'value' attribute, which will resolve to a number."""
    def __init__(self, value):
        self.name = 'expression'
        self.value = value
        return
    
    def __repr__(self, indent=0):
        output = []
        start = self._tab(indent) + self.name + ': {'
        if type(self.value) == int:
            output.append(start + str(self.value) + '},')
        else:
            output.append(start)
            output.append(self.value.__repr__(indent + 1))
            output.append(self._tab(indent) + '},')
        if output[-1].endswith(','):
            output[-1] = output[-1][:-1]
        return '\n'.join(output)
    
    def _get_value(self):
        return self.children[0]
        
    def _set_value(self, value):
        self.children = [value]
        return


class Operation(Expression):
    """Addition, subtraction, etc."""
    def __init__(self, op, *args):
        assert(isinstance(op, basestring))
        self.name = 'operation'
        self.op = op
        self.args = list(args)
        return
    
    def resolve(self):
        resolved_args = []
        for arg in self.args:
            if isinstance(arg, Expression):
                test = arg.value
            elif type(arg) == int:
                test = arg
            if type(test) != int:
                return None
            resolved_args.append(test)
                
        seed = resolved_args[0]
        for arg in resolved_args[1:]:
            seed = getattr(operator, self.name)(seed, arg)
        return seed
    
    def __repr__(self, indent=0):
        output = self._wrap(indent, self.name + ' ' + self.op, self.children)
        return '\n'.join(output)
    
    def _get_op(self):
        return self._op
    
    def _set_op(self, op):
        self._op = op.lower()
    
    op = property(_get_op, _set_op)
    
    def _get_args(self):
        return self.children
    
    def _set_args(self, args):
        for arg in args:
            assert(isinstance(arg, Expression))
        self.children = list(args)
        return
    
    args = property(_get_args, _set_args)


class Assignment(Expression):
    """Assigning an expression to a pointer."""
    def __init__(self, value=None, pointer=None):
        # Although 'assignment' has to be defined, so shouldn't technically be
        # a keyword argument, it's intentionally placed that way so that
        # the order of the arguments mirrors Axe.
        #     value -> pointer
        self.name = 'assignment'
        self.value = value
        self.pointer = pointer
        return
    
    def __repr__(self, indent=0):
        output = []
        output.append(self._tab(indent) + self.name + ': {')
        output.append(self._tab(indent + 1) + 'value : {' )
        output.append(self.value.__repr__(indent + 2))
        output.append(self._tab(indent + 1) + '},')
        output.append(self.pointer.__repr__(indent + 1))
        output.append(self._tab(indent) + '},')
        return '\n'.join(output)
    
    def _get_value(self):
        return self.children[0]
    
    def _set_value(self, value):
        assert(isinstance(value, Expression))
        self.children = [value]
        return
    

class Command(Node):
    def __init__(self, name, *args):
        self.name = name
        self.children = list(args)
        return

class Drawing(Command):
    def __init__(self, name, buf, start_x, start_y, **kwargs):
        self.name = name.lower()
        self.buf = buf
        self.start_x = start_x
        self.start_y = start_y
        self.kwargs = kwargs
        return
    
    def __repr__(self, indent=0):
        data = {
            'buffer_start' : self.buf,
            'start_x' : self.start_x,
            'start_y' : self.start_y,
        }
        data.update(self.kwargs)
        output = self._wrap_named(indent, self.name, **data)
        return '\n'.join(output)

class Buffer(Command):
    def __init__(self, name, buf, **kwargs):
        self.name = name.lower()
        self.buf = buf
        self.kwargs = kwargs
        return
    
    def __repr__(self, indent=0):
        kwargs = self.kwargs
        kwargs['buffer'] = self.buf
        output = self._wrap_named(indent, self.name, **kwargs)
        return '\n'.join(output)
        
class Getkey(Command):
    def __init__(self, name, number, **kwargs):
        self.name = name.lower()
        self.number = number
        self.kwargs = kwargs
        return
    
    def __repr__(self, indent=0):
        data = {'number' : self.number}
        data.update(self.kwargs)
        output = self._wrap_named(indent, self.name, **data)
        return '\n'.join(output)
        
class Label(Expression):
    def __init__(self, name, value):
        self.name = name
        self.value = value
        return
    
    def __repr__(self, indent=0):
        output = self._wrap_named(indent, self.name, self.value)
        return '\n'.join(output)

class Meta(Node):
    pass
        

class Pointer(Expression):
    constants = {
        'START':0,
        'AZ_VARS':35254,
        'R_VARS':33701,
        'CONSTS':40000,
        'L1':34540,
        'L2':35386,
        'L3':39026,
        'L4':33445,
        'L5':34056,
        'L6':37696,
        'TEMP':2000
    }
    
    def __init__(self, offset, size, const='START'):
        assert(const in Pointer.constants.keys())
        self.name = 'pointer'
        self.size = size
        if const != 'START':
            start = Expression(Pointer.constants[const])
            offset = Expression(offset)
            address = Operation('add', start, offset)
        else:
            assert(isinstance(offset, Expression))
            address = offset
        self.address = address
        return
    
    def _get_address(self):
        return self.value
    
    def _set_address(self, address):
        assert(isinstance(address, Expression))
        self.value = address
        return
    
    address = property(_get_address, _set_address)
    
class NotImplemented(Node):
    def __init__(self, *args):
        self.name = 'notimplemented'
        self.children = list(args)
        return
  

def debug(function, *args, **kwargs):
    global _debug
    def wrapper(p):
        if _debug:
            print '@', function.__name__, ':', list(p)
        function(p)
    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper

_debug = False
_temp_counter = 0
start = 'program'   # Automagically read by ply.



# General note:
# PLY will be reading through the below functions, and using the docstrings
# to parse the tokens.
#
# Also note that the order in which the functions below are written matter --
# if they are re-arranged, PLY will parse tokens in the incorrect order, leading
# to a garbled output.

## Program (start point) ##
@debug
def p_program_start(p):
    '''program : block'''
    # This rule is the very top of the program -- everything is resolved here.
    p[0] = Node('program', p[1])
    return

@debug
def p_program_continue(p):
    '''program : program block'''
    p[0] = Node('program', p[2])
    return

## Blocks (collection of lines) ##
@debug
def p_block_start(p):
    '''block : line
             | control'''
    p[0] = Node('block', p[1])
    return

@debug
def p_block_reduce(p):
    '''block : block block'''
    block = p[1]
    block.add_children(p[2].children)
    p[0] = block
    return

@debug
def p_block_reduce_newline(p):
    '''block : newline block'''
    p[0] = p[2]
    return

## Control Flow ##
@debug
def p_control_while(p):
    '''control : WHILE expression newline block END newline'''
    p[0] = Control('while', condition=p[2], body=p[4])
    return

@debug
def p_control_repeat(p):
    '''control : REPEAT expression newline block END newline'''
    p[0] = Control('repeat', condition=p[2], body=p[4])
    return

@debug
def p_node_full_for(p):
    '''control : FOR LPAREN pointer COMMA expression COMMA expression RPAREN newline block END newline'''
    p[0] = Control(
        'for', 
        pointer=p[3], 
        start=p[5], 
        end=p[7],
        increment=Expression(1),
        body=p[10])
    return

@debug
def p_node_const_for(p):
    '''control : FOR LPAREN expression RPAREN newline block END newline'''
    global temp_counter
    p[0] = Control(
        'for',
        pointer=Pointer(temp_counter, 2, 'TEMP'),
        start=Expression(0),
        end=p[3],
        increment=Expression(1),
        body=p[6])
    return

@debug
def p_control_if_single(p):
    '''control : IF expression newline block END newline'''
    p[0] = Control('if', condition=p[2], body=p[4])
    return

@debug
def p_control_if_double(p):
    '''control : IF expression newline block ELSE newline block END newline'''
    p[0] = Control('if_else', condition=p[2], body=Node('body', p[4], p[7]))
    return
    
@debug
def p_control_label(p):
    '''control : LBL NAME newline'''
    p[0] = Line(Control('label', target=p[2]))
    return

@debug
def p_control_goto(p):
    '''control : GOTO NAME newline'''
    p[0] = Line(Control('goto', target=p[2]))
    return
    
@debug
def p_control_goto_expression(p):
    '''control : GOTO LPAREN expression RPAREN newline'''
    p[0] = Line(Control('goto', target=p[3]))
    return


## Lines ##
@debug
def p_line_expression(p):
    '''line : expression newline'''
    p[0] = Line(p[1])
    return

@debug
def p_line_disp(p):
    '''line : DISP expression newline'''
    p[0] = Line(Command('disp', p[2]))
    return

@debug
def p_line_pause(p):
    '''line : PAUSE expression newline'''
    p[0] = Line(Command('pause', p[2]))
    return
    
@debug
def p_line_diagnostic(p):
    '''line : DIAGNOSTICON newline
            | DIAGNOSTICOFF newline'''
    p[0] = Line(NotImplemented(p[1].lower()))
    return

@debug
def p_line_meta(p):
    '''line : meta'''
    p[0] = Line(p[1])
    return

@debug
def p_line_factor(p):
    '''line : factor newline'''
    p[0] = Line(p[1])
    return
    
## Commands (doesn't return an expression) ##

## Drawing commands ##
@debug
def p_line_pxl(p):
    '''line : PXL_ON LPAREN expression COMMA expression RPAREN newline
            | PXL_OFF LPAREN expression COMMA expression RPAREN newline
            | PXL_CHANGE LPAREN expression COMMA expression RPAREN newline'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5]))
    return

@debug
def p_line_pxl_backbuffer(p):
    '''line : PXL_ON LPAREN expression COMMA expression RPAREN RMODIFIER newline
            | PXL_OFF LPAREN expression COMMA expression RPAREN RMODIFIER newline
            | PXL_CHANGE LPAREN expression COMMA expression RPAREN RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5]))
    return

@debug
def p_line_pxl_custom(p):
    '''line : PXL_ON LPAREN expression COMMA expression COMMA expression RPAREN newline
            | PXL_OFF LPAREN expression COMMA expression COMMA expression RPAREN newline
            | PXL_CHANGE LPAREN expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(p[7], 2, 'START')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5]))
    return
    
@debug
def p_line_screen_shift_buffer(p):
    '''line : HORIZONTAL ADD newline
            | HORIZONTAL SUB newline
            | VERTICAL ADD newline
            | VERTICAL SUB newline'''
    buf = Pointer(0, 2, 'L6')
    direction = 1
    if p[2] == 'SUB':
        direction = -1
    p[0] = Node(p[1].lower(), direction, buf)
    return

@debug 
def p_line_screen_shift_backbuffer(p):
    '''line : HORIZONTAL ADD RMODIFIER newline
            | HORIZONTAL SUB RMODIFIER newline
            | VERTICAL ADD RMODIFIER newline
            | VERTICAL SUB RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    direction = 1
    if p[2] == 'SUB':
        direction = -1
    p[0] = Node(p[1].lower(), direction, buf)
    return
    
@debug
def p_line_screen_shift_custom(p):
    '''line : HORIZONTAL ADD LPAREN expression RPAREN newline
            | HORIZONTAL SUB LPAREN expression RPAREN newline
            | VERTICAL ADD LPAREN expression RPAREN newline
            | VERTICAL SUB LPAREN expression RPAREN newline'''
    buf = Pointer(p[4], 2, 'START')
    direction = 1
    if p[2] == 'SUB':
        direction = -1
    p[0] = Node(p[1].lower(), direction, buf)
    return

@debug
def p_line_rect(p):
    '''line : RECT LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN newline
            | RECTI LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], width=p[7], height=p[9]))
    return

@debug
def p_line_rect_backbuffer(p):
    '''line : RECT LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN RMODIFIER newline
            | RECTI LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], width=p[7], height=p[9]))
    return

@debug
def p_line_rect_custom(p):
    '''line : RECT LPAREN expression COMMA expression COMMA expression COMMA expression COMMA expression RPAREN newline
            | RECTI LPAREN expression COMMA expression COMMA expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(p[11], 2, 'START')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], width=p[7], height=p[9]))
    return

@debug
def p_line_circle(p):
    '''line : CIRCLE LPAREN expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], radius=p[7]))
    return

@debug
def p_line_circle_backbuffer(p):
    '''line : CIRCLE LPAREN expression COMMA expression COMMA expression RPAREN RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], radius=p[7]))
    return
    
@debug
def p_line_circle_custom(p):
    '''line : CIRCLE LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(p[9], 2, 'START')
    p[0] = Line(Drawing(p[1], buf, p[3], p[5], radius=p[7]))
    return
    
@debug
def p_line_line(p):
    '''line : LINE LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Line(Drawing('draw_line', buf, p[3], p[5], end_x=p[7], end_y=p[9]))
    return

@debug
def p_line_line_backbuffer(p):
    '''line : LINE LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Line(Drawing('draw_line', buf, p[3], p[5], end_x=p[7], end_y=p[9]))
    return
    
@debug
def p_line_line_custom(p):
    '''line : LINE LPAREN expression COMMA expression COMMA expression COMMA expression COMMA expression RPAREN newline'''
    buf = Pointer(p[11], 2, 'START')
    p[0] = Line(Drawing('draw_line', buf, p[3], p[5], end_x=p[7], end_y=p[9]))
    return

## Screen and buffer ##
@debug
def p_line_dispgraph_monoscale(p):
    '''line : DISPGRAPH newline'''
    buffer_ = Pointer(0, 2, 'L6')
    state = Expression(2)
    p[0] = Line(Buffer(p[1], buffer_, state=state))
    return

@debug
def p_line_dispgraph_monoscale_custom(p):
    '''line : DISPGRAPH LPAREN expression RPAREN newline'''
    buf = Pointer(p[3], 2, 'START')
    p[0] = Line(Buffer(p[1], buf, state=Expression(2)))
    return

@debug
def p_line_dispgraph_3scale(p):
    '''line : DISPGRAPH RMODIFIER newline'''
    buf = Pointer(0, 2, 'L6')
    backbuf = Pointer(0, 2, 'L3')
    p[0] = Line(Buffer(p[1], buf, backbuffer=backbuf, state=Expression(3)))
    return

@debug
def p_line_dispgraph_3scale_custom(p):
    '''line : DISPGRAPH LPAREN expression COMMA expression RPAREN RMODIFIER newline'''
    buf = Pointer(p[3],2,'START')
    backbuf = Pointer(p[5],2,'START')
    p[0] = Line(Buffer(p[1], buf, backbuffer=backbuf, state=Expression(3)))
    return

@debug
def p_line_dispgraph_4scale(p):
    '''line : DISPGRAPH RMODIFIER RMODIFIER newline'''
    buf = Pointer(0,2,'L6')
    backbuf = Pointer(0,2,'L3')
    p[0] = Line(Buffer(p[1], buf, backbuffer=backbuf, state=Expression(4)))
    return

@debug
def p_line_dispgraph_4scale_custom(p):
    '''line : DISPGRAPH LPAREN expression COMMA expression RPAREN RMODIFIER RMODIFIER newline'''
    buf = Pointer(p[3], 2, 'START')
    backbuf = Pointer(p[5], 2, 'START')
    p[0] = Line(Buffer(p[1], buf, backbuffer=backbuf, state=Expression(4)))
    return
    


@debug
def p_line_clrdraw_buffer(p):
    '''line : CLRDRAW newline'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Line(Buffer(p[1], buf))
    return

@debug
def p_line_clrdraw_buffer_custom(p):
    '''line : CLRDRAW RPAREN expression LPAREN newline'''
    buf = Pointer(p[3], 2, 'START')
    p[0] = Line(Buffer(p[1], buf))
    return
 
@debug
def p_line_clrdraw_backbuffer(p):
    '''line : CLRDRAW RMODIFIER newline'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Line(Buffer(p[1], buf))
    return


## Expressions ##
@debug
def p_factor_start_number(p):
    '''factor : NUMBER'''
    p[0] = Expression(p[1])
    return

@debug
def p_factor_start_expression(p):
    '''factor : expression'''
    p[0] = p[1]
    return

@debug
def p_expression_increment(p):
    '''expression : pointer INCREMENT'''
    operation = Operation('add', p[1], Expression(1))
    assignment = Assignment(value=operation, pointer=p[1])
    p[0] = assignment
    return

@debug
def p_expression_decrement(p):
    '''expression : pointer DECREMENT'''
    operation = Operation('sub', p[1], Expression(1))
    assignment = Assignment(value=operation, pointer=p[1])
    p[0] = assignment
    return

@debug
def p_operation(p):
    '''expression : expression operator factor'''
    p[0] = Operation(p[2], p[1], p[3])
    return
    
@debug
def p_operation_double(p):
    '''expression : expression TWOMODIFIER'''
    p[0] = Operation('mul', p[1], p[1])

@debug
def p_factor_reduce_parenthesis(p):
    '''tempexpression : LPAREN factor RPAREN'''
    p[0] = p[2]
    return

@debug
def p_expression_reduce_parenthesis(p):
    '''tempexpression : LPAREN expression RPAREN'''
    p[0] = p[2]
    return

# Has a weaker priority then 'factor : NUMBER'
@debug
def p_expression_start_number(p):
    '''expression : NUMBER'''
    p[0] = Expression(p[1])
    return

@debug
def p_expression_negatives(p):
    '''factor : SUB expression'''
    p[0] = Operation('sub', Expression(0), p[2])
    return






## Pointers ##
@debug
def p_tempexpression_pointer(p):
    '''tempexpression : pointer'''
    p[0] = p[1]
    return

@debug
def p_pointer_start_single(p):
    '''pointer : LBRACK expression RBRACK'''
    p[0] = Pointer(p[2], 1)
    return

@debug
def p_pointer_start_double(p):
    '''pointer : LBRACK expression RBRACK RMODIFIER'''
    p[0] = Pointer(p[2], 2)
    return

@debug
def p_pointer_map_var(p):
    '''pointer : VAR'''
    var = p[1][4:]
    var_order = ['A', 'B', 'C', 'D', 'E',
              'F', 'G', 'H', 'I', 'J',
              'K', 'L', 'M', 'N', 'O', 
              'P', 'Q', 'R', 'S', 'T', 
              'U', 'V', 'W', 'X', 'Y', 
              'Z', 'THETA']
    p[0] = Pointer(var_order.index(var) * 2, 2, 'AZ_VARS')
    return

@debug
def p_tempexpression_dereference(p):
    '''tempexpression : DEREFERENCE pointer'''
    p[0] = Expression(Node(p[1].lower(), p[2]))
    return

@debug
def p_tempexpression_const(p):
    '''tempexpression : CONST'''
    p[0] = Pointer(0, 2, p[1][6:])
    return



@debug
def p_expression_tempexpression(p):
    '''factor : tempexpression'''
    p[0] = p[1]
    return


## Commands that return numbers ##

@debug
def p_tempexpression_rand(p):
    '''tempexpression : RAND'''
    p[0] = Expression(Command('rand'))
    return

@debug
def p_tempexpression_pxl_test(p):
    '''tempexpression : PXL_TEST LPAREN expression COMMA expression RPAREN'''
    buf = Pointer(0, 2, 'L6')
    p[0] = Expression(Drawing(p[1], buf, p[3], p[5]))
    return

@debug
def p_tempexpression_pxl_test_backbuffer(p):
    '''tempexpression : PXL_TEST LPAREN expression COMMA expression RPAREN RMODIFIER'''
    buf = Pointer(0, 2, 'L3')
    p[0] = Expression(Drawing(p[1], buf, p[3], p[5]))
    return

@debug
def p_tempexpression_pxl_test_custom(p):
    '''tempexpression : PXL_TEST LPAREN expression COMMA expression COMMA expression COMMA expression RPAREN'''
    buf = Pointer(p[7], 2, 'START')
    p[0] = Expression(Drawing(p[1], buf, p[3], p[5]))
    return

@debug
def p_expression_label_get_address(p):
    '''tempexpression : LMODIFIER NAME'''
    p[0] = Expression(Node('get_label', p[2]))
    return


@debug
def p_tempexpression_getkey(p):
    '''tempexpression : GETKEY LPAREN expression RPAREN'''
    p[0] = Expression(Getkey(p[1], p[3]))
    return

@debug
def p_expression_assignment_start(p):
    '''tempexpression : expression ASSIGN pointer'''
    p[0] = Assignment(value=p[1], pointer=p[3])
    return
    
    
@debug
def p_expression_factor_hack(p):
    '''expression : factor'''
    p[0] = p[1]
    return
    

## Combinations ##
@debug
def p_combination_newline(p):
    '''newline : COLON
               | NEWLINE'''
    p[0] = p[1]
    return

@debug
def p_combination_reduce_newline(p):
    '''newline : newline newline'''
    p[0] = p[1]
    return

@debug
def p_combination_operator(p):
    '''operator : ADD
                | SUB
                | MUL
                | DIV
                | MOD
                | LT
                | LE
                | EQ
                | NE
                | GT
                | GE
    '''
    p[0] = p[1]
    return

## Meta ##
@debug
def p_meta_exit(p):
    '''meta : EXIT newline'''
    p[0] = Meta('exit', 0)
    raise SystemExit(0)
    return

@debug
def p_meta_debug(p):
    '''meta : DEBUG expression newline'''
    global _debug  # A hack, I know.
    
    if p[2].value == 0:
        _debug = False
    else:
        _debug = True
    p[0] = Meta('debug', p[2])
    return

@debug
def p_meta_about(p):
    '''meta : ABOUT newline'''
    p[0] = Meta('about')
    return

@debug
def p_meta_help(p):
    '''meta : HELP newline'''
    p[0] = Meta('help')
    return

## Misc. ##
@debug
def p_id(p):
    '''line : ID'''
    p[0] = None
    return

def p_error(t):
    try:
        info = {'lineno': t.lineno, 'value':t.value}
        print "! > Syntax error @ line {lineno}: '{value}'".format(**info)
    except AttributeError:  # could not find lineno or value
        print "! > Syntax error."
    return

    
    

def build(tabmodule='parsing_rules'):
    return ply.yacc.yacc(tabmodule=tabmodule, debug=0)


def reset_counters():
    global _temp_counter
    _temp_counter = 0
    return


def test(text='', lexer_=None):
    """
    Tests the parser and prints the abstract syntax tree.
    
    Specifically, this allows the user to repeatedly enter text in via the
    console to see exactly how they are parsed and to see how the ast looks 
    like.
    
    This function will also require an instance of a Lexer object.
    """
    if not lexer_:
        lexer_ = lexer.build()
    parser = build()
    while True:
        if text:
            if text[-1] not in ('\n', ':'):
                text += '\n'
            result = parser.parse(text, lexer=lexer_)
            reset_counters()
            print result, '\n'
        try:
            text = raw_input('parser > ')
        except KeyboardInterrupt:
            print ''
            break
    return

if __name__ == '__main__':
    test()
    
