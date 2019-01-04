import numpy as np

def sum_scalar_list(scalar_list) :
    sum = 0
    for scalar in scalar_list :
        sum += scalar.value
    return Scalar([sum])


class Node :
    def __init__(self):
        raise NotImplementedError

    def update_symbol(self) :
        raise NotImplementedError

    def compute(self, feed_dict) :
        raise NotImplementedError

    def derivate(self) :
        raise NotImplementedError

    def derivate_n(self, symbol, n) :
        expression = self
        for i in range(n) :
            expression = expression.derivate(symbol)
        return expression

    def get_placeholder(self) :
        raise NotImplemented

    def reduce(self) :
        raise NotImplemented

    def print(self, depth_level=0) :
        raise NotImplemented

class Placeholder(Node):
    def __init__(self, symbol) :
        self.symbol = symbol

    def update_symbol(self) :
        return self.symbol

    def compute(self, feed_dict) :
        try :
            return feed_dict[self.symbol]
        except :
            raise 'Error: %s not given in the list of symbols.' % self.symbol

    def derivate(self, symbol) :
        if self.symbol == symbol :
            return Scalar([1])
        else :
            return Scalar([0])

    def get_placeholder(self) :
        return set([self])

    def reduce(self) :
        return self

    def print(self, depth_level=0) :
        print('-' * depth_level + self.symbol)


class Scalar(Node) :
    def __init__(self, value) :
        self.value = value[0]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(' + str(self.value) + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return self.value

    def derivate(self, symbol) :
        return Scalar([0])

    def get_placeholder(self) :
        return set()

    def reduce(self) :
        return self

    def print(self, depth_level=0) :
        print('-' * depth_level + self.symbol)

class Operator(Node) :
    def __init__(self, input) :
        self.input1 = input[0]
        self.input2 = input[1]
        self.update_symbol()

    def get_placeholder(self) :
        return self.input1.get_placeholder() | self.input2.get_placeholder()

    def reduce_inputs(self) :
        self.input1 = self.input1.reduce()
        self.input2 = self.input2.reduce()

    def print(self, depth_level=0) :
        print('-' * depth_level + str(type(self)))
        for i in range(len([self.input1, self.input2])) :
            print('-' * (depth_level+1) + 'input' + str(i) + ':')
            [self.input1, self.input2][i].print(depth_level+2)

class Function(Node) :
    def __init__(self, input) :
        self.input = input[0]
        self.update_symbol()

    def get_placeholder(self) :
        return self.input.get_placeholder()
    
    def reduce_input(self) :
        self.input = self.input.reduce()

    def reduce(self) :
        self.reduce_input()
        return self

    def print(self, depth_level=0) :
        print('-' * depth_level + self.symbol)
        self.input.print(depth_level+1)

class Negate(Function) :
    def update_symbol(self) :
        self.symbol = '(-' + self.input.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return -1 * self.input.compute(feed_dict)

    def derivate(self, symbol) :
        return Negate([self.input.derivate(symbol)])

    def reduce(self) :
        self.reduce_input()
        if isinstance(self.input, Scalar) :
            return Scalar([-1*self.input.value])
        return self
            
class Sommator(Operator):
    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "+" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return self.input1.compute(feed_dict) + self.input2.compute(feed_dict)

    def derivate(self, symbol) :
        return Sommator([self.input1.derivate(symbol), self.input2.derivate(symbol)])

    def explore(self) :
        scalar_list = []
        complement_list = []
        for inpt in [self.input1, self.input2] :
            if isinstance(inpt, Scalar) :
                scalar_list.append(inpt)
            elif isinstance(inpt, Sommator):
                result_scalar, result_complement = inpt.explore()
                if result_scalar != [] :
                    scalar_list += result_scalar
                if result_complement != [] :
                    complement_list += result_complement
            else :
                complement_list.append(inpt)

        return scalar_list, complement_list


    def build_up(self, scalar_list, complement_list) :
        if len(complement_list) == 0 :
            return sum_scalar_list(scalar_list)
        else :
            neutral_element = Scalar([0])
            new_node = Sommator([sum_scalar_list(scalar_list), neutral_element])
            current_node = new_node
            for index in range(len(complement_list)) :
                if index != len(complement_list) - 1 :
                    current_node.input2 = Sommator([complement_list[index], neutral_element])
                    current_node = current_node.input2
                else :
                    current_node.input2 = complement_list[index]
            new_node.update_symbol()
            return new_node 

    def reduce(self) :
        self.reduce_inputs()
        scalar_list, complement_list = self.explore()
        reduced_node = self.build_up(scalar_list, complement_list)
        return reduced_node

class Substractor(Sommator) :
    def __init__(self, input) :
        self.input1 = input[0]
        self.input2 = Negate([input[1]])
        self.update_symbol()

    def update_symbol(self) :
        if isinstance(self.input2, Negate) :
            self.symbol = '(' + self.input1.update_symbol() + "-" + self.input2.input.update_symbol() + ')'
        else :
            self.symbol = '(' + self.input1.update_symbol() + "+" + self.input2.update_symbol() + ')'
        return self.symbol


    '''
    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "-" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return self.input1.compute(feed_dict) - self.input2.compute(feed_dict)

    def derivate(self, symbol) :
        return Substractor([self.input1.derivate(symbol), self.input2.derivate(symbol)])
    '''

class Multiplicator(Operator) :
    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "*" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        if (isinstance(self.input1, Scalar) and self.input1.value == 0) or (isinstance(self.input2, Scalar) and self.input2.value == 0) :
            return 0
        else :
            return self.input1.compute(feed_dict) * self.input2.compute(feed_dict)

    def derivate(self, symbol) :
        return Sommator([Multiplicator([self.input1.derivate(symbol), self.input2]), Multiplicator([self.input1, self.input2.derivate(symbol)])])

    def reduce(self) :
        self.reduce_inputs()
        return self

class Divisor(Operator) :
    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "/" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return self.input1.compute(feed_dict) / self.input2.compute(feed_dict)

    def derivate(self, symbol) :
        return Divisor([Substractor([Multiplicator([self.input1.derivate(symbol), self.input2]), Multiplicator([self.input1, self.input2.derivate(symbol)])]), Power([self.input2, Scalar([2])])])
    
    def reduce(self) :
        self.reduce_inputs()
        return self

class Power(Operator) :
    def update_symbol(self) :
        self.symbol = '(' + self.input1.update_symbol() + "^" + self.input2.update_symbol() + ')'
        return self.symbol

    def compute(self, feed_dict) :
        return self.input1.compute(feed_dict) ** self.input2.compute(feed_dict)

    def derivate(self, symbol) :
        return Multiplicator([Power([self.input1, self.input2]), Sommator([Multiplicator([self.input1.derivate(symbol), Divisor([self.input2, self.input1])]), Multiplicator([self.input2.derivate(symbol), LogarithmNeperien([self.input1])])])])

    def reduce(self) :
        self.reduce_inputs()
        return self

class Logarithm(Node) :
    def __init__(self, input) :
        self.input = input[0]
        if len(input) < 2 :
            self.base = Scalar([np.e])
        else :
            self.base = input[1]
        self.update_symbol()

    def update_symbol(self) :
        self.symbol = '(log[' + self.base.update_symbol() + '](' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self, feed_dict) :
        arg_value = self.input.compute(feed_dict)
        base_value = self.base.compute(feed_dict)
        if arg_value > 0 and base_value > 0 and base_value != 1 :
            return np.log(arg_value) / np.log(base_value)
        else :
            return np.nan

    def derivate(self, symbol) :
        return Divisor([LogarithmNeperien([self.input]), LogarithmNeperien([self.base])]).derivate(symbol)

    def get_placeholder(self) :
        return self.input.get_placeholder() | self.base.get_placeholder()

    def reduce(self) :
        self.input = self.input.reduce()
        self.base = self.base.reduce()
        return self

    def print(self, depth_level=0) :
        print('-' * depth_level + self.symbol)
        print('-' * (depth_level+1) + "input:")
        self.input.print(depth_level+2)
        print('-' * (depth_level+1) + "base:")
        self.base.print(depth_level+2)

class LogarithmNeperien(Logarithm) :
    def update_symbol(self) :
        self.symbol = '(ln(' + self.input.update_symbol() + '))'
        return self.symbol

    def derivate(self, symbol) :
        return Divisor([self.input.derivate(symbol), self.input])

class Cos(Function) :
    def update_symbol(self) :
        self.symbol = '(cos(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self, feed_dict) :
        return np.cos(self.input.compute(feed_dict))

    def derivate(self, symbol) :
        return Multiplicator([Multiplicator([Scalar([-1]), Sin([self.input])]), self.input.derivate(symbol)])

class Sin(Function) :
    def update_symbol(self) :
        self.symbol = '(sin(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self, feed_dict) :
        return np.sin(self.input.compute(feed_dict))

    def derivate(self, symbol) :
        return Multiplicator([Cos([self.input]), self.input.derivate(symbol)])


class Tan(Function) :
    def update_symbol(self) :
        self.symbol = '(tan(' + self.input.update_symbol() + '))'
        return self.symbol

    def compute(self, feed_dict) :
        return np.tan(self.input.compute(feed_dict))

    def derivate(self, symbol) :
        return Divisor([Sin([self.input]), Cos([self.input])]).derivate(symbol)


if __name__ == '__main__' :

    x = Placeholder('x')
    n = Scalar([3])

    f = Substractor([n, x])

    print(f.symbol)
    print(f.derivate('x').symbol)
    print(f.compute({'x': 6}))
    print(f.derivate('x').compute({'x': 6}))
    print(f.reduce().symbol)
    print(Negate([Scalar([10])]).symbol)
    print(Negate([Scalar([10])]).reduce().symbol)
