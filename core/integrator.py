# Author: RajarshiB  AI-Assistant: Claude
#
# core/integrator.py
# ------------------
# Numerical ODE integration using SciPy solve_ivp (RK45).
#
# Functions:
#   solve_system(compiled_funcs, state_vars, param_vars, initial_conditions,
#                param_values, t_max, dt) -> dict[str, np.ndarray]
#       Builds a vector_field closure compatible with solve_ivp, executes RK45
#       integration, and returns a dict mapping variable names to solution arrays.
#       Raises RuntimeError if solve_ivp reports failure or exceeds TIMEOUT seconds.

import numpy as np
from collections.abc import Callable
from typing import Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout
from scipy.integrate import solve_ivp

TIMEOUT: float = 20.0


def solve_system(
    compiled_funcs: dict[str, Callable[..., Any]],
    state_vars: list[str],
    param_vars: list[str],
    initial_conditions: dict[str, float],
    param_values: dict[str, float],
    t_max: float,
    dt: float,
) -> dict[str, np.ndarray]:
    y0: list[float] = [initial_conditions[v] for v in state_vars]
    p_vals: list[float] = [param_values[p] for p in param_vars]

    def vector_field(t: float, state: np.ndarray) -> list[float]:
        args: list[Any] = list(state) + p_vals
        return [float(compiled_funcs[v](*args)) for v in state_vars]

    # Subtract half a step to avoid floating-point overshoot past t_span end
    t_eval: np.ndarray = np.arange(0.0, t_max - dt / 2.0, dt)

    def _run():
        return solve_ivp(
            vector_field,
            t_span=(0.0, t_max),
            y0=y0,
            method='RK45',
            t_eval=t_eval,
            dense_output=False,
            max_step=dt * 10,
        )

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run)
        try:
            sol = future.result(timeout=TIMEOUT)
        except _FuturesTimeout:
            raise RuntimeError(
                f"Integration timed out after {TIMEOUT:.0f}s. "
                "Try a larger dt or smaller t_max."
            )

    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")

    data: dict[str, np.ndarray] = {'t': sol.t}
    for i, v in enumerate(state_vars):
        data[v] = sol.y[i]
    return data
