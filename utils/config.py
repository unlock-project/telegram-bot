import configparser
from configparser import ConfigParser

config = configparser.ConfigParser()
config.read("config.ini")


def getToken():
    return config["TelegramAPI"]["token"]


def getAdmin():
    return int(config["Info"]["admin"])


def getDatabasePath():
    return config["DataBase"]["path"]


def getUnlockApiURL():
    return config["UnlockAPI"]["url"]
