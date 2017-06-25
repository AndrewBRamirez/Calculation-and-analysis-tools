# This document represents functions in a way that allows them to be easily
# differentiated. The methods and rules for differentiation, among other
# things, are included in this file. This file attempts to keep the
# process completely general, and ideally allow for partial differentiation
# of a scalar function for an arbitrary number of variables. Note this code
# was created with Python 3.x

# Any necessary import statements
import re

# Class definitions for functions


class Scalar:
    def __init__(self, val_list):
        # vals is a list of the factors that make up the scalar -
        # for example, a scalar of '12y' would be the list [12, 'y'].
        # Also note that inverted factors are represented '1 / factor' and
        # added/subtracted factors are represented e.g. ([1], [y], '+') for
        # '1 + y'
        self.factors = val_list[:]  # Copy the list
        
        # Simplify from the get-go
        self.simplify()

    # We'll want a function to simplify the scalar whenever possible
    def simplify(self):
        # Keep track of all of the simple numbers in the factors
        nums = 1
    
        # Also keep track of all tuple expressions encountered
        exprs = []
        
        # Loop through all factors
        for fact in self.factors:
            
            # Just multiply all numbers
            if isinstance(fact, int) or isinstance(fact, float):
                nums *= fact
            
            # Handle variables and expressions
            elif isinstance(fact, str):
                
                # Check the length before checking for an inversion this way
                if len(fact) >= 3:  # Could start with '1/' or '1 /'
                    
                    # Now actually check for the beginning of an inversion
                    if fact[:2] == '1/' or fact[:3] == '1 /':
                        
                        # Check only after the division symbol, removing
                        # excess white space
                        term = fact[fact.index('/') + 1:].strip()

                        # The non-inverse is already in the expression list
                        if term in exprs:
                            
                            # Then we cancel the non-inverse and continue
                            exprs.remove(term)
                        else:  # Then add it with no issue
                            exprs.append(fact)
                    else:
                        
                        # Check if the inverse is present - check all possible
                        # formats
                        if ('1/' + fact) in exprs:
                            exprs.remove('1/' + fact)
                        elif ('1 /' + fact) in exprs:
                            exprs.remove('1 /' + fact)
                        elif ('1/ ' + fact) in exprs:
                            exprs.remove('1/ ' + fact)
                        elif ('1 / ' + fact) in exprs:
                            exprs.remove('1 / ' + fact)
                        
                        # If no inverse deteced, simply add it to the factors
                        else:
                            exprs.append(fact)
                else:  # Can't possibly be an inverse expression or variable
                    
                    # Check if the inverse of the input is present in the
                    # factors - check all possible formats
                    if ('1/' + fact) in exprs:
                        exprs.remove('1/' + fact)
                    elif ('1 /' + fact) in exprs:
                        exprs.remove('1 /' + fact)
                    elif ('1/ ' + fact) in exprs:
                        exprs.remove('1/ ' + fact)
                    elif ('1 / ' + fact) in exprs:
                        exprs.remove('1 / ' + fact)
                    else:
                        exprs.append(fact)
            else:  # This is put mostly for debugging purposes
                raise ValueError('Unexpected input type: %s' % type(fact))
    
        # Apply these changes to the factor list
        self.factors = [nums] + exprs
                
    # If we were to call the scalar, as if it were a function y = scalar,
    # we'd just get the value of the scalar
    def __call__(self, *args):  # Same with any number of arguments
        
        # Simplify self before trying anything
        self.simplify()
        
        # Initialize the string to be returned at the end
        return_str = ''
        
        # If we have no abstract factors, we can just do a regular return
        if len(self.factors) == 1: # This would mean there's only a number
            return self.factors[0]
        else:
            
            # Indexing variable
            i = 0
            
            # Initialize the string we'd want to return, starting with the
            # numbers - if 1 is a factor and there are others, exclude it
            if self.factors[0] == 1:
                i += 1  # Skip the 1
            
            # Loop through all factors forming them into a nice string
            for fact in self.factors[i:]:
                return_str += ('(' + fact + ')')
            
            return return_str
    
    # Use the above syntax to denote an addition and subtraction of scalars
    def __add__(self, other):  # TODO: generalize once functions are more clear
        return Scalar([(self.get_vals(), other.get_vals(), '+')])
    
    def __sub__(self, other):  # TODO: generalize here as above too
        return Scalar([(self.get_vals(), other.get_vals(), '-')])
    
    def __mul__(self, other):
        # Scalars can be multiplied by other scalars or functions
        
        # Handle the various cases of multiplying with a scalar
        if isinstance(other, int) or isinstance(other, str):
            return Scalar(self.get_vals() + [other])
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
            
            return Scalar(self.get_vals() + [(1 / other)])
        elif isinstance(other, str):
            return Scalar(self.get_vals() + [('1/' + other)])
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
        
        # Simplify first
        self.simplify()
        
        # Initialize the string
        repr_str = ''
        
        # Format the string nicely
        for factor in self.factors:
            repr_str += str(factor) + ' * '

        # Remove the pesky 1 at the front
        if repr_str[:3] == '1 *':
            repr_str = repr_str[4:]
        
        # But add the one back if the string is then just empty
        if repr_str == '':
            repr_str += '1'
        
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


class Function:
    def __init__(self, functions=(None, None), scalar=Scalar([1]), op=None):
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
    
    def __mul__(self, other):
        # We can multiply functions by scalars or other functions
        if isinstance(other, Scalar):
            return other * self  # Refer to scalar multiplication - it's easier
        elif isinstance(other, Function):
            return Function((self, other), self.function['scalar'] *
                            other.function['scalar'], '*')
        elif isinstance(other, int) or isinstance(other, str):
            return Scalar([other]) * self
        else:
            raise ValueError('Multiplication by invalid object')
    
    def get_funcs(self):
        return self.function['funcs']
    
    def get_scalar(self):
        return self.function['scalar']
    
    def get_op(self):
        return self.function['operator']


# Define the universal base function for an arbitrary variable
class Base(Function):
    def __init__(self, scalar=Scalar([1]), variable='x'):
        # Note one of the defining characteristics of the universal
        # base function is the fact that its sole function is just the
        # variable itself with a scalar
        super().__init__((variable, variable), scalar, 'o')
    
    def diff(self):
        
        # Classic derivative
        return self.function['scalar']


# The class for raising an expression to a power
class Pow(Function):
    def __init__(self):
        pass  # TODO