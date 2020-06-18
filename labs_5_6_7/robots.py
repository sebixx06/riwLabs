import urllib.robotparser
from urllib.parse import urlparse
import os
from Header import robots_dictionary

def get_robo(baselink):

    rfp = urllib.robotparser.RobotFileParser()
    domain = urlparse(baselink).netloc
    rfp.set_url(baselink + '/robots.txt')
    try:
        rfp.read()
        robots_dictionary[domain] = rfp
    except:
            robots_dictionary[domain] = None
            rfp = None
    return rfp

def canfetch(robo,localpath,nume_robot):
    if robo.can_fetch(nume_robot,localpath):
        return True
    else:
        return False
