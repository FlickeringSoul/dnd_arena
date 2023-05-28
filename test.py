
from dataclasses import dataclass
import copy
import itertools

class B:
    def __init__(self, b: int) -> None:
        self.b = b

@dataclass
class A:
    a: list
    c: list

    def toto(self):
        for x in self.a:
            print('YOLO !')
            response = yield 'yield'
            print(f'response {response}')
            value = yield x
            print(f'YOUPI {value}')

b = B(1)
a = A([b], [])
a.c.append(a.a[0])
print(a)

a_bis = copy.deepcopy(a)

print(a_bis)
print(a_bis.a[0].b)
a_bis.a[0].b = 2
print(a_bis.c[0].b)

g1 = a.toto()
print(g1)
g1_bis, g2 = itertools.tee(g1)
print('After copy')
print(g1.send(None))
print(g1.send('toto'))
print(list(g1_bis))
print(list(g2))
print(list(g1))