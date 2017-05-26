#! /usr/bin/env python

''' 

Main code for running the UI. Main Window has been designed using QT Designer.
Plot window is constructed within the code (.ui file does not exists) 


Written by: Cagil Gumus 
email: cagil.guemues@desy.de
Date: 24.04.2017

'''

from PyQt4 import QtGui, QtCore, uic
import sys
import numpy as np
import pyqtgraph as pg
import deviceaccess


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('Demo_GUI.ui', self)
        self.setWindowTitle("DS8VM1 Demo")

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

        # Button Connections to the methods
        self.pushButton_connecttoboard.clicked.connect(self.connecttoboardispressed)
        self.pushButton_initializeboard.clicked.connect(self.initilizebuttonispressed)
        self.pushButton_startsampling.clicked.connect(self.samplingbuttonispressed)
        self.pushButton_resetboard.clicked.connect(self.resetbuttonispressed)
        self.pushButton_pllconfig.clicked.connect(self.pllconfiguration)

        #  Create emtpy object for instance from PlotWindow class
        self._plotWindow = None

    def connecttoboardispressed(self):

        slotnumber = self.getslotselection()

        connection_status = deviceaccess.connecttoboard(slotnumber)

        if connection_status:
            print('Connection Established')
            self.label_mainclock.setText("Main Clock Frequency: {} MHz"
                                         .format(float(deviceaccess.readinternalclockfrequency())/1000000))
            self.label_connectionstatus.setText('Connection Status: Connected')
        else:
            print('Cannot connect to DS8VM1')
            self.label_connectionstatus.setText('Connection Status: Failed')

    def initilizebuttonispressed(self):

        internalclockpreference = self.radioButton_internalclock.isChecked()
        externalclockpreference = self.radioButton_externalclock.isChecked()

        if internalclockpreference:
            print ('Starting Configuration')

            self.pushButton_initializeboard.setEnabled(False)

            print ('Initializing the clock')
            deviceaccess.clockinitilization()
            self.progressBar.setValue(40)

            print ('Configuring the ADCs of AMC')
            deviceaccess.configureadcs()
            self.progressBar.setValue(80)

            print ('Configure the Timing')
            deviceaccess.configuretiming()
            self.progressBar.setValue(100)

            print 'Configuration = Done'

            self.pushButton_initializeboard.setEnabled(True)

        elif externalclockpreference:
            print ('External Clock Configuration not available')

        else:
            print ('Signal Source not selected')

    def samplingbuttonispressed(self):
        # Create an instance of PlotWindow class

        self._plotWindow = PlotWindow(self)

        # Grab the information from the UI
        channels_to_plot = self.getlistofcheckedchannels()
        is_combine_all_checked = self.checkBox_combineall.isChecked()

        # If user selected any channels for display => show _plotWindow
        if len(channels_to_plot) != 0:
            self._plotWindow.showwindow(channels_to_plot, is_combine_all_checked)

        # Start Refresing the data on _plotWindow
        self._plotWindow.start_refreshing(is_combine_all_checked, FPS=self.FPS.value())

    def resetbuttonispressed(self):
        # Reset the AMC
        print ('Reseting AMC')
        deviceaccess.resetboard()
        print ('Reset Complete')

    def pllconfiguration(self):

        self.fileDialog = QtGui.QFileDialog.getOpenFileName(self)
        if self.fileDialog:
            print self.fileDialog

        # self.fileDialog = QtGui.QFileDialog(self)
        # self.fileDialog.show()

    def getlistofcheckedchannels(self):
        # Returns a list of id's of currently selected checkboxes.

        list_of_selected_chekboxes = []

        for index in range(0, len(self._list_of_channel_checkboxes)):

            if self._list_of_channel_checkboxes[index].isChecked():
                channel_id = index + 1
                list_of_selected_chekboxes.append(channel_id)

        return list_of_selected_chekboxes

    def getslotselection(self):

        self.slotselection = self.comboBox_slotnumber.currentText()
        return int(self.slotselection)


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

    def start_refreshing(self, is_combine_all_checked,FPS):
        # Start the timer and refresh the Plot Window every 50 ms by calling updateplot method

        self.timer.start(1000/FPS)  # timeout in milliseconds ... 50ms => 20 frames per second

        # If user has selected All in one plot => use different methods to refresh data
        if is_combine_all_checked:
            self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateplot_combined)
        else:
            self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.updateplot)

    def showwindow(self, list_of_channels_to_display, is_combine_all_checked):
        # Draw the grid first and then show the window

        self._redrawgrid(list_of_channels_to_display, is_combine_all_checked)
        if is_combine_all_checked:
            # TODO Add the missing functionality
            pass
        else:
            super(PlotWindow, self).show()

    def _redrawgrid(self, list_of_channels_to_display, is_combine_all_checked):
        self._cleargridlayout()

        # If user wants combined plot create only 1 Widget if not create as many as user desires
        if is_combine_all_checked:
            # TODO Add the missing functionality
            pass
        else:
            for channel_id in list_of_channels_to_display:
                self.gridLayout.addWidget(CustomPlotWidget(self, channel_id))

    def _cleargridlayout(self):
        childItem = self.gridLayout.takeAt(0)
        while (childItem != None):
            childItem.widget().deleteLater()
            childItem = self.gridLayout.takeAt(0)

    def updateplot(self):

        for index in range(0, self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().setData(self.signal_source.get_data())

        self.channel_1_data, self.channel_2_data, self.channel_3_data, self.channel_4_data, \
        self.channel_5_data, self.channel_6_data, self.channel_7_data, self.channel_8_data,\
            = deviceaccess.readdma(buffer_size=100)

        self.gridLayout.itemAt(0).widget().setData(self.channel_1_data)
        self.gridLayout.itemAt(1).widget().setData(self.channel_2_data)
        self.gridLayout.itemAt(2).widget().setData(self.channel_3_data)
        self.gridLayout.itemAt(3).widget().setData(self.channel_4_data)
        self.gridLayout.itemAt(4).widget().setData(self.channel_5_data)
        self.gridLayout.itemAt(5).widget().setData(self.channel_6_data)
        self.gridLayout.itemAt(6).widget().setData(self.channel_7_data)
        self.gridLayout.itemAt(7).widget().setData(self.channel_8_data)

    def updateplot_combined(self):
        # TODO Add the missing functionality
        # Refreshing the data for combine_all plot
        pass


class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent, channelId):
        # TODO Add additional values for custom class

        super(CustomPlotWidget, self).__init__(parent)
        self._channelId = channelId
        self.setTitle('Channel %d' % self._channelId)
        # self.resize(400, 400)
        # self.setRange(QtCore.QRectF(0, -10, 5000, 20))
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
