from ._vickersCB import VickersCB
from ._heatMapCB import HeatMapCB
from ._dataTableCB import DataTableCB
from ._hmPlotCB import HMPlotCB
from ._proyectoCB import ProyectoCB


class Callbacks:
    def __init__(self) -> None:
        self.imageProcessing = VickersCB(self)
        self.heatMap = HeatMapCB(self)
        self.dataTable = DataTableCB(self)  # Pass self to access other callbacks
        self.hmPlot = HMPlotCB(self)  # Heat map plot callback
        self.proyecto = ProyectoCB(self)  # Project management callback
