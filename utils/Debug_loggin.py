# Importar Modulos
from datetime import datetime

import logging
import os

class Debug_loggin():
    def __init__(self, path='logs/'):
        self.path = path
        try:
            os.stat(self.path)
        except:
            os.mkdir(self.path)
        
        logging.basicConfig(
            filename="{}log-{}.log".format(self.path, datetime.today().strftime('%Y-%m-%d')),
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s:%(message)s"
        )
    
    def log_debug(self, msg):
        logging.debug(str(msg))

    def log_info(self, msg):
        logging.info(str(msg))
        
    def log_warning(self, msg):
        logging.warning(str(msg))
    
    def log_error(self, msg):
        logging.error(str(msg))
    
    def log_critical(self, msg):
        logging.error(str(msg))
