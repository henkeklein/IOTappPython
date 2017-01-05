import getopt
import signal
import time
import sys
import json

try:
	import ibmiotf.application
except ImportError:
	# This part is only required to run the sample from within the samples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import ibmiotf"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import ibmiotf.application


tableRowTemplate = "%-33s%-30s%s"

def myEventCallback(event):
	print("%-33s%-30s%s" % (event.timestamp.isoformat(), event.device, event.event + ": " + json.dumps(event.data)))


def myStatusCallback(status):
	if status.action == "Disconnect":
		print(tableRowTemplate % (status.time.isoformat(), status.device, status.action + " " + status.clientAddr + " (" + status.reason + ")"))
	else:
		print(tableRowTemplate % (status.time.isoformat(), status.device, status.action + " " + status.clientAddr))


def interruptHandler(signal, frame):
	client.disconnect()
	sys.exit(0)


def usage():
	print(
		"simpleApp: Basic application connected to the IBM Internet of Things Cloud service." + "\n" +
		"\n" +
		"Options: " + "\n" +
		"  -h, --help          Display help information" + "\n" +
		"  -o, --organization  Connect to the specified organization" + "\n" +
		"  -i, --id            Application identifier (must be unique within the organization)" + "\n" +
		"  -k, --key           API key" + "\n" +
		"  -t, --token         Authentication token for the API key specified" + "\n" +
		"  -c, --config        Load application configuration file (ignore -o, -i, -k, -t options)" + "\n" +
		"  -T, --devicetype    Restrict subscription to events from devices of the specified type" + "\n" +
		"  -I, --deviceid      Restrict subscription to events from devices of the specified id" + "\n" +
		"  -E, --event         Restrict subscription to a specific event"
	)


if __name__ == "__main__":
	signal.signal(signal.SIGINT, interruptHandler)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "h:o:i:k:t:c:T:I:E:", ["help", "org=", "id=", "key=", "token=", "config=", "devicetype", "deviceid", "event"])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)
#token = JLwUBDeZt2r2&k2ax!
	organization = "rhq2jx"
	appId = "group3_receiver"
	authMethod = "token"
	authKey = "a-rhq2jx-rd8xc6cow6"
	authToken = "2XWSfo-ZG5lzD3268v"
	configFilePath = None
	deviceType = "+"
	deviceId = "+"
	event = "+"

	for o, a in opts:
		if o in ("-o", "--organizatoin"):
			organization = a
		elif o in ("-i", "--id"):
			appId = a
		elif o in ("-k", "--key"):
			authMethod = "apikey"
			authKey = a
		elif o in ("-t", "--token"):
			authToken = a
		elif o in ("-c", "--cfg"):
			configFilePath = a
		elif o in ("-T", "--devicetype"):
			deviceType = a
		elif o in ("-I", "--deviceid"):
			deviceId = a
		elif o in ("-E", "--event"):
			event = a
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			assert False, "unhandled option" + o

	client = None
	if configFilePath is not None:
		options = ibmiotf.application.ParseConfigFile(configFilePath)
	else:
		options = {"org": organization, "id": appId, "auth-method": authMethod, "auth-key": authKey, "auth-token": authToken}
	try:
		client = ibmiotf.application.Client(options)
		client.connect()
	except ibmiotf.ConfigurationException as e:
		print(str(e))
		sys.exit()
	except ibmiotf.UnsupportedAuthenticationMethod as e:
		print(str(e))
		sys.exit()
	except ibmiotf.ConnectionException as e:
		print(str(e))
		sys.exit()


	print("(Press Ctrl+C to disconnect)")

	client.deviceEventCallback = myEventCallback
	client.deviceStatusCallback = myStatusCallback

	client.subscribeToDeviceEvents(deviceType, deviceId, event)
	client.subscribeToDeviceStatus(deviceType, deviceId)

	print("=============================================================================")
	print(tableRowTemplate % ("Timestamp", "Device", "Event"))
	print("=============================================================================")

	while True:
		time.sleep(5)
