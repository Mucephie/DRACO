#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
This is the configuration class for Dorado which utilizes the Astropy configuration 
system.
'''

from astropy import config as _config
from configparser import ConfigParser
import dorado
import os

rootname = 'dorado'

class ConfigNamespace(_config.ConfigNamespace):
    rootname = 'dorado'
    get_config = _config.get_config(packageormod = rootname, rootname = rootname)
    config_dir = _config.get_config_dir(rootname)
    print(config_dir)
    
    
config = ConfigParser()
api_key= #enter api_key
config.read('api_key')
config.set('key', 'api_key', '#enter api_key')


with open('api_key', 'w') as f:
    config.write(f)
print (config.get('key', 'api_key'))

save_path = 'config'

    use_logger = _config.ConfigItem(
        True, 'Whether to use the Dorado logger system.')
    # _config.generate_config(pkgname = rootname)
    _config.get_config.write()

class ConfigItem(_config.ConfigItem):
    rootname = 'dorado'




conf = ConfigNamespace()
print('Dorado directory created: ', conf.config_dir)
# conf.get_config.write()

__all__ = ['conf']

