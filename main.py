#!/usr/bin/env python3

import argparse
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


drive: GoogleDrive
http = None


def upload(filename: str) -> None:
    if not os.path.exists(filename):
        print("Specified filename {} does not exist!".format(filename))
        return
    file_to_upload = drive.CreateFile()
    file_to_upload.SetContentFile(filename)
    file_to_upload.Upload(param={"http": http})
    file_to_upload.FetchMetadata()
    file_to_upload.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })
    print("Get it with: {}".format(file_to_upload['id']))
    print("URL: {}".format(file_to_upload['webContentLink']))


def main() -> None:
    global drive, http
    gauth: GoogleAuth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.CommandLineAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    http = drive.auth.Get_Http_Object()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--upload-file", help="Pass a file to be uploaded to GDrive", type=str)
    args = parser.parse_args()
    if args.upload_file:
        upload(args.upload_file)
    else:
        print("No valid options provided!")


if __name__ == '__main__':
    main()
