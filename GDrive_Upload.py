# -*- coding: utf-8 -*-

"""
    Upload folder to Google Drive
"""

# Enable Python3 compatibility
from __future__ import (unicode_literals, absolute_import, print_function,
                        division)

# Import Google libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFileList, ApiRequestError
import googleapiclient.errors

# Import general libraries
from argparse import ArgumentParser
import os
from sys import exit
import ast
import time, random


DEFAULT_Credential = "uitcamera_creds.txt"

def parse_args():
    """ 
        Parse arguments
    """

    parser = ArgumentParser(
        description="Upload local folder to Google Drive")
    parser.add_argument('-s', '--source', type=str, 
                        help='Folder to upload')
    parser.add_argument('-d', '--destination', type=str, 
                        help='Destination Folder in Google Drive')
    parser.add_argument('-p', '--parent', type=str, 
                        help='Parent Folder in Google Drive')

    return parser.parse_args()


def authenticate():
    """ 
        Authenticate to Google API
    """
    global DEFAULT_Credential
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile(DEFAULT_Credential)
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(DEFAULT_Credential)

    return GoogleDrive(gauth)


def get_folder_id(drive, parent_folder_id, folder_name):
    """ 
        Check if destination folder exists and return it's ID
    """

    # Auto-iterate through all files in the parent folder.
    file_list = GoogleDriveFileList()
    try:
        file_list = drive.ListFile(
            {'q': "'{0}' in parents and trashed=false".format(parent_folder_id)}
        ).GetList()
    # Exit if the parent folder doesn't exist
    except googleapiclient.errors.HttpError as err:
        # Parse error message
        message = ast.literal_eval(err.content)['error']['message']
        if message == 'File not found: ':
            print(message + folder_name)
            exit(1)
        # Exit with stacktrace in case of other error
        else:
            raise

    # Find the the destination folder in the parent folder's files
    for file1 in file_list:
        if file1['title'] == folder_name:
            print('title: %s, id: %s' % (file1['title'], file1['id']))
            return file1['id']


def create_folder(drive, folder_name, parent_folder_id):
    """ 
        Create folder on Google Drive
    """
    
    folder_metadata = {
        'title': folder_name,
        # Define the file type as folder
        'mimeType': 'application/vnd.google-apps.folder',
        # ID of the parent folder        
        'parents': [{"kind": "drive#fileLink", "id": parent_folder_id}]
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()

    # Return folder informations
    print('title: %s, id: %s' % (folder['title'], folder['id']))
    return folder['id']


def upload_files(drive, folder_id, src_folder_name):
    """ 
        Upload files in the local folder to Google Drive 
    """

    # Enter the source folder
    try:
        os.chdir(src_folder_name)
    # Print error if source folder doesn't exist
    except OSError:
        print(src_folder_name + 'is missing')
    # Auto-iterate through all files in the folder.
    AllFiles = os.listdir('.')
    count = 1
    for file1 in AllFiles:
        # Check the file's size
        statinfo = os.stat(file1)
        if statinfo.st_size > 0:
            print('[{}/{}] Uploading {}'.format(count, len(AllFiles), file1))
            # Upload file to folder.
            f = drive.CreateFile(
                {"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
            f.SetContentFile(file1)
            f.Upload()
            
            count += 1
        # Skip the file if it's empty
        else:
            print('file {0} is empty'.format(file1))


def upload_1_file(drive, folder_id, file_path):
    """ 
        Upload files in the local folder to Google Drive
        Update 30/01/2018:
            Handle error HTTP 403: because of too many requests per second
            Solution: Implementing exponential backoff
              https://developers.google.com/drive/v3/web/handle-errors#403_user_rate_limit_exceeded
              https://stackoverflow.com/questions/42557355/user-rate-limit-exceeded-after-a-few-requests/42562397#42562397
    """
    # Upload file to folder.
    
    # wait 2 second for opencv write image
    time.sleep(2)

    statinfo = os.stat(file_path)
    if statinfo.st_size == 0:
        print(">>> Error file {} empty!!!".format(file_path))
        return
        
    filename = os.path.basename(file_path)
    success = False
    n = 0
    error_count = 0
    while not success:
        try:         
            f = drive.CreateFile({'title':filename, "parents": [{"kind": "drive#fileLink", "id": folder_id}]})
            f.SetContentFile(file_path)
            f.Upload()
            
            time.sleep(random.randint(0,1000)/1000)
            success = True
        except ApiRequestError as e:
            # handle HTTP 403
            # exponential backoff
            wait = (2**n) + (random.randint(0,1000)/1000)
            error_count += 1
            print(">>> Error msg: {}".format(e))
            print(">>> This is {} times - file: {}".format(error_count, file_path))
            print(">>> Try again after: {} seconds\n".format(wait))
            
            time.sleep(wait)
            success = False
            n += 1
                
def test():
    """ 
        Testing
    """
    # args = parse_args()

    # src_folder_name = args.source
    # dst_folder_name = args.destination
    # parent_folder_name = args.parent

    src_folder_name = "Front_MMLAB/Front_MMLAB_27012018"
    dst_folder_name = "Front_MMLAB_27012018"
    # parent_folder_name = "CAMERA_UIT"

    # Authenticate to Google API
    drive = authenticate()
    # Get parent folder ID
    parent_folder_id_1 = get_folder_id(drive, 'root', "CAMERA_UIT")
    # Get destination folder ID
    parent_folder_id_2 = get_folder_id(drive, parent_folder_id_1, "Front_MMLAB")
    
    folder_id = get_folder_id(drive, parent_folder_id_2, dst_folder_name)

    # Create the folder if it doesn't exists
    if not folder_id:
        print('creating folder ' + dst_folder_name)
        folder_id = create_folder(drive, dst_folder_name, parent_folder_id_2)
    else:
        print('folder {0} already exists'.format(dst_folder_name))

    # Upload the files    
    upload_files(drive, folder_id, src_folder_name)


#if __name__ == "__main__":
#    test()