import time
import sys
import pprint
import uuid
import serial
from cloudant.client import Cloudant
import couchdb

#port = "/dev/cu.HC-06-DevB" # put your port name here Windows COM1/COM2/...
#baud = 9600 # the same baud rate in your Arduino Code
#ser = serial.Serial(port, baud, timeout=1)
 # open the serial port
#if ser.isOpen():
 #print(ser.name + ' is open...')
#while True:
 #command = ser.readline()
 #print command

#Organization ID: rhq2jx
#Device Type: Android
#Device ID: iot3
#Authentication Method: token
#Authentication Token: supersecret

{
  "credentials": {
    "url": "https://039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix:0ee17153c8ea9a820af80505f5eff56af2ec76eb56c7b734994178f23f84554c@039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix.cloudant.com",
    "username": "039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix",
    "password": "0ee17153c8ea9a820af80505f5eff56af2ec76eb56c7b734994178f23f84554c"
  }
}

{
  "username": "039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix",
  "password": "0ee17153c8ea9a820af80505f5eff56af2ec76eb56c7b734994178f23f84554c",
  "host": "039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix.cloudant.com",
  "port": 443,
  "url": "https://039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix:0ee17153c8ea9a820af80505f5eff56af2ec76eb56c7b734994178f23f84554c@039fb976-69d8-43e7-9c0f-3381bd237f77-bluemix.cloudant.com"
}



try:
	import ibmiotf.application
	import ibmiotf.device
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf.application" & "import ibmiotf.device"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.application
	import ibmiotf.device

def myAppEventCallback(event):
	print("Received live data from %s (%s) sent at %s: hello=%s x=%s" % (event.deviceId, event.deviceType, event.timestamp.strftime("%H:%M:%S"), data['hello'], data['x']))


organization = "rhq2jx"
deviceType = "Ardunio-Uno"
deviceId = "group3"
appId = deviceId + "_receiver"
authMethod = "token"
authToken = "supersecret"


# Initialize the application client.
try:
	appOptions = {"org": organization, "id": appId, "auth-method": authMethod, "auth-token": authToken}
	appCli = ibmiotf.application.Client(appOptions)
except Exception as e:
	print(str(e))
	sys.exit()

# Connect and configuration the application
# - subscribe to live data from the device we created, specifically to "greeting" events
# - use the myAppEventCallback method to process events
appCli.connect()
appCli.subscribeToDeviceEvents(deviceType, deviceId, "greeting")
appCli.deviceEventCallback = myAppEventCallback

# Initialize the device client.
try:
	deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
	deviceCli = ibmiotf.device.Client(deviceOptions)
except Exception as e:
	print("Caught exception connecting device: %s" % str(e))
	sys.exit()

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
deviceCli.connect()
print("---------Connected---------")
for x in range (0,20):
	data = { 'hello' : 'down', 'x' : x}
	def myOnPublishCallback():
		print("Confirmed event %s received by IoTF\n" % x)

	success = deviceCli.publishEvent("greeting", "json", data, qos=0, on_publish=myOnPublishCallback)
	if not success:
		print("Not connected to IoTF")
	time.sleep(1)


# Disconnect the device and application from the cloud
deviceCli.disconnect()
appCli.disconnect()
