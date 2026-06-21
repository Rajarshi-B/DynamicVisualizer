# Dynamical System Visualizer

Author: RajarshiB  
AI-Assistant: Claude

An interactive web app for exploring ordinary differential equations (ODEs) in 1D through 4D, built with Streamlit, SymPy, SciPy, and Plotly.

## Features

- Enter custom ODE equations using standard math notation
- Dimensions: 1D, 2D, 3D, 4D phase space visualization
- Strogatz Examples Library with 7 pre-loaded classic systems
- Editable parameter sliders with adjustable min/max range
- Adjustable initial conditions and integration settings
- 20-second integration timeout for safety
- Dark-themed interactive Plotly charts

## Included Systems (Strogatz Library)

| System | Dimension | Highlights |
|---|---|---|
| Logistic Equation | 1D | Fixed points, carrying capacity |
| Spruce Budworm Outbreak | 1D | Saddle-node bifurcation, hysteresis |
| Romeo and Juliet | 2D | Eigenvalues, linear stability |
| Lotka-Volterra Predator-Prey | 2D | Limit cycles, structural instability |
| Van der Pol Oscillator | 2D | Nonlinear damping, limit cycle |
| Lorenz Attractor | 3D | Chaos, butterfly effect |
| Rossler Attractor | 3D | Stretch-and-fold chaos mechanism |

## Tech Stack

- [Streamlit](https://streamlit.io) - UI framework
- [SymPy](https://www.sympy.org) - symbolic equation parsing
- [SciPy](https://scipy.org) - RK45 numerical integration
- [Plotly](https://plotly.com) - interactive charts
- [NumPy](https://numpy.org) - array operations

## Project Structure

```
app.py              main Streamlit entry point
config.py           constants, default systems, slider ranges
requirements.txt    Python dependencies
core/
    parser.py       equation parsing and function compilation
    integrator.py   ODE integration with timeout
    visualizer.py   Plotly figure builders
screenshots/        app screenshots
```

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
