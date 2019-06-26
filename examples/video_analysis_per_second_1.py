from imageai.Detection import VideoObjectDetection
import os
import operator
import time
import datetime
from matplotlib import pyplot as plt


execution_path = os.getcwd()

color_index = {'bus': 'red', 'handbag': 'steelblue', 'giraffe': 'orange', 'spoon': 'gray', 'cup': 'yellow', 'chair': 'green', 'elephant': 'pink', 'truck': 'indigo', 'motorcycle': 'azure', 'refrigerator': 'gold', 'keyboard': 'violet', 'cow': 'magenta', 'mouse': 'crimson', 'sports ball': 'raspberry', 'horse': 'maroon', 'cat': 'orchid', 'boat': 'slateblue', 'hot dog': 'navy', 'apple': 'cobalt', 'parking meter': 'aliceblue', 'sandwich': 'skyblue', 'skis': 'deepskyblue', 'microwave': 'peacock', 'knife': 'cadetblue', 'baseball bat': 'cyan', 'oven': 'lightcyan', 'carrot': 'coldgrey', 'scissors': 'seagreen', 'sheep': 'deepgreen', 'toothbrush': 'cobaltgreen', 'fire hydrant': 'limegreen', 'remote': 'forestgreen', 'bicycle': 'olivedrab', 'toilet': 'ivory', 'tv': 'khaki', 'skateboard': 'palegoldenrod', 'train': 'cornsilk', 'zebra': 'wheat', 'tie': 'burlywood', 'orange': 'melon', 'bird': 'bisque', 'dining table': 'chocolate', 'hair drier': 'sandybrown', 'cell phone': 'sienna', 'sink': 'coral', 'bench': 'salmon', 'bottle': 'brown', 'car': 'silver', 'bowl': 'maroon', 'tennis racket': 'palevilotered', 'airplane': 'lavenderblush', 'pizza': 'hotpink', 'umbrella': 'deeppink', 'bear': 'plum', 'fork': 'purple', 'laptop': 'indigo', 'vase': 'mediumpurple', 'baseball glove': 'slateblue', 'traffic light': 'mediumblue', 'bed': 'navy', 'broccoli': 'royalblue', 'backpack': 'slategray', 'snowboard': 'skyblue', 'kite': 'cadetblue', 'teddy bear': 'peacock', 'clock': 'lightcyan', 'wine glass': 'teal', 'frisbee': 'aquamarine', 'donut': 'mincream', 'suitcase': 'seagreen', 'dog': 'springgreen', 'banana': 'emeraldgreen', 'person': 'honeydew', 'surfboard': 'palegreen', 'cake': 'sapgreen', 'book': 'lawngreen', 'potted plant': 'greenyellow', 'toaster': 'ivory', 'stop sign': 'beige', 'couch': 'khaki'}


resized = False

detectRsl = {}

def merge(d1, d2, merge_fn=lambda x,y:y):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the optional merge
    function.  The default behavior replaces the values in d1
    with corresponding values in d2.  (There is no other generally
    applicable merge strategy, but often you'll have homogeneous 
    types in your dicts, so specifying a merge technique can be 
    valuable.)

    Examples:

    >>> d1
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1)
    {'a': 1, 'c': 3, 'b': 2}
    >>> merge(d1, d1, lambda x,y: x+y)
    {'a': 2, 'c': 6, 'b': 4}

    """
    result = dict(d1)
    for k,v in d2.items():
        if k in result:
            result[k] = merge_fn(result[k], v)
        else:
            result[k] = v
    return result

def completeScan(a1, a2, average_count):
    # print("\na1:", a1)
    # print("\na2:", a2)
    # print("\ncomplete_average_count:", average_count)
    s1 = sorted(average_count.items(), key = operator.itemgetter(1), reverse = True)
    print("result:", s1)
    return 0

def forSecond(frame_number, output_arrays, count_arrays, average_count, returned_frame):

    plt.clf()

    this_colors = []
    labels = []
    sizes = []

    counter = 0
    print("frame_num:", frame_number, ", returned_frame:", returned_frame)
    print("\ncount_arrays: ", count_arrays, "\naverage_count:", average_count)
    global detectRsl
    localV = detectRsl
    detectRsl = merge(average_count, localV, lambda x,y:x+y)
    for eachItem in average_count:
        counter += 1
        labels.append(eachItem + " = " + str(average_count[eachItem]))
        sizes.append(average_count[eachItem])
        this_colors.append(color_index[eachItem])

    global resized

    if (resized == False):
        manager = plt.get_current_fig_manager()
        # max_size = manager.window.maxsize()
        # max_size = (max_size[0], max_size[1] * 0.45)
        # manager.resize(*max_size)
        # manager.resize(width=1000, height=500)
        manager.resize(1000, 500)
        resized = True

    plt.subplot(1, 2, 1)
    plt.title("Second : " + str(frame_number))
    plt.axis("off")
    plt.imshow(returned_frame, interpolation="none")

    plt.subplot(1, 2, 2)
    plt.title("Analysis: " + str(frame_number))
    plt.pie(sizes, labels=labels, colors=this_colors, shadow=True, startangle=140, autopct="%1.1f%%")

    # plt.pause(0.01)
    figpath = os.path.join(execution_path, 'video_second_analysis/frame_{:}'.format(frame_number))
    plt.savefig(figpath)



testvideosPath = os.path.join(execution_path, 'dyvideo/')
print("testvideosPath: ", testvideosPath)
files = [f for f in os.listdir(testvideosPath) if os.path.isfile(os.path.join(testvideosPath,f))]
print("files: ", files)

video_detector = VideoObjectDetection()
video_detector.setModelTypeAsYOLOv3()
video_detector.setModelPath(os.path.join(execution_path, "yolo.h5")) # Download the model via this link https://github.com/OlafenwaMoses/ImageAI/releases/tag/1.0
print("model startload ", datetime.datetime.now())
video_detector.loadModel(detection_speed="normal")
print("model loaded ", datetime.datetime.now())

# plt.show()

for f in files:
    start = time.time()
    print("\nstart detect ", f)
    ret = video_detector.detectObjectsFromVideo(input_file_path=os.path.join(testvideosPath, f), output_file_path='',  frames_per_second=30, frame_detection_interval=90, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=False)
    end = time.time()
    print('Finish :', f, "\ncost:", end-start)



# video_detector.detectObjectsFromVideo(input_file_path=os.path.join(execution_path, "../videos/traffic-mini.mp4"), output_file_path='',  frames_per_second=30, frame_detection_interval=15, per_second_function=None, video_complete_function=completeScan, minimum_percentage_probability=50, return_detected_frame=False, save_detected_video=False, log_progress=True)
