# -*- coding:utf8 -*- 
#树莓派上运行
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
from picamera import PiCamera
import time
import cv2
import requests,json
from threading import Timer
from time import sleep
import glob,threading

#search 查找功能
def find_face(pic_name):
	url = 'https://api-cn.faceplusplus.com/facepp/v3/search'  
	payload['outer_id'] = 'test'
	files = {'image_file': open(pic_name, 'rb')}  
	r = requests.post(url,files=files,data=payload)  
	print(r.json())
	# print(type(r.json()))
	return r.json()

def onenet_put_pic(device,image_name):
	url='http://api.heclouds.com/bindata'
	headers={"api-key":'mqAq4mOMT=lZQMMsHmJx7Gj3hac=', #改成你的APIKEY
			 "Content-Type":"image/jpg",
			} 
	querystring = {"device_id": str(device), "datastream_id": "picture"}
	
	with open(image_name, 'rb') as f:
		r=requests.post(url, params=querystring, headers=headers, data=f)
		# print(r.json())
		print('向onenet提交图片成功')
		return r

def onenet_put_data(device,id,data):
	url='http://api.heclouds.com/devices/'+str(device)+'/datapoints'
	apiheaders={"api-key":'mqAq4mOMT=lZQMMsHmJx7Gj3hac='}
	values={ 'datastreams':[{"id":id,"datapoints":[{"value":data}]}] }
	jdata = json.dumps(values)   # 对数据进行JSON格式化编码
	#print(jdata) #打印json内容
	r=requests.post(url,headers=apiheaders,data=jdata)
	# print(r.json())
	return r

def take_pic(time_now):
	print("开始拍照")
	camera.rotation = 180 #旋转角度180
	#开始拍照
	camera.annotate_text = time_now
	pic_name1 = "./pic_r/"+time_now+".jpg"
	camera.capture(pic_name1)
	print("保存图片成功")

	# #读取图像，支持 bmp、jpg、png、tiff 等常用格式
	# img = cv2.imread(pic_name1)
	# cv2.imshow('test', img)
	return pic_name1

def read_tem():
	basic_dir='/sys/bus/w1/devices/'
	device_folder=glob.glob(basic_dir+ '28*')[0]
	device_folder=device_folder+'/w1_slave'
	tfile=open(device_folder) 
	text=tfile.readlines()
	tfile.close()
	
	equal_pos=text[1].find('t=')
	if equal_pos != -1:
		temperature = text[1][equal_pos+2:]
		temperature = float (temperature)/1000.0
		print('the temperature: %.1f' %temperature)
		return temperature

def onenet_put_data(device,id,data):
	url='http://api.heclouds.com/devices/'+str(device)+'/datapoints'
	values={ 'datastreams':[{"id":id,"datapoints":[{"value":data}]}] }
	jdata = json.dumps(values)   # 对数据进行JSON格式化编码
	r=requests.post(url,headers=apiheaders,data=jdata)
	# print(r.json())
	return r

#获取LED的状态信息 
def http_get(device):
	url='http://api.heclouds.com/devices/'+str(device)+'/datapoints'
	r=requests.get(url,headers=apiheaders) #获取信息
	led=r.json() #将json格式 变为字典格式
	
	for stream_items in led['data']['datastreams']:
		if stream_items['id']=='LED':#在每个数据流(类型为字典)中找到id为LED的值
			data=stream_items['datapoints'][0]['value']
			return data

def monitor():
	time_now = time.strftime('%m-%d %H.%M.%S',time.localtime(time.time()))

	pic_name1 = take_pic(time_now)#拍照 保存图片
	
	data = find_face(pic_name1) #对比人脸库
	# onenet_put_pic(device,pic_name1) #提交给onenet

	if "error_message" in data:
		flag_face = 0
		print("高并发报错")
	elif len(data["faces"]) == 0:
		flag_face = 0
		print('\n未检测到人脸')
		onenet_put_data(device,"people","没有人脸")
	else: #检测到人脸
		flag_face = 1
		width = data['faces'][0]['face_rectangle']['width']  
		top = data['faces'][0]['face_rectangle']['top']  
		height = data['faces'][0]['face_rectangle']['height']  
		left = data['faces'][0]['face_rectangle']['left']
		print(width,top,height,left)
		img = cv2.imread(pic_name1) #读取照片
		#给人脸画方框
		cv2.rectangle(img, (left, top), (left+width, top+height),(0, 255, 0), 2) 
		# cv2.imshow("Image", img)
		cv2.imwrite(pic_name1,img)

	onenet_put_pic(device,pic_name1) #提交给onenet
		
	if flag_face == 1:
		if data["results"][0]["face_token"] == "37752bc1efbc7af3a9b765eec9928ab9" and data["results"][0]["confidence"]>=data["thresholds"]["1e-4"]:
			print('\n这是蔡金川')
			onenet_put_data(device,"people","蔡金川")

		elif data["results"][0]["face_token"] == "5b15f6da55737907bf470db44f38f9d1" and data["results"][0]["confidence"]>=data["thresholds"]["1e-4"]:
			print('\n这是马立航')
			onenet_put_data(device,"people","马立航")

		elif data["results"][0]["face_token"] == "3376cf7516329637a32b32b7cc4f4189" and data["results"][0]["confidence"]>=data["thresholds"]["1e-4"]:
			print('\n这是张超')
			onenet_put_data(device,"people","张超")

		else:
			print('\n陌生人')
			onenet_put_data(device,"people","陌生人")
	if flag_esc == 0:
		t=Timer(t_fresh,monitor) #5s一次 
		t.start()

def control_led():
	GPIO.setmode(GPIO.BCM)
	# 输出模式
	GPIO.setup(26, GPIO.OUT)
	# while True:
	if flag_esc == 0:
		LED = http_get(device)
		GPIO.output(26, LED)

device = 22837269
t_fresh = 1 #10s刷新一次
flag_esc = 0 #初始化 不退出
payload = {
			'api_key': 'db9imPdwPuABdAUsaXzqLF8jnzKxuw7k',  
		    'api_secret': '8Zpr10gYFbIXeU5QWz-CJtEKlJejvpPd',
		   }
apiheaders={"api-key":'mqAq4mOMT=lZQMMsHmJx7Gj3hac='}

#线程的代码必须放在 这里执行
if __name__ == '__main__':
	
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 24
	camera.rotation = 180 #旋转角度180
	rawCapture = PiRGBArray(camera, size=(640, 480))
	#启动拍照子进程
	t=Timer(t_fresh,monitor) #5s一次 
	t.start()
	#启动控制LED的 子进程
	thread_tm = threading.Thread(target = control_led, args = ())
	thread_tm.start()
	#显示视频流
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		cv2.imshow("Frame", image)
		key = cv2.waitKey(1) & 0xFF
		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)
		#onenet_put_data(device,"temperature",0) 此行很关键，必须注释，数据回传没处理好
		
		if key == 27:
			flag_esc == 1 #退出
			camera.close()
			break




