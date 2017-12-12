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
    # [0] - internal board clock

    global boardwithmodules
    boardfrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ")
    return boardfrequency[0]


def readexternalclockfrequency():
    # provides frequency of clocks
    # [1] - external clock
    global boardwithmodules
    boardfrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ")
    return boardfrequency[1]


def readfirmwareversion():
    # TODO ask about difference between read and read_raw
    global boardwithmodules
    boardfirmware = boardwithmodules.read_raw("BOARD0", "WORD_FIRMWARE")
    return boardfirmware


def clockinitilization():
    # Configure the Muxes

    global boardwithmodules
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 3, 0)  # Mux 1A (Choose Quartz)
    time.sleep(0.01)  # Wait for 10ms
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 3, 1)  # Mux 1B (Choose Quartz)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 2)  # Mux 2A
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 3)  # Mux 2B
    time.sleep(0.01)

    # Resetting of the AD9510
    # Select internal clock to be used as a source (FPGA will use internal clock for briefly)
    # Once configuration is complete we will switch it back to external(better) clock
    boardwithmodules.write('BOARD0', 'WORD_CLK_SEL', 0)

    # Set Divider Reset Pin to function as reset
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x58))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x01), int(0x5A))
    time.sleep(0.02)

    # Reset Clock
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 0)
    time.sleep(0.01)

    # Configuration of the AD9510
    # Set Input Clock Source
    # 0 => Directly from RTM     1=> From Muxes
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', 1, int(0x45))
    time.sleep(0.01)

    # By pass the input divider
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x43), int(0x0A))
    time.sleep(0.01)

    # Enable outputs and set LVDS
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3C))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3D))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3E))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3F))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x40))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x41))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x42))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x43))
    time.sleep(0.01)

    # Enable Dividers, Synch
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x49))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x4B))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x4D))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x4F))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x51))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x53))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x55))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x57))
    time.sleep(0.01)

    # Set Dividers Value
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x48))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x4A))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x4C))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x4E))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x50))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x52))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x54))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x11), int(0x56))
    time.sleep(0.01)

    # Set Reset pin to function pin as SYNC
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x20), int(0x58))
    time.sleep(0.01)

    # Save send data
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x81), int(0x5A))
    time.sleep(0.01)

    # Send Sync
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 0)
    time.sleep(0.01)

    # Wait for Clock to Stabilize
    time.sleep(3)

    # Since External Clock is now stable, switch to it and start using it.
    boardwithmodules.write('BOARD0', 'WORD_CLK_SEL', 1)


def configureadcs():
    #   Configure the ADC via SPI Interface

    global boardwithmodules

    # Reset the FPGA
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 0)
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 1)
    time.sleep(0.5)     # Wait for 500 ms

    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x3C), int(0x00))
    time.sleep(1)       # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x01), int(0xFF))
    time.sleep(0.5)     # Wait for 500 ms

    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x41), int(0x14))
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x00), int(0x0D))
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x01), int(0xFF))

    boardwithmodules.write('BOARD0', 'WORD_ADC_ENA', 0)
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'WORD_ADC_ENA', 1)


def configuretiming(timing_frequency):
    # Configure trigger freq and DAQ

    global boardwithmodules

    # Set internal trigger freq for 10Hz (app_clk/(value+1)
    boardwithmodules.write('APP0', 'WORD_TIMING_FREQ', timing_frequency, 0)
    # Set Clock Divider for DAQ1 (app_clk/(value+1)
    boardwithmodules.write('APP0', 'WORD_TIMING_FREQ', 0, 7)
    # Select MAIN trigger line (available 8 lines)
    boardwithmodules.write('APP0', 'WORD_TIMING_TRG_SEL', 0)
    # enable internal triggers, bit0 - main trigger sleected FREQ[0] , bit7 - DAQ1 strobe enabled
    boardwithmodules.write('APP0', 'WORD_TIMING_INT_ENA', int(0x81))

    # Enable DAQ1 Application part
    # bit[0]  DAQ0 - controller
    # bit[1]  DAQ1 - field detection, IQ/AP/RAW
    boardwithmodules.write('APP0', 'WORD_DAQ_ENABLE', 2)
    boardwithmodules.write('APP0', 'WORD_DAQ_MUX', 0, 0)
    # Select for DAQ1 RAW ADC Data
    boardwithmodules.write('APP0', 'WORD_DAQ_MUX', 2, 1)

    '''
     Super Important Step (ADC Clock Phase Adjustment):
     There is a mux in front of dual ADCs that provide additional phase change. This is used when DMA region is not
     properly assigned. (When DMA region shows => Ch1 + Ch0 + Ch3 + Ch4 + Ch6 + Ch5 + Ch7 + Ch8
                         use WORD_ADC_REVERT_CLK = 0x1F (b'11111) to fix it
     Default value for WORD_ADC_REVERT_CLK = 0x18

     '''
    # ADC Clock Phase Adjustment
    boardwithmodules.write('BOARD0', 'WORD_ADC_REVERT_CLK', int(0x1F))


def resetboard():
    # Reset the board

    global boardwithmodules
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 0)
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 1)
    time.sleep(0.5)     # Wait for 500 ms


def readdma(buffer_size):
    # Read the DMA Area
    global boardwithmodules

    data = boardwithmodules.read_sequences('BOARD0', 'DMA_SECONDARY')

    channel_1_data = data[:buffer_size, 0]
    channel_2_data = data[:buffer_size, 1]
    channel_3_data = data[:buffer_size, 2]
    channel_4_data = data[:buffer_size, 3]
    channel_5_data = data[:buffer_size, 4]
    channel_6_data = data[:buffer_size, 5]
    channel_7_data = data[:buffer_size, 6]
    channel_8_data = data[:buffer_size, 7]
    channel_9_data = data[:buffer_size, 8]
    channel_10_data = data[:buffer_size, 9]

    return channel_1_data, channel_2_data, channel_3_data, channel_4_data,\
           channel_5_data, channel_6_data, channel_7_data, channel_8_data, channel_9_data, channel_10_data


def configurepll(registers):
    # Configure the PLL inside RTM

    global boardwithmodules

    for index in range(len(registers)):
        boardwithmodules.write('DS8VM1', 'WORD_PLL_DATA', int(registers[index]))
        time.sleep(1)  # Wait for 1 second


def getrtmfirmware():
    global boardwithmodules
    rtm_firmware = boardwithmodules.read("BOARD0", "WORD_FIRMWARE")
    return rtm_firmware


def getamcfirmware():
    global boardwithmodules
    amc_firmware = boardwithmodules.read("APP0", "WORD_FIRMWARE_APP")
    return amc_firmware


def getrtmrevision():
    global boardwithmodules
    rtm_revision = boardwithmodules.read("BOARD0", "WORD_REVISION")
    return rtm_revision


def getamcrevision():
    global boardwithmodules
    amc_firmware = boardwithmodules.read("APP0", "WORD_REVISION_APP")
    return amc_firmware


def setattvalues(channel1_att_value_set, channel2_att_value_set, channel3_att_value_set, channel4_att_value_set,
    channel5_att_value_set, channel6_att_value_set, channel7_att_value_set, channel8_att_value_set):

    global boardwithmodules

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000000001))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel1_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000000010))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel2_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000000100))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel3_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000001000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel4_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000010000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel5_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0000100000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel6_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0001000000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel7_att_value_set)
    time.sleep(0.01)

    boardwithmodules.write("DS8VM10", "WORD_ATT_SEL", int(0b0010000000))
    time.sleep(0.01)
    boardwithmodules.write("DS8VM10", "WORD_ATT_VAL", channel8_att_value_set)
    time.sleep(0.01)


def external_clock_initilization(PLLsetting):

    global boardwithmodules

    # reset the FPGA
    boardwithmodules.write("BOARD0", "WORD_RESET_N", 0)
    time.sleep(0.01)
    boardwithmodules.write("BOARD0", "WORD_RESET_N", 1)
    time.sleep(0.01)

    initial_clockFrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ", 1, 1)
    print("Initial Clock Frequency: " + str(initial_clockFrequency[0] / 1000000) + " MHz")

    """

    $$$$$   PLL Configuration of DS8VM1   $$$$$

    """

    print('Starting with PLL Configuration')

    # Bypassing the reference divider on DS8VM1     0x0=> divide by 1
    #                                               0x1=> divide by 2
    #                                               0x2=> divide by 3
    #                                               0x3=> divide by 4
    boardwithmodules.write('DS8VM10', 'WORD_DIV_B', 0)

    # Selecting the SMA CLK for CLKin1
    boardwithmodules.write('DS8VM10', 'WORD_VCO_MUX', 1)

    # 0 => SMA Ref goes to CLKin2 + CPout1 goes into OSCin  1 => SMA Ref goes directly into OSCin
    boardwithmodules.write('DS8VM10', 'WORD_SW_VCTL', 1)

    # Create empty array for PLL configuration data
    registers = []

    if PLLsetting == 'Clock Distribution':
        # Open the file that comes from CodeLoader
        pll_file = open('PLL_Config_Clock_Distr.txt')
        print 'Clock Distribution selected'

    elif PLLsetting == 'Clock Generation':
        pll_file = open('PLL_Config_260MHz_to_78MHz_clock.txt')
        print 'Clock generation selected'
    else:
        print('Undefined PLL Configuration')

    pll_data = pll_file.readlines()

    for line in pll_data:
        register_string = line.strip().split()  # get rid of OS dependency
        registers.append(int(register_string[-1], 16))  # Convert to int

    print('Here is all the PLL Configuration Registers: {}'.format(registers))

    for index in range(len(registers)):
        boardwithmodules.write('DS8VM10', 'WORD_PLL_DATA', registers[index])
        time.sleep(1)  # Wait for 1 second

    print('PLL Configuration is done')

    print('Configuring the clock of SIS8300L2')
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 0)  # Mux 1A (Choose RTM_CLK2)
    time.sleep(0.01)  # Wait for 10ms
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 1)  # Mux 1B (Choose RTM_CLK2)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 2)  # Mux 2A
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 3)  # Mux 2B
    time.sleep(0.01)

    # Resetting of the AD9510
    # Select internal clock to be used as a source (FPGA will use internal clock for briefly)
    # Once configuration is complete we will switch it back to external(better) clock
    boardwithmodules.write('BOARD0', 'WORD_CLK_SEL', 0)

    # Set Divider Reset Pin to function as reset
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x58))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x01), int(0x5A))
    time.sleep(0.02)

    # Reset Clock
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 0)
    time.sleep(0.01)

    # Configuration of the AD9510
    # Set Input Clock Source
    # 0 => Directly from RTM     1=> From Muxes
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', 0, int(0x45))
    time.sleep(0.01)

    # B counter bypass + FD Mode(divide by 1) + Synchronous power down
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x43), int(0x0A))
    time.sleep(0.01)

    # Setting output voltage for OUT0-3 to 660mV
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3C))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3D))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3E))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x0C), int(0x3F))
    time.sleep(0.01)

    # Choose 3.5 mA with 100 Ohm termination for OUT4-OUT7
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x40))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x41))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x42))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x02), int(0x43))
    time.sleep(0.01)

    print ('Clock dividers are OFF')
    # Bypass and power down divider logic route clock directly to output
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x49))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x4B))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x4D))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x4F))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x51))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x53))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x55))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x80), int(0x57))
    time.sleep(0.01)

    # Save send data
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x81), int(0x5A))
    time.sleep(0.01)

    # Wait for Clock to Stabilize
    time.sleep(3)

    print ('Configuring the ADCs')

    # Reset the FPGA
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 0)
    boardwithmodules.write('BOARD0', 'WORD_RESET_N', 1)
    time.sleep(0.5)  # Wait for 500 ms

    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x3C), int(0x00))
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x01), int(0xFF))
    time.sleep(0.5)  # Wait for 500 ms

    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x41), int(0x14))
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x00), int(0x0D))
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_SPI_ADC', int(0x01), int(0xFF))

    boardwithmodules.write('BOARD0', 'WORD_ADC_ENA', 0)
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'WORD_ADC_ENA', 1)

    print ('ADC Configuration DONE')
    print ('Configuring Timing (External Clock)')
    configuretiming(timing_frequency=7800000 - 1)

    clockFrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ", 1, 1)

    if (abs(clockFrequency[0] - 78000000) > 10000):
        print("*****************************************************")
        print("  Wrong clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
        print("*****************************************************")
    else:
        print("Correct clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
        # Since External Clock is now stable, switch to it and start using it.
        boardwithmodules.write('BOARD0', 'WORD_CLK_SEL', 1)


def writeboardstatus(status):
    global boardwithmodules
    boardwithmodules.write('BOARD0', 'WORD_USER', status)


def readboardstatus():
    global boardwithmodules
    boardstatus = boardwithmodules.read("BOARD0", "WORD_USER")
    return boardstatus
