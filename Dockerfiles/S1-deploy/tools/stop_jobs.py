import httplib
import urllib2
import urllib
import cookielib
import sys
import json
import time
import os

class RequestWithMethod(urllib2.Request):
    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)
    def get_method(self):
        return self._method

def buildSchedules(obj):
    schedules = []
    for e in obj["d"]["results"]:
        schedule = {
            "JOB": "/" + e["JOB_NAME"].replace("::","/").replace(".","/") + ".xsjob",
            "SCHEDULE": {
                "id": e["ID"],
                "description": e["DESCRIPTION"],
                "xscron": e["XSCRON"],
                "parameter": None if not e["PARAMETER"] else json.loads(e["PARAMETER"]),
                "active": False
            }
        }
        schedules.append(schedule)
    return schedules

def getCookieJar(cookieFile):
    cookiejar = cookielib.MozillaCookieJar(cookieFile)
    cookiejar.load(ignore_expires=True, ignore_discard=True)
    for cookie in cookiejar:
        cookie.expires = int(time.time()) + 24 * 3600
    return cookiejar

def getProxySetup():
    httpProxy = os.environ["http_proxy"]
    httpsProxy = os.environ["https_proxy"]
    httpProxy = httpProxy[(httpProxy.index("://") + 3):]
    httpsProxy = httpsProxy[(httpsProxy.index("://") + 3):]
    return {
        "http": httpProxy,
        "https": httpsProxy
    }

def httpCall(method, url, headers, payload, cookieFile):
    proxyHandler = urllib2.ProxyHandler(getProxySetup())
    httpHandler = urllib2.HTTPHandler()
    httpsHandler = urllib2.HTTPSHandler()
    cookieProcessor = urllib2.HTTPCookieProcessor(getCookieJar(cookieFile))
    opener = urllib2.build_opener(proxyHandler, httpHandler, httpsHandler, cookieProcessor)

    req = RequestWithMethod(method, url, payload, headers)
    res = opener.open(req)
    data = res.read()
    return data

def getSchedules(protocol, host, port, cookieFile):
    path = "/sap/hana/xs/admin/jobs/service/schedules.xsodata/Schedules?$filter=startswith(JOB_NAME,%27sap.sports%27)&$format=json"
    url = protocol + "://" + host + ":" + port + path
    return httpCall("GET", url, {}, None, cookieFile)

def updateSchedule(protocol, host, port, payload, token, cookieFile):
    path = "/sap/hana/xs/admin/jobs/server/common/editSchedule.xsjs"
    url = protocol + "://" + host + ":" + port + path
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-csrf-token": token
    }
    return httpCall("PUT", url, headers, payload, cookieFile)

def main(argv):
    protocol = argv[0]
    host = argv[1]
    port = argv[2]
    token = argv[3]
    cookies = argv[4]
    res = getSchedules(protocol, host, port, cookies)
    obj = json.loads(res)
    schedules = buildSchedules(obj)
    for schedule in schedules:
        if schedule["JOB"] == '/sap/sports/fnd/db/schema/authorization/generateAllUsersPrivileges.xsjob':
            continue
        print "Deactivate " + schedule["JOB"]
        try:
            result = updateSchedule(protocol, host, port, json.dumps(schedule), token, cookies)
            print "Success"
        except:
            print "Error: ", sys.exc_info()

if __name__ == "__main__":
    main(sys.argv[1:])
