#!/usr/bin/env python
"""
Axe Interpreter

An interpreter for programs written in the Axe Parser language for computers.

Author: Michael Lee (<michael.lee.0x2a@gmail.com>)
License: GNU Lesser GPL
"""


import os.path
import sys
import csv
import array

## 3rd party modules ##
import pygame

class Calculator(object):
    """
    Represents the calculator and manipulates both graphics and memory.
    
    This class uses pygame for graphics, which is fully integrated with memory.
    This shouldn't be directly be called, but is instead used primarily by 
    instances of an Interpreter class (see 'axe/interpreter.py').
    """
    ## Initialization ##
    def __init__(self, size=(96,64), pixel_size=3, caption="Axe Interpreter"):
        """
        Preps to set up graphics, memory, and a few other key components.
        
        Note that you need to run interpreter.init() in order to fully load
        everything and make the screen appear.
        
        Parameters:
        size=(96,64)
            A tuple of the screen dimensions.  By default, set to (96,64).
            Note that the screen isn't exactly 96 pixels across -- each
            calculator pixel is equal to multiple computer pixels.
        pixel_size=3
            An integer for how many computer pixels to a side a single 
            calculator pixel is equal to.
        caption="Axe Interpreter"
            The caption of the window
        """
        self.pixel_size = pixel_size
        self.size = size
        self.caption = caption
        return
    
    def init(self):
        """
        Sets up graphics, memory, and a few other key components.
        
        This NEEDS to be called first in order for anything to happen.  Calling
        this method will make the screen appear.
        """
        self._init_graphics()
        self._init_memory()
        self._init_getkey()
        
        self.disp_screen(37696)
        return
    
    def _init_graphics(self):
        """
        Initializes pygame.
        
        This should not be called directly, and will be called only once, when
        initializing.
        """
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.caption)
        
        self.WHITE = (255,255,255)
        self.LIGHT_GRAY = (170,170,170)
        self.GRAY = (128,128,128)
        self.DARK_GRAY = (85,85,85)
        self.BLACK = (0,0,0)
        
        def make_pixel(size, color):
            pixel = pygame.Surface(size)
            pixel.fill(color)
            return pixel
        
        pixel = (self.pixel_size, self.pixel_size)
        
        self.white_pixel = make_pixel(pixel, self.WHITE)
        self.light_gray_pixel = make_pixel(pixel, self.LIGHT_GRAY)
        self.gray_pixel = make_pixel(pixel, self.GRAY)
        self.dark_gray_pixel = make_pixel(pixel, self.DARK_GRAY)
        self.black_pixel = make_pixel(pixel, self.BLACK)
        
        strip = (self.pixel_size * 8, self.pixel_size)
        self.white_strip = make_pixel(strip, self.WHITE)
        self.light_gray_strip = make_pixel(strip, self.LIGHT_GRAY)
        self.gray_strip = make_pixel(strip, self.GRAY)
        self.dark_gray_strip = make_pixel(strip, self.DARK_GRAY)
        self.black_strip = make_pixel(strip, self.BLACK)
        
        self.mono = (
            self.white_pixel, 
            self.black_pixel)
        self.three = (
            self.white_pixel, 
            self.gray_pixel, 
            self.black_pixel, 
            self.black_pixel)
        self.four = (
            self.white_pixel, 
            self.light_gray_pixel, 
            self.dark_gray_pixel, 
            self.black_pixel)
            
        self.mono_optimize = {
            '00000000': self.white_strip,
            '11111111': self.black_strip}
        self.three_optimize = {
            '0000000000000000': self.white_strip,
            '0000000011111111': self.gray_strip,
            '1111111100000000': self.black_strip,
            '1111111111111111': self.black_strip}
        self.four_optimize = {
            '0000000000000000': self.white_strip,
            '0000000011111111': self.light_gray_strip,
            '1111111100000000': self.dark_gray_strip,
            '1111111111111111': self.black_strip}
        self.optimize = {
            2: self.mono_optimize,
            3: self.three_optimize,
            4: self.four_optimize}
        
        self.actual_size = self._screen_width // self.pixel_size
        
        self.clock = pygame.time.Clock()
        self.time = 0
        return
    
    def _init_memory(self):
        """
        Initializes memory.
        
        By default, memory is equal to 65535 bytes.  This should not be called
        directly, and will be called only once, when initializing.
        """
        self._memory_size = 256 * 256 - 1
        self._memory = array.array('H', [0 for i in xrange(self._memory_size)])
        return
    
    def _init_getkey(self):
        self._excluded_keys = (300, 301, 302)  # Num lock, Caps lock, Scroll lock
        self._keybindings = self._get_keybindings()
        return
        
    def _get_keybindings(self):
        temp = self._get_resource('../keybindings.config')
        keybindings = {}
        for computer_name in temp.keys():
            calc_code = int(temp[computer_name], 10)
            if calc_code == 0:
                continue    # If the code is set to zero, the key is unassigned.
            
            computer_code = getattr(pygame, computer_name)
            if calc_code not in keybindings:
                keybindings[calc_code] = [computer_code]
            else:
                keybindings[calc_code].append(computer_code)
        keybindings[0] = [0]
        return keybindings
    
    def _get_resource(self, path):
        full_path = os.path.join(self._curdir(), path)

        pairs = {}
        with open(full_path, 'r') as configfile:
            reader = csv.reader(configfile, delimiter=':')
            for line in reader:
                uncomment = lambda x: x[:x.find('#') if x.find('#') != -1 else None].strip()
                if line:
                    head = uncomment(line[0])
                    try:
                        tail = uncomment(line[1])
                    except IndexError:
                        continue
                    if head:
                        pairs[head] = tail
        return pairs
    
    def _curdir(self):
        if hasattr(sys, 'frozen'):  # If exe,
            curdir = os.path.dirname(sys.executable)
        elif __file__:
            curdir = os.path.dirname(__file__)
        return curdir
        
    def _fix_size(self, pair):
        """
        Converts calculator pixels to computer pixels.
        """
        return tuple([x * self.pixel_size for x in list(pair)])
    
    def sanity_check(self):
        self.time += self.clock.tick()
        if self.time > 200:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.kill_window()
                    sys.exit(0)
            self.time = 0
        return
    
    def kill_window(self):
        try:
            pygame.quit()
        except:
            pass
        return
    
    ## Getters and setters ##    
    def _get_size(self):
        return self._size
    def _set_size(self, size):
        self._size = self._fix_size(size)
        self._buffer_size = ((self.size[0]//self.pixel_size) * 
                            (self.size[1]//self.pixel_size)) // 8
        self._screen_width = self._size[0]
        self._screen_height = self._size[1]
        return
    size = property(_get_size, _set_size)
    
    ## Variables ##
    def set_var(self, location, value, size=2):
        """
        Sets a variable to some location in memory.
        
        This should effectively thought of as pointers. In python, the 
        following code...
        
            >>> import calculator
            >>> calc = calculator.Calculator
            >>> calc.set_var(3000, 1337, size=2)
            >>> calc.set_var(3002, 42, size=1)
        
        ...is equivalent in Axe to...
        
            .TEST
            1337->{3000}^^r
            42->{3002}
        
        This function will make sure overflowing numbers wrap around.
        
        Parameters:
        location
            The location in memory to change the value of.
        value
            The number to set to the location in memory.
        size=2
            An integer equaling either 1 or 2.  If equal to one, stores the
            value as a 1-byte var.  If equal to two, stores the value as a 
            2-byte var.
        """
        value = value % (256**size)
        if size == 1:
            self._memory[location] = value
        else:
            self._memory[location] = value % 256
            self._memory[location + 1] = value // 256
        return value
    
    def set_var_1(self, location, value):
        self._memory[location] = value % 256
        return value
    
    def set_var_2(self, location, value):
        value = value % 65536
        self._memory[location] = value % 256
        self._memory[location + 1] = value // 256
        return value
    
    def get_var(self, location, size):
        """
        Gets a variable from some location in memory.
        
        This should effectively thought of as pointers. In python, the 
        following code...
        
            >>> import calculator
            >>> calc = calculator.Calculator
            >>> A = calc.get_var(3000, size=2)
            >>> B = calc.set_var(3002, size=1)
        
        ...is conceptually equivalent in Axe to...
        
            .TEST
            {3000}^^r->A
            {3002}->B
        
        Parameters:
        location
            The location in memory to get the value from.
        size
            If equal to 1, gets a one-byte var.  If 2, gets a two-byte var.
        """
        if size == 1:
            return self._memory[location]
        else:
            return self._memory[location] + self._memory[location + 1] * 256
        return
    
    def get_var_1(self, location):
        return self._memory[location]
    
    def get_var_2(self, location):
        return self._memory[location] + self._memory[location + 1] * 256
    
    def disp_screen(self, buffer1_loc, buffer2_loc=None, scale=2):
        """
        Displays the contents of the buffers to the screen.
        
        Note that you need to manually load in the memory address of the 
        buffer(s) that you want to display on the screen.
        
        Parameters:
        buffer1_loc
            The location in memory of the first buffer.
        buffer2_loc=None
            The location in memory of the backbuffer.  If you aren't doing
            grayscale, you can ignore this.
        scale=2
            If scale equals 2, displays only the first buffer in black and 
            white.  If scale equals 3, displays in 3-scale grayscale.  If
            scale equals 4, displays 4-scale grayscale.
        """
        if scale == 2:
            self.disp_screen_mono(buffer1_loc)
            return
        buffer1 = self._memory[buffer1_loc : buffer1_loc + self._buffer_size]
        buffer2 = self._memory[buffer2_loc : buffer2_loc + self._buffer_size]
        
        for i in xrange(self._buffer_size):
            buf1 = bin(buffer1[i])[2:].rjust(8, '0')
            buf2 = bin(buffer2[i])[2:].rjust(8, '0')
            
            if buf1 + buf2 in self.optimize[scale].keys():
                actual_i = i * 8
                x = (actual_i % self.actual_size) * self.pixel_size
                y = (actual_i // self.actual_size) * self.pixel_size
                self.screen.blit(self.optimize[scale][buf1 + buf2], (x, y))
                continue 
                
            if scale == 3:
                colors = [self.three[int(buf1[c])*2 + int(buf2[c])] for c in xrange(8)]
            elif scale == 4:
                colors = [self.four[int(buf1[c])*2 + int(buf2[c])] for c in xrange(8)]
            
            for j in xrange(8):
                actual_i = i * 8 + j
                x = (actual_i % self.actual_size) * self.pixel_size
                y = (actual_i // self.actual_size) * self.pixel_size
                self.screen.blit(colors[7 - j], (x, y))
        pygame.display.update()
        return
    
    def disp_screen_mono(self, buffer1_loc):
        buffer1 = self._memory[buffer1_loc: buffer1_loc + self._buffer_size]
        
        rectangles = []
        for i in xrange(self._buffer_size):
            buf1 = bin(buffer1[i])[2:].rjust(8, '0')
            if buf1 in self.mono_optimize.keys():
                actual_i = i * 8
                x = (actual_i % self.actual_size) * self.pixel_size
                y = (actual_i // self.actual_size) * self.pixel_size
                self.screen.blit(self.mono_optimize[buf1], (x, y))
                continue
            
            colors = [self.mono[int(c)] for c in buf1]
            for j in xrange(8):
                actual_i = i * 8 + j
                x = (actual_i % self.actual_size) * self.pixel_size
                y = (actual_i // self.actual_size) * self.pixel_size
                self.screen.blit(colors[7-j], (x, y))
                
        pygame.display.update()
    
    def shift_buffer_vertical(self, buf, direction):
        if direction == 1: # shift down
            for i in xrange(0, 63):
                current = 63 - i
                pivot = buf + (current+1) * 96
                old_slice = self._memory[buf + current * 96 : pivot]
                self._memory[pivot : buf + (current+2) * 96] = old_slice
        elif direction == -1: # shift up
            for current in xrange(1,64):
                pivot = buf + current * 96
                old_slice = self._memory[pivot : buf + (current+1) * 96]
                self._memory[buf + (current-1) * 96 : pivot] = old_slice
        return
    
    def shift_buffer_horizontal(self, buf, direction):
        if direction == 1: # shift right
            for row_ in xrange(0, 63):
                for bit_index_ in xrange(1, 95):
                    bit_index = 96 - bit_index
                    coords = (bit_index, row)
                    if self.pxl_get(buf, (bit_index - 1, row)):
                        self.rect(buf, coords, (1,1))
                    else:
                        self.clear_rect(buf, coords, (1,1))
                self.clear_rect(buf, (95, row), (1,1))
        elif direction == -1:   #shift left
            for row in xrange(0, 63):
                for bit_index in xrange(0, 94):
                    coords = (bit_index, row)
                    if self.pxl_get(buf, (bit_index + 1, row)):
                        self.rect(buf, coords, (1,1))
                    else:
                        self.clear_rect(buf, coords, (1,1))
                self.clear_rect(buf, (95, row), (1,1))
        return
                    
        
    def line(self, buf, start, end):
        # Bresenham's line algorithm
        # (implementation copied from Wikipedia)
        x0, y0 = start
        x1, y1 = end
        abs = lambda x: -x if x < 0 else x
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx - dy
        while True:
            self.rect(buf, (x0, y0), (1,1))
            if x0 == x1 and y0 == y1:
                break
            error_2 = 2 * error
            if error_2 > -dy:
                error -= dy
                x0 += sx
            if error_2 < dx:
                error += dx
                y0 += sy
        return
    
    def circle(self, buf, coords, radius):
        # Bresenham's circle algorithm
        # (implementation copied from http://willperone.net/Code/codecircle.php)
        if not radius:
            return 1
        xm, ym = coords
        x = 0
        y = radius
        error = 3 - 2 * radius
        while y >= x:
            self.rect(buf, (xm-x, ym-y), (1,1))
            self.rect(buf, (xm-y, ym-x), (1,1))
            self.rect(buf, (xm+y, ym-x), (1,1))
            self.rect(buf, (xm+x, ym-y), (1,1))
            self.rect(buf, (xm-x, ym+y), (1,1))
            self.rect(buf, (xm-y, ym+x), (1,1))
            self.rect(buf, (xm+y, ym+x), (1,1))
            self.rect(buf, (xm+x, ym+y), (1,1))
            if error < 0:
                error += 4 * x + 6;
                x += 1
            else:
                error += 4 * (x - y) + 10
                x += 1
                y -= 1
        return
            
    def rect(self, buf, coords, size):
        """
        Draws a solid rectangle to the screen.
        
        Parameters:
        buf
            The location in memory of the start of the buffer you want to draw
            the rectangle to.
        coords
            A tuple (x, y) of integers where you want the top-left corner of
            the rectangle to start
        size
            A tuple (width, height) of how large you want the rectangle to be.
        """
        draw_solid = lambda buf, index: self._set_bit(buf, index)
        self._generic_rect(buf, coords, size, draw_solid)
        return

    def clear_rect(self, buf, coords, size):
        """
        Draws a white rectangle to the screen.

        Parameters:
        buf
            The location in memory of the start of the buffer you want to draw
            the rectangle to.
        coords
            A tuple (x, y) of integers where you want the top-left corner of
            the rectangle to start
        size
            A tuple (width, height) of how large you want the rectangle to be.
        """
        draw_clear = lambda buf, index: self._clear_bit(buf, index)
        self._generic_rect(buf, coords, size, draw_clear)
        return
    
    def inverse_rect(self, buf, coords, size):
        """
        Draws an inverted rectangle to the screen.
        
        Parameters:
        buf
            The location in memory of the start of the buffer you want to draw
            the rectangle to.
        coords
            A tuple (x, y) of integers where you want the top-left corner of
            the rectangle to start
        size
            A tuple (width, height) of how large you want the rectangle to be.
        """
        draw_inverse = lambda buf, index: self._flip_bit(buf, index)
        self._generic_rect(buf, coords, size, draw_inverse)
        return
    
    def pxl_get(self, buffer, coords):
        x, y = coords
        location = buffer + (y * 96 + x) // 8
        index = x % 8
        return int(self._get_bit(location, index))
    
    def _generic_rect(self, buf, coords, size, callback):
        """
        A generic rectangle-drawing function.
        
        This shouldn't directly be called, but is instead called by more
        specific drawing functions.
        
        Parameters:
        buf
            The location in memory of the start of the buffer you want to draw
            the rectangle to.
        coords
            A tuple (x, y) of integers where you want the top-left corner of
            the rectangle to start
        size
            A tuple (width, height) of how large you want the rectangle to be.
        callback
            A function provided which needs to accept two variables -- the 
            location of the byte to be drawn to, and the bit number.  The 
            function must implement exactly what happens to the bit (is it
            flipped?  Inverted? etc.)
        """
        x, y = coords
        w, h = size
        for j in xrange(y, y + h):
            for i in xrange(x, x + w):
                xt = i // 8
                yt = j * self.size[0] // self.pixel_size // 8
                callback(buf + xt + yt, i % 8)
        return
    
    def and_sprite(self, buf, coords, size, data_buf):
        """
        Draws a sprite to the screen (equivalent to Pt-On)
        
        TODO: change 'data' so it gets the value of a sprite from an arbitary
        location in memory, rather then feeding it directly.
        
        Parameters
        buf
            The location in memory of the start of the buffer you want to draw
            the rectangle to.
        coords
            A tuple (x, y) of integers where you want the top-left corner of
            the sprite to start
        size
            A tuple (width, height) of how large you want the sprite to be.
        data
            The location in memory to the start of the sprite data.  The rows 
            of the image needs to be padded with zeros to the nearest byte.
        """
        def and_operation(buf, index, value):
            if value:
                self._set_bit(buf, index)
            else:
                self._clear_bit(buf, index)
            return
        self._generic_sprite(buf, coords, size, data_buf, and_operation)
        return
    
    def _generic_sprite(self, loc, coords, size, data_buf, callback):
        x, y = coords
        w, h = size
        data = []
        for j in xrange(h):
            for i in xrange(x):
                data.append(self._get_bit(data_buf + (j*w+i)//8, (j*w+i) % 8))
        count = 0
        for j in xrange(y, y + h):
            for i in xrange(x, x + w):
                xt = i // 8
                yt = j * self.size[0] // self.pixel_size // 8
                callback(x + xt + yt, i % 8, data[count])
                count += 1
        return
    
    def _get_bit(self, loc, index):
        return self._get_bit2(self._memory[loc], index)
    def _get_bit2(self, byte_value, index):
        return ((byte_value & (1 << index) ) != 0)
    def _set_bit(self, loc, offset):
        num = self._memory[loc]
        mask = 1 << offset
        self._memory[loc] = num | mask
        return
    def _clear_bit(self, loc, offset):
        num = self._memory[loc]
        mask = ~(1 << offset)
        self._memory[loc] = num & mask
        return
    def _flip_bit(self, loc, offset):
        num = self._memory[loc]
        mask = 1 << offset
        self._memory[loc] = num ^ mask
        return
    
    def is_any_key_pressed(self):
        pygame.event.pump()
        keys = list(pygame.key.get_pressed())
        # I'm doing all this because I don't want 'GetKey(0)' to trigger
        # if the num lock or caps lock is held down.
        indices = [i for (i, x) in enumerate(keys) if x==1]
        if set(indices).issubset(self._excluded_keys):
            # If every single held key is in the list of excluded keys,
            # then we're going to say that no keys are held down.
            return 0
        else:
            return 1
        return
    
    def is_key_pressed(self, key_num):
        pygame.event.pump()
        keys = list(pygame.key.get_pressed())
        for key in self._keybindings[key_num]:
            if keys[key]:
                return 1
        return 0
