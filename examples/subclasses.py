from typing import Union, NoReturn, Any
from dataclasses import dataclass

# From http://blog.ezyang.com/2020/10/idiomatic-algebraic-data-types-in-python-with-dataclasses-and-union/


class Result:
    pass


class OK(Result):
    result: int


class Failure(Result):
    msg: str


def assert_never(x: NoReturn) -> NoReturn:
    raise AssertionError("Unhandled type: {}".format(type(x).__name__))


def show_result(r: Result) -> None:
    if isinstance(r, OK):
        print(r.result)
    elif isinstance(r, Failure):
        print(r.msg)
    else:
        assert_never(r)


show_result(OK())
