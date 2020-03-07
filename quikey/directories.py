from xdg import BaseDirectory
import os

class AppDirectories():
    def __init__(self, data=None, config=None, cache=None, directory='quikey/'):
        self.data = os.fspath(os.path.join(data or BaseDirectory.xdg_data_home, directory))
        self.config = os.fspath(os.path.join(config or BaseDirectory.xdg_config_home, directory))
        self.cache = os.fspath(os.path.join(cache or BaseDirectory.xdg_cache_home, directory))
        os.makedirs(self.data, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)    
        os.makedirs(self.cache, exist_ok=True)

