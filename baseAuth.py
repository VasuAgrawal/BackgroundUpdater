import requests
import json

class baseAuth(object):
    def __init__(self):
        self.auth_url = ""
        self.parameters = dict()

    def base_auth(self):
        self.r = None # clear existing response
        assert(self.auth_url)
        assert(self.parameters)
        r = requests.post(self.auth_url, data=self.parameters)
        r.raise_for_status() # might raise exception
        self.r = r

    def multi_auth(self, timeout=5, repeat=5):
        for i in range(repeat):
            try:
                self.base_auth()
                return
            except:
                time.sleep(timeout)
        raise AuthException("Unable to authenticate against server!")

    @staticmethod
    def getJSONResponse(url, params=dict()):
        r = requests.post(url, params=params)
        response = json.loads(r.content.decode("utf-8"))
        return response


# don't really need to do anything atm
class AuthException(Exception):
    pass
