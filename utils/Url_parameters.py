# Import Modules
import furl

class Url_parameters():
    def __init__(self):
        pass

    def url_parameters_convert(self, url, parameters = {}):
        f = furl.furl(url)
        f.args = parameters
        return f.url