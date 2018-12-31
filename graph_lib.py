
from node_lib import *
from pylab import plot, show

class Grapher :
    def __init__(self, *formula) :
        self.formula = formula

    def plot2d(self, value_dict, steps=100) :
        if self.do_formulas_have_same_placeholders() :
            not_fixed_placeholder = None
            for key in value_dict :
                if len(value_dict[key]) == 2 :
                    if not_fixed_placeholder == None :
                        not_fixed_placeholder = key
                    else :
                        raise 'at least two Placeholder have a range'
            if not_fixed_placeholder == None :
                raise 'no Placeholder found with range'
            for formula in self.formula :
                x = []
                y = []
                for scan_value in np.linspace(value_dict[not_fixed_placeholder][0], value_dict[not_fixed_placeholder][1], steps) :
                    feed_dict = {}
                    for key in value_dict :
                        if key == not_fixed_placeholder :
                            feed_dict[key] = scan_value
                        else :
                            feed_dict[key] = value_dict[key][0]

                    x.append(scan_value)
                    y.append(formula.compute(feed_dict))
                plot(x, y)
            show()

    def do_formulas_have_same_placeholders(self) :
        if len(self.formula) > 1 :
            reference_set = self.formula[0].get_placeholder()
            for formula in self.formula[1:] :
                current_set = formula.get_placeholder()
                if len(current_set) == len(reference_set) :
                    for k in current_set :
                        if k not in reference_set :
                            return False
                else :
                    return False
            return True
        else :
            return True

if __name__ == '__main__' :
    
    my_dict = {'x': [-10, 10], 'y': [5]}

    y = Placeholder('y')
    x = Placeholder('x')

    expression = Sommator([Power([x, Scalar([2])]), Multiplicator([Sin([Multiplicator([x, Scalar([10])])]), y])])

    my_grapher = Grapher(expression, expression.derivate('x'))
    my_grapher.plot2d(my_dict, 1000)

