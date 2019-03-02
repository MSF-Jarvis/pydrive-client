#!/usr/bin/env python3

import argparse
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
# pylint: disable=invalid-name
drive: GoogleDrive
http = None


def upload(filename: str, parent_folder: str = None) -> None:
    if not os.path.exists(filename):
        print("Specified filename {} does not exist!".format(filename))
        return
    file_params = {'title': filename.split('/')[-1]}
    if parent_folder:
        file_params['parents'] = [{"kind": "drive#fileLink", "id": parent_folder}]
    file_to_upload = drive.CreateFile(file_params)
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


def list_files(parent_folder: str = 'root', skip_print: bool = False) -> list:
    file_list = drive.ListFile({'q': f"'{parent_folder}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['mimeType'] == FOLDER_MIME_TYPE:
            continue
        if not skip_print:
            print('Title: {}\tid: {}'.format(file['title'], file['id']))
    return file_list


def download_file(file_id: str) -> None:
    file = drive.CreateFile({'id': file_id})
    files_to_dl = []
    file.FetchMetadata()
    if file.metadata["mimeType"] == FOLDER_MIME_TYPE:
        # TODO: Support folders inside folders
        print("{} is a folder, downloading recursively".format(file.metadata['title']))
        files_to_dl = list_files(file_id, skip_print=True)
    else:
        files_to_dl.append(file)
    for dl_file in files_to_dl:
        filename = dl_file['title']
        print("Downloading {0} -> {0}".format(filename))
        dl_file.GetContentFile(filename)
        print("Downloaded {}!".format(filename))


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
    parser.add_argument("-l", "--list-files", help="List the files in your drive",
                        action="store_true")
    parser.add_argument("-u", "--upload-file", help="Pass a file to be uploaded to GDrive",
                        type=str)
    parser.add_argument("-p", "--parent-folder", help="Only for use with with -u/--upload-file, "
                                                      "sets parent folder for uploaded file.",
                        type=str)
    parser.add_argument("-d", "--download-file", help="Download the requested file", type=str)
    args = parser.parse_args()
    if args.list_files:
        list_files()
    elif args.upload_file:
        upload(args.upload_file, args.parent_folder)
    elif args.download_file:
        download_file(args.download_file)
    else:
        print("No valid options provided!")


if __name__ == '__main__':
    main()
