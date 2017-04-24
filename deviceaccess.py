'''

This python code contains the useful functions for communicating with the board via PCIe 
using mtca4u module 

read(moduleName                 ===> The name of the device module to which the register belongs to. 
                                    If the register is not contained in a module, then provide an 
                                    empty string as the parameter value
                    
    registerName                ===> The name of the register to read from.
    
    numberOfElementsToRead=0    ===> (int, optional) Specifies the number of register elements 
                                    that should be read out. The width and fixed point representation 
                                    of the register element are internally obtained from the map file.
                                
    elementIndexInRegister=0)   ===> (int, optional)  This is a zero indexed offset from the first element 
                                    of the register. When an elementIndexInRegister parameter is specified, 
                                    the method reads out elements starting from this element index. 
                                    The elemnt at the index position is included in the read as well.
                                    
read_dma_raw(moduleName, DMARegisterName, numberOfElementsToRead=0, elementIndexInRegister=0)[source]

For more information about ChimeraTK please visit: 
https://chimeratk.github.io/DeviceAccess-PythonBindings/master/mtca4u.html#mtca4u.Device.read

Written by: Cagil Gumus 
email: cagil.guemues@desy.de
Date: 24.04.2017
                                                                    
'''



import mtca4u
import time     # Needed for delay operation
import numpy

mtca4u.set_dmap_location('dmapfile.dmap')
boardwithmodules = mtca4u.Device('HZDR')


def readinternalclockfrequency():
    # provides frequency of clocks
    # [0] - internal board clock

    boardfrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ")
    return boardfrequency[0]


def readexternalclockfrequency():
    # provides frequency of clocks
    # [1] - external clock

    boardfrequency = boardwithmodules.read("BOARD0", "WORD_CLK_FREQ")
    return boardfrequency[1]


def readfirmwareversion():
    boardfirmware = boardwithmodules.read_raw("BOARD0", "WORD_FIRMWARE")
    return boardfirmware


def clockinitilization():

    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 3, 0)
    time.sleep(0.01)  # Wait for 10ms
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 3, 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 2)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_MUX', 0, 3)
    time.sleep(0.01)

    # Resetting of the AD9510
    # Select internal clock to be used as a source
    boardwithmodules.write('BOARD0', 'WORD_CLK_SEL', 0)

    # Set Divider Reset Pin to function as reset
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x00), int(0x58))
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', int(0x01), int(0x5A))
    time.sleep(0.02)

    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 1)
    time.sleep(0.01)
    boardwithmodules.write('BOARD0', 'WORD_CLK_RST', 0)
    time.sleep(0.01)

    # Configuration of the AD9510
    boardwithmodules.write('BOARD0', 'AREA_SPI_DIV', 1, int(0x45))
    time.sleep(0.01)


def sis_adc():
    #   Configure the ADC via SPI Interface

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

    boardwithmodules.write('BOARD0', 'AREA_ADC_ENA', 0)
    time.sleep(1)  # Wait for 1 second
    boardwithmodules.write('BOARD0', 'AREA_ADC_ENA', 1)




print(readfirmwareversion())