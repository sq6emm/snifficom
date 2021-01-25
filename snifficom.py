#!/usr/bin/env python3

import serial

icom = serial.Serial('/dev/ic7300-remote', 19200, timeout=0)

def decode(input):
  if input[2] == 0x0 and len(input) == 8 and input[7] == 0x0: return("rx", rigfreq(input,3))
  elif input[2] == 0x1c and input[3] == 0 and input[4] == 0: return("ptt off")
  elif input[2] == 0x1c and input[3] == 0 and input[4] == 1: return("ptt on")
  elif input[2] == 0x1c and input[3] == 3 and len(input) == 9 and input[8] == 0x0: return("tx", rigfreq(input,4))
  else: return(None)

def rigfreq(input, start):
  freq = (input[start] & 0x0F) + (((input[start] >> 4) & 0x0F) * 10) + ((input[start+1] & 0x0F) * 100) + (((input[start+1] >> 4) & 0x0F) * 1000) + ((input[start+2] & 0x0F) * 10000) + (((input[start+2] >> 4) & 0x0F) * 100000) + ((input[start+3] & 0x0F) * 1000000) + (((input[start+3] >> 4) & 0x0F) * 10000000) + ((input[start+4] & 0x0F) * 100000000) + (((input[start+4] >> 4) & 0x0F) * 1000000000)
  return(freq, opband(freq))

def opband(input):
  if input >= 135700 and input <= 135800: band="2200m"
  elif input >= 472000 and input <= 479000: band="630m"
  elif input >= 1810000 and input <= 2000000: band="160m"
  elif input >= 3500000 and input <= 3800000: band="80m"
  elif input >= 5351500 and input <= 5366500: band="60m"
  elif input >= 7000000 and input <= 7200000: band="40m"
  elif input >= 10100000 and input <= 10150000: band="30m"
  elif input >= 14000000 and input <= 14350000: band="20m"
  elif input >= 18068000 and input <= 18168000: band="17m"
  elif input >= 21000000 and input <= 21450000: band="15m"
  elif input >= 24890000 and input <= 24990000: band="12m"
  elif input >= 28000000 and input <= 29700000: band="10m"
  elif input >= 50000000 and input <= 52000000: band="6m"
  elif input >= 70000000 and input <= 70500000: band="4m"
  else: band=None
  return band

def readFromIcom():
  result = b''
  while True:
    data = icom.read(1)
    if len(data):
      result = result + data
      if data == b'\xfd':
        if result[0] == 254 and result[1] == 254:
          temp=result[4:len(result)-1]
          for i in range(len(temp)):
            if temp[i] == 254 or temp[i] == 253:
              result = b''
          return(result[2:len(result)-1])
        result = b''

while True:
  outp = readFromIcom()
  if outp:
    if outp[0] == 0x00 or outp[0] == 0x01:
      result = decode(outp)
      if result:
        print(result)
