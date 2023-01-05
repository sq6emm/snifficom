#!/usr/bin/env -S python3 -u

import serial
import time
import threading
import socket
from dicttoxml import dicttoxml
import atuset
import atusettings

last_update = time.time()-6 # always start with old data
ready_to_send = False

radioinfo = {
  "app": "SniffICOM",
  "StationName": "SN6M",
  "RadioNr": 1,
  "Freq": 1417000,
  "TXFreq": 141700,
  "Mode": "",
  "OpCall": "SN6M",
  "IsRunning": "False",
  "FocusEntry": "",
  "EntryWindowHwnd": "",
  "Antenna": 1,
  "Rotors": "",
  "FocusRadioNr": 1,
  "IsStereo": "False",
  "IsSplit": "False",
  "ActiveRadioNr": 1,
  "IsTransmitting": "False",
  "FunctionKeyCaption": "",
  "RadioName": "",
  "AuxAntSelected": -1,
  "AuxAntSelectedName": "",
  "IsConnected": ""
}

icomRemote = serial.Serial('/dev/ttyAMA0', 19200, timeout=None)
icomUSB = serial.Serial('/dev/ic7610a', 19200, timeout=None)

def decode(input):
  if   input[0] == 0x00: return("rx", rigfreq(input,1), opband(rigfreq(input,1)))
  elif input[0] == 0x03: return("rx", rigfreq(input,1), opband(rigfreq(input,1)))
  elif input[0] == 0x1c and input[1] == 0 and input[2] == 0: return("ptt off")
  elif input[0] == 0x1c and input[1] == 0 and input[2] == 1: return("ptt on")
  elif input[0] == 0x1c and input[1] == 3: return("tx", rigfreq(input,2), opband(rigfreq(input,2)))
  else: return(None)

def rigfreq(input, start):
  freq = (input[start] & 0x0F) + (((input[start] >> 4) & 0x0F) * 10) + ((input[start+1] & 0x0F) * 100) + (((input[start+1] >> 4) & 0x0F) * 1000) + ((input[start+2] & 0x0F) * 10000) + (((input[start+2] >> 4) & 0x0F) * 100000) + ((input[start+3] & 0x0F) * 1000000) + (((input[start+3] >> 4) & 0x0F) * 10000000) + ((input[start+4] & 0x0F) * 100000000) + (((input[start+4] >> 4) & 0x0F) * 1000000000)
  return(freq)

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

def civFrameValidate(input):
  last = len(input)-1
  if input[0] == 0xfe and input[1] == 0xfe and input[3] == 0x98 and input[last] == 0xfd:
    return(input[4:last])
  else:
    return(None)

def readFromIcomRemote():
  result = icomRemote.read_until(bytes.fromhex("fd"))
  return(civFrameValidate(result))

def readFromIcomUSB():
  result = icomUSB.read_until(bytes.fromhex("fd"))
  return(civFrameValidate(result))

def UDPBroadCast():
  global last_update
  global radioinfo
  global ready_to_send
  UDP_IP = "192.168.253.255"
  UDP_PORT = 12060
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  sock.connect((UDP_IP, UDP_PORT))
  while True:
    if (time.time() - last_update > 0.2) and ready_to_send == True:
      MESSAGE = dicttoxml(radioinfo,custom_root="RadioInfo",attr_type=False)
      sock.send(MESSAGE)
      last_update = time.time()
      ready_to_send = False

def MainLoop():
  global radioinfo
  global ready_to_send
  band = None
  while True:
    outp = readFromIcomUSB()
    if outp:
      result = decode(outp)
      if result:
        band_old = band
        band = result[2]
        #print(result)
        if result[0] == "tx" or result[0] == "rx":
          radioinfo["TXFreq"] = int(int(result[1])/10)
          radioinfo["Freq"] = int(int(result[1])/10)
          ready_to_send = True
        if result[0] == "tx" and ( band == "160m" or band == "80m" ):
          atufreq=round(round(result[1]/1000),-1)
          if band != band_old:
            atuset.setC(0)
            atuset.setL(0)
            #print(band,band_old)
          hl = atusettings.atudata[atufreq][0]
          c = atusettings.atudata[atufreq][1]
          l = atusettings.atudata[atufreq][2]
          atuset.setCside(hl)
          atuset.setC(c)
          atuset.setL(l)
          #print(atufreq,hl,c,l)

def WatchdogLoop():
  global radioinfo
  global last_update
  global ready_to_send
  while True:
    if (time.time() - last_update > 9):
      data = 'fefe98e003fd'
      icomUSB.write(bytes.fromhex(data));
      icomUSB.flush();
      time.sleep(9)

def Main():
    t1 = threading.Thread(target = MainLoop)
    t2 = threading.Thread(target = WatchdogLoop)
    t3 = threading.Thread(target = UDPBroadCast)
    t1.start()
    t2.start()
    t3.start()

if __name__ == '__main__':

    Main()
