import webiopi
import time
from subprocess import *
import json
from time import sleep, strftime
from datetime import datetime
from webiopi import deviceInstance
from array import *
from random import randint
GPIO = webiopi.GPIO

tsl = deviceInstance("tsl")


#Raspberry Pi GPIO pin numbers assigned to variables
LCD_RS = 7
LCD_E = 8
LCD_D4 = 11
LCD_D5 = 9
LCD_D6 = 10
LCD_D7 = 25

#Other LCD variables (code used thanks to RaspberryPiIVBeginners from youtube.com)
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.00005
E_DELAY = 0.00005

global threshold
threshold = 200
global highestLight
highestLight = 0
global difference
difference = 0
global luminosity
global fileContent
global calibrationSleepTime
calibrationSleepTime = 2
timeSleep = 5.0
global timeSleep

#index 0 - calibration (first launch = 1)
#index 1 - difference
#index 2 - highestLight
#index 3 - last config manual/auto (0/1 respectively)
#index 4 - last threshold
#index 5 - time to sleep
fileContent = ["0","0","0","1","0","0"]


#autoEnabled variable, is true, when automatic light control mode is enabled
global autoEnabled
autoEnabled = True

#Lamp GPIO pin numbers
lamp1 = 4
lamp2 = 17
lamp3 = 18
lamp4 = 22

gpioArray = array('i', [4,17,18,22])
onArray = array('b', [False, False, False, False])

#Function called to set the lamp GPIOs to OUT
def setFunction():
  GPIO.setFunction(lamp1, GPIO.OUT)
  GPIO.setFunction(lamp2, GPIO.OUT)
  GPIO.setFunction(lamp3, GPIO.OUT)
  GPIO.setFunction(lamp4, GPIO.OUT)
   
     
#Function called at the startup of WebIOPi server  
def setup():

  global difference
  global highestLight
  global autoEnabled
  global threshold
  global timeSleep
  file = open("/home/pi/lightcontrol/python/settings.txt", "r")
  global fileContent
  fileContent = file.read().splitlines()
  file.close()
  print(fileContent)


  #Setting the LCD GPIOs to OUT
  GPIO.setup(LCD_E, GPIO.OUT)# E
  GPIO.setup(LCD_RS, GPIO.OUT)# RS
  GPIO.setup(LCD_D4, GPIO.OUT)# DB4
  GPIO.setup(LCD_D5, GPIO.OUT)# DB5
  GPIO.setup(LCD_D6, GPIO.OUT)# DB6
  GPIO.setup(LCD_D7, GPIO.OUT)# DB7

     #Intialising the LCD
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)
   
  #Welcome output for the LCD
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("The server has")
   
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string("been launched")

  time.sleep(2)

  #writing data to file for the first time
  if(fileContent[0]=="1"):
    fileContent[0] = "0"
    fileContent[3] = "0"
    print("filecontent[3] is 0")

  file2 = open("/home/pi/lightcontrol/python/settings.txt", "w")
  for item in fileContent:
    file2.write("%s\n" % str(item))
  print ("file written at startup")
  file2.close()

  #IP Address display
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("IP ADRESS (WLAN):")

  #after fileContent filled from file, those variables are set
  difference = float(fileContent[2])
  highestLight = int(fileContent[1])
  threshold = float(fileContent[4])
  timeSleep = float(fileContent[5])

  if(fileContent[3]=="0"):
    autoEnabled = False

  ipaddr = run_cmd(cmd)
  ipaddrStr = str(ipaddr)
  ipaddrStr = ipaddrStr[2:-3]
  print (ipaddrStr)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string(ipaddrStr)
  time.sleep(1)


def calibrateLight():

  #the purpouse of the alg is to check what is the lowest intensity light
  global highestLight
  global difference
  global calibrateDone
  global autoEnabled

  autoEnabled = False
  calibrateDone = False

  #SETS ALL STUFF TO LOW JUST IN CASE
  GPIO.digitalWrite(4,GPIO.HIGH)
  GPIO.digitalWrite(17,GPIO.HIGH)
  GPIO.digitalWrite(18,GPIO.HIGH)
  GPIO.digitalWrite(22,GPIO.HIGH)

  luminosityArray = array('d', [0,0,0,0,0,0,0,0])
  differenceArray = array('d', [0,0,0])
  #Performs check on the light intensity, 3 seconds
  GPIO.digitalWrite(4,GPIO.LOW)
  time.sleep(calibrationSleepTime)
  luminosityArray[0] = tsl.getLux()

  GPIO.digitalWrite(17,GPIO.LOW)
  time.sleep(calibrationSleepTime)
  luminosityArray[1] = tsl.getLux()

  difference1 = luminosityArray[1] - luminosityArray[0]
  print("difference1", difference1)
  differenceArray[0] = difference1

  GPIO.digitalWrite(18,GPIO.LOW)
  time.sleep(calibrationSleepTime)
  luminosityArray[2] = tsl.getLux()
  
  difference2 =  luminosityArray[2] - luminosityArray[1]
  print("difference2", difference2)
  differenceArray[1] = difference2

  GPIO.digitalWrite(22,GPIO.LOW)
  time.sleep(calibrationSleepTime)
  luminosityArray[3] = tsl.getLux()

  difference3 =  luminosityArray[3] - luminosityArray[2]
  print("difference3", difference3)
  differenceArray[2] = difference3
  
  difference = max(differenceArray) * 1.1
  print("difference", difference)

  global fileContent
  fileContent[2] = difference

  GPIO.digitalWrite(4,GPIO.HIGH)
  GPIO.digitalWrite(17,GPIO.HIGH)
  GPIO.digitalWrite(18,GPIO.HIGH)
  GPIO.digitalWrite(22,GPIO.HIGH)
  
  #Performs check on the light intensity, 3 seconds
  GPIO.digitalWrite(4,GPIO.LOW)
  time.sleep(5)
  luminosity5 = tsl.getLux()
  print("lum5", luminosity5)
  highestLight = 4
  GPIO.digitalWrite(4,GPIO.HIGH)
  
  # some debugging for finding if a light is not working
  if (luminosity5 < 10) :
    print("Light 1 doesn't work !")
  
  GPIO.digitalWrite(17,GPIO.LOW)
  time.sleep(5)
  luminosity6 = tsl.getLux()
  print("lum6", luminosity6)
  if(luminosity5<luminosity6):
    highestLight = 17
  GPIO.digitalWrite(17,GPIO.HIGH)
  
    # some debugging for finding if a light is not working
  if (luminosity6 < 10) :
    print("Light 2 doesn't work !")
  
  GPIO.digitalWrite(18,GPIO.LOW)
  time.sleep(5)
  luminosity7 = tsl.getLux()
  print("lum7", luminosity7)
  if(luminosity6<luminosity7):
    highestLight = 18
  GPIO.digitalWrite(18,GPIO.HIGH)
  
    # some debugging for finding if a light is not working
  if (luminosity7 < 10) :
    print("Light 3 doesn't work !")
  
  
  GPIO.digitalWrite(22,GPIO.LOW)
  time.sleep(5)
  luminosity8 = tsl.getLux()
  print("lum8", luminosity8)
  if(luminosity7<luminosity8):
    highestLight = 22
  GPIO.digitalWrite(22,GPIO.HIGH)
  
  # some debugging for finding if a light is not working
  if (luminosity8 < 10):
    print("Light 4 doesn't work !")
  
  time.sleep(1) # 1

  fileContent[1] = highestLight
  print("filecontent[1] is ", fileContent[1])
  file2 = open("/home/pi/lightcontrol/python/settings.txt", "w")
  for item in fileContent:
    file2.write("%s\n" % str(item))
  print("file written after calibration")
  file2.close()
  print("calibrate debug 255: threshold= " , threshold)
  calibrateDone = True;

#loop function is repeatedly called, until the script is terminated
def loop():

  lights_On = 0
  global luminosity
  global threshold
  global onArray
  #luminosity variable carries the number of lux detected by TSL2561 sensor
  luminosity = tsl.getLux()

  onArray = [False, False, False, False]

  #If the automatic mode is enabled, the control algorithm is used
  if(luminosity == -1):
    luminosity = 0

  print("\n ==============  STATUS  ============ \n")
  print("\tAUTO MODE:.." , autoEnabled)
  if not autoEnabled:
    print("\n ==============  \STATUS ============ \n")
  if (autoEnabled):
    if not GPIO.digitalRead(4):
      lights_On+=1
      onArray[0] = True
    if not GPIO.digitalRead(17):
      lights_On+=1
      onArray[1] = True          
    if not GPIO.digitalRead(18):
      lights_On+=1
      onArray[2] = True          
    if not GPIO.digitalRead(22):
      lights_On+=1
      onArray[3] = True
    if(lights_On==0 and luminosity<threshold):
      GPIO.digitalWrite(highestLight, GPIO.LOW)
    else:
      if(luminosity<threshold):
        i = randint(0,3)

        GPIO.digitalWrite(gpioArray[i],GPIO.LOW)

      if(luminosity>=(threshold+difference)):
        i = randint(0,3)

        GPIO.digitalWrite(gpioArray[i],GPIO.HIGH)

    #Debug information printed in the terminal 
    print("\tLux.........", luminosity)
    print("\tLights......", lights_On)
    print("\tThreshold...", threshold)
    print("\tRefresh Rate...", timeSleep)
    print("\tMaximum birghtness", threshold+difference)
    print("\n ==============  /STATUS ============ \n")

    lcd_byte(LCD_LINE_2, LCD_CMD)
    thresholdOutput = "%2.0f" % threshold
    maxOutput = "%2.0f" % (threshold+difference)
    outputString = "Range " + thresholdOutput + " to " + maxOutput
    lcd_string(outputString)

  else:
    lcd_byte(LCD_LINE_2, LCD_CMD)
    lcd_string("Manual Mode")
      
  #Debug information printed on the LCD. The luminosity is printed in the first line.
    
  lcd_byte(LCD_LINE_1, LCD_CMD)
  luminosityStr = "Luminosity %2.0f" % luminosity
  lcd_string(luminosityStr)

  #Refreshing interval
  time.sleep(timeSleep) # 0.5

#Function ordering the string given (thanks to RaspberryPiIVBeginners)
def lcd_string(message):
  message = message.ljust(LCD_WIDTH," ")

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

#Function outputting the values to the LCD (thanks to RaspberryPiIVBeginners)
def lcd_byte(bits, mode):
  GPIO.output(LCD_RS, mode)
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

   
#IP address display function
cmd = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"

def run_cmd(cmd):
  p = Popen(cmd, shell=True, stdout=PIPE)
  output = p.communicate()[0]
  return output
    
#Function called at the shutdown of WebIOPi server 
def destroy():
   
  #Disabling the lamps to save batteries (for debug purposes only)
  GPIO.digitalWrite(4,GPIO.HIGH)
  GPIO.digitalWrite(17,GPIO.HIGH)
  GPIO.digitalWrite(18,GPIO.HIGH)
  GPIO.digitalWrite(22,GPIO.HIGH)
   
  #Displaying goodbye information
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string("The server has")
   
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string("been shut down")

  print("The value of threshold is: ", threshold)
  file2 = open("/home/pi/lightcontrol/python/settings.txt", "w")
  for item in fileContent:
    file2.write("%s\n" % str(item))
  print ("file written at shutdown")
  file2.close()

def getLux():
  lumnst = tsl.getLux()
  if(lumnst == -1.0):
    lumnst = 0.1
  return lumnst

#getAutomaticControl returns the state of autoEnabled
@webiopi.macro
def getAutomaticControl():
  global autoEnabled
  if autoEnabled:
    return "yay"
  else:
    return "nay"
#dAutomaticControl disables automatic control
@webiopi.macro
def dAutomaticControl():
  global autoEnabled
  autoEnabled = False
  global fileContent
  fileContent[3] = "0"

#eAutomaticControl enables automatic control
@webiopi.macro
def eAutomaticControl():
  global autoEnabled
  autoEnabled = True
  global fileContent
  fileContent[3] = "1"

#calibrate runs calibration
@webiopi.macro
def calibrate():
  calibrateLight()

#return luminosity from sensor
@webiopi.macro
def getLuminosity():
  return float(getLux())

  
@webiopi.macro
def calibReady():
  global calibrateDone
  return calibrateDone

@webiopi.macro
def changeThreshold(value):
  global threshold
  threshold=int(value)
  fileContent[4] = threshold


@webiopi.macro
def getThreshold():
  global threshold
  return int(threshold)

@webiopi.macro
def setTimeSleep(value):
  global timeSleep
  print(value, " set")
  timeSleep = float(value)
  fileContent[5] = timeSleep

@webiopi.macro
def calibrationSleep(timeValue):
  global calibrationSleepTime
  calibrationSleepTime = float(timeValue)

@webiopi.macro
def returnRefresh():
  global timeSleep
  return float(timeSleep)