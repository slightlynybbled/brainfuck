# Purpose

BrainFuck toy.

# Variants

Implements four different variants:

 - BrainFuck
 - BrainFuck Type I
 - BrainFuck Type II
 - BrainFuck Type III (in progress)

# Usage

## Object-oriented

Basic object usage: (1) create the oject (2) load the program, and (3) evaluate the program.

    >>> from bfi import Bfi
    >>> bfi = Bfi()
    >>> bfi.load('++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.')
    >>> bfi.evaluate()
    Hello World!
    >>>

Object structure was utilized throughout `bfi/bfi.py` to allow for efficient coding using inheritance.

## Shortcut

A convenience method is also provided called `execute()`:

    >>> from bfi import execute
    >>> execute('++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.')
    Hello World!
    >>>
    
The `execute()` function takes these arguments:

 * `program: str`
 * `stack_length: int=2000`
 * `bfi_type: int=0`
