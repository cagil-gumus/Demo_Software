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


def configuretiming():
    # Configure trigger freq and DAQ

    global boardwithmodules

    # Set internal trigger freq for 10Hz (app_clk/(value+1)
    boardwithmodules.write('APP0', 'WORD_TIMING_FREQ', 6250000-1, 0)
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

    pass

    # global boardwithmodules
    #
    # for index in len(registers):
    #     boardwithmodules.write('BOARD0', 'WORD_PLL_DATA', int(registers[index]))
    #     time.sleep(1)  # Wait for 1 second


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


def external_clock_initilization():
    pass

    # global boardwithmodules
    #
    # status = boardwithmodules.read_raw("BOARD0", "WORD_BOOT_STATUS")
    #
    # if status == 0:
    #     print("Performing full initialisation...")
    #
    #     boardwithmodules.write("BOARD0", "WORD_ADC_REVERT_CLK", 0x18)
    #     time.sleep(0.01)
    #
    #     # reset clock division ICs
    #     boardwithmodules.write("BOARD0", "WORD_CLK_SEL", 0)
    #     time.sleep(0.01)
    #     boardwithmodules.write("BOARD0", "WORD_CLK_RST", 1)
    #     time.sleep(0.01)
    #     boardwithmodules.write("BOARD0", "WORD_CLK_RST", 0)
    #     time.sleep(0.01)
    #
    #     # programm clock mux
    #     # muxData = [3, 3, 0, 0, 0, 0]  # original HZDR server
    #     muxData = [0, 0, 3, 3, 0, 0]  # XFEL/FLASH gun server
    #     boardwithmodules.write("BOARD0", "WORD_CLK_MUX", muxData)
    #     time.sleep(0.01);
    #
    #     # SPI programming of the clock distribution IC
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0, 0x45)
    #     time.sleep(0.01);
    #     # boardwithmodules.write("BOARD0","AREA_SPI_DIV", 1, 0x0A)  # original HZDR server
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x43, 0x0A)  # XFEL/FLASH gun server
    #     time.sleep(0.01);
    #     # 810 mV LVDS swing
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x0C, 0x3C)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x0C, 0x3D)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x0C, 0x3E)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x0C, 0x3F)
    #     time.sleep(0.01);
    #     # 3.5 mA current
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 2, 0x40)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 2, 0x41)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 2, 0x42)
    #     time.sleep(0.01);
    #     # boardwithmodules.write("BOARD0","AREA_SPI_DIV", 0x80, 0x43)  # original HZDR server
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 2, 0x43)  # XFEL/FLASH gun server
    #     time.sleep(0.01);
    #     # bypass the divider
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x49)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x4B)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x4D)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x4F)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x51)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x53)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x55)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 0x80, 0x57)
    #     time.sleep(0.01);
    #     # update
    #     boardwithmodules.write("BOARD0", "AREA_SPI_DIV", 1, 0x5A)
    #     time.sleep(0.01);
    #
    #     # check clock frequency
    #     time.sleep(5)
    #     clockFrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ", 1, 1)
    #     if (abs(clockFrequency[0] - 81250000) > 10000):
    #         print("*****************************************************")
    #         print("  Wrong clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
    #         print("*****************************************************")
    #         sys.exit(1)
    #
    #     print("Correct clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
    #
    #     # external clock for application part
    #     boardwithmodules.write("BOARD0", "WORD_CLK_SEL", 1)
    #     time.sleep(0.01)
    #
    #     # reset the board
    #     boardwithmodules.write("BOARD0", "WORD_RESET_N", 0)
    #     time.sleep(0.01)
    #     boardwithmodules.write("BOARD0", "WORD_RESET_N", 1)
    #     time.sleep(0.01)
    #
    #     # program ADCs via SPI
    #     boardwithmodules.write("BOARD0", "AREA_SPI_ADC", 0x3C, 0x00)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_ADC", 0x41, 0x14)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_ADC", 0x00, 0x0D)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "AREA_SPI_ADC", 0x01, 0xFF)
    #     time.sleep(0.01);
    #
    #     # reset ADCs after programming clocks
    #     boardwithmodules.write("BOARD0", "WORD_ADC_ENA", 0)
    #     time.sleep(0.01);
    #     boardwithmodules.write("BOARD0", "WORD_ADC_ENA", 1)
    #     time.sleep(0.01);
    #
    #     # reset the board
    #     boardwithmodules.write("BOARD0", "WORD_RESET_N", 0)
    #     time.sleep(0.01)
    #     boardwithmodules.write("BOARD0", "WORD_RESET_N", 1)
    #     time.sleep(0.01)
    #
    #     # initialise timing registers
    #     boardwithmodules.write("APP0", "WORD_TIMING_INT_ENA", int('11111000', 2))
    #     boardwithmodules.write("APP0", "WORD_TIMING_FREQ", [499999, 2499999, 8, 8, 8, 8, 8, 8])
    #
    #     # configure trigger
    #     boardwithmodules.write("APP0", "WORD_TIMING_TRG_SEL", 1)  # must match x2timer configuration
    #
    #     # enable and configure DAQ
    #     boardwithmodules.write("APP0", "WORD_DAQ_ENABLE", 3)
    #     boardwithmodules.write("APP0", "WORD_DAQ_MUX", [0, 1])
    #
    #     # # enable DAC
    #     # boardwithmodules.write("BOARD0", "WORD_DAC_ENA", 1)
    #     # time.sleep(0.01)
    #     #
    #     # # program common mode DAC for VM
    #     # boardwithmodules.write("DS8VM1", "WORD_DACAB", 850)
    #     #
    #     # # write BOOT_STATUS flag to speed up initialisation on next server start
    #     # boardwithmodules.write("BOARD0", "WORD_BOOT_STATUS", 1)
    #
    # elif status == 1:
    #     print("Performing quick initialisation...")
    #
    #     clockFrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ", 1, 1)
    #     if (abs(clockFrequency[0] - 65000000) > 10000):
    #         print("*****************************************************")
    #         print("  Wrong clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
    #         print("*****************************************************")
    #         sys.exit(1)
    #
    #     print("Correct clock frequency detected: " + str(clockFrequency[0] / 1000000) + " MHz")
    #
    # else:
    #     print("*****************************************************")
    #     print("  Unexpected content of WORD_BOOT_STATUS found: " + str(status[0]))
    #     print("  PCIe communication problems?")
    #     print("*****************************************************")
    #
    # print("Initialisation complete.")