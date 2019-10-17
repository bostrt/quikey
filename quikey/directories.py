from xdg import BaseDirectory
import os

class AppDirectories():
    def __init__(self):
        self.data = os.fspath(BaseDirectory.xdg_data_home.joinpath('quikey/'))
        self.config = os.fspath(BaseDirectory.xdg_config_home.joinpath('quikey/'))
        self.cache = os.fspath(BaseDirectory.xdg_cache_home.joinpath('quikey/'))
        os.makedirs(self.data, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)    
        os.makedirs(self.cache, exist_ok=True)

