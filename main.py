#!/usr/bin/env python3

"""
Wrapper around PyDrive that implements convenience functions that we
relied on other command line tools for without requiring writing the
code for this every time we want to use it.
"""
import argparse
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'


class DriveApiClient:
    """
    Wrapper around functions provided by the GoogleDrive class
    """
    drive: GoogleDrive
    http = None
    initial_folder = None

    def __init__(self):
        gauth: GoogleAuth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(os.path.dirname(os.path.abspath(__file__)) + "/mycreds.txt")
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
        gauth.SaveCredentialsFile(os.path.dirname(os.path.abspath(__file__)) + "/mycreds.txt")
        self.drive = GoogleDrive(gauth)
        self.http = self.drive.auth.Get_Http_Object()

    def upload(self, filename: str, parent_folder: str = None) -> None:
        """
        Upload a given file to Google Drive, optionally under a specific parent folder
        :param filename: The path to the file you wish to upload
        :param parent_folder: Optional parent folder override, defaults to root
        :return: None
        """
        if not os.path.exists(filename):
            print(f"Specified filename {filename} does not exist!")
            return
        file_params = {'title': filename.split('/')[-1]}
        if parent_folder:
            file_params['parents'] = [{"kind": "drive#fileLink", "id": parent_folder}]
        file_to_upload = self.drive.CreateFile(file_params)
        file_to_upload.SetContentFile(filename)
        file_to_upload.Upload(param={"http": self.http})
        file_to_upload.FetchMetadata()
        file_to_upload.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        print(f"Get it with: {file_to_upload['id']}")
        print(f"URL: {file_to_upload['webContentLink']}")

    def list_files(self,
                   parent_folder: str = 'root',
                   print_to_stdout: bool = False) -> (list, list):
        """
        List all files under a specific folder
        :param parent_folder: Optional folder ID to list files under, defaults to root
        :param print_to_stdout: While aggregating the list of files, also print to stdout
        :return: A tuple of two lists, first of files and second of directories
        """
        file_list = self.drive.ListFile({'q': f"'{parent_folder}' in parents and trashed=false"}).GetList()
        for file in file_list:
            if file['mimeType'] == FOLDER_MIME_TYPE:
                continue
            if print_to_stdout:
                print(f"Title: {file['title']}\tid: {file['id']}")

        parent_folder = self.drive.CreateFile({'id': parent_folder})
        parent_folder.FetchMetadata()
        title = parent_folder.metadata['title']
        try:
            if self.initial_folder is not None:
                while parent_folder.metadata['id'] != self.initial_folder.metadata['id']:
                    parent_folder = parent_folder.metadata['parents'][0]['id']
                    parent_folder = self.drive.CreateFile({'id': parent_folder})
                    parent_folder.FetchMetadata()
                    title = os.path.join(parent_folder.metadata['title'], title)
        except IndexError:
            title = os.path.join(self.initial_folder.metadata['title'], title)
        files_list, folders_list = [], []
        for file in file_list:
            file['title'] = os.path.join(title, file['title'])
            if file['mimeType'] != FOLDER_MIME_TYPE:
                files_list.append(file)
            else:
                folders_list.append(file)
        return files_list, folders_list

    def download_file(self, file_id: str) -> None:
        """
        Download a give file
        :param file_id: File ID to download
        :return: None
        """
        files_to_dl, folders_to_dl = [], []
        file = self.drive.CreateFile({'id': file_id})
        file.FetchMetadata()
        if file.metadata["mimeType"] == FOLDER_MIME_TYPE:
            print(f"{file.metadata['title']} is a folder, downloading recursively")
            files_to_dl, folders_to_dl = self.list_files(file_id)
            if self.initial_folder is None:
                self.initial_folder = file
                if not os.path.isdir(file.metadata['title']):
                    os.mkdir(file.metadata['title'])
        else:
            files_to_dl.append(file)
        for dl_file in files_to_dl:
            filename = dl_file['title']
            if os.path.isfile(filename):
                print(f'{filename} already exists, skipping.')
                continue
            print(f"Downloading {filename} -> {filename}")
            dl_file.GetContentFile(filename)
            print(f"Downloaded {filename}!")

        for folder in folders_to_dl:
            folder_name = folder['title']
            folder_id = folder.metadata['id']
            if not os.path.isdir(folder_name):
                os.makedirs(folder_name)
            self.download_file(folder_id)


def main() -> None:
    """
    The meat and potatoes of it all, entry point for this module.
    :return: None
    """
    client = DriveApiClient()
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list-files", help="List the files in your drive",
                        type=str, const="root", nargs='?', action="store")
    parser.add_argument("-u", "--upload-file", help="Pass a file to be uploaded to GDrive",
                        type=str)
    parser.add_argument("-p", "--parent-folder", help="Only for use with with -u/--upload-file, "
                                                      "sets parent folder for uploaded file.",
                        type=str)
    parser.add_argument("-d", "--download-file", help="Download the requested file", type=str)
    args = parser.parse_args()
    if args.list_files:
        client.list_files(args.list_files, True)
    elif args.upload_file:
        client.upload(args.upload_file, args.parent_folder)
    elif args.download_file:
        client.download_file(args.download_file)
    else:
        print("No valid options provided!")


if __name__ == '__main__':
    main()
