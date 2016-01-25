# mirror
a web tool to replace the uiautomatorviewer(just for android)

环境依赖：
	
	1、python3.3.5 (以及某些模块)

	2、appium

version note:

	第一个版本,凑合着用,所有前端的请求都是同步的,所以响应比较慢的请求浏览器会让你觉得卡住了,其实等几秒会自动刷新,下个版本改成异步通信以及改善下用户体验


主要功能：

	1、支持uiautomatorview有关屏幕信息的获取、控件元素信息的查看等功能

	2、xpath全路径自动生成，可直接copy使用

	3、选择元素后,在红色方框内单击鼠标右键，可选择对手机进行实时操作，目前支持点击(click)、滑动(swipe)、输入文字(send_keys)功能