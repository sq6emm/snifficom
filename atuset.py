#!/usr/bin/env -S python3 -u

# The most important document to base on:
# http://g3ynh.info/zdocs/z_matching/index.html

import smbus
import time
import sys
import math

# Define registers values from datasheet
IODIRA = 0x00  # IO direction A - 1= input 0 = output
IODIRB = 0x01  # IO direction B - 1= input 0 = output    
IPOLA = 0x02  # Input polarity A
IPOLB = 0x03  # Input polarity B
GPINTENA = 0x04  # Interrupt-onchange A
GPINTENB = 0x05  # Interrupt-onchange B
DEFVALA = 0x00  # Default value for port A
DEFVALB = 0x00  # Default value for port B
INTCONA = 0x08  # Interrupt control register for port A
INTCONB = 0x09  # Interrupt control register for port B
IOCON = 0x0A  # Configuration register
GPPUA = 0x0C  # Pull-up resistors for port A
GPPUB = 0x0D  # Pull-up resistors for port B
INTFA = 0x0E  # Interrupt condition for port A
INTFB = 0x0F  # Interrupt condition for port B
INTCAPA = 0x10  # Interrupt capture for port A
INTCAPB = 0x11  # Interrupt capture for port B
GPIOA = 0x12  # Data port A
GPIOB = 0x13  # Data port B
OLATA = 0x14  # Output latches A
OLATB = 0x15  # Output latches B

i2cbus = smbus.SMBus(1)  # Create a new I2C bus
mcp1 = 0x27  # Address of MCP23017 device
mcp2 = 0x20  # Address of MCP23017 device

i2cbus.write_byte_data(mcp1, IOCON, 0x02)  # Update configuration register
i2cbus.write_byte_data(mcp1, IODIRA, 0x00)  # Set Port A as outputs
i2cbus.write_byte_data(mcp1, IODIRB, 0x00)  # Set Port B as outputs
i2cbus.write_byte_data(mcp1, GPIOA, 0) # Make sure all outputs are LOW
i2cbus.write_byte_data(mcp1, GPIOB, 0) # Make sure all outputs are LOW

i2cbus.write_byte_data(mcp2, IOCON, 0x02)  # Update configuration register
i2cbus.write_byte_data(mcp2, IODIRA, 0x00)  # Set Port A as outputs
i2cbus.write_byte_data(mcp2, IODIRB, 0x00)  # Set Port B as outputs
i2cbus.write_byte_data(mcp2, GPIOA, 0) # Make sure all outputs are LOW
i2cbus.write_byte_data(mcp2, GPIOB, 0) # Make sure all outputs are LOW

def setL(val):
  if val == None: val = 0
  i2cbus.write_byte_data(mcp1, GPIOB, val)
  time.sleep(0.01)
  rval=i2cbus.read_byte_data(mcp1, GPIOB)
  return("L", rval, format(rval, "08b"))

def setC(val):
  if val == None: val = 0
  i2cbus.write_byte_data(mcp1, GPIOA, val)
  time.sleep(0.01)
  rval=i2cbus.read_byte_data(mcp1, GPIOA)
  return("C", rval, format(rval, "08b"))

def setCside(impedance):
  if impedance == "CANT": val = 1
  elif impedance == "CTRX": val = 0
  else: return(None)

  i2cbus.write_byte_data(mcp2, GPIOA, val)
  time.sleep(0.01)
  rval=i2cbus.read_byte_data(mcp2, GPIOA)
  return(impedance, rval, format(rval, "08b")) # poprawic, aby odczytac i zwrocic wartosc mcp2.A0

def clearAll():
  i2cbus.write_byte_data(mcp2, GPIOA, 0) # poprawic, aby czyscic tylko mcp2.A0
  i2cbus.write_byte_data(mcp1, GPIOA, 0)
  i2cbus.write_byte_data(mcp1, GPIOB, 0)
  time.sleep(0.01)
