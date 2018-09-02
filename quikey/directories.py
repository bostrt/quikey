from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import os

class AppDirectories():
    def __init__(self):
        self.data = XDG_DATA_HOME + '/quikey/'
        self.config = XDG_CONFIG_HOME + '/quikey/'
        self.cache = XDG_CACHE_HOME + '/quikey/'
        os.makedirs(self.data, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)    
        os.makedirs(self.cache, exist_ok=True)

