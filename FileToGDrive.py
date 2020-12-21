import json
import requests

filedirectory = '###'
filename = '###'
folderid = '###'
access_token = '###'

metadata = {
    "name": filename,
    "parents": [folderid]
}
files = {
    'data': ('metadata', json.dumps(metadata), 'application/json'),
    'file': open(filedirectory, "rb").read()  # or  open(filedirectory, "rb")
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
    headers={"Authorization": "Bearer " + access_token},
    files=files
)
print(r.text)



from pydrive.drive import GoogleDrive 
from pydrive.auth import GoogleAuth 
   
# For using listdir() 
import os 
   
  
# Below code does the authentication 
# part of the code 
gauth = GoogleAuth() 
  
# Creates local webserver and auto 
# handles authentication. 
gauth.LocalWebserverAuth()        
drive = GoogleDrive(gauth) 
   
# replace the value of this variable 
# with the absolute path of the directory 
path = r"C:\Games\Battlefield"   
   
# iterating thought all the files/folder 
# of the desired directory 
for x in os.listdir(path): 
   
    f = drive.CreateFile({'title': x}) 
    f.SetContentFile(os.path.join(path, x)) 
    f.Upload() 
  
    # Due to a known bug in pydrive if we  
    # don't empty the variable used to 
    # upload the files to Google Drive the 
    # file stays open in memory and causes a 
    # memory leak, therefore preventing its  
    # deletion 
    f = None