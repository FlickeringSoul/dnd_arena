

from typing import Self


class A:
    def __new__(cls: type[Self]) -> Self:
        pass