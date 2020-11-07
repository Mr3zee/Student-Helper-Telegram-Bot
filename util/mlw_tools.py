"""this file is a mess, later i will fix it and make comments, maybe"""

from typing import Dict, TextIO
from static import consts
from util import util


class MLWText:
    def __init__(self, name, parsed_seq: list, local_vars: Dict[str, list] = None, cases: Dict[str, list] = None,
                 global_vars: Dict[str, str] = None, local_dict: dict = None, local_dict_keys: list = None):
        self.name = name
        self.__parsed_seq = parsed_seq
        self.__local_vars = (local_vars if local_vars else {})
        self.__cases = (cases if cases else {})
        self.__global_vars = (global_vars if global_vars else {})
        self.__local_dict = local_dict
        self.__local_dict_keys = local_dict_keys

    def __get_text(self, seq: list) -> str:
        new_seq = []
        prev = None
        for part in seq:
            if part == '\n' and prev == '\0':
                prev = None
                continue
            if len(part) and (part[0] == '&' or part[0] == '^'):
                element = self.__substitute_vars(part)
            elif part.startswith('_case'):
                element = self.__substitute_case(part)
                if not element or element == '\0':
                    prev = '\0'
            else:
                element = part
            new_seq.append(element)
        return ''.join(new_seq)

    def __load_from_local_dict(self, var_name):
        return util.get_value(
            self.__local_dict,
            *[*self.__local_dict_keys, self.name, var_name],
        )

    def __substitute_vars(self, var_name: str) -> str:
        if var_name[0] == '&':
            retval = self.__local_vars.get(var_name)
            if retval is None:
                retval = self.__load_from_local_dict(var_name[1:])
            if retval is not None:
                return self.__get_text(retval)
            raise ValueError(f'Undefined local variable: {var_name}')
        elif var_name[0] == '^':
            retval = self.__global_vars.get(var_name)
            if retval is not None:
                return retval
            raise ValueError(f'Undefined global variable: {var_name}')
        raise ValueError(f'Invalid var name: {var_name}')

    def __substitute_case(self, case_name: str) -> str:
        case_var, states = self.__cases[case_name]
        if case_var[0] == '&' or case_var[0] == '^':
            case_var = self.__substitute_vars(case_var)
        if case_var == consts.ALL and consts.ALL not in states.keys():
            all_values = list(states.values())
            substitution = [f'{self.__get_text(value)}\n\n' for value in all_values[:-1]]
            substitution.append(self.__get_text(all_values[-1]))
        else:
            substitution = states.get(case_var)
        return self.__get_text(substitution) if substitution else ''

    def add_global_vars(self, values: dict):
        self.__global_vars.update({f'^{key}': value for key, value in values.items()})

    def add_local_dict(self, local_dict: dict, local_dict_keys: list):
        self.__local_dict = local_dict
        self.__local_dict_keys = local_dict_keys

    def text(self, global_vars: Dict[str, str] = None) -> str:
        if global_vars:
            self.add_global_vars({key: str(value) for key, value in global_vars.items()})

        return self.__get_text(self.__parsed_seq)


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

    def roll_back(self, i):
        self.__pos -= i

    def get_tail(self):
        return self.__source[max(self.__pos - (1 if self.has_next() else 0), 0):]


class BaseParser:

    def __init__(self, input_text):
        self.__source = Source(input_text)
        self.__current = ''
        self._next_char()

    def _next_char(self):
        self.__current = self.__source.next()

    def _roll_back(self, i):
        self.__source.roll_back(i + 1)
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
        retval = self._next_with_filter(lambda ch: ch != '\n')
        self._next_char()
        return retval

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

    def _get_tail(self):
        return self.__source.get_tail()

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

    def _next_var(self):
        return self._next_word({'&', '^'})

    def __init__(self, input_text):
        super().__init__(input_text)
        self.__text_seq = []
        self.__local_vars = {}
        self.__cases = {}

    def parse(self) -> (MLWText, str):
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
        self._skip_redundant_symbols()
        return MLWText(main_tag, self.__text_seq, self.__local_vars, self.__cases), self._get_tail()

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

    def _parse_single_line_text(self) -> list:
        def make_retval():
            if text:
                retval.append(''.join(text))
            return retval

        retval = []
        text = []
        self._skip_redundant_symbols()
        while True:
            if self._is_ch('#'):
                self._next_line()
                return make_retval()
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
                make_retval()
                if self._is_closing_tag():
                    return retval
                retval.extend(self._parse_tag())
                text = []
                continue
            elif self._is_ch('\n'):
                return make_retval()
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
            while self._is_ch('\n'):
                retval.extend([self._take_char()])
                self._skip_comments()
            if self._is_closing_tag():
                break
        return retval

    def _parse_raw_text(self) -> str:
        text = []
        while not self._is_ch('['):
            if self._is_ch('\\'):
                self._take_char()
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
            value = self._parse_single_line_text()
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
        self._skip_comments()
        self._skip_whitespaces()

    def _skip_comments(self):
        while self._is_ch('#'):
            self._next_line()

    def _is_closing_tag(self):
        retval = False
        if self._is_ch('['):
            self._next_char()
            retval = self._is_ch('/')
            self._roll_back(1)
        return retval


test = '''
[test] 
[vars] 
&a : [raw]abcd[/raw]
&b : [m]hello, # not comment
there: ^a[/m]
[/vars]
[body]
--------------
^a
&a
&b
[case ^b]
o: one
t: two
[/case]
--------------
[/body]
[/test]
'''

# parsed_test, rest = MLWParser(test).parse()
# print(parsed_test.text({'^a': 'Hello, World', '^b': 'r'}))


def mlw_load(file: TextIO) -> Dict[str, MLWText]:
    retval = {}
    tail = file.read()
    while True:
        head, tail = MLWParser(tail).parse()
        retval[head.name] = head
        if not tail:
            break
    return retval
