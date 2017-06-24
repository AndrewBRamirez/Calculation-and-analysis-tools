# This document represents functions in a way that allows them to be easily
# differentiated. The methods and rules for differentiation, among other
# things, are included in this file. This file attempts to keep the
# process completely general, and ideally allow for partial differentiation
# of a scalar function for an arbitrary number of variables. Note this code
# was created with Python 3.x

# Class definitions for functions


class Function:
    def __init__(self, functions=(None, None), scalar=Scalar(1), op=None):
        """
        :param functions: the two comprising functions in a tuple.
        The functions themselves are Function objects
        :param scalar: a scalar in the real numbers by which to multiply the
        function. This produces dilation for functions
        :param op: operation joining the functions, which can be one of
        addition, subtraction, multiplication, division, and composition. Takes
        it as a string, where composition is 'o'. Note that if the operator
        is not commutative, the first function is taken as the first function
        to the operation, i.e. ((f1, f2), '-') = f1 - f2
        """
        
        # Make sure the user gave reasonable inputs
        if type(functions) is not tuple or type(scalar) is not Scalar or \
                type(op) is not str:
            raise ValueError('Check the input types')
        if len(functions) != 2 or None in functions:
            raise ValueError('Please enter two functions')
        if op is None:
            raise ValueError('Please enter an operator')
        
        # Set instance variables
        self.function = dict()
        self.function['funcs'] = functions
        self.function['scalar'] = scalar
        self.function['operator'] = op
    
    def __mul__(self, other, changeself=True):
        # We can multiply functions by scalars or other functions
        if isinstance(other, Scalar):
            return other * self  # Refer to scalar multiplication - it's easier
        elif isinstance(other, Function):
            if not changeself:
                return Function((self, other), self.function['scalar'] *
                                other.function['scalar'], '*')
            else:
                self.function['funcs'] = (self)
    
    def get_funcs(self):
        return self.function['funcs']
    
    def get_scalar(self):
        return self.function['scalar']
    
    def get_op(self):
        return self.function['operator']


# Define the universal base function for an arbitrary variable
class Base(Function):
    def __init__(self, scalar=Scalar(1), variable='x'):
        # Note one of the defining characteristics of the universal
        # base function is the fact that its sole function is just the
        # variable itself with a scalar
        super().__init__((variable, variable), scalar, 'o')
    
    def diff(self):
        """
        :return: the differentiated function
        """
        
        # Classic derivative
        return self.function['scalar']


class Scalar:
    def __init__(self, val_list):
        # vals is a list of the factors that make up the scalar -
        # for example, a scalar of '12y' would be the list [12, 'y'].
        # Also note that inverted factors are represented '1 / factor' and
        # added/subtracted factors are represented e.g. ([1], [y], '+') for
        # '1 + y'
        self.factors = val_list[:]  # Copy the list
    
    # Use the above syntax to denote an addition of scalars
    def __add__(self, other):
        return Scalar([(self.get_vals(), other.get_vals(), '+')])
    
    def __sub__(self, other):
        return Scalar([(self.get_vals(), other.get_vals(), '-')])
    
    def __mul__(self, other):
        # Scalars can be multiplied by other scalars or functions
        
        # Handle the various cases of multiplying with a scalar
        if isinstance(other, int) or isinstance(other, str):
            return Scalar(self.get_vals().append(other))
        elif isinstance(other, Function):
            return Function(functions=other.get_funcs(),
                            scalar=Scalar(other.get_scalar().get_vals().extend(
                                self.get_vals())), op=other.get_op())
        elif isinstance(other, Scalar):
            
            # If 0 is a factor for either, it results in a 0 scalar
            if 0 in self.get_vals() or 0 in other.get_vals():
                return Scalar([0])
            
            return Scalar(self.get_vals().extend(other.get_vals()))
        else:
            raise ValueError('Multiplication by invalid object')
    
    def __truediv__(self, other):
        # Scalars can be divided by other scalars or functions
        
        # Handle the various cases of dividing with a scalar
        if isinstance(other, int):
            
            # No dividing by zero
            if other == 0:
                raise ValueError('Divide by zero error')
            
            return Scalar(self.get_vals().append(1 / other))
        elif isinstance(other, str):
            return Scalar(self.get_vals().append('1/' + other))
        elif isinstance(other, Function):
            pass  # TODO once function inverse defined
        elif isinstance(other, Scalar):
            
            # If 0 is a factor in self, it results in a 0 scalar
            if 0 in self.get_vals() and 0 not in other.get_vals():
                return Scalar([0])
            elif 0 in other.get_vals() and 0 not in self.get_vals():
                raise ValueError('Divide by zero error')
            elif 0 in self.get_vals() and 0 in other.get_vals():  # Both zero
                raise ValueError('Indeterminate form: 0/0')
            
            return Scalar(self.get_vals().extend(other.get_vals()))
        else:
            raise ValueError('Division by invalid object')
    
    def __repr__(self):
        
        # Initialize the string
        repr_str = ''
        
        # Format the string nicely
        for factor in self.factors:
            repr_str += str(factor) + ' * '
        
        # Strip useless characters from the end, if needed
        if repr_str != '':
            return repr_str[:-4]
        
        return repr_str
    
    # Get the value of the scalar, aka its factor list
    def get_vals(self):
        return self.factors
    
    # Add a value to the scalar
    def add_val(self, val):
        self.factors.append(val)
    
    # Differentiation, made static since it's the same for all instances
    @staticmethod
    def diff():  # Another classic, simple differentiation
        return Scalar([0])

# The class for raising an expression to a power
class Pow(Function):
    def __init__(self):
        pass  # TODO