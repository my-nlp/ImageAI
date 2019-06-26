from imageai.Detection import VideoObjectDetection
import sys, getopt
import os
import operator
import time
import datetime
import json
from flask import Flask, Response, request
import logging, logging.handlers
app = Flask(__name__)

execution_path = os.getcwd()

video_detector = None

parse_result = {}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='myapp.log',
    filemode='a')
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('VDLOG').addHandler(console)

def completeScan(a1, a2, average_count):
    global parse_result
    s1 = sorted(average_count.items(), key = operator.itemgetter(1), reverse = True)
    loginfo("result:", dict(s1))
    parse_result = dict(s1)
    return 0

@app.route('/')
def hello_world():
    return 'Hello, World!'

def videoDetectorInit() :
    global video_detector
    if video_detector == None :
        video_detector = VideoObjectDetection()
        video_detector.setModelTypeAsYOLOv3()
        video_detector.setModelPath(os.path.join(execution_path, "yolo.h5")) # Download the model via this link https://github.com/OlafenwaMoses/ImageAI/releases/tag/1.0
        loginfo("model startload ", datetime.datetime.now())
        video_detector.loadModel(detection_speed="normal")
        loginfo("videoDetector init: ", video_detector)
        loginfo("model loaded ", datetime.datetime.now())

    return

def loginfo(*msg, sep='') :
    print(*msg, sep)
    logging.getLogger("VDLOG").info(msg)


@app.route('/parseFolder', methods=['POST'])
def parse_videoFolder() :
    loginfo ("isJson :", request.is_json)
    content = request.get_json()
    loginfo (content)

    if "fullpath" in content :
        video_path = content["fullpath"]
        # ignore relate path
        pass
    elif "rpath" in content :
        # local test
        relate_path = content["rpath"]
        video_path = os.path.join(execution_path, relate_path)
    else :
        return jsonResponse(code=-1, result="no video path found")

    infos = []
    totalstart = time.time()
    if video_path != None :
        videoDetectorInit()
        files = [f for f in os.listdir(video_path) if os.path.isfile(os.path.join(video_path,f))]
        # print("files: ", files)
        loginfo("files: ", files)
        for f in files:
            start = time.time()
            loginfo("start detect ", f)
            ret = video_detector.detectObjectsFromVideo(input_file_path=os.path.join(video_path, f), output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
            end = time.time()
            loginfo('Finish :', f, "\ncost:", end-start)
            info = {"video" : f, "predict" : parse_result, "cost" : end-start}
            infos.append(info)

    return jsonResponse(result=infos, cost=time.time()-totalstart)


@app.route('/parseMulti', methods=['POST'])
# {videos : [xx.mp4, ...], video_path : "the video folder path"}
def parse_multiVideos() :
    loginfo (request.is_json)
    content = request.get_json()
    loginfo (content)
    videos = content["videos"]
    if "video_path" in content :
        root_video_path = content["video_path"]
    else :
        # local test
        root_video_path = os.path.join(execution_path, 'dyvideo/')

    infos = []

    totalstart = time.time()
    for videoName in videos:
        video_path = os.path.join(root_video_path, videoName)
        if (os.path.isfile(video_path)):
            videoDetectorInit()
            start = time.time()
            loginfo("\nstart detect ", videoName)
            ret = video_detector.detectObjectsFromVideo(input_file_path=video_path, output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
            end = time.time()
            loginfo('Finish :', videoName, "\ncost:", end-start)
            info = {"video" : videoName, "predict" : parse_result, "cost" : end-start}
            infos.append(info)
    
    return jsonResponse(result=infos, cost=time.time()-totalstart)


@app.route('/parse/<videoName>')
def parse_video(videoName):
    video_path = os.path.join(execution_path, 'dyvideo/', videoName)
    loginfo("parse video_path: ", video_path)
    if (os.path.isfile(video_path)):
        videoDetectorInit()

        start = time.time()
        # print("\nstart detect ", videoName)
        loginfo("\nstart detect ", videoName)
        ret = video_detector.detectObjectsFromVideo(input_file_path=video_path, output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
        end = time.time()
        loginfo('Finish :', videoName, "\ncost:", end-start)
        info = {"video" : videoName, "predict" : parse_result}
        return jsonResponse(code=0, result=info, cost=end-start)

    else :
        return jsonResponse(code=-1, result='video {} not found'.format(videoName))
        

def jsonResponse(result, code=0, cost=None) :
    resp = {"code" : code, "result" : result, "cost" : cost}
    return Response(json.dumps(resp), mimetype='application/json')


if __name__ == "__main__":
    app.run(threaded=False, debug=True, port=5000, host='0.0.0.0')
