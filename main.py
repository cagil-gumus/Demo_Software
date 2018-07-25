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
import pyqtgraph as pg
import deviceaccess
import time


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
                                            self.checkBox_channel8,
                                            self.checkBox_channel9,     # DC Channel 1
                                            self.checkBox_channel10]    # DC Channel 2

        self._checkBox_combineall = self.checkBox_combineall.isChecked()
        self._console = self.textBrowser_console
        self._bufferlength = self.bufferlength

        # Button Connections to the methods
        self.pushButton_connecttoboard.clicked.connect(self.connecttoboardispressed)
        self.pushButton_readboardinfo.clicked.connect(self.readboardinfoispressed)
        self.pushButton_initializeboard.clicked.connect(self.initilizebuttonispressed)
        self.pushButton_startsampling.clicked.connect(self.samplingbuttonispressed)
        self.pushButton_resetboard.clicked.connect(self.resetbuttonispressed)
        self.pushButton_pllconfig.clicked.connect(self.pllconfiguration)
        self.pushButton_set_att_values.clicked.connect(self.setattvalueispressed)

        #  Create emtpy object for instance from PlotWindow class
        self._plotWindow = PlotWindow(self)

        # Configuration Parameters
        self.max_freq_jitter = 100000     # 1kHz
        self.internal_clock_frequency = 62500000    # 62.5 MHz
        self.external_clock_frequency = 78000000    # 78 MHz

    def connecttoboardispressed(self):

        slotnumber = self.getslotselection()

        connection_status = deviceaccess.connecttoboard(slotnumber)

        if connection_status:
            self.textBrowser_console.append('Connection Established')
            if deviceaccess.readboardstatus() != 0:
                self.label_connectionstatus.setText('Connection Status: Connected \nBoard is Initialized')
            else:
                self.label_connectionstatus.setText('Connection Status: Connected \nBoard is not Initialized')

        else:
            self.textBrowser_console.append('Cannot connect to AMC')
            self.label_connectionstatus.setText('Connection Status: Failed')

    def initilizebuttonispressed(self):

        internalclockpreference = self.radioButton_internalclock.isChecked()
        externalclockpreference = self.radioButton_externalclock.isChecked()
        clockgenerationpreference = self.radioButton_clock_generation.isChecked()

        if internalclockpreference:
            self.textBrowser_console.append('Starting internal clock setting configuration...')
            self.progressBar.setValue(0)
            # Disable the button until init ends
            self.pushButton_initializeboard.setEnabled(False)

            # Bring board out of reset state
            self.textBrowser_console.append('Cycle Reset the FPGA')
            deviceaccess.resetboard()
            self.progressBar.setValue(10)

            # Switch to internal clock for application for short time
            self.textBrowser_console.append('Application clock gets internal fabric FPGA clock for short time')
            deviceaccess.applicationclocksource(source='internal')
            self.progressBar.setValue(15)

            self.textBrowser_console.append('Initializing the clock')
            deviceaccess.muxconfiguration(mux_config='quartz')
            self.progressBar.setValue(30)

            self.textBrowser_console.append('Configuring the PLL of SIS8300L2')
            deviceaccess.configureclockdividers(divider_input='from_muxes', division=4)
            self.progressBar.setValue(50)

            self.textBrowser_console.append('Configuring the ADCs of AMC')
            deviceaccess.configureadcs()
            self.progressBar.setValue(60)

            self.textBrowser_console.append('Configure the Triggers')
            deviceaccess.configuretiming(timing_frequency=6250000-1)
            self.progressBar.setValue(70)

            self.textBrowser_console.append('Configure the DAQ')
            deviceaccess.configureDAQ()
            self.progressBar.setValue(80)

            self.textBrowser_console.append('Releasing Interlock')
            deviceaccess.setinterlock(state=1)
            self.progressBar.setValue(85)

            self.textBrowser_console.append('Enabling DACs of SIS8300L2')
            deviceaccess.setDAC(state=1)
            self.progressBar.setValue(90)

            self.textBrowser_console.append('Setting Common Voltage for Vector Modulator')
            # Some f*cking magic number. Dont ask why
            deviceaccess.setcommonmodeDAC(value=13600)
            self.progressBar.setValue(95)

            # Switch to internal clock for application for short time
            self.textBrowser_console.append('Application gets clock coming outside of the FPGA')
            deviceaccess.applicationclocksource(source='external')
            self.progressBar.setValue(100)

            # We wait for 2 seconds to get stable frequency readout
            time.sleep(2)

            if deviceaccess.readexternalclockfrequency() - self.internal_clock_frequency < self.max_freq_jitter:
                self.textBrowser_console.append('Board Configuration Completed with internal clock setting.  '
                                                '\n Frequency = {} Hz'.format(deviceaccess.readexternalclockfrequency()))
                deviceaccess.writeboardstatus(status=1)     # Writing 1 for internal clock initialization

            else:
                self.textBrowser_console.append('Wrong clock frequency detected. \n Frequency = {} Hz'.
                                                format(deviceaccess.readexternalclockfrequency()))

            self.pushButton_initializeboard.setEnabled(True)

        elif clockgenerationpreference or externalclockpreference:

            self.textBrowser_console.append('Starting external clock configuration')
            self.progressBar.setValue(0)
            # Disable the button until init ends
            self.pushButton_initializeboard.setEnabled(False)

            # Bring board out of reset state
            self.textBrowser_console.append('Cycle Reset the FPGA')
            deviceaccess.resetboard()
            self.progressBar.setValue(10)

            # Switch to internal clock for application for short time
            self.textBrowser_console.append('Application clock gets internal fabric FPGA clock for short time')
            deviceaccess.applicationclocksource(source='internal')
            self.progressBar.setValue(12)

            if clockgenerationpreference:
                self.textBrowser_console.append('Configuring the PLL of DS8VM1 for clock generation mode...')
                deviceaccess.configureDS8VM1pll(PLLsetting='Clock Generation')
                self.progressBar.setValue(15)
            elif externalclockpreference:
                self.textBrowser_console.append('Configuring the PLL of DS8VM1 for clock distribution mode...')
                deviceaccess.configureDS8VM1pll(PLLsetting='Clock Distribution')
                self.progressBar.setValue(15)
            else:
                print 'ERROR: Invalid Configuration setting!'

            self.textBrowser_console.append('Initializing the clock')
            deviceaccess.muxconfiguration(mux_config='zone3_clock')
            self.progressBar.setValue(30)

            self.textBrowser_console.append('Configuring the PLL of SIS8300L2')
            deviceaccess.configureclockdividers(divider_input='from_RTM', division=0)
            self.progressBar.setValue(50)

            self.textBrowser_console.append('Configuring the ADCs of AMC')
            deviceaccess.configureadcs()
            self.progressBar.setValue(60)

            # We are expecting 78MHz coming from RTM hence we change our timing_frequency in order to have 10Hz trigger
            self.textBrowser_console.append('Configure the Triggers')
            deviceaccess.configuretiming(timing_frequency=7800000 - 1)
            self.progressBar.setValue(70)

            self.textBrowser_console.append('Configure the DAQ')
            deviceaccess.configureDAQ()
            self.progressBar.setValue(80)

            self.textBrowser_console.append('Releasing Interlock') # Let RF go wild
            deviceaccess.setinterlock(state=1)
            self.progressBar.setValue(85)

            self.textBrowser_console.append('Enabling DACs of SIS8300L2')
            deviceaccess.setDAC(state=1)
            self.progressBar.setValue(90)

            self.textBrowser_console.append('Setting Common Voltage for Vector Modulator')
            # Some f*cking magic number. Dont ask why
            deviceaccess.setcommonmodeDAC(value=13600)
            self.progressBar.setValue(95)

            # Switch to internal clock for application for short time
            self.textBrowser_console.append('Application gets clock coming outside of the FPGA')
            deviceaccess.applicationclocksource(source='external')
            self.progressBar.setValue(100)

            # Waiting for clock frequency readout to be stable
            time.sleep(2)

            if abs(deviceaccess.readexternalclockfrequency() - self.external_clock_frequency) < self.max_freq_jitter:
                self.textBrowser_console.append('Board Configuration Completed with external clock. '
                                                ' \n Frequency = {} Hz'.format(deviceaccess.readexternalclockfrequency()))
                if externalclockpreference:
                    # Writing 2 for external clock initialization with clock distr.
                    deviceaccess.writeboardstatus(status=2)
                elif clockgenerationpreference:
                    # Writing 3 for external clock init with clock generation
                    deviceaccess.writeboardstatus(status=3)
            else:
                self.textBrowser_console.append('Wrong clock frequency detected. \n Frequency = {} Hz'.
                                                format(deviceaccess.readexternalclockfrequency()))
                deviceaccess.writeboardstatus(status=0)  # Writing 0 for failed clock initialization

            # Make button active again
            self.pushButton_initializeboard.setEnabled(True)

        else:
            self.textBrowser_console.append('Please choose clock source first')

    def samplingbuttonispressed(self):

        # Grab the information from the UI
        channels_to_plot = self.getlistofcheckedchannels()
        is_combine_all_checked = self.checkBox_combineall.isChecked()

        # If user selected any channels for display => show _plotWindow
        if len(channels_to_plot) != 0:
            self._plotWindow.showwindow(channels_to_plot, is_combine_all_checked)

        # Stop the timers (this is here because of possibility of user pressing Start Sampling while PlotWindow is on
        self._plotWindow.stop_timers()

        # Start Refresing the data on _plotWindow
        self._plotWindow.start_refreshing(is_combine_all_checked=is_combine_all_checked, FPS=self.FPS.value(),
                                          channels_to_plot=self.getlistofcheckedchannels())

        self.textBrowser_console.append('Sampling Started')

    def resetbuttonispressed(self):
        # Reset the AMC
        self.textBrowser_console.append('Reseting the AMC')
        deviceaccess.resetboard()
        self.textBrowser_console.append('Reset Completed')

    def readboardinfoispressed(self):

        self.label_revision.setText('Firmware Revision: r{}'.format(deviceaccess.getamcrevision()))
        self.label_mainclock.setText("Main Clock Frequency: {} MHz"
                                     .format(float(deviceaccess.readexternalclockfrequency()) / 1000000))
        self.label_rtm_boardtemperature.setText("Board Temperature: {} Celcius".format(int(deviceaccess.getrtmtemperature())>>8))

        pll_status = int(deviceaccess.getrtmpllstatus())
        print pll_status

        if pll_status == 1:
            self.label_pll_status.setText("PLL Status: Locked to Reference Signal")
            self.label_pll_status_2.setText("PLL Status: Locked to Reference Signal")
        else:
            self.label_pll_status.setText("PLL Status: Not Locked")
            self.label_pll_status_2.setText("PLL Status: Not Locked")

    def setattvalueispressed(self):

        channel1_att_value_set = 63 - self.channel1_att_value.value()*2
        channel2_att_value_set = 63 - self.channel2_att_value.value()*2
        channel3_att_value_set = 63 - self.channel3_att_value.value()*2
        channel4_att_value_set = 63 - self.channel4_att_value.value()*2
        channel5_att_value_set = 63 - self.channel5_att_value.value()*2
        channel6_att_value_set = 63 - self.channel6_att_value.value()*2
        channel7_att_value_set = 63 - self.channel7_att_value.value()*2
        channel8_att_value_set = 63 - self.channel8_att_value.value()*2

        print channel1_att_value_set

        deviceaccess.setattvalues(channel1_att_value_set, channel2_att_value_set, channel3_att_value_set,
                                  channel4_att_value_set, channel5_att_value_set, channel6_att_value_set,
                                  channel7_att_value_set, channel8_att_value_set)

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
            return

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

    def getbufferlength(self):
        self._bufferlength = self.bufferlength.value()
        return self._bufferlength


class PlotWindow(QtGui.QWidget):
    def __init__(self, parent):
        super(PlotWindow, self).__init__(parent, QtCore.Qt.Window)

        # Set preferences for Plot Window
        self.setWindowTitle("ADC Data Plot")
        self.setGeometry(0, 0, 1000, 1000)

        self._checkBox_combineall = parent._checkBox_combineall
        self.console = parent._console
        self._bufferlength = parent.bufferlength

        # Construct the Grid Layout
        self.gridLayout = QtGui.QGridLayout(self)

        # Create Timer for refreshing the window
        self.timer1 = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()

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
        # This is where we refresh the data on plot
        list_of_channels_to_display = self._list_of_channels_to_display

        # Get all channels (readdma always returns all channels)
        channel_1_data, channel_2_data, channel_3_data, channel_4_data, \
        channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data = \
            deviceaccess.readdma(buffer_size=self._bufferlength.value())

        channels = [channel_1_data, channel_2_data, channel_3_data, channel_4_data,
                    channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data]

        for index in range(self.gridLayout.count()):
            self.gridLayout.itemAt(index).widget().setData(channels[list_of_channels_to_display[index]-1])

    def updateplot_combined(self):

        list_of_channels_to_display = self._list_of_channels_to_display

        channel_1_data, channel_2_data, channel_3_data, channel_4_data, \
        channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data = \
            deviceaccess.readdma(buffer_size=self._bufferlength.value())

        channels = [channel_1_data, channel_2_data, channel_3_data, channel_4_data,
                    channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data]

        self.gridLayout.itemAt(0).widget().updatedata(channels, list_of_channels=list_of_channels_to_display)

    def closeEvent(self, QCloseEvent):
        # When user closes the PlotWindow stop the timer (disconnect from updateplot method)
        self.stop_timers()
        # self._cleargridlayout()
        self.console.append('Sampling Ended')

    def stop_timers(self):
        self.timer1.stop()
        self.timer2.stop()


class CustomPlotWidget(pg.PlotWidget):

    def __init__(self, parent, channelId):
        super(CustomPlotWidget, self).__init__(parent)
        self._channelId = channelId
        self.setTitle('Channel %d' % self._channelId)
        self.setLabels(left='ADC Value', bottom='Time')

        self._plot_item = self.plot()

    def setData(self, signal):  # setData replaces the data on plot (plot(data) will overwrite)
        self._plot_item.setData(signal)


class CombinedPlotWidget(pg.GraphicsWindow):  # GraphicsWindow cannot have parent(Might be problematic)
    # This class is used when user selects combine all option from MainWindow since this time we need only one widget
    # and that widget will have multiple curves

    def __init__(self, list_of_channels):

        super(CombinedPlotWidget, self).__init__()

        self._list_of_channels = list_of_channels

        self._plot_item = self.addPlot()

        # Display Adjustment
        self._plot_item.showGrid(x=True, y=True)
        self._plot_item.setLabel('left', 'ADC Value')
        self._plot_item.setLabel('bottom', 'Time')
        self._plot_item.addLegend()

        # We have one plot item which holds 10 curves
        self._curve1_item = self._plot_item.plot(pen=(255, 0, 0),           name='Channel 1')
        self._curve2_item = self._plot_item.plot(pen=(255, 128, 0),         name='Channel 2')
        self._curve3_item = self._plot_item.plot(pen=(255, 255, 0),         name='Channel 3')
        self._curve4_item = self._plot_item.plot(pen=(128, 255, 0),         name='Channel 4')
        self._curve5_item = self._plot_item.plot(pen=(0, 255, 0),           name='Channel 5')
        self._curve6_item = self._plot_item.plot(pen=(0, 255, 128),         name='Channel 6')
        self._curve7_item = self._plot_item.plot(pen=(0, 128, 255),         name='Channel 7')
        self._curve8_item = self._plot_item.plot(pen=(0, 0, 255),           name='Channel 8')
        self._curve9_item = self._plot_item.plot(pen=(127, 0, 255),         name='DC Channel 1')
        self._curve10_item = self._plot_item.plot(pen=(255, 0, 255),        name='DC Channel 2')

        self.curves = [self._curve1_item, self._curve2_item, self._curve3_item, self._curve4_item, self._curve5_item,
                       self._curve6_item, self._curve7_item, self._curve8_item, self._curve9_item, self._curve10_item]

    def updatedata(self, signals, list_of_channels):

        for index in range(len(list_of_channels)):
            self.curves[list_of_channels[index]-1].setData(signals[list_of_channels[index]-1])


def main():
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.resize(200, 200)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
