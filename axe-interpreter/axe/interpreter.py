#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""

from __future__ import print_function
import os.path
import operator
import threading
import webbrowser #temporary?
import random
import time


import axe.lexer
import axe.parser
import axe.calculator

class AxeRuntimeError(Exception):
    """Errors that occur during runtime."""
    pass
    
class MissingLabelException(AxeRuntimeError):
    """A goto or function is referencing a missing label."""
    pass

class Interpreter(object):
    """
    Takes an abstract syntax tree and runs it.
    
    This is the final step in the process.  It requires an abstract syntax tree
    (see 'axe/parser.py'), quickly converts it into a flattened form, and runs
    it.
    
    This class will also require an instance of a 'Calculator' object 
    (see 'axe/calculator.py') to handle graphics and memory.
    """
    # A note (because I'll forget), but not formally part of the docs
    # (because I'm too impatient to make this coherent):
    #
    # Closures.
    # Each line becomes a function (or lambda, whatever) added to a Code object
    # which is essentially a list with extra stuff.
    #
    # Upon finishing appending each lambda/function and converting the ast
    # into a sequence of callable objects, each item is called in sequence.
    # The Code object has a counter object, which is used to show the position
    # within the list.
    #
    # Each closure gets access to both the Code and Calculator namespaces, 
    # along with whatever values it got at compile time in the Interpreter
    # object.  The closures themselves will possibly contain more callable
    # functions, which are called at runtime, not Interpreter-time, so stuff like
    # accessing variables can be done dynamically.
    # 
    # The demo interpreter itself saves the state of the calculator so that 
    # subsequent statements can be 
    # (although it 
    def __init__(self, calculator):
        self.calculator = calculator
        return
    
    def start(self):
        self.calculator.init()
        return
    
    def execute(self, ast):
        code = Code()
        self.check = 'before'
        self.flatten(code, ast)
        self.check = 'after'
        self.run(code)
        return

    def flatten(self, code, ast):
        if not ast:
            return None
        return getattr(self, '_' + ast.name)(code, ast)

    def run(self, code):
        out = None
        try:
            while True:
                out = code.next()(code)
        except TypeError:
            pass
        print('... ', out)
        return
    
    def sanity_check(self):
        self.calculator.sanity_check()
        return
    
    ### System components ###
    
    def _program(self, code, ast):
        for subtree in ast.children:
            self.flatten(code, subtree)
        return
    
    def _block(self, code, ast):
        for subtree in ast.children:
            self.flatten(code, subtree)
        return
    
    def _line(self, code, ast):
        line = ast.children[0]
        l_output = self.flatten(code, line)
        assert(type(l_output) != int)
        code.append(l_output)
        return l_output
    
    ### Numerical components ###
    
    def _expression(self, code, ast):
        if type(ast.value) == int:
            def l_expression(other):
                return ast.value
            return l_expression     # using lambdas makes it harder to debug.
        else:
            return self.flatten(code, ast.value)
        return
    
    def _operation(self, code, ast):
        def collapse(list_, op):
            seed = list_[0]
            for num in list_[1:]:
                seed = getattr(operator, op)(seed, num)
            return seed
        
        args = []
        numbers_args = []
        for arg in ast.args:
            if type(arg) == int:
                numbers_args.append(arg)
            elif type(arg) == bool:
                numbers_args.append(int(arg, 10))
            else:
                if len(numbers_args) >= 2:
                    args.append(collapse(numbers_args, ast.op))
                else:
                    args.extend(numbers_args)
                numbers_arg = []
                args.append(arg)
        if len(numbers_args) >= 2:
            args.append(collapse(numbers_args, ast.op))
        else:
            args.extend(numbers_args)
        
        l_seed = self.flatten(code, args[0])
        operation = getattr(operator, ast.op)
        subargs = args[1:]
        def l_operation(other):
            s_seed = l_seed(other)
            for l_expression in subargs:
                s_term = self.flatten(code, l_expression)(other)
                s_seed = operation(s_seed, s_term)
            return s_seed
        return l_operation
    
    ### Pointers and assignment ###
    
    def _assignment(self, code, ast):
        l_address = self.flatten(code, ast.pointer.address)
        s_size = ast.pointer.size
        l_value = self.flatten(code, ast.value)
        
        if s_size == 1:
            def l_set_var(other):
                return self.calculator.set_var_1(l_address(other), l_value(other))
        elif s_size == 2:
            def l_set_var(other):
                s_value = l_value(other)
                return self.calculator.set_var_2(l_address(other), l_value(other))
            
        return l_set_var
    
    def _pointer(self, code, ast):
        l_address = self.flatten(code, ast.address)
        s_size = ast.size
        
        if s_size == 1:
            def l_pointer(other):
                return self.calculator.get_var_1(l_address(other))
        elif s_size == 2:
            def l_pointer(other):
                return self.calculator.get_var_2(l_address(other))
        
        return l_pointer
    
    def _dereference(self, code, ast):
        l_address = self.flatten(code, ast.children[0].address)
        def dereference(other):
            s_address = l_address(other)
            return s_address
        return dereference
    
    ### Control structures ###
    
    def _while(self, code, ast):
        # Add condition checking placeholder
        l_condition = self.flatten(code, ast.children['condition'])
        s_start = code.append('PLACEHOLDER')
        
        # Add body (should be done automatically)
        self.flatten(code, ast.children['body'])
        
        # Add jump to condition checking
        def l_jump_while(other):
            other.jump(s_start)
        s_end = code.append(l_jump_while)
        
        # Modify placeholder
        def l_check_while(other):
            if l_condition(other) == 0:
                other.jump(s_end + 1)
            return 0
        
        code.replace(s_start, l_check_while)
        
        return lambda other: 0
    
    def _repeat(self, code, ast):
        l_condition = self.flatten(code, ast.children['condition'])
        s_start = code.append('PLACEHOLDER')
        
        self.flatten(code, ast.children['body'])
        def l_jump_repeat(other):
            other.jump(s_start)
        s_end = code.append(l_jump_repeat)
        
        def l_check_repeat(other):
            if l_condition(other):
                other.jump(s_end + 1)
            return 1
        
        code.replace(s_start, l_check_repeat)
        
        return lambda other: 0
    
    def _for(self, code, ast):
        # initialize loop variable
        # label TOP: if not condition, jump to label EXIT
        #     body
        #     update var
        #     jump to label TOP
        # label EXIT
        
        # Get initial vars
        l_pointer = self.flatten(code, ast.children['pointer'])
        l_address = self.flatten(code, ast.children['pointer'].address)
        s_size = ast.children['pointer'].size
        
        if s_size == 1:
            calc_set_var = self.calculator.set_var_1
        elif s_size == 2:
            calc_set_var = self.calculator.set_var_2
        
        l_start = self.flatten(code, ast.children['start'])
        l_end = self.flatten(code, ast.children['end'])
        l_increment = self.flatten(code, ast.children['increment'])
        
        # Init loop variable
        def l_init_for(other):
            s_value = l_start(other)
            s_value = calc_set_var(l_address(other), s_value)
            return s_value
        
        code.append(l_init_for)
        
        # Condition checking placeholder
        s_check = code.append('PLACEHOLDER')
        
        # Body
        self.flatten(code, ast.children['body'])
        # Update var and goto start
        def l_update_for(other):
            s_increment = l_increment(other)
            s_address = l_address(other)
            def l_update_mem_for(other):
                s_value = l_pointer(other) + s_increment
                return calc_set_var(s_address, s_value)
            other.internal_replace(l_update_mem_for)
            
            s_value = l_pointer(other) + s_increment
            other.jump(s_check)
            return calc_set_var(s_address, s_value)
        
        code.append(l_update_for)
        
        # Goto start
        def l_jump_for(other):
            other.jump(s_check)
        s_exit = code.append(l_jump_for)
        
        # Replace placeholder w/ actual checking.
        def l_condition_for(other):
            s_loop = l_pointer(other)
            s_end = l_end(other)
            if s_loop > s_end:
                other.jump(s_exit + 1)
            #other.ans = s_end - s_loop  # idk why; ask Runer112 or Quigbo.
            #return other.ans
        
        code.replace(s_check, l_condition_for)
        return lambda other: 0
            
    
    
    def _if(self, code, ast):
        l_condition = self.flatten(code, ast.children['condition'])
        s_start = code.append('PLACEHOLDER')
        
        self.flatten(code, ast.children['body'])
        s_end = code.counter
        
        def l_check_if(other):
            if l_condition(other) == 0:
                other.jump(s_end + 1)
            return 0
        
        code.replace(s_start, l_check_if)
        
        return lambda other: 0
    
    def _if_else(self, code, ast):
        l_condition = self.flatten(code, ast.children['condition'])
        s_start = code.append('PLACEHOLDER')
        
        self.flatten(code, ast.children['body'].children[0])
        
        s_jump = code.append('PLACEHOLDER')
        
        self.flatten(code, ast.children['body'].children[1])
        
        s_exit = code.counter
        
        def l_check_ifelse(other):
            if l_condition(other) == 0:
                other.jump(s_jump + 1)
            return 0
        
        def l_jump_ifelse(other):
            other.jump(s_exit + 1)
        
        code.replace(s_start, l_check_ifelse)
        code.replace(s_jump, l_jump_ifelse)
        
        return lambda other: 0
        
    def _label(self, code, ast):
        s_target = ast.children['target'] # Gets a string, not another node
        code.add_label(s_target, code.counter + 1)
        return lambda other: code.counter + 1
    
    def _goto(self, code, ast):
        l_target = ast.children['target']
        if isinstance(l_target, basestring):
            def l_goto1(other):
                other.jump(other.get_label(l_target))
                return other.next_token
            return l_goto1
        else:
            def l_goto2(other):
                s_target = l_target(other)
                other.jump(s_target)
                return other.next_token
            return l_goto2
        return
    
    def _get_label(self, code, ast):
        s_target = ast.children[0] # Gets a string, not another node
        def l_get_label(other):
            return other.get_label(s_target)
        return l_get_label
        

    ### Drawing ###
    def pxl_commands(self, code, ast, drawing_func):
        l_buffer = self.flatten(code, ast.buf.address)
        l_x = self.flatten(code, ast.start_x)
        l_y = self.flatten(code, ast.start_y)
        s_size = (1, 1)
        def l_pxl(other):
            s_buffer = l_buffer(other)
            s_x = l_x(other)
            s_y = l_y(other)
            s_coords = (s_x, s_y)
            drawing_func(s_buffer, s_coords, s_size)
            return 1
        return l_pxl
    
    def _pxl_on(self, code, ast):
        return self.pxl_commands(code, ast, self.calculator.rect)

    def _pxl_off(self, code, ast):
        return self.pxl_commands(code, ast, self.calculator.clear_rect)
    
    def _pxl_change(self, code, ast):
        return self.pxl_commands(code, ast, self.calculator.inverse_rect)
    
    def _pxl_test(self, code, ast):
        l_buffer = self.flatten(code, ast.buf.address)
        l_x = self.flatten(code, ast.start_x)
        l_y = self.flatten(code, ast.start_y)
        s_size = (1, 1)
        def l_pxl_test(other):
            s_buffer = l_buffer(other)
            s_x = l_x(other)
            s_y = l_y(other)
            return self.calculator.pxl_get(s_buffer, (s_x, s_y))
        return l_pxl_test
        
    def _vertical(self, code, ast): # not working
        s_direction = ast.children[0]
        l_buffer = self.flatten(code, ast.children[1])
        def l_vertical(other):
            self.calculator.shift_buffer_vertical(l_buffer(other), s_direction)
            return
        return l_vertical
    
    def _horizontal(self, code, ast): # not working
        s_direction = ast.children[0]
        l_buffer = self.flatten(code, ast.children[1])
        def l_horizontal(other):
            self.calculator.shift_buffer_horizontal(l_buffer(other), s_direction)
            return
        return l_horizontal
    
    def rect_commands(self, code, ast, drawing_func):
        l_buffer = self.flatten(code, ast.buf.address)
        l_x = self.flatten(code, ast.start_x)
        l_y = self.flatten(code, ast.start_y)
        l_width = self.flatten(code, ast.kwargs['width'])
        l_height = self.flatten(code, ast.kwargs['height'])
        def l_rect(other):
            s_buffer = l_buffer(other)
            s_coords = (l_x(other), l_y(other))
            s_size = (l_width(other), l_height(other))
            drawing_func(s_buffer, s_coords, s_size)
            return 1
        return l_rect
        
    def _rect(self, code, ast):
        return self.rect_commands(code, ast, self.calculator.rect)
        
    def _recti(self, code, ast):
        return self.rect_commands(code, ast, self.calculator.inverse_rect)
    
    def _circle(self, code, ast):
        l_buffer = self.flatten(code, ast.buf.address)
        l_x = self.flatten(code, ast.start_x)
        l_y = self.flatten(code, ast.start_y)
        l_radius = self.flatten(code, ast.kwargs['radius'])
        def l_circle(other):
            s_buffer = l_buffer(other)
            s_coords = (l_x(other), l_y(other))
            s_radius = l_radius(other)
            self.calculator.circle(s_buffer, s_coords, s_radius)
            return 1
        return l_circle
    
    def _draw_line(self, code, ast):
        l_buffer = self.flatten(code, ast.buf.address)
        l_start_x = self.flatten(code, ast.start_x)
        l_start_y = self.flatten(code, ast.start_y)
        l_end_x = self.flatten(code, ast.kwargs['end_x'])
        l_end_y = self.flatten(code, ast.kwargs['end_y'])
        def l_draw_line(other):
            s_buffer = l_buffer(other)
            s_start = (l_start_x(other), l_start_y(other))
            s_end = (l_end_x(other), l_end_y(other))
            self.calculator.line(s_buffer, s_start, s_end)
            return 1
        return l_draw_line

    def _dispgraph(self, code, ast):
        l_buffer = self.flatten(code, ast.buf.address)
        s_state = ast.kwargs['state'].value
        if s_state > 2:
            l_backbuffer = self.flatten(code, ast.kwargs['backbuffer'].address)
            def l_dispgraph(other):
                s_buffer = l_buffer(other)
                s_backbuffer = l_backbuffer(other)
                self.calculator.disp_screen(s_buffer, s_backbuffer, s_state)
                return
        else:
            def l_dispgraph(other):
                s_buffer = l_buffer(other)
                self.calculator.disp_screen_mono(s_buffer)
                return
        return l_dispgraph
    
    def _clrdraw(self, code, ast):
        l_buffer = self.flatten(code, ast.buf.address)
        def l_clrdraw(other):
            s_buffer = l_buffer(other)
            self.calculator.clear_rect(s_buffer, (0,0), (96,64))
            return 1
        return l_clrdraw
        
    ### Commands ###
    
    def _disp(self, code, ast):
        l_value = self.flatten(code, ast.children[0])
        def l_disp(other):
            s_out = l_value(other)
            print('Disp:', s_out)
            return s_out
            
        return l_disp
    
    def _getkey(self, code, ast):
        l_number = self.flatten(code, ast.number)
        def l_getkey(other):
            s_number = l_number(other)
            if s_number:
                return self.calculator.is_key_pressed(s_number)
            else:
                return self.calculator.is_any_key_pressed()
            return
        return l_getkey
    
    def _rand(self, code, ast):
        def l_rand(other):
            return random.randint(0, 256**2 - 1)
        return l_rand
        
    def _pause(self, code, ast):
        l_delay = self.flatten(code, ast.children[0])
        def l_pause(other):
            time.sleep(l_delay(other) / 1800)
            return 0
        return l_pause
        
    def _notimplemented(self, code, ast):
        def l_not_implemented(other):
            return 0
        return l_not_implemented
    
    ## Meta ##
    
    def _debug(self, code, ast):
        l_debug = self.flatten(code, ast.children[0])
        return lambda other: l_debug(other)

    def _about(self, code, ast):
        def l_about(other):
            print("Opening readme in web browser...")
            webbrowser.open(os.path.realpath(r"readme/index.html"), 2)
            return 1
        return l_about
    
    def _help(self, code, ast):
        def l_help(other):
            print("Opening readme in web browser...")
            webbrowser.open(os.path.realpath(r"readme/index.html"), 2)
            return 1
        return l_help
        
class Code(object):
    def __init__(self):
        self.code = []
        self.data = []
        self.labels = {}
        self._counter = [-1]
        self.next_token = 0
        self.ans = 0
        return
    
    def append(self, value):
        self.code.append(value)
        self.counter += 1
        return self.counter
    
    def replace(self, value, line):
        self.code[value] = line
        return
    
    def internal_replace(self, line):
        """For replacing a function during runtime inside of itself.
        (The function can calculate certain, constant values at runtime,
        then replace itself with a function internalizing those constants
        for added speed.)"""
        self.code[self.next_token - 1] = line
        return
    
    def next(self):
        try:
            out = self.code[self.next_token]
        except IndexError:
            return None
        self.next_token += 1
        return out
    
    def jump(self, line=0):
        self.next_token = line
        return
     
    def push_location(self, line):
        self._counter.append(line)
        return self.counter
    
    def pop_location(self, line):
        self._counter.pop()
        return self.counter
    
    def add_label(self, name, line):
        self.labels[name] = line
        return
        
    def get_label(self, name):
        if name not in self.labels:
            raise MissingLabelException('Missing label: ' + str(name))
        return self.labels[name]
        
    def _get_counter(self):
        return self._counter[-1]
    def _set_counter(self, value):
        self._counter[-1] = value
        return
    counter = property(_get_counter, _set_counter)
    
    def _is_eval_needed(self, ast):
        if isinstance(ast, axe.parser.Expression):
            if type(ast.value) == int:
                return True
        return False
        
_thread_text = ''

def test(lexer=None, parser=None, 
         calculator=axe.calculator.Calculator(), text=''):
    """
    This tests the interpreter.
    """
    global _thread_text
    global _draw
    _draw = False
    
    if not lexer:
        lexer = axe.lexer.build()
    if not parser:
        parser = axe.parser.build()
    
    class _console_thread(threading.Thread):
        def run(self):
            global _thread_text
            lock = threading.Lock()
            with lock:
                _thread_text = raw_input('axe> ').strip()
            return
    
    interpreter = Interpreter(calculator)
    interpreter.start()
    
    while True:
        if text:
            if text[-1] not in ('\n', ':'):
                text += '\n'
            result = parser.parse(text, lexer=lexer)
            
            try:
                interpreter.execute(result)
            except AxeRuntimeError, e:
                print('Runtime error: ', e)
        
        try:
            _thread_text = ''
            t = _console_thread()
            t.start()
            while True:
                interpreter.sanity_check()
                if _thread_text != '':
                    break
            t.join()
            text = _thread_text
        except KeyboardInterrupt:
            print('')
            break
            
    return

if __name__ == '__main__':
    test()
    
