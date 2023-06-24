import copy
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction


def config_logging():
    handler = logging.StreamHandler()
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def debug_decorator(function):
    def wrapped_function(*args, **kwargs):
        logging.debug(f'Function {function.__name__} called with args={args} and kwargs={kwargs}')
        res = function(*args, **kwargs)
        logging.debug(f'Function {function.__name__} returned with value = {res}')
        return res
    return wrapped_function

### ExplainedValue types


@dataclass
class HistoryAddition:
    values: list['History'] = field(default_factory=list)


@dataclass
class HistoryMultiplication:
    factor: str
    history: 'History'


History = HistoryAddition | HistoryMultiplication | str


def flatten_history(history: History) -> dict[tuple, list[str]]:
    memory = defaultdict(list)
    match history:
        case HistoryAddition(values=sum_list):
            for inner_history in sum_list:
                for k, v in flatten_history(inner_history).items():
                    memory[k].extend(v)
        case HistoryMultiplication(factor=factor, history=history):
            for k, v in flatten_history(history).items():
                memory[k + (factor,)] = v
        case str():
            memory[()] = [history]
    return memory


def repr_history(history: History) -> str:
    return '\n'.join(' * '.join(k) + ' * (' + ' + '.join(v) + ')' for k, v in flatten_history(history).items())



@dataclass
class ExplainedValue:
    value: Fraction = field(default_factory=Fraction)
    history: History = HistoryAddition([])

    def __add__(self, other: 'ExplainedValue') -> 'ExplainedValue':
        if isinstance(self.history, HistoryAddition):
            history_addition = copy.deepcopy(self.history) # copy should be enough ?
            history_addition.values.append(other.history)
        else:
            history_addition = HistoryAddition(
                values=[self.history, other.history]
            )
        return ExplainedValue(
            value=self.value + other.value,
            history=history_addition
        )

    def __mul__(self, other: 'ExplainedValue') -> 'ExplainedValue':
        if not isinstance(self.history, str):
            raise ValueError
        return ExplainedValue(
            value=self.value * other.value,
            history=HistoryMultiplication(
                factor=self.history,
                history=other.history
            )
        )
