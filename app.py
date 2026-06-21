# Author: RajarshiB  AI-Assistant: Claude
#
# app.py
# ------
# Main Streamlit application entry point for the Modular Dynamical System Visualizer.
# Wires together the parser, integrator, and visualizer modules.
#
# UI Layout:
#   Sidebar:
#     - Dimension selectbox (1D / 2D / 3D / 4D)
#     - Per-variable initial condition number inputs
#     - t_max slider and dt selectbox
#     - Dynamic parameter sliders (generated after first solve)
#   Main area:
#     - Per-variable equation text inputs
#     - "Solve" button
#     - Error / warning display
#     - Plotly charts via st.plotly_chart

import streamlit as st
import numpy as np

from config import (
    DIMENSIONS, STATE_VARS, DEFAULT_EQUATIONS, DEFAULT_ICS,
    DEFAULT_TMAX, DEFAULT_DT, AVAILABLE_DT,
    SYSTEM_PARAM_DEFAULTS, SYSTEM_SLIDER_RANGES,
    STROGATZ_EXAMPLES,
)
from core.parser import parse_equations, compile_functions
from core.integrator import solve_system
from core.visualizer import plot_1d, plot_2d, plot_3d, plot_4d

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Dynamical System Visualizer",
    page_icon="🌀",
    layout="wide",
)
st.title("Dynamical System Visualizer")

# ── Session state helpers ─────────────────────────────────────────────────────

def _auto_slider_range(val: float) -> tuple[float, float]:
    """Return a (min, max) that comfortably spans the given parameter value."""
    abs_v = max(abs(val), 1.0)
    lo = round(val - 3.0 * abs_v, 2)
    hi = round(val + 3.0 * abs_v, 2)
    return (lo, hi)


def _init_state() -> None:
    defaults = {
        'last_dim': None,
        'parsed_eqs': None,
        'compiled_funcs': None,
        'param_names': [],
        'solution_data': None,
        'active_example': None,
        'strogatz_value': None,  # set to _EXAMPLE_NONE after constants are defined
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_for_dim(dim: str) -> None:
    """Seed session state with defaults for the newly selected dimension."""
    for var, eq in DEFAULT_EQUATIONS[dim].items():
        st.session_state[f'eq_{var}'] = eq
        # Also reset the widget key so the text_input reflects the new equation.
        # Without this, shared widget keys (ti_x, ti_y) retain values from the
        # previous dimension when switching (e.g. 2D Lotka-Volterra → 3D Lorenz).
        st.session_state[f'ti_{var}'] = eq
    for var, ic in DEFAULT_ICS[dim].items():
        st.session_state[f'ic_{var}'] = ic
        # Same fix for number_input widget keys.
        st.session_state[f'ni_{var}'] = ic
    for p, (mn, mx, dflt, _) in SYSTEM_SLIDER_RANGES.get(dim, {}).items():
        st.session_state[f'param_{p}'] = dflt
        st.session_state[f'sl_{p}'] = dflt
        # Reset range backing keys AND their widget keys so the min/max inputs
        # reflect the new dimension's intended ranges on next render.
        st.session_state[f'rng_min_{p}'] = mn
        st.session_state[f'rng_max_{p}'] = mx
        st.session_state[f'ni_rng_min_{p}'] = mn
        st.session_state[f'ni_rng_max_{p}'] = mx
    st.session_state['parsed_eqs'] = None
    st.session_state['compiled_funcs'] = None
    st.session_state['solution_data'] = None
    st.session_state['param_names'] = []
    st.session_state['last_dim'] = dim


_init_state()

# ── Sidebar: dimension selector ───────────────────────────────────────────────

_EXAMPLE_NONE = "— Custom / Blank —"
_EXAMPLE_NAMES: list[str] = [_EXAMPLE_NONE] + list(STROGATZ_EXAMPLES.keys())

with st.sidebar:
    st.header("System Setup")

    # ── Strogatz library picker ───────────────────────────────────────────────
    # Use a plain backing key (not a widget key) so it can be modified at any
    # point in the script — Streamlit forbids modifying a widget's own key after
    # the widget has already rendered in the current run.
    if 'strogatz_value' not in st.session_state:
        st.session_state['strogatz_value'] = _EXAMPLE_NONE

    _strogatz_idx: int = (
        _EXAMPLE_NAMES.index(st.session_state['strogatz_value'])
        if st.session_state['strogatz_value'] in _EXAMPLE_NAMES else 0
    )
    selected_example: str = st.selectbox(
        "📖 Strogatz Example",
        _EXAMPLE_NAMES,
        index=_strogatz_idx,
    )
    # Keep backing key in sync with whatever the widget currently shows.
    st.session_state['strogatz_value'] = selected_example

    if selected_example != _EXAMPLE_NONE:
        if st.session_state.get('active_example') != selected_example:
            ex = STROGATZ_EXAMPLES[selected_example]
            new_dim: str = ex['dim']
            _reset_for_dim(new_dim)
            for var, eq in ex['equations'].items():
                st.session_state[f'eq_{var}'] = eq
                st.session_state[f'ti_{var}'] = eq
            for var, ic in ex['ics'].items():
                st.session_state[f'ic_{var}'] = float(ic)
                st.session_state[f'ni_{var}'] = float(ic)
            for p, val in ex['params'].items():
                fval = float(val)
                st.session_state[f'param_{p}'] = fval
                st.session_state[f'sl_{p}'] = fval
                # Auto-compute a range that covers the example's param value
                # (including negative values like a=-1 in Romeo & Juliet).
                mn_auto, mx_auto = _auto_slider_range(fval)
                st.session_state[f'rng_min_{p}'] = mn_auto
                st.session_state[f'rng_max_{p}'] = mx_auto
                st.session_state[f'ni_rng_min_{p}'] = mn_auto
                st.session_state[f'ni_rng_max_{p}'] = mx_auto
            st.session_state[f't_max_{new_dim}'] = ex['t_max']
            st.session_state[f'dt_{new_dim}'] = ex['dt']
            st.session_state['active_example'] = selected_example
            st.session_state['dim_select'] = new_dim
            st.rerun()
    else:
        st.session_state['active_example'] = None

    # ── Dimension selector ────────────────────────────────────────────────────
    if 'dim_select' not in st.session_state:
        st.session_state['dim_select'] = '2D'

    dim: str = st.selectbox(
        "Dimension",
        DIMENSIONS,
        key='dim_select',
    )

    if st.session_state['last_dim'] != dim:
        _reset_for_dim(dim)
        # User manually changed dimension — clear the Strogatz selection.
        # Safe to modify 'strogatz_value' here because it is not a widget key.
        if st.session_state.get('active_example') is not None:
            st.session_state['strogatz_value'] = _EXAMPLE_NONE
            st.session_state['active_example'] = None
            st.rerun()

    state_vars: list[str] = STATE_VARS[dim]

    st.subheader("Initial Conditions")
    for var in state_vars:
        ic_key = f'ic_{var}'
        if ic_key not in st.session_state:
            st.session_state[ic_key] = DEFAULT_ICS[dim][var]
        st.session_state[ic_key] = st.number_input(
            f"{var}₀",
            value=float(st.session_state[ic_key]),
            step=0.1,
            format="%.4f",
            key=f'ni_{var}',
        )

    st.subheader("Integration Settings")
    t_max_key = f't_max_{dim}'
    if t_max_key not in st.session_state:
        st.session_state[t_max_key] = DEFAULT_TMAX[dim]
    t_max: float = st.slider(
        "t_max",
        min_value=1.0,
        max_value=1000.0,
        value=float(st.session_state[t_max_key]),
        step=1.0,
        key=t_max_key,
    )

    dt_key = f'dt_{dim}'
    if dt_key not in st.session_state:
        st.session_state[dt_key] = DEFAULT_DT[dim]
    dt_default = st.session_state[dt_key]
    dt_idx = AVAILABLE_DT.index(dt_default) if dt_default in AVAILABLE_DT else 4
    dt: float = st.selectbox(
        "Time step (dt)",
        AVAILABLE_DT,
        index=dt_idx,
        key=dt_key,
        format_func=lambda x: str(x),
    )

    # Dynamic parameter sliders — rendered after first successful solve
    param_names: list[str] = st.session_state['param_names']
    if param_names:
        st.subheader("Parameters")
        slider_ranges = SYSTEM_SLIDER_RANGES.get(dim, {})
        fallback = (0.0, 10.0, 1.0, 0.1)
        for p in param_names:
            p_key   = f'param_{p}'
            mn_key  = f'rng_min_{p}'
            mx_key  = f'rng_max_{p}'
            _, _, dflt, base_step = slider_ranges.get(p, fallback)

            # Initialise range keys if not already set (custom equation path)
            if mn_key not in st.session_state:
                st.session_state[mn_key] = slider_ranges.get(p, fallback)[0]
            if mx_key not in st.session_state:
                st.session_state[mx_key] = slider_ranges.get(p, fallback)[1]
            if p_key not in st.session_state:
                st.session_state[p_key] = dflt

            # Editable range row: [param name] [min input] [max input]
            lbl_c, mn_c, mx_c = st.columns([1.2, 1, 1])
            with lbl_c:
                st.markdown(f"**{p}**")
            with mn_c:
                new_mn: float = st.number_input(
                    "min", value=float(st.session_state[mn_key]),
                    key=f'ni_rng_min_{p}', step=0.1, format="%.2f",
                )
                st.session_state[mn_key] = new_mn
            with mx_c:
                new_mx: float = st.number_input(
                    "max", value=float(st.session_state[mx_key]),
                    key=f'ni_rng_max_{p}', step=0.1, format="%.2f",
                )
                st.session_state[mx_key] = new_mx

            # Guard: ensure range is valid before passing to slider
            if new_mx <= new_mn:
                new_mx = new_mn + 0.1

            # Compute a step that always fits inside the (possibly user-modified) range
            safe_step = max(min(float(base_step), (new_mx - new_mn) / 2.0), 1e-4)
            current_val = float(np.clip(st.session_state.get(p_key, dflt), new_mn, new_mx))

            st.session_state[p_key] = st.slider(
                p,
                min_value=float(new_mn),
                max_value=float(new_mx),
                value=current_val,
                step=safe_step,
                key=f'sl_{p}',
                label_visibility="collapsed",
            )

# ── Main area: equation inputs + solve button ─────────────────────────────────

# ── Strogatz significance blurb ───────────────────────────────────────────────
active_ex = st.session_state.get('active_example')
if active_ex and active_ex in STROGATZ_EXAMPLES:
    st.info(f"**{active_ex}** — {STROGATZ_EXAMPLES[active_ex]['significance']}")

st.subheader("Equations")
eq_cols = st.columns(max(len(state_vars), 1))
eq_dict: dict[str, str] = {}
for i, var in enumerate(state_vars):
    eq_key = f'eq_{var}'
    if eq_key not in st.session_state:
        st.session_state[eq_key] = DEFAULT_EQUATIONS[dim][var]
    with eq_cols[i]:
        eq_dict[var] = st.text_input(
            f"d{var}/dt =",
            value=st.session_state[eq_key],
            key=f'ti_{var}',
        )
        st.session_state[eq_key] = eq_dict[var]

solve_clicked = st.button("▶ Solve", type="primary", use_container_width=False)

# ── Parse + compile on Solve click ───────────────────────────────────────────

if solve_clicked:
    if dt >= t_max:
        st.warning("dt must be smaller than t_max.")
        st.stop()

    try:
        parsed_eqs, param_names_new = parse_equations(eq_dict, state_vars)
        compiled = compile_functions(parsed_eqs, state_vars, param_names_new)
        st.session_state['parsed_eqs'] = parsed_eqs
        st.session_state['compiled_funcs'] = compiled
        st.session_state['param_names'] = param_names_new
        # Seed any new params not yet in session state
        slider_ranges = SYSTEM_SLIDER_RANGES.get(dim, {})
        for p in param_names_new:
            p_key = f'param_{p}'
            if p_key not in st.session_state:
                _, _, dflt, _ = slider_ranges.get(p, (0.0, 10.0, 1.0, 0.1))
                st.session_state[p_key] = dflt
        st.rerun()
    except Exception as exc:
        st.error(f"Equation parse error: {exc}")
        st.stop()

# ── Re-integrate on every rerun when compiled funcs exist ─────────────────────

compiled_funcs = st.session_state.get('compiled_funcs')
param_names = st.session_state['param_names']

if compiled_funcs is not None:
    initial_conditions = {var: float(st.session_state[f'ic_{var}']) for var in state_vars}
    param_values = {p: float(st.session_state.get(f'param_{p}', 1.0)) for p in param_names}

    if dt >= t_max:
        st.warning("dt must be smaller than t_max.")
    else:
        try:
            data = solve_system(
                compiled_funcs=compiled_funcs,
                state_vars=state_vars,
                param_vars=param_names,
                initial_conditions=initial_conditions,
                param_values=param_values,
                t_max=t_max,
                dt=dt,
            )
            st.session_state['solution_data'] = data
        except RuntimeError as exc:
            st.error(f"Integration error: {exc}")
            st.session_state['solution_data'] = None
        except Exception as exc:
            st.error(f"Unexpected error during integration: {exc}")
            st.session_state['solution_data'] = None

# ── Render plots ──────────────────────────────────────────────────────────────

solution_data = st.session_state.get('solution_data')

if solution_data is not None:
    st.divider()
    st.subheader("Phase Space Visualization")

    if dim == "1D":
        fig_ts, fig_pl = plot_1d(
            data=solution_data,
            compiled_funcs=compiled_funcs,
            state_vars=state_vars,
            param_vars=param_names,
            param_values=param_values,
        )
        # uirevision=dim preserves zoom/pan when slider values change;
        # the view resets only when the user switches to a different dimension.
        fig_ts.update_layout(uirevision=dim)
        fig_pl.update_layout(uirevision=dim)
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(fig_ts, use_container_width=True)
        with col_b:
            st.plotly_chart(fig_pl, use_container_width=True)

    elif dim == "2D":
        fig = plot_2d(solution_data)
        fig.update_layout(uirevision=dim)
        st.plotly_chart(fig, use_container_width=True)

    elif dim == "3D":
        fig = plot_3d(solution_data)
        fig.update_layout(uirevision=dim)
        st.plotly_chart(fig, use_container_width=True)

    elif dim == "4D":
        color_var = st.selectbox(
            "Color 4th variable by:",
            options=state_vars,
            index=state_vars.index('w') if 'w' in state_vars else len(state_vars) - 1,
        )
        fig = plot_4d(solution_data, color_var=color_var)
        fig.update_layout(uirevision=dim)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.get('compiled_funcs') is None:
    st.info("Enter your equations above and click **▶ Solve** to visualize the system.")
