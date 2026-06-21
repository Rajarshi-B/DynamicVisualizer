# Author: RajarshiB  AI-Assistant: Claude
#
# config.py
# ---------
# Constants for the Dynamical System Visualizer.
#
# Contents:
#   DIMENSIONS          : available dimension labels
#   STATE_VARS          : maps dimension label to its state variable list
#   DEFAULT_EQUATIONS   : default ODE strings per dimension
#   SYSTEM_SLIDER_RANGES: per-dimension slider (min, max, default, step) for each param
#   SYSTEM_PARAM_DEFAULTS: per-dimension default param values (subset used for seeding)
#   DEFAULT_ICS         : per-dimension initial conditions
#   DEFAULT_TMAX        : per-dimension integration end time
#   DEFAULT_DT          : per-dimension time step

from typing import Final

DIMENSIONS: Final[list[str]] = ["1D", "2D", "3D", "4D"]

STATE_VARS: Final[dict[str, list[str]]] = {
    "1D": ["x"],
    "2D": ["x", "y"],
    "3D": ["x", "y", "z"],
    "4D": ["x", "y", "z", "w"],
}

DEFAULT_EQUATIONS: Final[dict[str, dict[str, str]]] = {
    "1D": {
        "x": "r*x*(1 - x/k)",
    },
    "2D": {
        "x": "a*x - b*x*y",
        "y": "-c*y + d*x*y",
    },
    "3D": {
        "x": "s*(y - x)",
        "y": "x*(r - z) - y",
        "z": "x*y - b*z",
    },
    "4D": {
        # Modified Lorenz 4D: stable, bounded; w feeds into x and is driven by x.
        # Rössler hyperchaos avoided — its dz/dt = c + x*z diverges when x > 0.
        "x": "s*(y - x) + w",
        "y": "r*x - y - x*z",
        "z": "x*y - b*z",
        "w": "c*x - d*w",
    },
}

# Per-dimension slider config: param -> (min, max, default, step)
# Keeps per-system ranges separate so same letter (e.g. 'b') can differ across systems.
SYSTEM_SLIDER_RANGES: Final[dict[str, dict[str, tuple[float, float, float, float]]]] = {
    "1D": {
        "r": (0.1,  5.0,   2.0,   0.1),
        "k": (1.0,  20.0,  10.0,  0.5),
    },
    "2D": {
        "a": (0.1,  3.0,   1.0,   0.05),
        "b": (0.01, 1.0,   0.1,   0.01),
        "c": (0.1,  3.0,   1.5,   0.05),
        "d": (0.01, 0.5,   0.075, 0.005),
    },
    "3D": {
        "s": (1.0,  20.0,  10.0,  0.5),
        "r": (0.0,  50.0,  28.0,  0.5),
        "b": (0.1,  5.0,   2.667, 0.1),
    },
    "4D": {
        "s": (1.0,  20.0,  10.0,  0.5),
        "r": (0.0,  50.0,  28.0,  0.5),
        "b": (0.1,  5.0,   2.667, 0.1),
        "c": (0.0,  5.0,   2.0,   0.1),
        "d": (0.1,  5.0,   1.0,   0.1),
    },
}

# Default param values per system (mirrors the 'default' field above, for convenience)
SYSTEM_PARAM_DEFAULTS: Final[dict[str, dict[str, float]]] = {
    dim: {p: v[2] for p, v in ranges.items()}
    for dim, ranges in SYSTEM_SLIDER_RANGES.items()
}

DEFAULT_ICS: Final[dict[str, dict[str, float]]] = {
    "1D": {"x": 0.5},
    "2D": {"x": 10.0, "y": 5.0},
    "3D": {"x": 1.0,  "y": 1.0,  "z": 1.0},
    "4D": {"x": 1.0,  "y": 1.0,  "z": 1.0, "w": 1.0},
}

DEFAULT_TMAX: Final[dict[str, float]] = {
    "1D": 15.0,
    "2D": 50.0,
    "3D": 50.0,
    "4D": 100.0,
}

DEFAULT_DT: Final[dict[str, float]] = {
    "1D": 0.05,
    "2D": 0.1,
    "3D": 0.01,
    "4D": 0.01,
}

AVAILABLE_DT: Final[list[float]] = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]

# ── Strogatz Examples Library ─────────────────────────────────────────────────
# Each entry: dim, equations (SymPy-safe strings), params, ics, t_max, dt,
#             significance (display text from Strogatz Ch. references).

STROGATZ_EXAMPLES: Final[dict[str, dict]] = {
    "Logistic Equation": {
        "dim": "1D",
        "equations": {"x": "r*x*(1 - x/K)"},
        "params": {"r": 1.0, "K": 10.0},
        "ics": {"x": 0.1},
        "t_max": 15.0,
        "dt": 0.05,
        "significance": (
            "The starting point for nonlinear dynamics. It introduces 'fixed points' "
            "and 'linear stability analysis,' demonstrating how an environment's carrying "
            "capacity forces a population to plateau."
        ),
    },
    "Spruce Budworm Outbreak": {
        "dim": "1D",
        "equations": {"x": "r*x*(1 - x/K) - x**2/(1 + x**2)"},
        "params": {"r": 0.5, "K": 10.0},
        "ics": {"x": 0.5},
        "t_max": 50.0,
        "dt": 0.05,
        "significance": (
            "This ecological model introduces Hysteresis and the Saddle-Node Bifurcation. "
            "It explains sudden catastrophic jumps in nature, showing why an insect population "
            "can remain manageable for years and then suddenly explode."
        ),
    },
    "Romeo and Juliet": {
        "dim": "2D",
        "equations": {"x": "a*x + b*y", "y": "c*x + d*y"},
        "params": {"a": -1.0, "b": 1.0, "c": 1.0, "d": -1.0},
        "ics": {"x": 1.0, "y": 1.0},
        "t_max": 20.0,
        "dt": 0.05,
        "significance": (
            "A highly memorable linear system used to teach Eigenvalues and Matrix "
            "Trace/Determinants. By modeling love/hate dynamics as harmonic oscillators, "
            "it makes the classification of 2D fixed points intuitive."
        ),
    },
    "Lotka-Volterra Predator-Prey": {
        "dim": "2D",
        "equations": {"x": "a*x - b*x*y", "y": "c*x*y - d*y"},
        "params": {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0},
        "ics": {"x": 2.0, "y": 1.0},
        "t_max": 30.0,
        "dt": 0.05,
        "significance": (
            "Used to teach a cautionary tale about Structural Instability. The model "
            "produces perfect infinite rings of oscillations, but it is a fragile "
            "mathematical artifact destroyed by any slight change to the equations."
        ),
    },
    "Van der Pol Oscillator": {
        "dim": "2D",
        "equations": {"x": "y", "y": "mu*(1 - x**2)*y - x"},
        "params": {"mu": 1.5},
        "ics": {"x": 1.0, "y": 1.0},
        "t_max": 40.0,
        "dt": 0.05,
        "significance": (
            "Originally modeling vacuum tubes, this is the champion for Limit Cycles and "
            "Relaxation Oscillations. It shows 'nonlinear damping'—adding energy when "
            "oscillation is small and bleeding it when large, creating a robust rhythmic heartbeat."
        ),
    },
    "Lorenz Attractor": {
        "dim": "3D",
        "equations": {
            "x": "sigma*(y - x)",
            "y": "x*(rho - z) - y",
            "z": "x*y - beta*z",
        },
        "params": {"sigma": 10.0, "rho": 28.0, "beta": 2.667},
        "ics": {"x": 0.0, "y": 1.0, "z": 1.05},
        "t_max": 50.0,
        "dt": 0.01,
        "significance": (
            "The centerpiece of chaos theory. It demonstrates Sensitive Dependence on "
            "Initial Conditions (The Butterfly Effect) and Strange Attractors, showing how "
            "deterministic systems can produce entirely unpredictable, fractal trajectories."
        ),
    },
    "Rössler Attractor": {
        "dim": "3D",
        "equations": {
            "x": "-y - z",
            "y": "x + a*y",
            "z": "b + z*(x - c)",
        },
        "params": {"a": 0.2, "b": 0.2, "c": 5.7},
        "ics": {"x": 1.0, "y": 1.0, "z": 1.0},
        "t_max": 80.0,
        "dt": 0.02,
        "significance": (
            "An artificially constructed chaotic system designed to be the simplest equations "
            "yielding a strange attractor. It clearly visualizes the 'Stretch and Fold' "
            "topological mechanism of chaos."
        ),
    },
}
