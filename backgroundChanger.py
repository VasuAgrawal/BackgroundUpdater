from deviantArt import deviantArt
import os
import requests
import subprocess
import time
import desktop

downloader = deviantArt()

oldtime = time.time()
for url in downloader.getWallpaperURL():
    with open("urls.txt", "a+") as urlFile:
        urlFile.write(url + "\n")
    filename = url[url.rfind("/")+1:] 
    filename = os.path.join("images", filename)

    r = requests.get(url, stream=True) 
    try:
        r.raise_for_status()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb+") as f:
            for chunk in r:
                f.write(chunk)
        abspath = os.path.abspath(filename)
        print(abspath)
        sleeptime = max((5*60) - (time.time() - oldtime), 0)
        print("sleeping for", sleeptime)
        # sleep for 5 minutes between attempts
        time.sleep(sleeptime)
        oldtime = time.time()

        print("setting wallpaper now!")
        retval = desktop.set_wallpaper(abspath)
        if not retval:
            print("failed to set desktop wallpaper")
        else:
            print("successfully set desktop wallpaper")

        # xfce specific, this section needs to be generalized
        # TODO make this work on all systems?
        #subprocess.call(["xfconf-query", "-c", "xfce4-desktop", "-p",
        #                 "/backdrop/screen0/monitor0/workspace0/last-image", "-s", abspath])
        #subprocess.call(["xfconf-query", "-c", "xfce4-desktop", "-p",
        #                 "/backdrop/screen0/monitor0/image-path", "-s", abspath])
    except:
        continue
