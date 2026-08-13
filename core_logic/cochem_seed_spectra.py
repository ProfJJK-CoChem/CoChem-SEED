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

import logging

logger = logging.getLogger("CoChem_SEED_Spectra")


# -------------------------------------------------------------------------
# DATA MOCKING & PARSING (For Vault Integration)
# -------------------------------------------------------------------------
def _dev_bootstrap_spectra() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generates analytical Lorentzian/Gaussian spectral lineshapes."""
    x = np.linspace(400, 4000, 1000)
    y_exp = 0.1 + 1e-6 * (x - 2000)**2
    gamma1 = 20.0
    y_exp += 0.8 * (gamma1**2 / ((x - 1715)**2 + gamma1**2))
    gamma2 = 80.0
    y_exp += 0.6 * (gamma2**2 / ((x - 3350)**2 + gamma2**2))
    gamma3 = 15.0
    y_exp += 0.4 * np.exp(-((x - 2950)**2) / (2 * gamma3**2))
    
    x_theory = np.array([1715, 2950, 3350])
    y_theory = np.array([1.4, 0.7, 1.1])
    return x, y_exp, x_theory, y_theory

def fetch_spectra_data(rxn_id: str | int | None, mode: str = "curated") -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pulls experimental spectra and theoretical tensors from the curriculum vault database."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT spectra_data FROM reactions WHERE rxn_id=?", (rxn_id,))
            row = cur.fetchone()
            conn.close()
            if row and row[0]:
                data = json.loads(row[0])
                x = np.array(data["x"])
                y_exp = np.array(data["y_exp"])
                x_theory = np.array(data["x_theory"])
                y_theory = np.array(data["y_theory"])
                return x, y_exp, x_theory, y_theory
        except Exception:
            pass
            
    return _dev_bootstrap_spectra()

def simulate_ir_spectrum(molecule_str: str, engine: str = "pyscf_mace") -> dict:
    """Zero-ORCA IR Spectral Simulation placeholder."""
    logger.info(f"Simulating IR spectrum using engine: {engine}")
    # Return a dummy spectrum dictionary for the pedagogical lab
    return {
        "frequencies": [1715.0, 2950.0, 3350.0],
        "intensities": [1.4, 0.7, 1.1]
    }

# -------------------------------------------------------------------------
# UI & TRAP MECHANICS
# -------------------------------------------------------------------------
def render_spectra_fitter() -> None:
    if not PARAMS_PATH.exists() or not CONFIG_PATH.exists():
        display(HTML("<span style='color: red;'>Missing configuration. Run Stages 1-3 first.</span>"))
        return

    with open(PARAMS_PATH, "r", encoding="utf-8") as f:
        params = json.loads(f.read())
    try:
        from cochem_base.config_loader import load_system_config_dict
        cfg = load_system_config_dict(CONFIG_PATH)
    except ImportError:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.loads(f.read())

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

    def update_plot(scale: float, shift: float) -> None:
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

    def on_hint_clicked(b: Any) -> None:
        state["hints_used"] += 1
        with msg_out:
            msg_out.clear_output()
            display(HTML(
                "<div style='background-color: #ebcb8b; color: #2e3440; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                f"<b>Hint #{state['hints_used']}:</b> Notice the broad experimental peak around 3300 cm⁻¹. "
                "Calculated harmonic frequencies typically overestimate this stretch. Try applying a negative shift."
                "</div>"
            ))

    def on_lock_clicked(b: Any) -> None:
        state["final_scale"] = scale_slider.value
        state["final_shift"] = shift_slider.value
        
        with open(TELEMETRY_PATH, "w", encoding="utf-8") as f:
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