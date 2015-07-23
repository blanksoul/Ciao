import os, logging, json

#basepath to look for conf/connectors/whatelse
basepath = os.path.dirname(os.path.abspath(__file__)) + os.sep

#enable/disable fake.stdin - TESTING PURPOSE
# atm this params has to be set to True only
# if you want to use a file as stdin instead of the real one
use_fakestdin = True

#configuration dictionary
conf = {
	"server": {
		"host" : "localhost",
		"port" : 8900
	},
	# path starting with slash will be handled like absolute ones
	"paths": {
		"conf" : "conf/",
		"connectors" : "connectors/"
	},
	"log": {
		"file" : "ciao.log",
		"level" : "debug",
		"format" : "%(asctime)s %(levelname)s %(name)s - %(message)s",
		"maxSize" : 1 , # maxSize is expressed in MBytes
		"maxRotate" : 5 # maxRotate expresses how much time logfile has to be rotated before deletion
	}
}

#map of actions accepted from bridge(MCU-side)
actions_map = {
	"r": "read", #usually requires 2/3 params - connector;action;data(optional)
	"w": "write", #usuallyrequires 3 params - connector;action;data
	"wr": "writeresponse" #usually requires 4 params - connector;action;reference;data
}

#serialization settings
# ASCII code for GroupSeparator (non-printable char)
entry_separator = chr(30)
# ASCII code for UnitSeparator (non-printable char)
keyvalue_separator = chr(31)

#DO NOT CHANGE ANYTHING BELOW (UNLESS YOU ARE REALLY SURE)

#adjust some settings about paths
if not conf['paths']['conf'].startswith(os.sep): #relative path
	conf['paths']['conf'] = basepath + conf['paths']['conf']
if not conf['paths']['conf'].endswith(os.sep):
	conf['paths']['conf'] += os.sep
if not conf['log']['file'].startswith(os.sep): #relative path
	conf['log']['file'] = basepath + conf['log']['file']

#adjust settings about logging
DLEVELS = {
	'debug': logging.DEBUG,
	'info': logging.INFO,
	'warning': logging.WARNING,
	'error': logging.ERROR,
	'critical': logging.CRITICAL
}
conf['log']['level'] = DLEVELS.get(conf['log']['level'], logging.NOTSET)
conf['log']['maxSize'] *= 1024*1024 #it's expressed in MBytes but we need bytes

def load_connectors(logger):
	global conf

	conf_path = conf['paths']['conf']
	#loading configuration for connectors
	try:
		conf_list = os.listdir(conf_path)
	except Exception, e:
		logger.debug("Problem opening conf folder: %s" % e)
		return
	else:
		conf['connectors'] = {}
		for conf_file in conf_list:
			if conf_file.endswith(".json.conf"):
				try:
					conf_json = open(conf_path + conf_file).read()
					conf_plain = json.loads(conf_json)
					if 'name' in conf_plain:
						connector_name = conf_plain['name']
					else:
						logger.debug("Missing connector name in configuration file(%s)" % conf_file)
						connector_name = conf_file[:-len(".json.conf")]		
					if "enabled" in conf_plain and conf_plain['enabled']:
						conf['connectors'][connector_name] = conf_plain
						logger.debug("Loaded configuration for %s connector" % connector_name)
					else:
						logger.debug("Ignoring %s configuration: connector not enabled" % connector_name)
				except Exception, e:
					logger.debug("Problem loading configuration file (%s): %s" % (conf_file, e))
		conf['backlog'] = len(conf['connectors'])

def init():
	global conf
	if not conf['paths']['conf'].startswith(os.sep): #relative path
		global basepath
		conf['paths']['conf'] = basepath + conf['paths']['conf']
