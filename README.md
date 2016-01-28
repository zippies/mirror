# mirror
a web tool to replace the uiautomatorviewer(just for android)

环境依赖：
	
	1、python3.3.5及以上 (以及flask模块,pip install flask)

	2、appium

配置使用：

	1、将目录下aapt.exe拷贝至本机任意目录,并将该目录加入环境变量path中,确保在dos下运行:aapt,能够输出正常信息

	2、修改config.py中的apk存放路径、设备信息以及port(默认8088)

	3、dos命令行进入主目录，运行：python mirror.py 

	4、打开浏览器，访问：http://localhost:8088


主要功能：

	1、支持uiautomatorview有关屏幕信息的获取、控件元素信息的查看等功能

	2、xpath全路径自动生成，可直接copy使用

	3、选择元素后,在红色方框内单击鼠标右键，可选择对手机进行实时操作，目前支持点击(click)、滑动(swipe)、输入文字(send_keys)、清除内容(clear)功能

