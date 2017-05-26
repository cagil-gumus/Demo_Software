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

    return channel_1_data, channel_2_data, channel_3_data, channel_4_data, channel_5_data,\
           channel_6_data, channel_7_data, channel_8_data


