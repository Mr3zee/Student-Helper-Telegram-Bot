from typing import Dict


class MLWText:
    def __init__(self, name, parsed_seq, local_vars, cases, global_vars: Dict[str, str] = None):
        self.__name = name
        self.__parsed_seq = parsed_seq
        self.__local_vars = local_vars
        self.__cases = cases
        self.__global_vars = global_vars

    def print_(self):
        print(self.__parsed_seq)
        print(self.__local_vars)
        print(self.__cases)

    def __substitute_local_vars(self, var_name: str) -> list:
        retval = self.__local_vars.get(var_name)
        if retval:
            return retval
        raise ValueError('Undefined local variable')


class Source:

    def __init__(self, source):
        self.__source = source
        self.__pos = 0

    def has_next(self):
        return self.__pos < len(self.__source)

    def next(self):
        if not self.has_next():
            return '\0'
        retval = self.__source[self.__pos]
        self.__pos += 1
        return retval

    def rollback(self, i):
        self.__pos -= i


class BaseParser:

    def __init__(self, input_text):
        self.__source = Source(input_text)
        self.__current = ''
        self._next_char()

    def _next_char(self):
        self.__current = self.__source.next()

    def _rollback(self, i):
        self.__source.rollback(i + 1)
        self._next_char()

    def _next_word(self, first_symbols: set = None):
        self._skip_whitespaces()
        first = ''
        if first_symbols:
            first = self._get_current()
            self._next_char()
            if first not in first_symbols:
                raise SyntaxError(f'Expected on of these symbols: {first_symbols}, found {first}')

        retval = first + self._next_with_filter(
            lambda ch:
            ch.isdigit() or ch.isalpha() or ch == '_'
        )
        return retval

    def _next_line(self):
        return self._next_with_filter(lambda ch: ch != '\n')

    def _next_with_filter(self, char_filter):
        ch_list = []
        while char_filter(self.__current):
            ch_list.append(self.__current)
            self._next_char()
        return ''.join(ch_list)

    def _skip_whitespaces(self):
        while self.__current.isspace():
            self._next_char()

    def _is_ch(self, ch):
        return self.__current == ch

    def _get_current(self):
        return self.__current

    @staticmethod
    def _is_valid_var_name(var_name):
        if len(var_name) == 0 or var_name[0].isdigit() or var_name[0] == '_':
            return False
        start = 0
        if var_name[0] == '&' or var_name[0] == '^':
            if len(var_name) == 1:
                return False
            else:
                start = 1
        for i in range(start, len(var_name)):
            ch = var_name[i]
            if not (ch.isdigit() or ch.isalpha() or ch == '_'):
                return False
        return True


class MLWParser(BaseParser):
    __text_seq = []

    __local_vars = {}

    __cases = {}

    def _next_var(self):
        return self._next_word({'&', '^'})

    def __init__(self, input_text):
        super().__init__(input_text)

    def parse(self) -> MLWText:
        self._skip_redundant_symbols()
        main_tag, args = self._take_tag()
        if len(args) != 0:
            raise SyntaxError('Unexpected args for main tag')
        self._skip_redundant_symbols()
        tag, args = self._take_tag()
        if tag == 'vars':
            if len(args) != 0:
                raise SyntaxError('Unexpected args for [vars] tag')
            self._parse_vars()
            tag, args = self._take_tag()
        if tag == 'body':
            if len(args) != 0:
                raise SyntaxError('Unexpected args for [body] tag')
            self._parse_body()
        else:
            raise SyntaxError(f'Unexpected tag: {tag}')
        self._validate_tag(f'/{main_tag}')
        return MLWText(main_tag, self.__text_seq, self.__local_vars, self.__cases)

    def _parse_vars(self):
        self._skip_redundant_symbols()
        cases = self._parse_var_value_syntax({'&'})
        self._skip_redundant_symbols()
        self._validate_tag('/vars')
        self.__local_vars = cases

    def _parse_body(self):
        body = self._parse_multiline_text()
        self._validate_tag('/body')
        self.__text_seq = body

    def _parse_single_line_text(self, with_linebreaks: bool = True) -> list:
        retval = []
        text = []
        self._skip_redundant_symbols()
        while True:
            if self._is_ch('#'):
                self._next_line()
                continue
            elif self._is_ch('&') or self._is_ch('^'):
                if text:
                    retval.append((''.join(text)))
                var_name = self._next_var()
                if not self._is_valid_var_name(var_name):
                    raise SyntaxError(f'Invalid var name: {var_name}')
                retval.append(var_name)
                text = []
                continue
            elif self._is_ch('['):
                if text:
                    retval.append(''.join(text))
                if self._is_closing_tag():
                    return retval
                retval.extend(self._parse_tag())
                text = []
                continue
            elif self._is_ch('\n'):
                if with_linebreaks:
                    text.append(self._take_char())
                if text:
                    retval.append(''.join(text))
                return retval
            elif self._is_ch('\\'):
                self._next_char()

            text.append(self._take_char())

    def _parse_tag(self) -> list:
        tag, args = self._take_tag()
        if tag == 'm':
            if len(args) != 0:
                raise ValueError('Unexpected arguments for tag [m]')
            retval = self._parse_multiline_text()
            self._validate_tag('/m')
            return retval
        elif tag == 'raw':
            if len(args) != 0:
                raise ValueError('Unexpected arguments for tag [raw]')
            return [self._parse_raw_text()]
        elif tag == 'case':
            return [self._parse_case(args)]
        else:
            SyntaxError(f'Invalid tag name: [{tag}]')

    def _parse_multiline_text(self) -> list:
        retval = []
        self._skip_redundant_symbols()
        while True:
            retval.extend(self._parse_single_line_text())
            self._skip_redundant_symbols()
            if self._is_closing_tag():
                break
        return retval

    def _parse_raw_text(self) -> str:
        text = []
        while not self._is_ch('['):
            if self._is_ch('\\'):
                text.append(self._take_char())
            text.append(self._take_char())
        self._validate_tag('/raw')
        return ''.join(text)

    def _parse_case(self, args: list) -> str:
        if len(args) != 1:
            raise ValueError(f'Wrong number of arguments for case tag: {len(args)}')
        arg = args[0]
        case_body = [arg]
        cases = self._parse_var_value_syntax()
        self._validate_tag('/case')
        case_body.append(cases)
        case_id = f'_case{len(self.__cases)}'
        self.__cases[case_id] = case_body
        return case_id

    def _parse_var_value_syntax(self, starts_with: set = None) -> Dict[str, list]:
        cases = {}
        self._skip_redundant_symbols()
        while not self._is_ch('['):
            var = self._next_word(starts_with)
            if not self._is_valid_var_name(var):
                raise ValueError('Invalid var name/value')
            self._skip_whitespaces()
            if not self._is_ch(':'):
                raise SyntaxError('Expected \':\' symbol after var name')
            self._next_char()
            value = self._parse_single_line_text(with_linebreaks=False)
            cases[var] = value
            self._skip_redundant_symbols()
        return cases

    def _validate_tag(self, tag_name: str, empty_args: bool = True):
        closing = tag_name[0] == '/'
        tag, args = self._take_tag(closing)
        if tag_name != tag or (not args if not empty_args else args):
            raise SyntaxError(f'Invalid tag syntax: {tag}')

    def _take_tag(self, closing: bool = False) -> (str, list):
        self._skip_redundant_symbols()
        if self._is_ch('['):
            self._next_char()
        else:
            raise SyntaxError('Expected tag opening parenthesis')
        tag = self._next_word({'/'} if closing else None)
        args = []
        while not self._is_ch(']'):
            arg = self._next_var()
            if not self._is_valid_var_name(arg):
                raise SyntaxError(f'Invalid argument name: {arg}')
            args.append(arg)
        self._next_char()
        return tag, args

    def _take_char(self) -> str:
        ch = self._get_current()
        self._next_char()
        return ch

    def _skip_redundant_symbols(self):
        self._skip_whitespaces()
        if self._is_ch('#'):
            self._next_line()
        self._skip_whitespaces()

    def _is_closing_tag(self):
        retval = False
        if self._is_ch('['):
            self._next_char()
            retval = self._is_ch('/')
            self._rollback(1)
        return retval


test = '''
[test] # comment
[vars] # comment
&a : [raw]abcd[/raw]
&b : [m]hello, # not comment
there[/m]
[/vars] # comment
[body] # comment
Hello, world!
How are you?
&a_bgh#comment
- I, m fine
\^ # comment
not comment # comment
[case &d]
a: case1
b: [m]
case
2
[/m]
text: ^case3
[/case]
\[m\]
^dfghj
[/body] # comment
[/test]
'''

MLWParser(test).parse().print_()
