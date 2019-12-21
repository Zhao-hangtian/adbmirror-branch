# 实时 Android to WIndows 画面捕捉与控制(基于sft)
## require
- python 3.6
- adb-tools
- **minitouch(binary), minicap(binary), minitouch.so**
**see: 	https://github.com/openstf/minicap
		https://github.com/openstf/minitouch
		to compile them,**
		or refer to my blog https://willtian.cn/?p=157
## usage 
Run:  **(two step)**
1.  Open terminal:
    `python3 start-mirror.py`  transfer minitouch, minicap, minitouch.so to your Android
2.  In another terminal:
    `python gui.py 540x960 1080x1920 /data/local/tmp/adbmirror/`
	**Modify the size to reflect your phone**
## my modification
1.	modify to adaptive to all screen size devices
2.	define more mouse click event:
		left: touch
		middle: home
		right: back
## others(orginal author said)
Copy and Paste with serval lines modification from below :
https://github.com/openstf
https://github.com/Macuyiko/adbmirror
http://blog.macuyiko.com/post/2017/note-to-self-fast-android-screen-capture.html
https://github.com/fhorinek/adbmirror
