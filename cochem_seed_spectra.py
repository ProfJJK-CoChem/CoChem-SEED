import json
import sqlite3
import pathlib
import numpy as np
import ipywidgets as widgets
import plotly.graph_objects as go
from IPython.display import display, HTML

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------
CONFIG_PATH = pathlib.Path("cochem_system_config.json")
PARAMS_PATH = pathlib.Path("seed_run_params.json")
DB_PATH = pathlib.Path("seed_curriculum.db")
TELEMETRY_PATH = pathlib.Path("eval_telemetry.json")

# -------------------------------------------------------------------------
# DATA MOCKING & PARSING (For Vault Integration)
# -------------------------------------------------------------------------
def _dev_bootstrap_spectra():
    """Generates authentic-looking noisy baseline data if real JDX is missing."""
    x = np.linspace(400, 4000, 1000)
    # Synthetic noisy background + pedagogical peaks
    y_exp = 0.05 * np.random.normal(size=1000) + 0.1
    y_exp += 0.8 * np.exp(-((x - 1700)**2) / 400) # Carbonyl stretch
    y_exp += 0.6 * np.exp(-((x - 3300)**2) / 2000) # Broad OH stretch
    
    # "Theoretical" unscaled sticks
    x_theory = np.array([1750, 3400])
    y_theory = np.array([1.5, 1.2]) 
    return x, y_exp, x_theory, y_theory

def fetch_spectra_data(rxn_id, mode="curated"):
    """Pulls experimental JDX and theoretical tensors from the vault."""
    # In a production environment, this parses the JDX string from sqlite3.
    # For this safe-context implementation, we use the pedagogical mock.
    return _dev_bootstrap_spectra()

# -------------------------------------------------------------------------
# UI & TRAP MECHANICS
# -------------------------------------------------------------------------
def render_spectra_fitter():
    if not PARAMS_PATH.exists() or not CONFIG_PATH.exists():
        display(HTML("<span style='color: red;'>Missing configuration. Run Stages 1-3 first.</span>"))
        return

    with open(PARAMS_PATH, "r") as f:
        params = json.load(f)
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)

    use_traps = cfg.get("UI_Settings", {}).get("unphysical_fit_traps", True)
    
    # Fetch Data
    x_exp, y_exp, x_th_base, y_th_base = fetch_spectra_data(
        params.get("reaction_id"), 
        mode=params.get("mode")
    )
    
    # Telemetry State
    state = {"hints_used": 0, "traps_triggered": 0, "final_scale": 1.0, "final_shift": 0.0}

    # UI Elements
    title = widgets.HTML("<h3 style='font-family: sans-serif; color: #2e3440;'>Spectroscopic Fitting Arena</h3>")
    
    # Notice the slider min is explicitly set to -0.5 to allow the trap to trigger
    scale_slider = widgets.FloatSlider(value=1.0, min=-0.5, max=2.5, step=0.05, description='Intensity Scale:')
    shift_slider = widgets.FloatSlider(value=0, min=-200, max=200, step=5, description='Freq Shift (cm⁻¹):')
    
    hint_btn = widgets.Button(description='Request Hint', button_style='warning', icon='lightbulb')
    lock_btn = widgets.Button(description='Lock Fit & Generate Report', button_style='success', icon='lock')
    
    plot_out = widgets.Output()
    msg_out = widgets.Output()

    def update_plot(scale, shift):
        with msg_out:
            msg_out.clear_output()
            # -------------------------------------------------------------
            # SOCRATIC TRAP LOGIC
            # -------------------------------------------------------------
            if use_traps and scale < 0.0:
                state["traps_triggered"] += 1
                display(HTML(
                    "<div style='background-color: #bf616a; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                    "<b>SOCRATIC TRAP TRIGGERED:</b> Negative intensity scaling is physically impossible in standard absorption spectroscopy "
                    "(it implies molecular emission without excitation). Resetting to 0.1."
                    "</div>"
                ))
                # Force slider back to a physical reality to prevent WebGL update
                scale_slider.value = 0.1
                return
        
        # Apply transformation
        x_th_adj = x_th_base + shift
        y_th_adj = y_th_base * scale

        with plot_out:
            plot_out.clear_output(wait=True)
            fig = go.Figure()
            
            # Experimental Trace
            fig.add_trace(go.Scatter(
                x=x_exp, y=y_exp, mode='lines', 
                line=dict(color='black', width=1.5), name='Experimental (Noisy)'
            ))
            
            # Theoretical Sticks
            fig.add_trace(go.Bar(
                x=x_th_adj, y=y_th_adj, width=15,
                marker_color='red', name='Predicted (Scaled)'
            ))
            
            # ACS Standard Formatting
            fig.update_layout(
                xaxis_title="Wavenumber (cm⁻¹)",
                yaxis_title="Normalized Absorbance",
                xaxis=dict(autorange="reversed"), # Standard IR orientation
                template="simple_white",
                margin=dict(l=60, r=20, t=30, b=40),
                font=dict(family="Arial", size=14, color="black"),
                legend=dict(x=0.02, y=0.98, bordercolor="black", borderwidth=1)
            )
            fig.show()

    def on_hint_clicked(b):
        state["hints_used"] += 1
        with msg_out:
            msg_out.clear_output()
            display(HTML(
                "<div style='background-color: #ebcb8b; color: #2e3440; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                f"<b>Hint #{state['hints_used']}:</b> Notice the broad experimental peak around 3300 cm⁻¹. "
                "Calculated harmonic frequencies typically overestimate this stretch. Try applying a negative shift."
                "</div>"
            ))

    def on_lock_clicked(b):
        state["final_scale"] = scale_slider.value
        state["final_shift"] = shift_slider.value
        
        with open(TELEMETRY_PATH, "w") as f:
            json.dump(state, f, indent=4)
            
        with msg_out:
            display(HTML(
                "<div style='background-color: #a3be8c; color: #2e3440; padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                "<b>Fit Locked!</b> Telemetry data secured. Proceed to Stage 5.0 for Report Generation."
                "</div>"
            ))
        scale_slider.disabled = True
        shift_slider.disabled = True
        hint_btn.disabled = True
        lock_btn.disabled = True

    # Bind widgets
    widgets.interactive_output(update_plot, {'scale': scale_slider, 'shift': shift_slider})
    hint_btn.on_click(on_hint_clicked)
    lock_btn.on_click(on_lock_clicked)

    # Layout
    controls = widgets.VBox([
        title,
        scale_slider, 
        shift_slider,
        widgets.HBox([hint_btn, lock_btn]),
        msg_out
    ], layout=widgets.Layout(padding='15px', border='1px solid #d8dee9', background_color='#eceff4', border_radius='5px'))

    display(controls, plot_out)
    
    # Trigger initial plot
    update_plot(scale_slider.value, shift_slider.value)

if __name__ == "__main__":
    render_spectra_fitter()