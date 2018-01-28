# --------------------------------------------------------
# UIT Dataset - UIT Camera
#
#   Directly View UIT camera stream
#
# @author: Hoang Huu Tin
# --------------------------------------------------------

import cv2
import os
import shutil
import argparse
import time

def ViewCamera_FromLink(link, camera_name):
    '''
        Extract keyframes from video with sampling rate (number of frames will be taken per second)
        Example:
            sampling rate = 0.5
                => extract 1 keyframe after 2 seconds
    '''
    if (camera_name == ""):
        camera_name = "test"
     
    print("View camera stream from link: {}".format(link))

    # opencv video capture
    vidcap = cv2.VideoCapture(link)

    success,image = vidcap.read()
    
    success = True

    print('Camera\'s width = {}'.format(int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))))
    print('Camera\'s height = {}'.format(int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    # 
    while success:
        success, img = vidcap.read()
        cv2.imshow(camera_name, img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
            
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Keyframes Extraction from Video')
    parser.add_argument('--camera_link', dest='camera_link', help='Link to camera stream', default="rtsp://test:12345@192.168.75.27:554")
    parser.add_argument('--camera_name', dest='camera_name', help='Name of camera stream', default="Front_MMLAB")
    args = parser.parse_args()
    
    #Keyframe_Extract(args.video_path, args.sampling_rate)
    
    #LINK = "rtsp://test:12345@192.168.75.27:554"
    #camera_name = "Front_MMLAB"
    
    ViewCamera_FromLink(link = args.camera_link, camera_name = args.camera_name)


if __name__ == '__main__':
    main()