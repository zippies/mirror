from flask import Flask,render_template,request,url_for,jsonify,redirect
from multiprocessing import Process
from xml.dom import minidom
from config import debug,port
from datetime import datetime
from subprocess import Popen,PIPE
from main.basecase import AndroidDevice
import os,json,re,platform,requests,time,signal,sys,copy

app = Flask(__name__)
_id = 0
appium_port = 14111
bootstrap_port = 14112
appium_log_level = "error"
driver = None
nodeDatas = []
nodeinfos = {}
frameinfos = {}
reversedframe = False
reverseframe = {}

def getChildNodes(node):
	nodes = [n for n in node.childNodes if n.nodeName !='#text']
	return len(nodes)

def parseBounds(bound_str):
	global driver,_id,reversedframe
	start_p,end_p = bound_str.strip("[]").split("][")
	start_x,start_y = start_p.split(",")
	end_x,end_y = end_p.split(",")

	if int(end_x) > driver.device_width or int(end_y) > driver.device_height:
		reversedframe = True
	else:
		reversedframe = False

	height = round((int(end_y) - int(start_y))*0.4)
	width = round((int(end_x) -int(start_x))*0.4)
	return (round(int(start_x)*0.4),round(int(start_y)*0.4),height,width)


def setXpath(node,xpaths):
	xpathinfo = None
	if node.nodeName != "hierarchy":
		index = int(node.getAttribute("index"))
		parent_node = node.parentNode
		if index > 0:
			deep = 1
			for n in parent_node.childNodes:
				if n.nodeName == node.nodeName and int(n.getAttribute("index")) < int(node.getAttribute("index")):
					deep += 1
			xpathinfo = "%s[%s]" %(node.nodeName,deep)
		else:
			xpathinfo = node.nodeName

		xpaths.append(xpathinfo)

		setXpath(parent_node,xpaths)

		return xpaths

def setNodeInfo(node,nodeinfos,frameinfos):
	global _id
	nodeinfo = {}
	notes = {}
	xpaths = []
	cared_attributes = ["index",
						"text",
						"class",
						"package",
						"content-desc",
						"checkable",
						"checked",
						"clickable",
						"enabled",
						"focusable",
						"focused",
						"scrollable",
						"long-clickable",
						"password",
						"selected",
						"bounds",
						"resource-id",
						"instance"
						]
	for attr in cared_attributes:
		nodeinfo[attr] = node.getAttribute(attr)

	if node.hasAttribute("bounds"):
		bounds = parseBounds(node.getAttribute("bounds"))
		notes["x1"],notes["y1"],notes["height"],notes["width"] = bounds
		notes["note"] = node.nodeName
		notes["id"] = _id

	xpaths = setXpath(node,xpaths)

	if xpaths:
		nodeinfo["xpath"] = "//%s" %"/".join(xpaths[::-1])
	else:
		nodeinfo["xpath"] = ""

	nodeinfo['id'] = _id
	nodeinfos[_id] = nodeinfo
	frameinfos[_id] = notes

def getNodes(index,node,nodeinfos,frameinfos):
	global _id
	if node.nodeName != "#text":
		datadict = None
		childNodeCount = getChildNodes(node)
		_id += 1
		setNodeInfo(node,nodeinfos,frameinfos)
		
		if childNodeCount > 0:
			datadict = {
				"id": _id,
				"text": "(%s)%s" %(index,node.nodeName),
				"href":"#",
				"tags":['%s' %childNodeCount],
				"nodes":[]
			}
		else:
			datadict = {
				"id": _id,
				"text": "(%s)%s" %(index,node.nodeName),
				"href":"#",
				"tags":['%s' %childNodeCount]
			}

		for i,n in enumerate([n for n in node.childNodes if n.nodeName !="#text"]):
			data = getNodes(i+1,n,nodeinfos,frameinfos)
			if data:
				datadict['nodes'].append(data)

		return datadict


def getDeviceState():
	cmd = "adb devices"
	devices = []
	p = Popen(cmd,stdout=PIPE,shell=True)
	for info in p.stdout.readlines():
		info = info.decode()
		if 'List' in info:
			continue
		elif 'offline' in info or 'unauthorized' in info or 'device' in info:
			device = {}
			name,state = [n.strip() for n in info.split('\t') if n.strip()]
			device["deviceName"] = name
			device["state"] = state
			if ":" in name:
				device["replacedName"] = name.replace(".","").replace(":","")
			else:
				device["replacedName"] = name
			devices.append(device)
		else:
			continue
	
	p.kill()
	
	return devices

def is_Appium_Alive(port):
	'''
		检查指定端口的appium是否已启动
	'''
	try:
		if requests.get('http://localhost:%s/wd/hub' %port,timeout=(0.5,0.5)).status_code == 404:
			return True
		else:
			return False
	except Exception as e:
		return False

def stopAppium():
	'''
		关闭所有appium服务
	'''
	if platform.system() == 'Windows':
		os.system("taskkill /F /IM node.exe")
	else:
		os.system("killall node")


@app.route("/connect/<devicename>",methods=['POST'])
def connectDevice(devicename):
	appiumlog = os.path.join(os.getcwd(),"logs",datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),"appium.log")
	os.makedirs(os.path.dirname(appiumlog))
	cmd = "appium\
			 -a localhost \
			 -p %s \
			 -bp %s \
			 -g %s \
			 --log-timestamp \
			 --log-level %s \
			 -U %s \
			 --log-no-colors" %(appium_port,bootstrap_port,appiumlog,appium_log_level,devicename)
	p = Process(target=os.system,args=(cmd,))
	if is_Appium_Alive(appium_port):
		stopAppium()
	p.daemon = True
	p.start()
	info = "Starting Appium on port : %s bootstrap_port: %s for device %s" %(appium_port,bootstrap_port,devicename)

	return info

@app.route("/isappiumready")
def isAppiumReady():
	data = None
	if is_Appium_Alive(appium_port):
		data = {"status":True,"info":"appium is ready!"}
	else:
		data = {"status":False,"info":"appium is not ready,keep waitting.."}

	return jsonify(data)

@app.route("/swipe/<direction>")
def swipe(direction):
	global driver,frameinfos
	resp = {"status":True,"info":None}
	id = request.args.get("id")
	px = request.args.get("px")
	elem = frameinfos.get(int(id))
	start_x,start_y = round((elem['x1']+round(elem['width']/2))/0.4),round((elem['y1']+round(elem['height']/2))/0.4)
	if direction == 'up':
		end_x,end_y = start_x,start_y - int(px)
	elif direction == 'down':
		end_x,end_y = start_x,start_y + int(px)
	elif direction == 'left':
		end_x,end_y = start_x - int(px),start_y
	elif direction == 'right':
		end_x,end_y = start_x + int(px),start_y
	else:
		resp = {"status":False,"info":"No such direction:%s" %direction}

	if end_x < driver.device_width and end_y < driver.device_height:
		driver.swipe((start_x,start_y),(end_x,end_y))
		freshScreen()
	else:
		resp = {"status":False,"info":"swipe out of device screen"}
	return jsonify(resp)

@app.route("/click/<id>")
def click(id):
	global driver,frameinfos
	resp = {"status":True,"info":None}
	elem = frameinfos.get(int(id))

	try:
		x,y = round((elem['x1']+round(elem['width']/2))/0.4),round((elem['y1']+round(elem['height']/2))/0.4)
		print("click at:",x,y)
		driver.click_point(x,y)
		freshScreen()
	except Exception as e:
		resp["status"] = False
		resp["info"] = str(e)
	
	return jsonify(resp)

@app.route("/sendtext/<id>")
def sendText(id):
	global driver,nodeinfos
	resp = {"status":True,"info":None}
	text = request.args.get('text')
	elem = nodeinfos[int(id)]
	elem_id = elem.get("resource-id")
	try:
		if elem_id:
			driver.input('id',elem_id,text)
			freshScreen()
		else:
			resp["status"] = False
			resp["info"] = "Make sure this element has an id"
	except Exception as e:
		resp["status"] = False
		resp["info"] = str(e)

	return jsonify(resp)

@app.route("/sendkeycode/<code>")
def back(code):
	global driver
	resp = {"status":True,"info":None}
	try:
		driver.press_keycode(code)
		freshScreen()
	except Exception as e:
		resp["status"] = False
		resp["info"] = str(e)

	return jsonify(resp)

def getAppInfo(apk):
	cmd_activity = "aapt d badging %s|findstr launchable-activity" %apk
	cmd_package = "aapt d badging %s|findstr package" %apk
	activity = Popen(cmd_activity,stdout=PIPE,shell=True)
	package = Popen(cmd_package,stdout=PIPE,shell=True)
	activity_name = activity.stdout.read().decode().split("name='")[1].split("'")[0]
	package_name = package.stdout.read().decode().split("name='")[1].split("'")[0]
	activity.kill()
	package.kill()
	return (package_name,activity_name)

def freshScreen():
	global _id,driver,nodeDatas,nodeinfos,frameinfos
	_id = 0
	nodeDatas,nodeinfos,frameinfos = [],{},{}
	driver.save_screen(os.path.join(os.getcwd(),'static','images',"current.png"))
	page_source = driver.page_source
	page_source = re.sub("[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",page_source)
	try:
		root = minidom.parseString(page_source).documentElement
	except Exception as e:
		print(e)

	for i,node in enumerate([n for n in root.childNodes if n.nodeName !="#text"]):
		if node.nodeName != "#text":
			datadict = getNodes(i+1,root,nodeinfos,frameinfos)
			nodeDatas.append(datadict)


@app.route('/getscreen',methods=["GET","POST"])
def getScreen():
	global driver,nodeDatas,nodeinfos,frameinfos,reversedframe,reverseframe
	if reversedframe:
		reverseframe = copy.deepcopy(frameinfos)
		for id in reverseframe.keys():
			if id - 1:
				x1 = round(driver.device_width*0.4-reverseframe[id]['y1']-reverseframe[id]['height'])
				y1 = reverseframe[id]['x1']
				width = reverseframe[id]['height']
				height = reverseframe[id]['width']
				reverseframe[id]['x1'],reverseframe[id]['y1'],reverseframe[id]['width'],reverseframe[id]['height'] = x1,y1,width,height

	if request.method == "POST":
		apk = "C:\\Users\\Administrator\\Downloads\\apks\\backup.apk"
		packageName,main_activity = getAppInfo(apk)
		capabilities = {
			"deviceName": "M3LDU15424001636",
			"platformName": "Android",
			"platformVersion": "4.4",
			#"app": apk,
			"appPackage": packageName,
			"appActivity": main_activity,
			"newCommandTimeout": 300,
			"noSign": True,
			"unicodeKeyboard":True,
			"resetKeyboard":True
		}
		driver = AndroidDevice("http://localhost:%s/wd/hub" %appium_port,capabilities)
		driver.sleep(5)
		freshScreen()
		print("current_activity:",driver.current_activity)
		return "ok"

	return render_template(
							"deviceinfo.html",
							nodeDatas=nodeDatas,
							nodeinfos=nodeinfos,
							frameinfos=frameinfos if not reversedframe else reverseframe
	)

@app.route("/showcloser")
def showCloser():
	global frameinfos,reverseframe,reversedframe
	x,y = request.args.get('x'),request.args.get('y')
	closer = 0
	minner = 100000000
	frame = frameinfos if not reversedframe else reverseframe
	for i,v in frame.items():
		if i and v and v['x1']<int(x)<v['x1']+v['width'] and v['y1']<int(y)<v['y1']+v['height']:
			if v['width']*v['height'] < minner:
				minner =  v['width'] * v['height'] 
				closer = i

	return str(closer)

@app.route('/')
def index():
	global nodeDatas
	isconnect = False
	devices = getDeviceState()

	if is_Appium_Alive(appium_port):
		isconnect = True
	
	return render_template(
							"index.html",
							devices=devices,
							isconnect=isconnect
	)

if __name__ == "__main__":
	app.debug = debug
	app.run('10.88.0.40',port=port)