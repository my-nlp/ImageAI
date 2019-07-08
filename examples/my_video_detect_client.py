from imageai.Detection import VideoObjectDetection
import sys, getopt
import os
import operator
import time
import datetime
import json
import threading
import urllib.request
from flask import Flask, Response, request
from my_client_db import app, db, execution_path, VideoInfo, v_log

video_detector = None

parse_result = {}

db.create_all()

def completeScan(a1, a2, average_count):
    showThreadInfo("CS")
    global parse_result
    s1 = sorted(average_count.items(), key = operator.itemgetter(1), reverse = True)[:5]
    loginfo("result:", dict(s1))
    parse_result = dict(s1)
    return 0

@app.route('/')
def hello_world():
    showThreadInfo("HI")
    return 'Hello, World!'

def videoDetectorInit() :
    showThreadInfo("VI")
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
    v_log.debug(msg)


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

@app.route('/parseVideoUrls', methods=['POST'])
# {'video_urls' : [xxx,xxx]}
def parseVideoUrls():
    loginfo (request.is_json)
    content = request.get_json()
    loginfo(content)
    vinfos = []
    startA = time.time()
    if "video_urls" in content :
        links = content["video_urls"]
        for link in links:
            vinfo = VideoInfo.query.filter_by(url=link).first()
            if vinfo != None :
                info = {"video" : link, "predict" : json.loads(vinfo.detectInfo)}
                vinfos.append(info)
            else :
                loginfo("Download: ", link)
                site = urllib.request.urlopen(url=link)
                meta = site.info()
                loginfo("meta: ", meta)
                file_size = meta.get("Content-Length")
                ts = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
                if float(file_size) > 20*1024*1024 :
                    loginfo("video size is {} large than 20M, ignore".format(file_size))
                    continue
                
                filename="download_{}.mp4".format(ts)
                video_path = os.path.join(execution_path, 'DVideos/')
                if not os.path.isdir(video_path) :
                    os.mkdir(video_path)
                video_path = os.path.join(video_path, filename)
                f = open(video_path, "wb")

                file_size_dl = 0
                block_sz = 8192
                while True:
                    buffer = site.read(block_sz)
                    if not buffer:
                        break

                    file_size_dl += len(buffer)
                    f.write(buffer)
                    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / float(file_size))
                    status = status + chr(8)*(len(status)+1)
                    print(status)

                f.close()
                site.close()
                if file_size_dl == float(file_size) :
                    # return jsonResponse(result={"len" : file_size, "file_name":filename})
                    # video_path = os.path.join(execution_path, filename)
                    loginfo("parse video_path: ", video_path)
                    if (os.path.isfile(video_path)):
                        videoDetectorInit()

                        start = time.time()
                        # print("\nstart detect ", videoName)
                        loginfo("\nstart detect ", filename)
                        ret = video_detector.detectObjectsFromVideo(input_file_path=video_path, output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
                        end = time.time()
                        loginfo('Finish :', filename, "\ncost:", end-start)
                        info = {"video" : link, "predict" : parse_result}
                        # remove video if need
                        os.remove(video_path)
                        vinfo = VideoInfo(url=link, detectInfo=json.dumps(parse_result))
                        db.session.add(vinfo)
                        db.session.commit()
                        vinfos.append(info)
                        # return jsonResponse(code=0, result=info, cost=end-start)
        
        endA = time.time()
        return jsonResponse(result=vinfos, cost=endA-startA)

    return jsonResponse(result="no urls provide")


@app.route('/parseVideoUrl', methods=['POST'])
# {"videolink" : xxx}
def parseVideoUrl():
    loginfo (request.is_json)
    content = request.get_json()
    loginfo(content)
    if "videolink" in content :
        link = content["videolink"]
        vinfo = VideoInfo.query.filter_by(url=link).first()
        if vinfo != None:    
            info = {"video" : link, "predict" : json.loads(vinfo.detectInfo)}
            return jsonResponse(code=0, result=info, cost=0)
        site = urllib.request.urlopen(url=link)
        meta = site.info()
        loginfo("meta: ", meta)
        file_size = meta.get("Content-Length")
        ts = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())
        if float(file_size) > 20*1024*1024 :
            return jsonResponse(code=-1, result="video size is {} large than 20M".format(file_size))

        filename="download_{}.mp4".format(ts)
        # file_name, headers = urllib.request.urlretrieve(url=link, filename="download_{}.mp4".format(ts))
        # print("headers: ", headers)
    
        loginfo("Downloading: %s Bytes: %s" % (filename, file_size))

            
        video_path = os.path.join(execution_path, 'DVideos/')
        if not os.path.isdir(video_path) :
            os.mkdir(video_path)
        video_path = os.path.join(video_path, filename)
        f = open(video_path, "wb")

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = site.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / float(file_size))
            status = status + chr(8)*(len(status)+1)
            print(status)

        f.close()
        site.close()
        if file_size_dl == float(file_size) :
            # return jsonResponse(result={"len" : file_size, "file_name":filename})
            # video_path = os.path.join(execution_path, filename)
            loginfo("parse video_path: ", video_path)
            if (os.path.isfile(video_path)):
                videoDetectorInit()

                start = time.time()
                # print("\nstart detect ", videoName)
                loginfo("\nstart detect ", filename)
                ret = video_detector.detectObjectsFromVideo(input_file_path=video_path, output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
                end = time.time()
                loginfo('Finish :', filename, "\ncost:", end-start)
                info = {"video" : link, "predict" : parse_result}
                # remove video if need
                os.remove(video_path)
                vinfo = VideoInfo(url=link, detectInfo=json.dumps(parse_result))
                db.session.add(vinfo)
                db.session.commit()
                return jsonResponse(code=0, result=info, cost=end-start)


        # f = open("download.mp4", "wb")
        # f.write(site.read())
        # site.close()
        # f.close()

        return jsonResponse(code=-1, result='video download fail, please try again')
    else :
        return jsonResponse(code=-1, result='video link not provided')


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
    showThreadInfo("Parse")    
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

def showThreadInfo(prefix = "M"):
    print(' {} Current thread:{} {}'.format(prefix, hex(id(threading.currentThread())), threading.currentThread()))

if __name__ == "__main__":
    showThreadInfo()    
    app.run(threaded=False, debug=True, port=5000, host='0.0.0.0')
