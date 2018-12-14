
import numpy as np

class Node :
    def __init__(self):
        raise NotImplementedError

    def update_symbol(self) :
        raise NotImplementedError

    def compute(self) :
        raise NotImplementedError

    def derivate(self) :
        raise NotImplementedError

class Placeholder(Node):
    def __init__(self, symbol, value=None) :
        self.symbol = symbol
        self.value = value

    def update_symbol(self) :
        return self.symbol

    def compute(self) :
        return self.value

    def derivate(self, symbol) :
        if self.symbol == symbol :
            return Scalar([1])
        else :
            return Scalar([0])

class Scalar(Node) :
    def __init__(self, value) :
        self.value = value[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + str(self.value) + ')'
        return self.symbol

    def compute(self) :
        return self.value

    def derivate(self, symbol) :
        return Scalar([0])

class Operator(Node) :
    def __init__(self, input) :
        self.input1 = input[0]
        self.input2 = input[1]

class Sommator(Operator):
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "+" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() + self.input2.compute()

    def derivate(self, symbol) :
        return Sommator([self.input1.derivate(symbol), self.input2.derivate(symbol)])

class Substractor(Operator):
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "-" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() - self.input2.compute()

    def derivate(self, symbol) :
        return Substractor([self.input1.derivate(symbol), self.input2.derivate(symbol)])

class Multiplicator(Operator) :
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "*" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() * self.input2.compute()

    def derivate(self, symbol) :
        return Sommator([Multiplicator([self.input1.derivate(symbol), self.input2]), Multiplicator([self.input1, self.input2.derivate(symbol)])])

class Divisor(Operator) :
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "/" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() / self.input2.compute()

    def derivate(self, symbol) :
        return Divisor([Substractor([Multiplicator([self.input1.derivate(symbol), self.input2]), Multiplicator([self.input1, self.input2.derivate(symbol)])]), Power([self.input2, Scalar([2])])])

class Power(Operator) :
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "^" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() ** self.input2.compute()

    def derivate(self, symbol) :
        if isinstance(self.input2, Scalar) :
            return Multiplicator([Multiplicator([self.input2, Power([self.input1, Scalar([self.input2.value - 1])])]), self.input1.derivate(symbol)])
        else :
            raise NotImplementedError

class LogarithmNeperien(Node) :
    def __init__(self, input) :
        self.input = input[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(ln(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self) :
        return np.log(self.input.compute())

    def derivate(self, symbol) :
        return Divisor([self.input.derivate(symbol), self.input])

class Logarithm(Node) :
    def __init__(self, input) :
        self.input = input[0]
        if input[1] == None :
            self.base = Scalar([np.e])
        else :
            self.base = input[1]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(log[' + self.base.update_symbol() + '](' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self) :
        return np.log(self.input.compute()) / np.log(self.base.compute())

    def derivate(self, symbol) :
        return Divisor([LogarithmNeperien([self.input]), LogarithmNeperien([self.base])]).derivate(symbol)

class Cos(Node) :
    def __init__(self, input) :
        self.input = input[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(cos(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self) :
        return np.cos(self.input.compute())

    def derivate(self, symbol) :
        return Multiplicator([Multiplicator([Scalar([-1]), Sin([self.input])]), self.input.derivate(symbol)])

class Sin(Node) :
    def __init__(self, input) :
        self.input = input[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(sin(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self) :
        return np.sin(self.input.compute())

    def derivate(self, symbol) :
        return Multiplicator([Cos([self.input]), self.input.derivate(symbol)])

class Tan(Node) :
    def __init__(self, input) :
        self.input = input[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(tan(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self) :
        return np.tan(self.input.compute())

    def derivate(self, symbol) :
        return Divisor([Sin([self.input]), Cos([self.input])]).derivate(symbol)


if __name__ == '__main__' :

    x = Placeholder('x', np.pi)
    u = Placeholder('u', 3)

    f1 = Sin([x])
    f2 = Cos([f1])
    t = Tan([x])

    print(f1.update_symbol())
    print(f1.compute())
    print(f1.derivate('x').update_symbol())

    print(f2.update_symbol())
    print(f2.compute())
    print(f2.derivate('x').update_symbol())

    print(t.update_symbol())
    print(t.compute())
    print(t.derivate('x').update_symbol())
