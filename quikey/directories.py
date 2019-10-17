from xdg import BaseDirectory
import os

class AppDirectories():
    def __init__(self):
        self.data = os.fspath(os.path.join(BaseDirectory.xdg_data_home, 'quikey/'))
        self.config = os.fspath(os.path.join(BaseDirectory.xdg_config_home, 'quikey/'))
        self.cache = os.fspath(os.path.join(BaseDirectory.xdg_cache_home, 'quikey/'))
        os.makedirs(self.data, exist_ok=True)
        os.makedirs(self.config, exist_ok=True)    
        os.makedirs(self.cache, exist_ok=True)

