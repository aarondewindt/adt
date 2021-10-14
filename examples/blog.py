from typing import Union, NoReturn
from dataclasses import dataclass

# From http://blog.ezyang.com/2020/10/idiomatic-algebraic-data-types-in-python-with-dataclasses-and-union/


@dataclass(frozen=True)
class OK:
    result: int


@dataclass(frozen=True)
class Failure:
    msg: str


Result = Union[OK, Failure]


def assert_never(x: NoReturn) -> NoReturn:
    raise AssertionError("Unhandled type: {}".format(type(x).__name__))


def show_result(r: Result) -> None:
    if isinstance(r, OK):
        print(r.result)
    elif isinstance(r, Failure):
        print(r.msg)
    else:
        assert_never(r)


show_result(OK(1))
