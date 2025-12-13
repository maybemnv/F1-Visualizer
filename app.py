import warnings
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash
from config import HOST, PORT
from dashboard.callbacks import register_callbacks
from dashboard.layout import app_layout

# Silent SettingWithCopyWarning
pd.options.mode.chained_assignment = None

# Silent Fastf1 FutureWarning regarding the use of plotting functions
warnings.filterwarnings(action="ignore", message="Driver", category=FutureWarning)

# Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SANDSTONE],
    title="F1 Visualizer - A F1 Strategy Dashboard",
    update_title="Crunching numbers...",
)
server = app.server
app.layout = app_layout

# Register all callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
