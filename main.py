#! /usr/bin/env python

from PyQt4 import QtGui, QtCore, uic
import sys
import numpy as np
import pyqtgraph as pg
import time


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('main_window.ui', self)
        self.setWindowTitle("SIS8300-L2 Demo")

        #   Setting up App Icon on Task Bar
        self.app_icon = QtGui.QIcon()
        self.app_icon.addFile('DESY_LOGO.png', QtCore.QSize(48, 48))
        self.setWindowIcon(self.app_icon)

        # Checkboxes inside MainWindow
        self._list_of_channel_checkboxes = [self.checkBox_channel1,
                                            self.checkBox_channel2,
                                            self.checkBox_channel3,
                                            self.checkBox_channel4,
                                            self.checkBox_channel5,
                                            self.checkBox_channel6,
                                            self.checkBox_channel7,
                                            self.checkBox_channel8]

        self._checkBox_combineall = self.checkBox_combineall.isChecked()

        # If PushButton is clicked call the method 'button is pressed'
        self.pushButton_startsampling.clicked.connect(self.buttonispressed)

        # Create emtpy object for instance from PlotWindow class
        self._plotWindow = None

    def buttonispressed(self):
        # Create an instance of PlotWindow class

        self._plotWindow = PlotWindow(self)

        # Grab the information from the UI
        channels_to_plot = self.getListOfCheckedChannels()
        is_combine_all_checked = self.checkBox_combineall.isChecked()

        # If user selected any channels for display => show _plotWindow
        if len(channels_to_plot) != 0:
            self._plotWindow.showwindow(channels_to_plot, is_combine_all_checked)

        self._plotWindow.start_refresing(is_combine_all_checked)

    def getListOfCheckedChannels(self):
        # Returns a list of id's of currently selected checkboxes.

        list_of_selected_chekboxes = []

        for index in range(0, len(self._list_of_channel_checkboxes)):

            if self._list_of_channel_checkboxes[index].isChecked():
                channel_id = index + 1
                list_of_selected_chekboxes.append(channel_id)

        return list_of_selected_chekboxes


class PlotWindow(QtGui.QWidget):
    def __init__(self, parent):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.Window)

        # Set preferences for Plot Window
        self.setWindowTitle("Super Great ADC Data Plot")
        self.setGeometry(0, 0, 1000, 1000)

        self._checkBox_combineall = MainWindow()._checkBox_combineall

        # Construct the Grid Layout
        self.gridLayout = QtGui.QGridLayout(self)

        # Create Timer for refreshing the window
        self.timer = QtCore.QTimer()

        # Get random signal from Data Generator
        self.signal_source = DataGenerator()

    def start_refresing(self, is_combine_all_checked):
        # Start the timer and refresh the Plot Window every 50 ms by calling updateplot method
        self.timer.start(50)  # timeout in milliseconds ... 50ms => 20 frames per second

        # If user has selected All in one plot => use different methods to refresh data
        if is_combine_all_checked:
            self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateplot_combined)
        else:
            self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateplot)

    def showwindow(self, list_of_channels_to_display, is_combine_all_checked):
        self._redrawGrid(list_of_channels_to_display, is_combine_all_checked)
        if is_combine_all_checked:
            pass
        else:
            super(PlotWindow, self).show()

    def _redrawGrid(self, list_of_channels_to_display, is_combine_all_checked):
        self._clearGridLayout()

        # If user wants combined plot create only 1 Widget if not create as many as user desires
        if is_combine_all_checked:
            pass
        else:
            for channel_id in list_of_channels_to_display:
                self.gridLayout.addWidget(CustomPlotWidget(self, channel_id))

    def _clearGridLayout(self):
        childItem = self.gridLayout.takeAt(0)
        while (childItem != None):
            childItem.widget().deleteLater()
            childItem = self.gridLayout.takeAt(0)

    def updateplot(self):

        for index in range(0, self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().setData(self.signal_source.get_data())

    def updateplot_combined(self):
        pass



class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent, channelId):
        super(CustomPlotWidget, self).__init__(parent)
        self._channelId = channelId
        self.setTitle('Channel %d' % self._channelId)
        self.resize(400, 400)
        self.setRange(QtCore.QRectF(0, -10, 5000, 20))
        self.setLabels(left='Voltage (MV)', bottom='time')

        self._plot_item = self.plot()

    def setData(self, signal):
        self._plot_item.setData(signal)


# Data_Generator generates "random white noise"
class DataGenerator:
    def __init__(self):
        self.data = np.random.normal(size=(50, 5000))
        self.ptr = 0

    def get_data(self):
        self.ptr += 1
        signal = self.data[self.ptr % 10]
        return signal


def main():
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.resize(200, 200)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
