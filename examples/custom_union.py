from typing import Union

from adt import ADTMeta


class Result(metaclass=ADTMeta):
    a: None
    b: int
    c: float


print(Result.b())
print(Result == Union[Result.a, Result.b, Result.c])

result = Result()

