'''

This python code contains the useful functions for communicating with the board via PCIe
using mtca4u module

Written by: Cagil Gumus
email: cagil.guemues@desy.de
Date: 24.04.2017

'''

import mtca4u
import time     # Needed for delay operation
import sys
import numpy as np
import pyqtgraph as pg


# Create empty object for the board (Later it will be overwritten by connecttoboard method)
boardwithmodules = None


def connecttoboard(slotnumber):
    #TODO When you are connecting to board make sure the right firmware is there otherwise throw error

    try:
        mtca4u.set_dmap_location('devices.dmap')
        global boardwithmodules
        boardwithmodules = mtca4u.Device('Slot{}'.format(slotnumber))
        return True

    except:     # Catch all expections

        # print('Cannot connect to the board')
        return False


def readinternalclockfrequency():
    # provides frequency of clocks
    # [0] - internal Fabric clock

    global boardwithmodules
    boardfrequency = boardwithmodules.read("BOARD.0", "WORD_CLK_FREQ")
    return boardfrequency[0]


def readexternalclockfrequency():
    # provides frequency of clocks
    # [1] - external clock
    global boardwithmodules
    boardfrequency = boardwithmodules.read("BOARD.0", "WORD_CLK_FREQ")
    return boardfrequency[1]


def readfirmwareversion():
    # TODO ask about difference between read and read_raw
    global boardwithmodules
    boardfirmware = boardwithmodules.read_raw("BOARD.0", "WORD_FIRMWARE")
    return boardfirmware


def configureDS8VM1pll(PLLsetting):
    global boardwithmodules

    # Bypassing the reference divider on DS8VM1     0x0=> divide by 1
    #                                               0x1=> divide by 2
    #                                               0x2=> divide by 3
    #                                               0x3=> divide by 4
    boardwithmodules.write('DS8VM1.0', 'WORD_DIV_B', 0)

    # Selecting the SMA CLK for CLKin1
    boardwithmodules.write('DS8VM1.0', 'WORD_VCO_MUX', 1)

    # 0 => SMA Ref goes to CLKin2 + CPout1 goes into OSCin  1 => SMA Ref goes directly into OSCin
    boardwithmodules.write('DS8VM1.0', 'WORD_SW_VCTL', 1)

    # Create empty array for PLL configuration data
    registers = []

    if PLLsetting == 'Clock Distribution':
        # Open the file that comes from CodeLoader
        pll_file = open('PLL_Config_Clock_Distr.txt')

    elif PLLsetting == 'Clock Generation':
        pll_file = open('PLL_config_260MHz_to_78MHz_clock.txt')
    else:
        print('Undefined PLL Configuration')

    pll_data = pll_file.readlines()

    for line in pll_data:
        register_string = line.strip().split()  # get rid of OS dependency
        registers.append(int(register_string[-1], 16))  # Convert to int

    for index in range(len(registers)):
        boardwithmodules.write('DS8VM1.0', 'WORD_PLL_DATA', registers[index])
        time.sleep(0.1)  # Wait for 1 second


def muxconfiguration(mux_config):
    # Configure the 853S057AGILF to feed clock into AD9510
    # 2 options available:
    # 'quartz' => Feed on-board quartz clock to AD9510
    # 'zone3_clock' => Feed clock coming from Zone 3 (from RTM) to AD9510
    # 'backplane_CLK1' => Choose clock coming from backplane of MTCA Crate (CLK1)

    global boardwithmodules

    if mux_config == 'quartz':

        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 3, 0)  # Mux 1A (Choose Quartz)
        time.sleep(0.01)  # Wait for 10ms
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 3, 1)  # Mux 1B (Choose Quartz)
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 2)  # Mux 2A
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 3)  # Mux 2B
        time.sleep(0.01)
    elif mux_config == 'zone3_clock':

        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 0)  # Mux 1A (Choose RTM Clock)
        time.sleep(0.01)  # Wait for 10ms
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 1)  # Mux 1B (Choose RTM Clock)
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 2)  # Mux 2A
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 3)  # Mux 2B
        time.sleep(0.01)

    elif mux_config == 'backplane_CLK1':

        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 2, 0)  # Mux 1A (Choose Quartz)
        time.sleep(0.01)  # Wait for 10ms
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 2, 1)  # Mux 1B (Choose Quartz)
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 2)  # Mux 2A
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'WORD_CLK_MUX', 0, 3)  # Mux 2B
        time.sleep(0.01)
    else :
        print("Error: Invalid Mux Configuration Setting!")


def configureclockdividers(divider_input,division):
    # Configure the PLL inside the SIS8300L2

    global boardwithmodules

    # Select internal clock to be used as a source (FPGA will use internal clock for briefly)
    # Once configuration is complete we will switch it back to external(better) clock
    boardwithmodules.write('BOARD.0', 'WORD_CLK_SEL', 0)

    # Set Divider FUNCTION Pin to function as resetb
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x58))
    time.sleep(0.01)
    # Update Registers of AD9510
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x01), int(0x5A))
    time.sleep(0.02)

    # Reset PLL by using FUNCTION pin to restore to default state (just in case if it was badly configured)
    boardwithmodules.write('BOARD.0', 'WORD_CLK_RST', 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'WORD_CLK_RST', 0)
    time.sleep(0.01)


    # Configuration of the AD9510
    # Set Input Clock Source
    # 0 => Directly from RTM     1=> From Muxes
    if divider_input == 'from_muxes':
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', 1, int(0x45))
        time.sleep(0.01)

    elif divider_input == 'from_RTM' :
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', 0, int(0x45))
        time.sleep(0.01)
    else:
        print 'ERROR: Invalid Divider Input selection'

    # PLL Power Down Mode is set to: Synchronous Power Down, PreScaler Mode -> Divider Value set to 1,
    # B Counter bypassed
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x43), int(0x0A))
    time.sleep(0.01)

    # Enable outputs, set 660mV output single ended voltage level for LVPECL outputs
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x0C), int(0x3C))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x0C), int(0x3D))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x0C), int(0x3E))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x0C), int(0x3F))
    time.sleep(0.01)

    # LVDS/CMOS ON, 3.5mA output current with 100 ohm termination
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x02), int(0x40))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x02), int(0x41))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x02), int(0x42))
    time.sleep(0.01)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x02), int(0x43))
    time.sleep(0.01)

    if division == 0:
        # Bypass and power down divider logic; route clock directly to output
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x49))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x4B))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x4D))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x4F))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x51))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x53))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x55))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x80), int(0x57))
        time.sleep(0.01)
    elif division == 4:
        # Enable Dividers, Synch
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x49))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x4B))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x4D))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x4F))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x51))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x53))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x55))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x00), int(0x57))
        time.sleep(0.01)

        # Set Dividers Value
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x48))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x4A))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x4C))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x4E))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x50))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x52))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x54))
        time.sleep(0.01)
        boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x11), int(0x56))
        time.sleep(0.01)
    else:
        print 'ERROR: Invalid Division value!'


    # Update Registers
    boardwithmodules.write('BOARD.0', 'AREA_SPI_DIV', int(0x1), int(0x5A))
    time.sleep(0.01)

    # Wait for Clock to Stabilize
    time.sleep(1)


def configureadcs():
    #   Configure the ADC via SPI Interface

    global boardwithmodules

    boardwithmodules.write('BOARD.0', 'AREA_SPI_ADC', int(0x3C), int(0x00))
    time.sleep(0.1)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_ADC', int(0x01), int(0xFF))
    time.sleep(0.1)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_ADC', int(0x41), int(0x14))
    time.sleep(0.1)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_ADC', int(0x00), int(0x0D))
    time.sleep(0.1)
    boardwithmodules.write('BOARD.0', 'AREA_SPI_ADC', int(0x01), int(0xFF))
    time.sleep(0.1)
    boardwithmodules.write('BOARD.0', 'WORD_ADC_ENA', 1)


def configuretiming(timing_frequency):
    # Configure trigger freq and DAQ

    global boardwithmodules

    # Select first line as MAIN trigger  (available 8 lines)
    boardwithmodules.write('APP.0', 'WORD_TIMING_TRG_SEL', 0)

    # First trigger line will use application clock as trigger line
    boardwithmodules.write('APP.0', 'WORD_TIMING_INT_ENA', 1)

    # Set trigger freq for application to 10Hz (app_clk/(value+1)
    boardwithmodules.write('APP.0', 'WORD_TIMING_FREQ', timing_frequency, 0)


def configureDAQ():
    global boardwithmodules

    # Enable DAQ1 Application part
    # bit[0]  DAQ0 - controller
    # bit[1]  DAQ1 - field detection, IQ/AP/RAW
    boardwithmodules.write('APP.0', 'WORD_DAQ_ENABLE', 2)

    # Select for DAQ1 RAW ADC Data
    boardwithmodules.write('APP.0', 'WORD_DAQ_MUX', 2, 1)

    # DAQ1 will have 16384 samples on each transaction
    boardwithmodules.write('APP.0', 'WORD_DAQ_SAMPLES', 16384, 1)

    # Divider value for DAQ strobe is 1 => DAQ1 will be strobed with same freq as main trigger line (app_clock)
    boardwithmodules.write('APP.0', 'WORD_DAQ_FREQ', 0, 1)

    # '''
    #  Super Important Step (ADC Clock Phase Adjustment):
    #  There is a mux in front of dual ADCs that provide additional phase change. This is used when DMA region is not
    #  properly assigned. (When DMA region shows => Ch1 + Ch0 + Ch3 + Ch4 + Ch6 + Ch5 + Ch7 + Ch8
    #                      use WORD_ADC_REVERT_CLK = 0x1F (b'11111) to fix it
    #  Default value for WORD_ADC_REVERT_CLK = 0x18
    #
    #  '''
    # # # ADC Clock Phase Adjustment
    # # boardwithmodules.write('BOARD.0', 'WORD_ADC_REVERT_CLK', int(0x1F))


def resetboard():
    # Reset the board

    global boardwithmodules
    boardwithmodules.write('BOARD.0', 'WORD_RESET_N', 0)
    boardwithmodules.write('BOARD.0', 'WORD_RESET_N', 1)
    time.sleep(0.5)     # Wait for 500 ms


def readdma(buffer_size):
    # Read the DMA Area
    global boardwithmodules

    data = boardwithmodules.read_sequences('APP.0', 'DAQ1_BUF0_RAW')

    channel_1_data = data[:buffer_size, 1]
    channel_2_data = data[:buffer_size, 0]
    channel_3_data = data[:buffer_size, 3]
    channel_4_data = data[:buffer_size, 2]
    channel_5_data = data[:buffer_size, 5]
    channel_6_data = data[:buffer_size, 4]
    channel_7_data = data[:buffer_size, 7]
    channel_8_data = data[:buffer_size, 6]
    channel_9_data = data[:buffer_size, 9]
    channel_10_data = data[:buffer_size, 8]

    return channel_1_data, channel_2_data, channel_3_data, channel_4_data,\
           channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data


def configurepll(registers):
    # Configure the PLL inside RTM

    global boardwithmodules

    for index in range(len(registers)):
        boardwithmodules.write('DS8VM1.0', 'WORD_PLL_DATA', int(registers[index]))
        time.sleep(1)  # Wait for 1 second


def getamcrevision():
    global boardwithmodules
    amc_firmware = int(boardwithmodules.read("BOARD.0", "WORD_REVISION")) >> 16
    return amc_firmware


def getrtmtemperature():
    global boardwithmodules
    rtm_temperature = boardwithmodules.read("DS8VM1.0", "WORD_TEMP_E")
    return  rtm_temperature


def getrtmpllstatus():
    global boardwithmodules
    pll_status = boardwithmodules.read("DS8VM1.0", "WORD_IO_STATUS")
    return pll_status


def setattvalues(channel1_att_value_set, channel2_att_value_set, channel3_att_value_set, channel4_att_value_set,
    channel5_att_value_set, channel6_att_value_set, channel7_att_value_set, channel8_att_value_set):

    global boardwithmodules

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000000001))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel1_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000000010))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel2_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000000100))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel3_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000001000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel4_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000010000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel5_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0000100000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel6_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0001000000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel7_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM1.0", "WORD_ATT_SEL", int(0b0010000000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM1.0", "WORD_ATT_VAL", channel8_att_value_set)
    time.sleep(0.01)


def writeboardstatus(status):
    global boardwithmodules
    boardwithmodules.write('BOARD.0', 'WORD_USER', status)


def readboardstatus():
    global boardwithmodules
    boardstatus = boardwithmodules.read('APP.0', "WORD_USER")
    return boardstatus


def applicationclocksource(source):
    # Choose which clock domain will be used for application part of the firmware
    global boardwithmodules

    if source == 'external':
        boardwithmodules.write('BOARD.0', 'WORD_CLK_SEL', 1)
    elif source == 'internal':
        boardwithmodules.write('BOARD.0', 'WORD_CLK_SEL', 0)
    else:
        print 'Invalid Selection for App Clock'


def setinterlock(state):
    # When CON_RTM_INTERLOCK_NEGATE = 0 => WORD_INTERLOCK = 1 means drive is permitted
    global boardwithmodules
    boardwithmodules.write('DS8VM1.0', 'WORD_INTERLOCK', state)


def setDAC(state):
    # Enable/Disable DACs of SIS8300L2
    global boardwithmodules
    boardwithmodules.write('BOARD.0', 'WORD_DAC_ENA', state)


def setcommonmodeDAC(value):
    # DAC for VM inside DS8VM1
    global boardwithmodules
    boardwithmodules.write('DS8VM1.0', 'WORD_DAC_A', value)
    time.sleep(0.01)
    boardwithmodules.write('DS8VM1.0', 'WORD_DAC_B', value)


def disablelimiters():
    global boardwithmodules
    boardwithmodules.write('FD.0', 'WORD_AMP_LIMIT_DISABLE', int(0xFF))


def updateFFtable(I, Q):
    global boardwithmodules

    # FF_I = np.full(shape=[16384], fill_value=I)
    # FF_Q = np.full(shape=[16384], fill_value=Q)
    #
    # print FF_I
    # print FF_Q
    #
    # boardwithmodules.write('CTABLES.0', 'AREA_FF_I', FF_I)
    # boardwithmodules.write('CTABLES.0', 'AREA_FF_Q', FF_Q)
    #
    # for index in range(0, 16383):
    #     boardwithmodules.write('CTABLES.0', 'AREA_FF_I', I, index)
    #     boardwithmodules.write('CTABLES.0', 'AREA_FF_Q', Q, index)

    #
    # # Swap the buffers inside the FPGA
    # boardwithmodules.write('CTABLES.0', 'BIT_CTL_TABLES_BUF', 1)
    # time.sleep(0.1)
    # boardwithmodules.write('CTABLES.0', 'BIT_CTL_TABLES_BUF', 0)

def enablefeedforward(status):
    # Enable/Disable Feed Forward 1 => Enable 0=> Disable

    global boardwithmodules
    boardwithmodules.write('CTRL.0', 'BIT_FF_ENA', int(status))
