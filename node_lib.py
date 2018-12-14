
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
        return Divisor([Substractor([Multiplicator([self.input1.derivate(symbol), self.input2]), Multiplicator([self.input1, self.input2.derivate(symbol)])]), Power([self.input2, Scalar(2)])])

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

class Logarithm(Node) :
    def __init__(self, input, base=None) :
        self.input = input[0]
        if base == None :
            self.base = np.e
        elif isinstace(base, Scalar) :
            self.base  = base.value
        else :
            self.base = base
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(log[' + str(self.base) + '](' + self.input.update_symbol() + ')'
        return self.symbol

    def compute(self) :
        return np.log(self.input.compute()) / np.log(self.base)

    def derivate(self, symbol) :
        return Divisor([self.input.derivate(symbol), Multiplicator([self.input, Scalar([np.log(self.base)])])])


if __name__ == '__main__' :

    # ((((x^(10))+(x^(-2)))+(x^(7.5)))+(19)) .derivate(x) =>
    # ((((((10)*(x^(9)))*(1))+(((-2)*(x^(-3)))*(1)))+(((7.5)*(x^(6.5)))*(1)))+(0))

    x = Placeholder('x', None)
    power1 = Scalar([10])
    power2 = Scalar([-2])
    power3 = Scalar([7.5])
    d = Scalar([19])

    a = Power([x, power1])
    b = Power([x, power2])
    c = Power([x, power3])
    sum1 = Sommator([a, b])
    sum2 = Sommator([sum1, c])
    sum3 = Sommator([sum2, d])

    print(sum3.update_symbol())
    print(sum3.derivate('x').update_symbol())
