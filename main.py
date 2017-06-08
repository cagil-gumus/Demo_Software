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
import re


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
        self._console = self.textBrowser_console

        # Button Connections to the methods
        self.pushButton_connecttoboard.clicked.connect(self.connecttoboardispressed)
        self.pushButton_initializeboard.clicked.connect(self.initilizebuttonispressed)
        self.pushButton_startsampling.clicked.connect(self.samplingbuttonispressed)
        self.pushButton_resetboard.clicked.connect(self.resetbuttonispressed)
        self.pushButton_pllconfig.clicked.connect(self.pllconfiguration)

        #  Create emtpy object for instance from PlotWindow class
        self._plotWindow = PlotWindow(self)

    def connecttoboardispressed(self):

        slotnumber = self.getslotselection()

        connection_status = deviceaccess.connecttoboard(slotnumber)

        if connection_status:
            self.textBrowser_console.append('Connection Established')
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
            self.textBrowser_console.append('Starting Configuration')

            self.pushButton_initializeboard.setEnabled(False)

            self.textBrowser_console.append('Initializing the clock')
            deviceaccess.clockinitilization()
            self.progressBar.setValue(40)

            self.textBrowser_console.append('Configuring the ADCs of AMC')
            deviceaccess.configureadcs()
            self.progressBar.setValue(80)

            self.textBrowser_console.append('Configure the Timing')
            deviceaccess.configuretiming()
            self.progressBar.setValue(100)

            self.textBrowser_console.append('Timing Configuration Completed')

            self.pushButton_initializeboard.setEnabled(True)

        elif externalclockpreference:
            self.textBrowser_console.append('External Clock Configuration not available')

        else:
            print ('Signal Source not selected')

    def samplingbuttonispressed(self):

        # Grab the information from the UI
        channels_to_plot = self.getlistofcheckedchannels()
        is_combine_all_checked = self.checkBox_combineall.isChecked()

        # If user selected any channels for display => show _plotWindow
        if len(channels_to_plot) != 0:
            self._plotWindow.showwindow(channels_to_plot, is_combine_all_checked)

        # Start Refresing the data on _plotWindow
        self._plotWindow.start_refreshing(is_combine_all_checked=is_combine_all_checked, FPS=self.FPS.value(),
                                          channels_to_plot=self.getlistofcheckedchannels())

        self.textBrowser_console.append('Sampling Started')

    def resetbuttonispressed(self):
        # Reset the AMC
        self.textBrowser_console.append('Reseting the AMC')
        # deviceaccess.resetboard()
        self.textBrowser_console.append('Reset Completed')



    def pllconfiguration(self):
        # Grabs the txt file from user, parses it, grabs the values for registers
        # Sends it to FPGA ( FPGA uses I2C to configure the PLL of DS8VM1)

        registers = []

        # Show user the Dialog to select the file
        self.fileDialog = QtGui.QFileDialog.getOpenFileName(self)

        if self.fileDialog:
            self.textBrowser_console.append('Codeloader File Location: {}'.format(self.fileDialog))
            self.label_codeloader_status.setText('File Location: {}'.format(self.fileDialog))
        else:
            self.label_codeloader_status.setText('File Location: Error')
            self.textBrowser_console.append('Cannot find the file location')

        try:  # Try to open the file
            pll_file = open(self.fileDialog)

        except IOError: # If something happens throw error message
            self.label_codeloader_status.setText('Cannot read the file')

        pll_data = pll_file.readlines()

        try:
            for line in pll_data:
                register_string = line.strip().split()  # get rid of OS dependency
                registers.append(int(register_string[-1], 16))  # Convert to int

        except:
            self.textBrowser_console.append('PLL Configuration File Error')

        # Send the register values to FPGA
        deviceaccess.configurepll(registers)

        self.textBrowser_console.append('PLL Configuration Completed')

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
        self.setWindowTitle("ADC Data Plot")
        self.setGeometry(0, 0, 1000, 1000)

        self._checkBox_combineall = parent._checkBox_combineall

        self.console = parent._console

        # Construct the Grid Layout
        self.gridLayout = QtGui.QGridLayout(self)

        # Create Timer for refreshing the window
        self.timer1 = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()

        # Get random signal from Data Generator
        self.signal_source = DataGenerator()

        self._list_of_channels_to_display = []

    def start_refreshing(self, is_combine_all_checked, FPS, channels_to_plot):

        self._list_of_channels_to_display = channels_to_plot
        # Start the timer and refresh the Plot Window every 50 ms by calling updateplot method

        # If user has selected All in one plot => use different methods to refresh data
        if is_combine_all_checked:
            self.timer2.start(1000 / FPS)  # timeout in milliseconds ... 50ms => 20 frames per second
            self.connect(self.timer2, QtCore.SIGNAL('timeout()'), self.updateplot_combined)
        else:
            self.timer1.start(1000 / FPS)  # timeout in milliseconds ... 50ms => 20 frames per second
            self.connect(self.timer1, QtCore.SIGNAL('timeout()'), self.updateplot)

        self.console.append('Sampling Started')

    def showwindow(self, list_of_channels_to_display, is_combine_all_checked):
        # Draw the grid first and then show the window

        self._redrawgrid(list_of_channels_to_display, is_combine_all_checked)

        super(PlotWindow, self).show()

    def _redrawgrid(self, list_of_channels_to_display, is_combine_all_checked):
        # Clear the grid before laying out a new one
        self._cleargridlayout()

        # If user wants combined plot create only 1 Widget if not create as many as user desires
        if is_combine_all_checked: # Add only one widget where all plots will be put inside
            self.gridLayout.addWidget(CombinedPlotWidget(list_of_channels=list_of_channels_to_display))

        else:  # Add multiple widgets for each individual channels
            for channel_id in list_of_channels_to_display:
                self.gridLayout.addWidget(CustomPlotWidget(self, channel_id))

    def _cleargridlayout(self):
        childItem = self.gridLayout.takeAt(0)
        while (childItem != None):
            childItem.widget().deleteLater()
            childItem = self.gridLayout.takeAt(0)

    def updateplot(self):

        list_of_channels_to_display = self._list_of_channels_to_display

        channel_1_data, channel_2_data, channel_3_data, channel_4_data, \
        channel_5_data, channel_6_data, channel_7_data, channel_8_data = deviceaccess.readdma(buffer_size=100)

        channels = [channel_1_data, channel_2_data, channel_3_data, channel_4_data,
                    channel_5_data, channel_6_data, channel_7_data, channel_8_data]

        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().setData(channels[list_of_channels_to_display[index]-1])

    def updateplot_combined(self):
        self.console.append('Now showing with combined combined plot')


    def closeEvent(self, QCloseEvent):
        # When user closes the PlotWindow stop the timer (disconnect from updateplot method)
        self.timer1.stop()
        self.timer2.stop()
        self.console.append('Sampling Ended')

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent, channelId):
        # TODO Add additional values for custom class
        # pg.setConfigOption('background', 'w')
        # pg.setConfigOption('foreground', 'k')

        # pen = pg.mkPen('y', width=3, style=QtCore.Qt.DashLine)

        super(CustomPlotWidget, self).__init__(parent)
        self._channelId = channelId
        self.setTitle('Channel %d' % self._channelId)
        # self.resize(400, 400)
        # self.setRange(QtCore.QRectF(0, -10, 5000, 20))
        self.setLabels(left='ADC Value', bottom='Time')
        self._plot_item = self.plot()


    def setData(self, signal):
        self._plot_item.setData(signal)


class CombinedPlotWidget(pg.GraphicsWindow):
    def __init__(self, list_of_channels):

        super(CombinedPlotWidget, self).__init__()

        self._list_of_channels = list_of_channels


        self._plot_item = self.addPlot()
        self._plot_item.plot(np.random.normal(size=100), pen=(255, 0, 0))
        self._plot_item.plot(np.random.normal(size=100), pen=(0, 255, 0))
        self._plot_item.plot(np.random.normal(size=100), pen=(0, 0, 255))



    # def addPlots(self, list_of_channels, signal):
    #     for index in list_of_channels:
    #         self._plot_item.plot(signal)



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
