# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> gui >> controllers
"""
import pathlib
from PyQt5 import QtCore

class ExperimentController(QtCore.QObject):
    # navigation
    currentTraceChanged = QtCore.pyqtSignal(object)
    # MPL
    mplMotionNotifyEvent = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.filename = None
        self.expt = None
        self.trc = None
        self.index = None

    # ==========================================================================
    # navigation
    # ==========================================================================
    def update_index(self, value):
        """ handles indexChanged events from widgets;
            sets internal index broadcast current trace """
        self.index = value
        self.trc = self.expt[self.index]
        self.currentTraceChanged.emit(self.trc)

    # ==========================================================================
    # matplotlib
    # ==========================================================================
    def motion_notify(self, evt):
        """ redistribute MPL motion_notify_event """
        self.mplMotionNotifyEvent.emit(evt)

    # ==========================================================================
    # experiment
    # ==========================================================================
    def import_experiment_from_pma(self):
        pass

    def merge_experiments(self):
        pass

    def open_experiment(self):
        pass

    def save_experiment(self):
        pass

    def save_experiment_as(self):
        pass

    def detect_baseline(self):
        pass

    def set_experiment_bleed(self):
        pass

    def set_experiment_gamma(self):
        pass

    def train_selected_traces(self):
        pass

    # ==========================================================================
    # trace
    # ==========================================================================
    def set_trace_offsets(self):
        pass

    def set_trace_offset_time_window(self):
        pass

    def reset_trace_offsets(self):
        pass

    def set_trace_limits(self):
        pass

    def set_trace_start_time(self):
        pass

    def set_trace_stop_time(self):
        pass

    def reset_trace_limits(self):
        pass

    def set_trace_cluster_index(self):
        pass

    def toggle_trace(self):
        pass

    def train_trace(self):
        pass
