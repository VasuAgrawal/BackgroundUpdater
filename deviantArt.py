import baseAuth
import json
import time

class deviantArt(baseAuth.baseAuth):


    # by the end of this we should have an access token or have otherwise 
    # signaled that we weren't able to get one
    def __init__(self):
        self.readConfig()
        self.readKey()

        self.parameters = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }
        self.auth_url = "https://www.deviantart.com/oauth2/token"
        self.multi_auth()
        response = json.loads(self.r.content.decode("utf-8"))
        keys = response.keys()
        if "error" in keys:
            raise baseAuth.AuthException("Authentication failure from server!")
        elif "status" in keys:
            assert response["status"] == "success"
            self.access_token = response["access_token"]
            self.access_token_dict = {
                    "access_token": self.access_token,
                }

    def getDailyDeviations(self, date=""):
        dailyDeviationsURL = "https://www.deviantart.com/api/v1/oauth2/browse/dailydeviations"
        response = baseAuth.baseAuth.getJSONResponse(dailyDeviationsURL, self.access_token_dict)
        return response

    def getPopularAlltime(self, offset=0):
        popularURL = "https://www.deviantart.com/api/v1/oauth2/browse/popular"
        params = {
                "timerange": "8hr",
                "offset": str(offset),
            }
        params.update(self.access_token_dict)
        response = baseAuth.baseAuth.getJSONResponse(popularURL, params)
        return response

    def getPopularAlltimeItem(self):
        while(True):
            response = self.getPopularAlltime(offset=self.popular_offset)
            results = response.get("results", [])
            for r in results:
                yield r

            # craft next page
            # will reset to 0 instead of returning
            if (response.get("has_more") == "true") or (response.get("has_more") == True):
                self.popular_offset = int(response.get("next_offset"))
            else:
                self.popular_offset = 0

            print(self.popular_offset)
            self.writeConfig()
            time.sleep(1)

    def getImageURLFromItem(self, item):
        try:
            if (item.get("is_downloadable") and not item.get("is_deleted")):
                content = item.get("content")
                # must have same aspect ratio as 1080p
                height = content.get("height")
                width = content.get("width")
                assert((height >= 1080) and (width >= 1920) and
                       (round(height / width, 3) == round(1080 / 1920, 3)))
                return content.get("src")
        except:
            return ""

    def getWallpaperURL(self):
        url = ""
        pop = self.getPopularAlltimeItem()
        while(True):
            while(not url):
                url = self.getImageURLFromItem(next(pop))
            yield url
            url = ""

    def writeConfig(self):
        config = {
                "popular_offset": self.popular_offset,
            }
        with open("da.config", "w") as da:
            json.dump(config, da)

    def readConfig(self):
        try:
            with open("da.config", "r") as da:
                config = json.load(da)
                self.popular_offset = config.get("popular_offset")
        except:
            self.loadDefaultConfig()

    def loadDefaultConfig(self):
        self.popular_offset = 0

    def readKey(self):
        try:
            with open("da.key", "r") as da:
                config = json.load(da)
                self.client_id = config.get("client_id")
                self.client_secret = config.get("client_secret")
        except:
            raise baseAuth.AuthException("No key / value pair found in file!")
