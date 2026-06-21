# Author: RajarshiB  AI-Assistant: Claude
#
# core/parser.py
# --------------
# Symbolic equation parsing and compilation using SymPy.
#
# Functions:
#   _build_local_dict(state_vars)
#       Builds a local_dict for parse_expr that pre-declares state vars, time,
#       and ~40 common parameter names as Symbol objects, preventing SymPy from
#       interpreting names like 'beta', 'gamma', 'sigma' as built-in functions.
#
#   parse_equations(eq_dict, state_vars) -> tuple[dict[str, Expr], list[str]]
#       Parses each ODE string via parse_expr with local_dict.
#       Returns (parsed_expr_dict, sorted_param_name_list).
#       Raises SympifyError / ValueError on parse failure.
#
#   compile_functions(parsed_eqs, state_vars, param_vars) -> dict[str, Callable]
#       Lambdifies each expression with fixed arg order [*state_vars, *param_vars].
#       All compiled functions share the same calling signature.

from typing import Any
from collections.abc import Callable
from sympy import Symbol, Expr
from sympy.parsing.sympy_parser import parse_expr
from sympy import lambdify

_COMMON_PARAM_NAMES: list[str] = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'k', 'm', 'n',
    'p', 'q', 'r', 's', 'u', 'v',
    'A', 'B', 'C', 'D', 'K', 'L', 'M', 'N', 'R', 'S',
    'alpha', 'beta', 'gamma', 'delta', 'sigma', 'rho', 'omega',
    'mu', 'nu', 'lambda_', 'epsilon', 'eta', 'theta',
    'kappa', 'tau', 'phi', 'psi', 'xi',
]


def _build_local_dict(state_vars: list[str]) -> dict[str, Symbol]:
    local: dict[str, Symbol] = {}
    for name in state_vars + ['t'] + _COMMON_PARAM_NAMES:
        local[name] = Symbol(name)
    return local


def parse_equations(
    eq_dict: dict[str, str],
    state_vars: list[str],
) -> tuple[dict[str, Expr], list[str]]:
    local_dict = _build_local_dict(state_vars)
    state_symbols: set[Symbol] = {local_dict[v] for v in state_vars}
    t_symbol: Symbol = local_dict['t']

    parsed: dict[str, Expr] = {}
    all_free: set[Symbol] = set()

    for var, eq_str in eq_dict.items():
        expr: Expr = parse_expr(eq_str.strip(), local_dict=local_dict)
        parsed[var] = expr
        all_free |= expr.free_symbols

    param_symbols = all_free - state_symbols - {t_symbol}
    param_names = sorted(str(s) for s in param_symbols)
    return parsed, param_names


def compile_functions(
    parsed_eqs: dict[str, Expr],
    state_vars: list[str],
    param_vars: list[str],
) -> dict[str, Callable[..., Any]]:
    local_dict = _build_local_dict(state_vars + param_vars)
    arg_symbols = [local_dict[v] for v in state_vars + param_vars]

    compiled: dict[str, Callable[..., Any]] = {}
    for var, expr in parsed_eqs.items():
        compiled[var] = lambdify(arg_symbols, expr, modules='numpy')
    return compiled
