"""voxel.apps.sas.toolkit.

Toolkit to support SAS
"""
from . import _version
from .eda.plotting import corr_heatmap, hist_plotter, pca_explained_variance_plot
from .feature_selection.correlation_tools import top_correlations
from .feature_selection.vif import variance_inflation_factor
from .modelling.diagnostics import classification_plots, regression_plots, shuffle_test
from .modelling.metrics import confusion_numbers
from .preprocessing.data_quality import const_cols, missing_data
from .preprocessing.timeseries import (
    correlation_calc,
    correlation_plot_multi,
    correlation_plot_single,
    time_to_supervised,
)
from .preprocessing.utilities import camel_to_snake, read_folder


__all__ = [
    "corr_heatmap",
    "hist_plotter",
    "pca_explained_variance_plot",
    "top_correlations",
    "variance_inflation_factor",
    "classification_plots",
    "regression_plots",
    "shuffle_test",
    "confusion_numbers",
    "const_cols",
    "missing_data",
    "correlation_calc",
    "correlation_plot_multi",
    "correlation_plot_single",
    "time_to_supervised",
    "camel_to_snake",
    "read_folder",
]


__version__ = _version.get_versions()["version"]
