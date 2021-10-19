from typing import Union

from adt import ADTMeta


class Foo:
    qwerty: str


class Result(Foo, metaclass=ADTMeta):
    a: None
    b: int
    c: Union[str, int]


# print(type(Result.b))
# print(Result.b())
# print(Result == Union[Result.a, Result.b, Result.c])

result = Result()
result.bit_count()
