from typing import Callable, Literal, NamedTuple, Optional, TypeVar, Dict, overload
from .sympy_helpers import to_basis
from sympy import Expr, sympify
from sympy.physics.units import UnitSystem, Quantity
from sympy.physics.units.util import convert_to
from sympy.physics.units.systems import SI
from functools import cache
from random import getrandbits
import sys

class QuantityMapper(NamedTuple):
    """
    For any given salt value and quantity, returns a number
    between 0.01 and 100. Uniformly distributed (hopefully) for
    the variable x in 10**x. This should just work for any other
    hashable quantity representation, but for now it's specific to
    sympy.
    """
    salt: Optional[int] = None

    @classmethod
    def random(cls):
        width = sys.hash_info.width
        return cls(getrandbits(width - 1) - getrandbits(width - 1))

    @classmethod
    def unitary(cls):
        return cls(None)
    
    @cache
    def map(self, quantity: Quantity) -> float:
        if self.salt is None:
            return 1
        zero_to_one = ((hash(quantity) ^
                        hash(quantity.dimension) ^
                        self.salt) / (
            2 ** sys.hash_info.width)) + 0.5
        return 10 ** (zero_to_one * 4 - 2)


T=TypeVar('T')
class NumericalBasis(NamedTuple):
    mapper: QuantityMapper
    proxy_system: UnitSystem

    @property
    def numeric_map(self) -> Dict[Quantity, float]:
        return {b: self.mapper.map(b) for b in self.proxy_system._base_units}

    @property
    def symb_basis(self):
        return self.proxy_system._base_units
    
    @overload
    def to_numeric(self, expr: Expr, *, type: Callable[[Expr], T]) -> T: ...
    
    @overload
    def to_numeric(self, expr: Expr, *, as_expr: Literal[True]) -> Expr: ...
    
    @overload
    def to_numeric(self, expr: Expr) -> float: ...
    
    def to_numeric(self, expr: Expr, **kwargs):
        type_ = kwargs.get('type', float)
        as_expr = kwargs.get('as_expr', False)
        symb = to_basis(self.proxy_system, expr
            ).xreplace(self.numeric_map)
        # workaround for dimentionless quantities, like radians, percent or degrees
        #symb = convert_to(symb, 1, self.proxy_system)
        return symb if as_expr else type_(symb)

    @overload
    def to_scalar(self, units_of: Expr, numeric, *, type: Callable[[Expr], T]) -> T: ...
    
    @overload
    def to_scalar(self, units_of: Expr, numeric, *, as_expr: Literal[True]) -> Expr: ...
    
    @overload
    def to_scalar(self, units_of: Expr, numeric) -> float: ...

    def to_scalar(self, units_of: Expr, numeric, **kwargs):
        type_ = kwargs.get('type', float)
        as_expr = kwargs.get('as_expr', False)
        factor = convert_to(units_of, self.symb_basis, self.proxy_system
            ).xreplace(self.numeric_map)
        symb = numeric / factor
        return symb if as_expr else type_(symb)

    def to_symb(self, units_of: Expr, numeric) -> Expr:
        return units_of * self.to_scalar(units_of, numeric, as_expr=True)

def basis(system=SI, unitary=False):
    return NumericalBasis(
        QuantityMapper.unitary() if unitary else QuantityMapper.random(), system)
