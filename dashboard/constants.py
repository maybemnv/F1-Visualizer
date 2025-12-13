"""Constants and magic numbers for the dashboard module."""

# Slider defaults
DEFAULT_UPPER_BOUND = 107
UPPER_BOUND_MIN = 100
UPPER_BOUND_MAX = 150

# Lap filtering thresholds
LAP_REP_LOWER_BOUND = -5  # Filter outliers in PctFromLapRep
MIN_LAPS_FOR_DISTPLOT = 6  # Minimum laps for driver to appear in distplot
MIN_COMPOUND_LAP_RATIO = 20  # Compound must have at least 1/20 of total laps

# Plot dimensions
PLOT_WIDTH = 1250
PLOT_HEIGHT_MIN = 300
PLOT_HEIGHT_DEFAULT = 500
DRIVER_HEIGHT_MULTIPLIER = 50

# Subplot configuration
SUBPLOT_MAX_COLS = 4

# Compound order for sorting
COMPOUND_ORDER = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

# Slider tick intervals
LAP_TICK_INTERVAL = 5
POSITION_TICK_INTERVAL = 5
