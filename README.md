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


version note:

	第一个版本,凑合着用,所有前端的请求都是同步的,每个事件(click等)的请求都会等待2秒再返回,所以响应比较慢的请求浏览器会让你觉得卡住了,其实等几秒会自动刷新,下个版本改成异步通信以及改善下用户体验


主要功能：

	1、支持uiautomatorview有关屏幕信息的获取、控件元素信息的查看等功能

	2、xpath全路径自动生成，可直接copy使用

	3、选择元素后,在红色方框内单击鼠标右键，可选择对手机进行实时操作，目前支持点击(click)、滑动(swipe)、输入文字(send_keys)、清除内容(clear)功能

