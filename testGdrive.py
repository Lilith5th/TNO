import os

def uploadFile(localFolder, filename, targetFolderName):
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
    print('ok')
   
   
    folders = drive.ListFile(
        {'q': "title='" + targetFolderName+ "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
    for folder in folders:
        if folder['title'] == targetFolderName:
            file2 = drive.CreateFile({'parents': [{'id': folder['id']}]})
            file2.SetContentFile(filename)
            file2.Upload() 



#    # iterating thought all the files/folder 
#    # of the desired directory 
#    for x in os.listdir(localFolder): 
#        
#        f = drive.CreateFile({'title': x}) 
#        f.SetContentFile(os.path.join(localFolder, x)) 
#        f.Upload() 
#  
#        # Due to a known bug in pydrive if we  
#        # don't empty the variable used to 
#        # upload the files to Google Drive the 
#        # file stays open in memory and causes a 
#        # memory leak, therefore preventing its  
#        # deletion 
#        f = None
#        
#        
#folderName = '###'  # Please set the folder name.



if __name__ == "__main__":
    try:
        photoFolder= os.path.join(os.getcwd() ,"Photos")
        uploadFile(photoFolder,"photo_12_18-14_02_13.jpg","testing")
    except Exception as e:
        print (e)
