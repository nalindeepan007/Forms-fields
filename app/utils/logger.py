import logging
import os
from logging.handlers import RotatingFileHandler


os.makedirs("logs", exist_ok=True)


logger = logging.getLogger("forms_service")
logger.setLevel(logging.INFO)


consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)


fileHandler = RotatingFileHandler(
    "logs/forms_service.log", 
    maxBytes=10485760,  # file size abhi 10 MB, loggfile change hoti rahe
    backupCount=5
)
fileHandler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)


logger.addHandler(consoleHandler)
logger.addHandler(fileHandler)

def getLogger():
    return logger