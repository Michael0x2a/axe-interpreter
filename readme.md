# Axe Interpreter #

## Synopsis ##

Axe Interpreter is a version of Axe meant to be run on computers.  This is currently under heavy development, and will currently allow only a _very_ limited subset of Axe to be used.  I created this program because I was...

1.  Bored.
2.  Wanted to try making a decent cross-platform development platform for Axe.

This program is written in Python, and should be compatible with all major operating systems, provided they have Python installed.

### Metadata ###
Author: Michael Lee <michael.lee.0x2a@gmail.com>  
License: [GNU Lesser GPL](LICENSE.markdown)
Version: 0.3
Released: May 12, 2012


## Running this program ##

### Quick Start Guide ###

You can run this program either as an executable or via the source code.  To run the exe, navigate to either the 'Windows' folder or the 'Linux' folder  (whichever is appropriate).

Double-click it to run the interpreter.  Two windows should pop up -- one is the console or command prompt, while the other is a small white window.  Type in commands to the console to make them happen.  A [full list](docs/commands.html) of supported tokens can be found in the docs folder.

To run axe code, type it into a txt file and drag it over the exe.  Running 8xp source code is currently unsupported.

### Running the source code ### {#running-this-program_source-code}
You will need the following:

*   [Python 2.7](http://python.org)
*   [Pygame 1.9.1](http://pygame.org)

In addition, this program also uses [PLY 3.4](http://www.dabeaz.com/ply/), but you don't need to install that: it should be included.

This program is run via Command Prompt.  To run the interpreter, type:

    $ python ./axe-interpreter

To execute a program, type:

    $ python ./axe-interpreter myprogram.txt
    
If you want to test specific components of the program, type one of the below:

    $ python ./axe-interpreter --test lexer
    $ python ./axe-interpreter --test parser
    $ python ./axe-interpreter --test interpreter

Typing either `@EXIT` or hitting ctrl-C should end exit you out from any mode.


## Restrictions and Limitations ## {#restrictions}

I only started working on this a few months ago.  There are loads of limitations and restrictions.

*   You can only use the variables A to Z
*   You can only use numbers.  Strings, hex, binary, etc. are not supported yet
*   You can't declare constants yet
*   Only a limited subset of tokens are currently implemented (see the [full list](docs/commands.html)
*   You cannot use subroutines, or returns.

## Tokens ##

Currently, only a very limited subset of tokens are allowed.  See the 
[complete list](docs/commands.html).

Some notes:
*   **Disp** currently prints things to the command line.
   
### Meta ### {#tokens_meta}

Meta tokens are ones which are not implemented in Axe, but do stuff to this interpreter in particular.  Meta tokens work in both in interpreter mode and while running a file.

*   @EXIT  
    Ends the program in both interpreter and drawing mode.
*   @HELP and @ABOUT  
    Opens this readme in the web browser.
*   @DEBUG  
    Displays extra info to the command line for debugging.  Type `@DEBUG 1` to turn it on and '@DEBUG 0' to turn it off.  Off by default, you shouldn't need this token.

### The getKey config file ### {#misc_getkey-config}

Included should be a file named _keybindings.config_.  This needs to be in the same directory as the executable or source code when run.  When you open it, you should see some comments at the top, and a row of keys, like so:

    K_BACKSPACE        :   15
    K_TAB              :   0
    K_CLEAR            :   0
    K_RETURN           :   09
    K_PAUSE            :   0
    K_ESCAPE           :   41
    K_SPACE            :   0

This means that that **getKey(15)** will return 1 when the backspace key is held, **getKey(9)**  will return 1 when Enter is held, etc.  The tab, clear, pause, and spacebar keys are assigned a value of zero, which means that they will not register any getKey codes.  Feel free to edit this file as you want.

## Version History ##

*   Version 0.3: May 12th, 2012  
    Completely remade the parser and interpreter to make the underlying structure more flexible.  Pointers, grayscale, some additional drawing commands, and gotos/labels have been supported.
*   Version 0.2: December 22nd, 2011  
    Getkey, rudimentary pointers, L1-L6 buffers, and more drawing commands.  Source and exe provided.
*   Version 0.1: December 21th, 2011  
    A quick release -- basically a rerelease of 0.0 in exe form.
*   Version 0.0: December 20th, 2011  
    Has only numbers, rudimentary drawing primitives, and a few control structures.  Source only.


## Roadmap ##

*   Adding better memory handling, pointers, and constants.
*   Attempting to integrate the memory and Pygame buffers to each other
*   Adding more drawing commands
*   Adding more control structures
*   Optimizing and decreasing memory footprint
*   Grayscale


## Thanks and credits ##

*   Kevin Horowitz (a.k.a. Quigibo):  
    For making Axe Parser.
*   The Omnimaga Community:  
    For general support and inspiration
*   PLY (Python Lex Yacc):  
    For providing lexing and parsing tools
*   Pygame:  
    For graphics and pixel manipulation