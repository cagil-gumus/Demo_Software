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
    boardfirmware = boardwithmodules.read("BOARD0", "WORD_FIRMWARE")
    return boardfirmware


def initilazeboard():
    pass

