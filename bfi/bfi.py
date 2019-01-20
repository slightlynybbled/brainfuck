import logging


def execute(program: str, stack_length=2000):
    bfi = Bfi(stack_length=stack_length)
    bfi.load(program)
    bfi.evaluate()


class Bfi:
    def __init__(self, stack_length=2000, log_level=logging.INFO):
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
        self.program = program

        self._logger.debug(f'loading "{self.program}"')

        if validate:
            brace_count = 0
            for c in self.program:
                if c == '[':
                    brace_count += 1
                elif c == ']':
                    brace_count -= 1

            if brace_count != 0:
                raise ValueError('program not valid (braces do not match)')

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

    def dec_ptr(self):
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

    def step(self):
        c = self.program[self.inst_ptr]
        self._logger.debug(f'executing instruction "{c}" at {self.inst_ptr}')

        if c in self.command_map.keys():
            self.command_map[c]()

        self._logger.debug(f'data stack: {self.stack}')
        self._logger.debug(f'inst stack: {self.inst_stack}')

        self.inst_ptr += 1
        self.cycles += 1

    def evaluate(self):
        self.inst_ptr = 0
        program_length = len(self.program)
        while self.inst_ptr < program_length:
            self.step()

        self._logger.info(f'completed in {self.cycles} cycles')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    bfi = Bfi(stack_length=32)

    hello_world = '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.'

    bfi.load(hello_world, validate=False)
    bfi.evaluate()

