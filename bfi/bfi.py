import logging
from sys import exit


def execute(program: str, stack_length: int=2000, bfi_type: int=0):
    bfi_dict = {
        0: Bfi,
        1: BfiT1,
        2: BfiT2,
        3: BfiT3
    }

    if bfi_type not in bfi_dict.keys():
        raise ValueError('invalid BF type (should be 0, 1, 2, or 3)')

    bfi = bfi_dict[bfi_type](stack_length)

    bfi.load(program)
    bfi.evaluate()


class Bfi:
    """
    Implements 'standard' BrainFuck interpreter
    """
    def __init__(self, stack_length=32, log_level=logging.INFO):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self.stack_length = stack_length
        self.stack = [0] * self.stack_length
        self.stack_ptr = 0

        self.inst_stack = []
        self.inst_ptr = 0

        self.cycles = 0

        self.program = ''

        self.command_map = {
            '+': self.inc,
            '-': self.dec,
            '>': self.inc_ptr,
            '<': self.dec_ptr,
            '.': self.put_char,
            ',': self.get_char,
            '[': self.open_brace,
            ']': self.close_brace
        }

    def load(self, program: str, validate: bool=True):
        self._logger.info(f'attempting to load "{program}"')

        if validate:
            brace_count = 0
            for c in program:
                if c == '[':
                    brace_count += 1
                elif c == ']':
                    brace_count -= 1

            if brace_count != 0:
                raise ValueError('program not valid (braces do not match)')
        self.program = [b for b in program if b in self.command_map.keys()]
        self._logger.info(f'loaded {len(self.program)} executable characters from the program')

        self.reset()

    def reset(self):
        self._logger.info('resetting interpreter')

        self.stack = [0] * self.stack_length
        self.stack_ptr = 0
        self.inst_ptr = 0
        self.cycles = 0

    def inc(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] + 1) % 256
        self._logger.debug(f'incrementing data at {self.stack_ptr} to {self.stack[self.stack_ptr]}')

    def dec(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] - 1) % 256
        self._logger.debug(f'decrementing data at {self.stack_ptr} to {self.stack[self.stack_ptr]}')

    def inc_ptr(self):
        self.stack_ptr = (self.stack_ptr + 1) % self.stack_length
        self._logger.debug(f'incrementing data pointer to {self.stack_ptr}')

        if self.stack_ptr == 0:
            self._logger.warning('data pointer incrementing at max, rolling over to 0')

    def dec_ptr(self):
        if self.stack_ptr == 0:
            self._logger.warning('data pointer decrementing at 0, defaulting to max stack address')

        self.stack_ptr = (self.stack_ptr - 1) % self.stack_length
        self._logger.debug(f'decrementing data pointer to {self.stack_ptr}')

    def put_char(self):
        c = chr(self.stack[self.stack_ptr])
        print(c, end='')

        self._logger.debug(f'printing {c} ({self.stack[self.stack_ptr]})')

    def get_char(self):
        self.stack[self.stack_ptr] = input()[0]
        self._logger.debug('retrieving character input')

    def open_brace(self):
        self._logger.debug(f'opening brace at {self.inst_ptr}')

        self.inst_stack.insert(0, self.inst_ptr)

    def close_brace(self):
        if self.stack[self.stack_ptr] != 0:
            self._logger.debug(f'closing brace at {self.inst_ptr}, looping')
            self.inst_ptr = self.inst_stack[0]
        else:
            self._logger.debug(f'closing brace at {self.inst_ptr}, end loop')
            self.inst_stack.pop(0)

    def show_internals(self):
        self._logger.debug(f'status: {self.stack} {self.inst_stack}\n')

    def step(self):
        c = self.program[self.inst_ptr]
        self._logger.debug(f'executing instruction "{c}" at {self.inst_ptr}')

        if c in self.command_map.keys():
            self.command_map[c]()

        self.show_internals()

        self.inst_ptr += 1
        self.cycles += 1

    def evaluate(self):
        self.inst_ptr = 0
        program_length = len(self.program)
        while self.inst_ptr < program_length:
            self.step()

        self._logger.info(f'completed in {self.cycles} cycles')


class BfiT1(Bfi):
    """
    Implements BrainFuck Type I extension
    """
    def __init__(self, stack_length=32, log_level=logging.INFO):
        super().__init__(
            stack_length=stack_length, log_level=log_level
        )

        self.storage = 0

        self.command_map['@'] = self.end_prog
        self.command_map['$'] = self.store_data
        self.command_map['!'] = self.load_data
        self.command_map['}'] = self.right_shift
        self.command_map['{'] = self.left_shift
        self.command_map['~'] = self.bitwise_not
        self.command_map['^'] = self.bitwise_xor
        self.command_map['&'] = self.bitwise_and
        self.command_map['|'] = self.bitwise_or

    def show_internals(self):
        self._logger.debug(f'status: {self.storage} {self.stack} {self.inst_stack}\n')

    def end_prog(self):
        self._logger.info(f'program termination in {self.cycles} cycles')
        exit(0)

    def store_data(self):
        self._logger.debug(f'storing {self.stack[self.stack_ptr]} from {self.stack_ptr}')
        self.storage = self.stack[self.stack_ptr]

    def load_data(self):
        self._logger.debug(f'loading {self.storage} to {self.stack_ptr}')
        self.stack[self.stack_ptr] = self.storage

    def right_shift(self):
        self._logger.debug(f'right shift value at {self.stack_ptr}')
        self.stack[self.stack_ptr] >>= 1

    def left_shift(self):
        self._logger.debug(f'left shift value at {self.stack_ptr}')
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] << 1) & 0xff

    def bitwise_not(self):
        self._logger.debug(f'bitwise not value at {self.stack_ptr}')
        self.stack[self.stack_ptr] = (~self.stack[self.stack_ptr] % 256)

    def bitwise_xor(self):
        self._logger.debug(f'bitwise xor {self.stack[self.stack_ptr]} at {self.stack_ptr} with {self.storage}')
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] ^ self.storage) % 256

    def bitwise_and(self):
        self._logger.debug(f'bitwise and {self.stack[self.stack_ptr]} at {self.stack_ptr} with {self.storage}')
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] & self.storage) % 256

    def bitwise_or(self):
        self._logger.debug(f'bitwise or {self.stack[self.stack_ptr]} at {self.stack_ptr} with {self.storage}')
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] | self.storage) % 256


class BfiT2(BfiT1):
    """
    Implements BrainFuck Type II extension (does not support self-modification)
    """
    def __init__(self, stack_length=32, log_level=logging.INFO):
        super().__init__(
            stack_length=stack_length, log_level=log_level
        )

        self.initializer_data = []

        self.command_map['?'] = self.load_inst_ptr
        self.command_map[')'] = self.insert_data_cell
        self.command_map['('] = self.remove_data_cell
        self.command_map['*'] = self.mul
        self.command_map['/'] = self.div
        self.command_map['='] = self.add
        self.command_map['_'] = self.sub
        self.command_map['%'] = self.mod

    def load(self, program: str, validate: bool=True):
        # split the data and the parts
        parts = program.split('@')

        if len(parts) > 1:
            program = '@'.join(parts[0:-1])
            init_data = parts[-1]
        else:
            program = parts[0]
            init_data = ''

        super().load(program)
        self.initializer_data = [ord(c) for c in init_data]

        self.reset()

    def reset(self):
        super().reset()

        # initialize data
        for i, e in enumerate(self.initializer_data):
            self.stack[i] = e

    def load_inst_ptr(self):
        self.inst_ptr = (self.stack[self.stack_ptr] - 1) % len(self.program)

    def insert_data_cell(self):
        self.stack.insert(self.stack_ptr, 0)

    def remove_data_cell(self):
        self.stack.pop(self.stack_ptr)

    def mul(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] * self.storage) % 256

    def div(self):
        self.stack[self.stack_ptr] = int(self.stack[self.stack_ptr] / self.storage) % 256

    def add(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] + self.storage) % 256

    def sub(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] - self.storage) % 256

    def mod(self):
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] % self.storage) % 256


class BfiT3(BfiT2):
    """
    Implements BrainFuck Type III extension
    """
    def __init__(self, stack_length=32, log_level=logging.INFO):
        super().__init__(
            stack_length=stack_length, log_level=log_level
        )

        self.storage_ptr = None

        self.command_map['X'] = self.cmd_X
        self.command_map['x'] = self.cmd_x
        self.command_map['M'] = self.cmd_M
        self.command_map['m'] = self.cmd_m
        self.command_map['L'] = self.lock_cell
        self.command_map['l'] = self.unlock_cell
        self.command_map[':'] = self.move_ptr
        self.command_map['0'] = self.init_0
        self.command_map['1'] = self.init_1
        self.command_map['2'] = self.init_2
        self.command_map['3'] = self.init_3
        self.command_map['4'] = self.init_4
        self.command_map['5'] = self.init_5
        self.command_map['6'] = self.init_6
        self.command_map['7'] = self.init_7
        self.command_map['8'] = self.init_8
        self.command_map['9'] = self.init_9
        self.command_map['A'] = self.init_A
        self.command_map['B'] = self.init_B
        self.command_map['C'] = self.init_C
        self.command_map['D'] = self.init_D
        self.command_map['E'] = self.init_E
        self.command_map['F'] = self.init_F
        self.command_map['#'] = self.comment

    def reset(self):
        super().reset()
        self.storage_ptr = None

    def store_data(self):
        self._logger.debug(f'storing {self.stack[self.stack_ptr]} from {self.stack_ptr}')
        to_store = self.stack[self.stack_ptr]

        if self.storage_ptr is None:
            self.storage = to_store
        else:
            self.stack[self.storage_ptr] = to_store

    def load_data(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self._logger.debug(f'loading {storage} to {self.stack_ptr}')
        self.stack[self.stack_ptr] = storage

    def mul(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] * storage) % 256

    def div(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self.stack[self.stack_ptr] = int(self.stack[self.stack_ptr] / storage) % 256

    def add(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] + storage) % 256

    def sub(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] - storage) % 256

    def mod(self):
        storage = self.storage if self.storage_ptr is None else self.stack[self.storage_ptr]
        self.stack[self.stack_ptr] = (self.stack[self.stack_ptr] % storage) % 256

    def cmd_X(self):
        pass

    def cmd_x(self):
        pass

    def cmd_M(self):
        self.storage_ptr = self.stack_ptr

    def cmd_m(self):
        self.storage_ptr = None

    def lock_cell(self):
        pass

    def unlock_cell(self):
        pass

    def move_ptr(self):
        pass

    def init_0(self):
        self.stack[self.stack_ptr] = 0 * 16

    def init_1(self):
        self.stack[self.stack_ptr] = 1 * 16

    def init_2(self):
        self.stack[self.stack_ptr] = 2 * 16

    def init_3(self):
        self.stack[self.stack_ptr] = 3 * 16

    def init_4(self):
        self.stack[self.stack_ptr] = 4 * 16

    def init_5(self):
        self._logger.debug(f'pre-loading {self.stack_ptr} to 0x50')
        self.stack[self.stack_ptr] = 5 * 16

    def init_6(self):
        self.stack[self.stack_ptr] = 6 * 16

    def init_7(self):
        self.stack[self.stack_ptr] = 7 * 16

    def init_8(self):
        self.stack[self.stack_ptr] = 8 * 16

    def init_9(self):
        self.stack[self.stack_ptr] = 9 * 16

    def init_A(self):
        self.stack[self.stack_ptr] = 10 * 16

    def init_B(self):
        self.stack[self.stack_ptr] = 11 * 16

    def init_C(self):
        self.stack[self.stack_ptr] = 12 * 16

    def init_D(self):
        self.stack[self.stack_ptr] = 13 * 16

    def init_E(self):
        self.stack[self.stack_ptr] = 14 * 16

    def init_F(self):
        self.stack[self.stack_ptr] = 15 * 16

    def comment(self):
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    bfi = BfiT2(stack_length=32, log_level=logging.DEBUG)

    hello_world = '++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.'
    hello_world_e1 = '++++{+{{{.$>-}}^>++{{{++$<^.$>[-]++{{+^..$>+++|.>++{{{{.<<<<$>>>>>-}}}^.<<.+++.<.<-.>>>+.>>+++++{.@'
    hello_world_e2_0 = '>++{{$+*.>!++$*+.>!*=--..$>!+++.>++{${*.>++$</$>![<]!-$>=.>>>.+++.<.<-.<<=+++.@'
    hello_world_e2_1 = '[.>]@HelloWorld!'
    hello_world_e3 = '>5--------.7-----------.+++++++..+++.<2.5+++++++.>.+++.------.--------.2+.'

    bfi.load(hello_world_e3)
    bfi.evaluate()
