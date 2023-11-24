import re
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Any, Type, Callable, Optional, List, Tuple, Dict, Iterable
import warnings

from ask.utils.datetime_format import explain_datetime_format
from ask.utils.paths import trim_path
from ask.utils.predicates import is_valid_url, join


class Question:
    def __init__(self, name: str, type: Type, prompt: str, default: Any = None, required: bool = False,
                 predicate: Optional[Callable[[Any], bool]] = None, warn_on_type_mismatch=True):
        self.name = name
        self.type = type
        self.prompt = prompt
        self.default = default
        self.required = required
        self.predicate = predicate
        self.warn_on_type_mismatch = warn_on_type_mismatch

    def make_type_prompt(self) -> str:
        return '(' + self.type.__name__ + ')'

    def process_input(self, inpt):
        return self.type(inpt)

    def format_default(self) -> str:
        return str(self.default)

    def __str__(self):
        ans = f'{self.prompt} {self.make_type_prompt()}'

        if self.default is not None:
            ans += f' [default: {self.format_default()}]'

        if self.required:
            ans = '*' + ans

        return ans + ': '

    def __repr__(self):
        return f'Question({self.name}, {self.type})'

    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def ask(self):
        ans = self.default
        flag = True

        while flag:
            inpt = input(self.__str__())

            if inpt:
                try:
                    ans = self.process_input(inpt)

                    if (self.type is not Any) and (type(ans) is not self.type) and self.warn_on_type_mismatch:
                        warnings.warn(f'Warning: your process_input() returns a different type from'
                                      f' the type you specified for {self.__repr__()}. Is this intentional?')

                    if (self.predicate is not None) and (not self.predicate(ans)):
                        print(f'Invalid input: {inpt}. Please, try again!')
                        ans = None
                    else:
                        flag = False
                except Exception as e:
                    print(f'Unexpected input: {inpt}. Please, try again!')
                    print(e)
            else:
                if self.required and ans is None:
                    print('Input is required!')
                else:
                    flag = False

        return ans


class TextQuestion(Question):
    def __init__(self, name: str, prompt: str, default: int = None, required: bool = False,
                 predicate: Optional[Callable[[str], bool]] = None):
        super().__init__(name, str, prompt, default, required, predicate)


class IntQuestion(Question):
    def __init__(self, name: str, prompt: str, default: int = None, required: bool = False,
                 predicate: Optional[Callable[[Any], bool]] = None):
        super().__init__(name, int, prompt, default, required, predicate)


class FloatQuestion(Question):
    def __init__(self, name: str, prompt: str, default: float = None, required: bool = False,
                 predicate: Optional[Callable[[float], bool]] = None):
        super().__init__(name, float, prompt, default, required, predicate)


class BoolQuestion(Question):
    def __init__(self, name: str, prompt: str, default: bool = None, required: bool = False):
        super().__init__(name, bool, prompt, default, required)

    def process_input(self, inpt):
        if inpt.lower() in ('yes', 'true', 'y', '1'):
            return True
        elif inpt.lower() in ('no', 'false', 'n', '0'):
            return False
        else:
            raise ValueError("Expected answer 'yes'/'y' or 'no'/'n'")

    def make_type_prompt(self):
        return '(y/n)'

    def format_default(self) -> str:
        if self.default:
            return 'y'
        else:
            return 'n'


class DateTimeQuestion(Question):
    def __init__(self, name: str, prompt: str, datetime_formats: List[str], default: datetime = None,
                 required: bool = False,
                 predicate: Optional[Callable[[datetime], bool]] = None,
                 human_readable_format: str = '%d %B %Y',
                 n_prompts_to_show: Optional[int] = None):
        super().__init__(name, datetime, prompt, default, required, predicate)

        self.datetime_formats = datetime_formats
        self.human_readable_format = human_readable_format

        if n_prompts_to_show is None:
            n_prompts_to_show = len(self.datetime_formats)
        self.n_formats_to_show = n_prompts_to_show

    def format_default(self) -> str:
        return self.default.strftime(self.human_readable_format)

    def process_input(self, inpt):
        for date_format in self.datetime_formats:
            try:
                return datetime.strptime(inpt, date_format)
            except ValueError:
                continue
        raise ValueError(f"Input does not match any of the accepted formats: {', '.join(self.datetime_formats)}")

    def make_type_prompt(self):
        dtfs = self.datetime_formats[:self.n_formats_to_show]

        if len(dtfs) == 1:
            return f"({explain_datetime_format(dtfs[0])} format)"

        formats = ' | '.join([explain_datetime_format(x) for x in dtfs])

        if len(dtfs) < len(self.datetime_formats):
            formats += ' | ...'

        return f'({formats})'


class ChoiceQuestion(Question):
    def __init__(self, name: str, prompt: str, options: Iterable[Tuple[str, Any] | Any] | Dict[str, Any],
                 default: Any = None, required: bool = False, max_opt_width=30):
        super().__init__(name, Any, prompt, default, required)
        self.options = ChoiceQuestion._make_option_dict(options)
        self.max_opt_width = max_opt_width

    @staticmethod
    def _make_option_dict(options: Iterable[Tuple[str, Any] | Any] | Dict[str, Any]):
        if isinstance(options, dict):
            return options
        else:
            ans = {}

            for ind, item in enumerate(options):
                if isinstance(item, tuple):
                    key, opt = item
                else:
                    key, opt = ind, item
                ans[str(key)] = opt

            return ans

    def get_key(self, opt: Any) -> str | None:
        for key in self.options.keys():
            if self.options[key] == opt:
                return str(key)
        return None

    def process_input(self, inpt):
        try:
            return self.options[inpt]
        except KeyError as e:
            raise ValueError(f"Bad option name {inpt}") from e

    def make_type_prompt(self) -> str:
        opts = [f'{self.get_key(x)} - {x}' for x in self.options.values()]
        if sum([len(x) for x in opts]) > self.max_opt_width:
            opts = [f'\t{x}\n' for x in opts]
            return '\nPlease, choose one of the following options:\n' + ''.join(opts) + 'Option'
        else:
            return '(' + ', '.join(opts) + ')'


class MultiChoiceQuestion(ChoiceQuestion):
    def __init__(self, name: str, prompt: str, options: Iterable[Tuple[str, Any] | Any] | Dict[str, Any],
                 default: Any = 'all', required: bool = False, max_opt_width=30):
        super().__init__(name, prompt, options, default, required, max_opt_width)

        if default.lower() in ('all', '*'):
            self.default = self.options.values()
        else:
            self.default = default

    def process_input(self, inpt):
        if inpt.lower() in ('all', '*'):
            return list(self.options.values())

        choices = re.compile('[,;\s]').split(inpt)
        ans = []

        for choice in choices:
            try:
                ans.append(self.options[choice])
            except KeyError as e:
                raise ValueError(f"Bad option name {inpt}") from e

        return ans

    def make_type_prompt(self) -> str:
        opts = [f'{self.get_key(x)} - {x}' for x in self.options.values()]

        if sum([len(x) for x in opts]) > self.max_opt_width:
            opts = [f'\t{x}\n' for x in opts]
            return '\nPlease, choose some of the following options, separated by ",":\n' + ''.join(opts) + 'Option'
        else:
            return '(' + ', '.join(opts) + ')'


class PathQuestion(Question):
    def __init__(self, name: str, prompt: str, default: Optional[Path] = None, required: bool = False,
                 predicate: Optional[Callable[[float], bool]] = None):
        super().__init__(name, Path, prompt, default, required, predicate, False)

    def process_input(self, inpt):
        return Path(inpt).expanduser().resolve()

    def format_default(self) -> str:
        return trim_path(self.default, 3)


class UrlQuestion(Question):
    def __init__(self, name: str, prompt: str, default: Optional[str] = None, required: bool = False,
                 predicate: Optional[Callable[[float], bool]] = None):

        super().__init__(name, str, prompt, default, required, join(predicate, is_valid_url))
