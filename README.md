# mirror
a web tool to replace the uiautomatorviewer(just for android)

环境依赖：
	
	1、python3.3.5及以上 download_url : https://www.python.org/downloads/release/python-335/

	2、下载安装setuptools、pip模块

	3、进入mirror目录，执行:pip install -r requirments.txt 安装依赖模块

	4、安装appium并配置好环境变量(确保在命令行下输入:appium -a localhost -p 4723  命令行能正常输出启动信息)


配置使用：

	1、修改config.py中的设备信息以及port(默认8088)

	3、dos命令行进入主目录，运行：python mirror.py 

	4、打开浏览器，访问：http://localhost:8088


主要功能：

	1、支持uiautomatorview有关屏幕信息的获取、控件元素信息的查看等功能

	2、自动获取apk的包名和启动activity

	3、xpath全路径自动生成，可直接copy使用

	4、选择元素后,在红色方框内单击鼠标右键，可选择对手机进行实时操作，目前支持点击(click)、滑动(swipe)、输入文字(send_keys)、清除内容(clear)功能

