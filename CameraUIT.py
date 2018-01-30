# --------------------------------------------------------
# UIT Dataset - UIT Camera
#
#   Extract frame from UIT camera stream
#
#  Additional Libaries:
#        python-opencv
#        schedule - scheduluing tasks - install: pip install schedule
#        pydrive - google drive lib - install: pip install pydrive
#
#
#  Upload to Google Folder: https://drive.google.com/drive/u/1/folders/1ZuJIs8o1SSbgGQvKZSPJ01QgK-bOC3WQ
#
# @author: Hoang Huu Tin
# --------------------------------------------------------

import cv2
import os
import shutil
import argparse
import time
from threading import Thread

import GDrive_Upload

import schedule        # install by: pip install schedule

def checkCamera(link):
    '''check to see if capturing camera work'''
    vidcap = cv2.VideoCapture(link)
    success, image = vidcap.read()  
    
    cv2.imwrite('test.jpg', image)

    print("Camera info: ")
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    # Get fps of video
    if int(major_ver)  < 3 :
        fps = int(round(vidcap.get(cv2.cv.CV_CAP_PROP_FPS)))
        print ("\tCamera\'s fps: {0}".format(fps))
    else :
        fps = int(round(vidcap.get(cv2.CAP_PROP_FPS)))
        print ("\tCamera\'s fps: {0}".format(fps))
    print('\tCamera\'s width = {}'.format(int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))))
    print('\tCamera\'s height = {}'.format(int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    
    vidcap.release()

    return success

def ExtractFrame_FromCameraLink(link, authdrive, master_Folder_ID, camera_name = 'test', sampling_rate = 1, end_time = '08:00', store_mode = 1, img_quality = 100):
    '''
        Extract keyframes from camera stream with sampling rate (number of frames will be taken per second)
        Example:
            sampling rate = 0.5
                => extract 1 keyframe after 2 seconds
    '''

    ############################# INIT local folders ############################################## 
    
    # Get date info
    date = time.strftime("%d%m%Y")
    start_time = time.strftime("%H:%M:%S")    # Use for log
    
    if not os.path.exists(camera_name):
        os.mkdir(camera_name)
    else:  
        if (store_mode == 3):
            # Delete local files after each day
            shutil.rmtree(camera_name)
            os.mkdir(camera_name)
  
    # Create sub-folder for each day in local disk
    folder_day = date
    if not os.path.exists(camera_name + '/' + folder_day):
        os.mkdir(camera_name + '/' + folder_day)
        
    end_t = int(end_time.replace(':', ''))
  
    
    ############################# Calculate framestep ############################################## 
    # opencv video capture
    vidcap = cv2.VideoCapture(link)
    success,image = vidcap.read()
    success = True
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    # Get fps of video
    if int(major_ver)  < 3 :
        fps = int(round(vidcap.get(cv2.cv.CV_CAP_PROP_FPS)))
    else :
        fps = int(round(vidcap.get(cv2.CAP_PROP_FPS)))
        
    framestep = max(1, min(int(round(fps / sampling_rate)), int(fps)))
    
    
    print("="*40)
    print('Extract frames from UIT CAMERA')
    print("Date: {}".format(time.strftime("%d/%m/%Y")))
    print("Camera Link: {}".format(link))
    print("Sampling rate: {} frames/sec".format(sampling_rate))
    print ("Camera\'s fps: {0}".format(fps)) 
    print('framestep = {} - extract one frame after each framestep'.format(framestep))
  
    ############################## Create folders in Google Drive #############################################
    if store_mode != 0: 
        # Create folder in Google Drive
        dst_folder_name = folder_day
       
        # Get camera_name folder, each camera has its own name
        camera_folder_ID = GDrive_Upload.get_folder_id(authdrive, master_Folder_ID, camera_name)
        # Create the folder if it doesn't exists
        if not camera_folder_ID:
            print('Creating folder ' + camera_name)
            camera_folder_ID = GDrive_Upload.create_folder(authdrive, camera_name, master_Folder_ID)
            
        folder_id = GDrive_Upload.get_folder_id(authdrive, camera_folder_ID, dst_folder_name)
    
        # Create the folder if it doesn't exists
        if not folder_id:
            print('Creating folder ' + dst_folder_name)
            folder_id = GDrive_Upload.create_folder(authdrive, dst_folder_name, camera_folder_ID)
        else:
            print('Drive Folder {0} already exists'.format(dst_folder_name))
        

    
    count_kf = 0
    count = 0
    
    ############################# CAPTURING LOOP ############################################## 
    # loop through all frame, only get frame with sampling_rate
    while success:
        success,image = vidcap.read()
         
        if (count % framestep == 0):
            count_kf += 1  
            
            if (count_kf % 20 == 0) or (count_kf == 1):    
                print('\t{}: Extracting at time: {}'.format(count_kf, time.strftime("%H:%M:%S")))
            
            time_hms = time.strftime("%H-%M-%S")
            imgfilepath = camera_name + "/" + folder_day + "/" + camera_name + "_{}___{}.jpg".format(date + "_" + time_hms, count_kf)
            cv2.imwrite(imgfilepath, image, [int(cv2.IMWRITE_JPEG_QUALITY), img_quality])
        
            if (store_mode == 2) or (store_mode == 3):
                # Upload frame ASAP
                thread1 = Thread(target = GDrive_Upload.upload_1_file, args = (authdrive, folder_id, imgfilepath))
                thread1.start()
                
        # Check end time
        cur_t = int(time.strftime("%H%M"))
        if cur_t >= end_t:
            break
        
        count += 1

    vidcap.release()
    
    print("="*40)
    print('\nDone!\nDay: {}\nTotal frames ={}'.format(date, count_kf))
    print('Local folder: {}'.format(folder_day))
    
    if (store_mode == 1):
        print("="*40) 
        print('UPLOAD FOLDER TO GOOGLE DRIVE')
        GDrive_Upload.upload_files(authdrive, folder_id, camera_name + '/' + folder_day)
        
    
    # Writing Log
    with open("log.txt", "a") as log:
        log.write("="*40 + '\r\n')
        log.write("Date: {}\r\n".format(time.strftime("%d/%m/%Y")))
        log.write('Camera name: {}\r\n'.format(camera_name))
        log.write('Camera link: {}\r\n'.format(link))
        log.write('Sampling rate: {} frames/s\r\n'.format(sampling_rate))
        log.write('Start time: {}\r\n'.format(start_time))
        log.write('End time: {}\r\n'.format(end_time))
        log.write('Store mode: {}\r\n'.format(store_mode))
        log.write('Image quality: {}\r\n'.format(img_quality))
        log.write('\r\nTotal captured frames = {}\r\n'.format(count_kf))
        

def main():
    parser = argparse.ArgumentParser(description='Keyframes Extraction from Video')
    parser.add_argument('-camera_link', dest='camera_link', help='Link to camera stream', default="rtsp://test:12345@192.168.75.27:554")
    parser.add_argument('-camera_name', dest='camera_name', help='Name of camera stream', default="Test")
    parser.add_argument('-sampling_rate', dest='sampling_rate', type=float,
                       help='sampling rate (number of frames will be captured per second)',
                       default=1)
    parser.add_argument('-start_time', dest='start_time', type=str,
                       help='Start capturing time of the day. \nExample: input \'07:15\' for 7:15 AM',
                       default='07:00')
    parser.add_argument('-end_time', dest='end_time', type=str,
                       help='End capturing time of the day. \nExample: input \'17:00\' for 5:00 PM',
                       default='08:00')
    parser.add_argument('-store_mode', dest='store_mode', type=int,
                       help='Storing mode. \nGuide: \
                             0 - only store in local machine, \
                             1 - local + upload folder of frames to google drive each day session \
                             2 - local + upload frame as soon as possible it\'s captured \
                             3 - only store in Google Drive (upload frame as soon as possible it\'s captured), local folder will be deleted on the next day',
                       default=0)
    parser.add_argument('-image_quality', dest='image_quality', type=int,
                       help='Image JPG quality (default = 100)',
                       default=100)
    args = parser.parse_args()
    
    # GET Goolge Drive Authenticate, RECOMMEND: use unlimited account
    if args.store_mode != 0:
        authdrive = GDrive_Upload.authenticate()
    else:
        authdrive = None
        
    # ID to folder CAMERA_UIT: https://drive.google.com/drive/u/1/folders/1ZuJIs8o1SSbgGQvKZSPJ01QgK-bOC3WQ
    MASTER_FOLDER_ID = "1ZuJIs8o1SSbgGQvKZSPJ01QgK-bOC3WQ"
    
    # Print screen
    print("="*20 + 'Capturing frames from UIT CAMERA' + "="*20)
    print('Camera name: {}'.format(args.camera_name))
    print('Camera link: {}'.format(args.camera_link))
    print('Sampling rate: {} frames/s'.format(args.sampling_rate))
    print('Start time: {}'.format(args.start_time))
    print('End time: {}'.format(args.end_time))
    print('Store mode: {}'.format(args.store_mode))
    print('Image quality: {}'.format(args.image_quality))
        
    print('\nChecking capturing camera...')
    if checkCamera(args.camera_link):
        print('Capturing status: OK!')
        print('Check file test.jpg for testing result.')
    else:
        print('Something error!')    # Dummy code, above exception in checkCamera() will print error message instead of this
        return
        
    print('\nCurrent system time is: {}'.format(time.strftime("%H:%M:%S")))
    print('Waiting to start time ...')
    
    # DEBUG
    #LINK = "rtsp://test:12345@192.168.75.27:554"
    #camera_name = "Front_MMLAB"
    #end_t = int(args.end_time.replace(':', ''))
    
    #ExtractFrame_FromCameraLink(args.camera_link, authdrive, MASTER_FOLDER_ID, 
    #                      args.camera_name, float(args.sampling_rate), '23:59', args.store_mode, args.image_quality)
    

    schedule.every().day.at(args.start_time).do(ExtractFrame_FromCameraLink, args.camera_link, authdrive, MASTER_FOLDER_ID, 
                          args.camera_name, float(args.sampling_rate), args.end_time, args.store_mode, args.image_quality)
    
    while True:
        schedule.run_pending()
        time.sleep(1) # wait 1s
    

if __name__ == '__main__':
    main()