
import numpy as np

class Node :
    def __init__(self):
        raise NotImplementedError

    def sign(self):
        raise NotImplementedError

    def reduce(self) :
        raise NotImplementedError

    def update_symbol(self) :
        raise NotImplementedError

    def compute(self) :
        raise NotImplementedError

    def derivate(self) :
        raise NotImplementedError

    def derivate_n(self, symbol, n) :
        expression = self
        for i in range(n) :
            expression = expression.derivate(symbol)
        return expression

class Placeholder(Node):
    def __init__(self, symbol, value=None) :
        self.symbol = symbol
        self.value = value

    def sign(self):
        return 2

    def reduce(self) :
        return self

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

    def sign(self):
        if self.value < 0:
            return -1
        elif self.value == 0:
            return 0
        else:
            return 1

    def reduce(self) :
        return self

    def update_symbol(self) :
        self.symbol = '(' + str(self.value) + ')'
        return self.symbol

    def compute(self) :
        return self.value

    def derivate(self, symbol) :
        return Scalar([0])

    def negate(self) :
        return Scalar([-self.value])

class Operator(Node) :
    def __init__(self, input) :
        self.input1 = input[0]
        self.input2 = input[1]

class Sommator(Operator):
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def sign(self):
        if self.input1.sign() == self.input2.sign():
            return self.input1.sign()
        elif self.input1.sign() == 0:
            return self.input2.sign()
        elif self.input2.sign() == 0:
            return self.input1.sign()
        else:
            return 2

    def reduce(self) :
        input1 = self.input1.reduce()
        input2 = self.input2.reduce()
        if isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        elif input1.sign() == 0:
            return input2
        elif input2.sign() == 0:
            return input1
        elif isinstance(input2, Scalar) and (input2.sign() == -1):
            return Substractor([input1, input2.negate()]).reduce()
        elif isinstance(input1, Scalar) and (input1.sign() == -1):
            return Substractor([input2, input1.negate()]).reduce()
        else:
            return Sommator([input1, input2])

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

    def sign(self):
        if self.input1.sign() == -self.input2.sign():
            return self.input1.sign()
        elif self.input1.sign() == 0:
            return -self.input2.sign()
        elif self.input2.sign() == 0:
            return self.input1.sign()
        else:
            return 2

    def reduce(self) :
        input1 = self.input1.reduce()
        input2 = self.input2.reduce()
        if isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        elif input2.sign() == 0:
            return input1
        elif isinstance(input2, Scalar) and (input2.sign() == -1):
            return Sommator([input1, input2.negate()]).reduce()
        else:
            return Substractor([input1, input2])

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

    def sign(self):
        sign = self.input1.sign() * self.input2.sign()
        if (sign >= -1) and (sign <= 1):
            return sign
        else:
            return 2

    def reduce(self):
        input1 = self.input1.reduce()
        input2 = self.input2.reduce()
        if isinstance(input1, Scalar) and (input1.compute() == 0):
            return Scalar([0])
        elif isinstance(input1, Scalar) and (input1.compute() == 1):
            return input2
        elif isinstance(input2, Scalar) and (input2.compute() == 0):
            return Scalar([0])
        elif isinstance(input2, Scalar) and (input2.compute() == 1):
            return input1
        elif isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        else:
            return Multiplicator([input1, input2])

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

    def sign(self):
        sign = self.input1.sign() * self.input2.sign()
        if (sign == -1) or (sign == 1) or ((sign == 0) and (self.input2.sign() != 0)):
            return sign
        elif self.input2.sign() == 0:
            return np.nan
        else:
            return 2

    def reduce(self):
        input1 = self.input1.reduce()
        input2 = self.input2.reduce()
        if isinstance(input1, Scalar) and (input1.compute() == 0):
            return Scalar([0])
        elif isinstance(input2, Scalar) and (input2.compute() == 1):
            return input1
        elif isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        else:
            return Divisor([input1, input2])

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

    def sign(self):
        if input2.sign() <= 1:
            return 1

    def reduce(self):
        input1 = self.input1.reduce()
        input2 = self.input2.reduce()
        if isinstance(input2, Scalar) and (input2.compute() == 0):
            return Scalar([1])
        elif isinstance(input2, Scalar) and (input2.compute() == 1):
            return input1
        elif isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        else:
            return Power([input1, input2])

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

    def sign(self):
        return 2

    def reduce(self):
        input = self.input.reduce()
        if isinstance(input, Scalar):
            return Scalar([self.compute()])
        else:
            return LogarithmNeperien([input])

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

    def sign(self):
        return 2

    def reduce(self):
        input1 = self.input.reduce()
        input2 = self.base.reduce()
        if isinstance(input1, Scalar) and isinstance(input2, Scalar):
            return Scalar([self.compute()])
        else:
            return Logarithm([input1, input2])

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

    def sign(self):
        return 2

    def reduce(self):
        return Cos([self.input.reduce()])

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

    def sign(self):
        return 2

    def reduce(self):
        return Sin([self.input.reduce()])

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

    def sign(self):
        return 2

    def reduce(self):
        return Tan([self.input.reduce()])

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
    print(f1.derivate_n('x', 2).update_symbol())
