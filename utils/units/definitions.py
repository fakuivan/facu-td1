from sympy.physics.units import Quantity, newtons as N, ohm, V, Hz, second as s, farad
from sympy.physics.units.prefixes import micro, milli, kilo, nano
from .sympy_helpers import unit_relative_to, unit_with_prefix
from sympy import Rational as R, pi

uN = unit_with_prefix(micro, N)
mN = unit_with_prefix(milli, N)
mV = unit_with_prefix(milli, V)
kHz = unit_with_prefix(kilo, Hz)
rpm = unit_relative_to(Quantity("rpm"), R("1/60"), 1/s)
kohm = unit_with_prefix(kilo, ohm)
uF = unit_with_prefix(micro, farad)
nF = unit_with_prefix(nano, farad)

# I'm not sure how one would define or convert from angular frequency to
# pulsing frequency with sympy (it doesn't help that these units are not
# defined in the module).
# ``convert_to(2*pi*rad/seg, Hz)`` gives us ``2*pi*Hz`` instead of Hz, so it
# would seem like sympy has no notion of angular frequency vs pulsing
# frequency.
rps = unit_relative_to(Quantity(
    "radians_per_second", abbrev="rps", latex_repr="\\text{rad/s}"), 1/(2*pi), 1/s)
rpms = unit_relative_to(Quantity(
    "radians_per_millisecond", abbrev="rpms", latex_repr="\\text{rad/ms}"), kilo, rps)