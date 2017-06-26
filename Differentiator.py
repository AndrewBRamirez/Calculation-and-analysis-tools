# This document represents functions in a way that allows them to be easily
# differentiated. The methods and rules for differentiation, among other
# things, are included in this file. This file attempts to keep the
# process completely general, and ideally allow for partial differentiation
# of a scalar function for an arbitrary number of variables. Note this code
# was created with Python 3.x

# TODO: add multi-variable functionality
# TODO: add a derivative library to lessen the load of recursive differentiation
# TODO: add good documentation to everything, not just sparse comments
# Any and all necessary import statements
import re

# Global variable(s)
deriv_lib = dict()

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
        nums = 1.0
    
        # Also keep track of all expressions encountered
        exprs = []
        
        # Loop through all factors
        for fact in self.factors:
            
            # Just multiply all numbers
            if isinstance(fact, int) or isinstance(fact, float):
                nums *= fact
            
            # Handle variables and expressions
            elif isinstance(fact, str):
    
                # Do a quick check for just numbers combined in a term
                if re.search('[a-zA-Z]', fact) is None:
                    
                    # No letters/vars, so we can just eval the numbers
                    nums *= eval(fact)
                    continue  # And we're done with this factor
                
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
        if len(self.factors) == 1:  # This would mean there's only a number
            return self.factors[0]
        else:
            
            # Indexing variable
            i = 0
            
            # Initialize the string we'd want to return, starting with the
            # numbers - if 1 is a factor and there are others, exclude it
            if self.factors[0] == 1.0:
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
        if isinstance(other, int):
            return Scalar(self.get_vals() + [float(other)])
        elif isinstance(other, str) or isinstance(other, float):
            return Scalar(self.get_vals() + [other])
        elif isinstance(other, Function):
            return Function(other.get_funcs(), Scalar(
                other.get_scalar().get_vals() + self.factors), other.get_op())
        elif isinstance(other, Scalar):
            
            # If 0 is a factor for either, it results in a 0 scalar
            if 0.0 in self.get_vals() or 0.0 in other.get_vals():
                return Scalar([0.0])
            
            return Scalar(self.get_vals() + other.get_vals())
        else:
            raise ValueError('Multiplication by invalid object')
    
    def __truediv__(self, other):
        # Scalars can be divided by other scalars or functions
        
        # Handle the various cases of dividing with a scalar
        if isinstance(other, int) or isinstance(other, float):
            
            # No dividing by zero
            if float(other) == 0.0:
                raise ValueError('Divide by zero error')
            
            return Scalar(self.get_vals() + [(1 / other)])
        elif isinstance(other, str):
            return Scalar(self.get_vals() + [('1/' + other)])
        elif isinstance(other, Function):
            pass  # TODO once function inverse defined
        elif isinstance(other, Scalar):
            
            # If 0 is a factor in self, it results in a 0 scalar
            if 0.0 in self.get_vals() and 0.0 not in other.get_vals():
                return Scalar([0.0])
            elif 0.0 in other.get_vals() and 0.0 not in self.get_vals():
                raise ValueError('Divide by zero error')
            elif 0.0 in self.get_vals() and 0.0 in other.get_vals():  # Both 0
                raise ValueError('Indeterminate form: 0/0')

            return self * other.invert()  # Easier reroute for division
        else:
            raise ValueError('Division by invalid object')
    
    def invert(self):
        
        # Begin with a simplification to make things easy
        self.simplify()
        
        # Initialize a new factor list
        new_lst = []
        
        # Loop through all factors and invert them
        for fact in self.factors:
            
            # Just invert an actual number
            if isinstance(fact, int) or isinstance(fact, float):
                new_lst.append(1 / fact)
            elif isinstance(fact, str):
                # Check the length before checking for an inversion this way
                if len(fact) >= 3:  # Could start with '1/' or '1 /'
        
                    # Now actually check for the beginning of an inversion
                    if fact[:2] == '1/' or fact[:3] == '1 /':

                        # Check only after the division symbol, removing
                        # excess white space
                        term = fact[fact.index('/') + 1:].strip()
                        
                        new_lst.append(term)
                    else:  # No inversion, so we must now just invert the term
                        new_lst.append('1/' + fact)
                else:  # Can't be an inverted expression, so just invert
                    new_lst.append('1/' + fact)
            else:  # As with simplify(), this is mostly for debugging purposes
                raise ValueError('Unexpected input type: %s' % type(fact))
        return Scalar(new_lst)
                
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
            return '1'
        
        return repr_str[:-3]
    
    # Get the value of the scalar, aka its factor list
    def get_vals(self):
        return self.factors
    
    # Differentiation, made static since it's the same for all instances
    @staticmethod
    def diff():  # Another classic, simple differentiation
        return Scalar([0.0])


class Function:
    def __init__(self, functions=(None, None), scalar=Scalar([1]), op=None):
        """
        :param functions: the two comprising functions in a tuple.
        The functions themselves are usually Function objects. The only
        exceptions to this are the universal base function, which uses strings
        representing a variable, and scalars, which don't have functions but
        rather just factors.
        :param scalar: a scalar in the real numbers by which to multiply the
        function. This produces dilation for functions
        :param op: operation joining the functions, which can be one of
        addition, subtraction, multiplication, division, or composition. Takes
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
        self.funcs = functions
        self.scalar = scalar
        self.operator = op
        
        # TODO: add simplification for user giving simple and simplifiable
        # functions like Base() o Base() --> 2 * Base()
    
    def __repr__(self):
        
        # Initialize the string to return
        repr_str = ''
        
        # Save the functions for easier notation
        func1 = self.funcs[0]
        func2 = self.funcs[1]
        
        # Recursive definition is the most intuitive way to represent it
        repr_str += func1.__repr__() + (' %s ' % operator) + func2.__repr__()
        
        # Note that the base cases for this recursion are the universal base
        # function and scalars
        
        return repr_str
    
    # TODO: add simplify function for added terms with same factors
    def __add__(self, other):
        # We can add functions to scalars or other functions
        if isinstance(other, float) or isinstance(other, int) or \
                isinstance(other, str):
            return Function((self.funcs, Scalar([other])), Scalar([1]), '+')
        elif isinstance(other, Scalar):
            return Function((self.funcs, other), Scalar([1]), '+')
        elif isinstance(other, Function):
            return Function((self, other), Scalar([1]), '+')
        else:
            raise ValueError('Addition with invalid object')
    
    def __sub__(self, other):
        # We can subtract scalars or other functions from functions
        if isinstance(other, float) or isinstance(other, int) or \
                isinstance(other, str):
            return Function((self.funcs, Scalar([other])), Scalar([1]), '-')
        elif isinstance(other, Scalar):
            return Function((self.funcs, other), Scalar([1]), '-')
        elif isinstance(other, Function):
            return Function((self, other), Scalar([1]), '-')
        else:
            raise ValueError('Addition with invalid object')
    
    def __mul__(self, other):
        # We can multiply functions by scalars or other functions
        if isinstance(other, Scalar):
            return other * self  # Refer to scalar multiplication - it's easier
        elif isinstance(other, Function):
            return Function((self, other), self.scalar * other.scalar, '*')
        elif isinstance(other, str) or isinstance(other, float):
            return Scalar([other]) * self
        elif isinstance(other, int):
            return Scalar([float(other)]) * self
        else:
            raise ValueError('Multiplication by invalid object')
    
    def __truediv__(self, other):
        # We can divide functions by scalars or other functions
        if isinstance(other, Scalar) or isinstance(other, float) or \
                isinstance(other, int) or isinstance(other, str):
            return Function(self.funcs, self.scalar / other,
                            self.operator)
        elif isinstance(other, Function):
            return Function((self, other), self.scalar / other.scalar, '/')
        else:
            raise ValueError('Multiplication by invalid object')
    
    def get_funcs(self):
        return self.funcs
    
    def get_scalar(self):
        return self.scalar
    
    def get_op(self):
        return self.operator


# Define the universal base function for an arbitrary variable
class Base(Function):
    def __init__(self, scalar=Scalar([1]), variable='x'):
        # Note one of the defining characteristics of the universal
        # base function is the fact that its sole function is just the
        # variable itself with a scalar
        super().__init__((variable, variable), scalar, 'o')
        self.variable = variable
    
    def __repr__(self):
        
        # Get the scalar's repr string
        scalar_repr = self.scalar.__repr__()
        
        # Simplify the representation by leaving out a leading 1
        if scalar_repr == '1.0':
            return self.variable
        return scalar_repr + self.variable
    
    def __mul__(self, other):
        
        if isinstance(other, Scalar) or isinstance(other, int) or isinstance(
              other, float) or isinstance(other, str):
            return Base(self.scalar * other, self.variable)
        elif isinstance(other, Function):
            return other * self  # Point to function definition of mul instead
        else:
            raise ValueError('Unexpected type for multiplication: %s' %
                             type(other))
    
    def diff(self):
        
        # Classic derivative
        return self.scalar


# The class for raising an expression to a power
class Pow(Function):
    def __init__(self):
        pass  # TODO