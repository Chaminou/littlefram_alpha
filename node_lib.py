
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
            return Scalar(1)
        else :
            return Scalar(0)

class Scalar(Node) :
    def __init__(self, value) :
        self.value = value
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + str(self.value) + ')'
        return self.symbol

    def compute(self) :
        return self.value

    def derivate(self, symbol) :
        return Scalar(0)

class Operator(Node) :
    def __init__(self, input) :
        self.input1 = input[0]
        self.input2 = input[1]

class Sommator(Operator):
    def __init__(self, input):
        super().__init__(input)
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + str(self.input1.update_symbol()) + "+" +str(self.input2.update_symbol()) + ')'
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
        self.symbol = '(' + str(self.input1.update_symbol()) + "-" +str(self.input2.update_symbol()) + ')'
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
        self.symbol = '(' + str(self.input1.update_symbol()) + "*" +str(self.input2.update_symbol()) + ')'
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
        self.symbol = '(' + str(self.input1.update_symbol()) + "/" +str(self.input2.update_symbol()) + ')'
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
        self.symbol = '(' + str(self.input1.update_symbol()) + "^" +str(self.input2.update_symbol()) + ')'
        return self.symbol

    def compute(self) :
        return self.input1.compute() ** self.input2.compute()

    def derivate(self) :
        return NotImplementedError

class Logarithm(Operator) :
    def __init__(self, input, base) :
        super().__init__(input)
        raise NotImplementedError


if __name__ == '__main__' :
    x = Placeholder('x', 10)
    y = Placeholder('y', 20)
    nombre = Scalar(-4)
    sommateur = Sommator((x, y))
    multiplicateur = Multiplicator((sommateur, nombre))

    print(multiplicateur.update_symbol())
    print(multiplicateur.derivate('x').update_symbol())
