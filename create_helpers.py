#!/usr/bin/env python3
import os

from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile


class _GoogleDriveFile(GoogleDriveFile):
    is_folder = False

    def __init__(self, file: GoogleDriveFile):
        super().__init__(file.auth, file.metadata)


def get_file(drive: GoogleDrive, filename: str, params: dict = None) -> _GoogleDriveFile:
    is_folder = False
    file_params = params if params else {}
    file_params['title'] = get_file_name(filename)
    if os.path.isdir(filename):
        file_params['mimeType'] = 'application/vnd.google-apps.folder'
        is_folder = True
    file = _GoogleDriveFile(drive.CreateFile(file_params))
    file.is_folder = is_folder
    if not is_folder:
        file.SetContentFile(filename)
    return file


def get_file_name(filename: str) -> str:
    return filename.split('/')[-1]
