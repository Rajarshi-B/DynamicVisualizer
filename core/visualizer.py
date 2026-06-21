# Author: RajarshiB  AI-Assistant: Claude
#
# core/visualizer.py
# ------------------
# Plotly figure generation for each system dimensionality.
#
# Functions:
#   plot_1d(data, compiled_funcs, state_vars, param_vars, param_values)
#       -> tuple[go.Figure, go.Figure]
#       Returns (time_series_fig, phase_line_fig).
#       Phase line shows dx/dt vs x with equilibrium point markers.
#
#   plot_2d(data) -> go.Figure
#       Returns a 2D phase portrait (x vs y) as go.Scatter lines.
#
#   plot_3d(data) -> go.Figure
#       Returns a 3D phase diagram (x, y, z) as go.Scatter3d lines.
#
#   plot_4d(data, color_var) -> go.Figure
#       Returns a 3D phase diagram (x, y, z) colored by the 4th variable
#       using the Viridis continuous colorscale.

import numpy as np
import plotly.graph_objects as go
from collections.abc import Callable
from typing import Any

_LAYOUT_DEFAULTS: dict = dict(
    template='plotly_dark',
    margin=dict(l=40, r=40, t=60, b=40),
)


def plot_1d(
    data: dict[str, np.ndarray],
    compiled_funcs: dict[str, Callable[..., Any]],
    state_vars: list[str],
    param_vars: list[str],
    param_values: dict[str, float],
) -> tuple[go.Figure, go.Figure]:
    t = data['t']
    x = data['x']

    fig_ts = go.Figure(
        go.Scatter(x=t, y=x, mode='lines', line=dict(color='#00d4ff', width=2), name='x(t)'),
    )
    fig_ts.update_layout(
        title='Time Series: x(t)',
        xaxis_title='t',
        yaxis_title='x',
        **_LAYOUT_DEFAULTS,
    )

    margin = (x.max() - x.min()) * 0.2 + 0.5
    x_range = np.linspace(x.min() - margin, x.max() + margin, 500)
    p_vals = [param_values[p] for p in param_vars]
    raw = compiled_funcs['x'](x_range, *p_vals)
    # Handle constant expression returning a scalar
    dxdt = np.broadcast_to(np.asarray(raw, dtype=float), x_range.shape).copy()

    sign_changes = np.where(np.diff(np.sign(dxdt)))[0]
    eq_x = [(x_range[i] + x_range[i + 1]) / 2.0 for i in sign_changes]

    fig_pl = go.Figure()
    fig_pl.add_trace(go.Scatter(
        x=x_range, y=dxdt, mode='lines',
        line=dict(color='#ff6e54', width=2), name='dx/dt',
    ))
    fig_pl.add_hline(y=0, line_dash='dash', line_color='white', line_width=1)
    if eq_x:
        fig_pl.add_trace(go.Scatter(
            x=eq_x, y=[0.0] * len(eq_x), mode='markers',
            marker=dict(size=10, color='yellow', symbol='circle'),
            name='Equilibria',
        ))
    fig_pl.update_layout(
        title='Phase Line: dx/dt vs x',
        xaxis_title='x',
        yaxis_title='dx/dt',
        **_LAYOUT_DEFAULTS,
    )
    return fig_ts, fig_pl


def plot_2d(data: dict[str, np.ndarray]) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=data['x'], y=data['y'],
        mode='lines',
        line=dict(width=1.5, color='#00d4ff'),
        name='trajectory',
    ))
    fig.update_layout(
        title='Phase Portrait: y vs x',
        xaxis_title='x',
        yaxis_title='y',
        **_LAYOUT_DEFAULTS,
    )
    return fig


def plot_3d(data: dict[str, np.ndarray]) -> go.Figure:
    fig = go.Figure(go.Scatter3d(
        x=data['x'], y=data['y'], z=data['z'],
        mode='lines',
        line=dict(width=2, color='#00d4ff'),
        name='trajectory',
    ))
    fig.update_layout(
        title='3D Phase Diagram',
        scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'),
        **_LAYOUT_DEFAULTS,
    )
    return fig


def plot_4d(
    data: dict[str, np.ndarray],
    color_var: str = 'w',
) -> go.Figure:
    fig = go.Figure(go.Scatter3d(
        x=data['x'], y=data['y'], z=data['z'],
        mode='lines',
        line=dict(
            width=3,
            color=data[color_var],
            colorscale='Viridis',
            colorbar=dict(title=color_var, thickness=15),
        ),
        name='trajectory',
    ))
    fig.update_layout(
        title=f'4D Phase Diagram (color = {color_var})',
        scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'),
        **_LAYOUT_DEFAULTS,
    )
    return fig
