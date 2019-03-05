from xdg import XDG_DATA_HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME
import os

class AppDirectories():
    def __init__(self):
        self.data = os.fspath(XDG_DATA_HOME.joinpath('quikey/'))
        self.config = os.fspath(XDG_CONFIG_HOME.joinpath('quikey/'))
        self.cache = os.fspath(XDG_CACHE_HOME.joinpath('quikey/'))
        os.makedirs(self.data, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)    
        os.makedirs(self.cache, exist_ok=True)

