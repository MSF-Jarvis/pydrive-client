# pydrive-client
Basic client for Google Drive uploads and downloads, built with [PyDrive](https://github.com/gsuitedevs/PyDrive)


### Requirements

* Python 3.7 or higher
* pip
* virtualenv


### Installation

```shell
# Create a virtualenv to avoid polluting the global module store
python3.7 -m virtualenv --no-site-packages venv
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

Read on to know how to setup authentication before you can actually start using this.


### Set up OAuth

*  Visit the [Google Cloud Console](https://console.developers.google.com/apis/credentials)
* Go to the OAuth Consent tab, fill it, and save.
* Go to the Credentials tab and click Create Credentials -> OAuth Client ID
* Choose Other and Create.
* Use the download button to download your credentials.
* Move that file to the root of pydrive-client, and rename it to `client_secret.json`

### Enable the Drive API

* Visit the [Google API Library](https://console.developers.google.com/apis/library) page.
* Search for Drive.
* Make sure that it's enabled. Enable it if not.

### Authenticating

* When first running pydrive-client, you will be prompted to follow an OAuth URL that will take you to the Google Drive login page, and then give you a code to paste on the terminal. Once that's done, these credentials will be cached and you will not be prompted again.

### Usage

```
$ ./main.py -h
usage: main.py [-h] [-l [LIST_FILES]] [-u UPLOAD_FILE] [-p PARENT_FOLDER]
               [-d DOWNLOAD_FILE] [-s | -f]

optional arguments:
  -h, --help            show this help message and exit
  -l [LIST_FILES], --list-files [LIST_FILES]
                        List the files in your drive
  -u UPLOAD_FILE, --upload-file UPLOAD_FILE
                        Pass a file to be uploaded to GDrive
  -p PARENT_FOLDER, --parent-folder PARENT_FOLDER
                        Only for use with with -u/--upload-file, sets parent
                        folder for uploaded file.
  -d DOWNLOAD_FILE, --download-file DOWNLOAD_FILE
                        Download the requested file
  -s, --skip            Skip existing files while downloading
  -f, --force           Re-download existing files
```
