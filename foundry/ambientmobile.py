"""
Interim SMS gateway solution. This may or may not belong in foundry.
"""

import urllib2
from time import time
from xml.dom import minidom

class NotTextNodeError:
    pass

class AmbientSMSError(Exception):

    def __init__(self, code_or_error):

        self.msg = ERROR_CODES.get(code_or_error, code_or_error)

    def __str__(self):
        return repr(self.msg)

ERROR_CODES = {
    0: "Message successfully submitted. Success",
    1: "Message successfully submitted, but contained recipient errors. Success",
    2: "Message successfully submitted, but contained duplicates and recipient errors. Success",
    1000: "Message successfully submitted, but contained duplicates. Success",
    1001: "Invalid HTTP POST. Failure",
    1002: "HTTP Post Empty no XML string found. Failure",
    1003: "Malformed XML. Failure",
    1004: "Invalid XML.Failure",
    1005: "Authentication Error: API-Key empty. Failure",
    1006: "Authentication Error: API-Key invalid.Failure",
    1007: "Authentication Error: Password empty. Failure",
    1008: "Authentication fail.Failure",
    1009: "No recipients found. Failure",
    1010: "Invalid Recipient(s) Failure",
    1011: "Message body empty. Failure",
    1012: "Message body exceeds maximum message length.Failure",
    1013: "Message body contains invalid characters. Failure",
    1014: "There were duplicates found. Failure",
    1015: "Authentication Error: IP address not allowed. Failure",
    1016: "Invalid message id. Failure",
    1017: "Insufficient credits. Failure",
    1018: "Account suspended.Failure",
    1019: "Account deactivated.Failure",
}

def dictFromXml(xmlString):
    'retuns the a dictionary from the xml string'

    dom = minidom.parseString(xmlString)
    return nodeToDic(dom.childNodes[0])

def getTextFromNode(node):
    """
    scans through all children of node and gathers the
    text. if node has non-text child-nodes, then
    NotTextNodeError is raised.
    """
    t = ""
    for n in node.childNodes:
	if n.nodeType == n.TEXT_NODE:
	    t += n.nodeValue
	else:
	    raise NotTextNodeError
    return t

def nodeToDic(node):
    dic = {}
    multlist = {} # holds temporary lists where there are multiple children
    multiple = False
    for n in node.childNodes:
        if n.nodeType != n.ELEMENT_NODE:
            continue

        # find out if there are multiple records
        if len(node.getElementsByTagName(n.nodeName)) > 1:
            multiple = True
            # and set up the list to hold the values
            if not multlist.has_key(n.nodeName):
                multlist[n.nodeName] = []

        try:
            #text node
            text = getTextFromNode(n)
        except NotTextNodeError:
            if multiple:
                # append to our list
                multlist[n.nodeName].append(nodeToDic(n))
                dic.update({n.nodeName:multlist[n.nodeName]})
                continue
            else:
                # 'normal' node
                dic.update({n.nodeName:nodeToDic(n)})
                continue

        # text node
        if multiple:
            multlist[n.nodeName].append(text)
            dic.update({n.nodeName:multlist[n.nodeName]})
        else:
            dic.update({n.nodeName:text})
    return dic


class AmbientSMS(object):
    """
    Provides a wrapper around the AmbientSMS HTTP/S API interface
    """

    def __init__ (self, api_key, password):
        """
        Initialise the AmbientSMS class

        Expects:
         - api_key - your AmbientSMS Central username
         - password - your AmbientSMS Central password
        """
        self.api_key = api_key
        self.password = password


    def getbalance(self, url='http://services.ambientmobile.co.za/credits'):
        """
        Get the number of credits remaining at AmbientSMS
        """
        postXMLList = []
        postXMLList.append("<api-key>%s</api-key>" % self.api_key)
        postXMLList.append("<password>%s</password>" % self.password)
        postXML = '<sms>%s</sms>' % "".join(postXMLList)
        result = self.curl(url, postXML)

        if result.get("credits", None):
            return result["credits"]
        else:
            raise AmbientSMSError, result["status"]


    def sendmsg(self,
                message,
                recipient_mobiles=[],
                url='http://services.ambientmobile.co.za/sms',
                concatenate_message=True,
                message_id=str(time()).replace(".", ""),
                reply_path=None,
                allow_duplicates=True,
                allow_invalid_numbers=True,
                ):

        """
        Send a mesage via the AmbientSMS API server
        """
        if not recipient_mobiles or not(isinstance(recipient_mobiles, list) or  isinstance(recipient_mobiles, tuple)):
            raise AmbientSMSError, "Missing recipients"

        if not message or not len(message):
            raise AmbientSMSError, "Missing message"

        postXMLList = []
        postXMLList.append("<api-key>%s</api-key>" % self.api_key)
        postXMLList.append("<password>%s</password>" % self.password)
        postXMLList.append("<recipients>%s</recipients>" % "".join(["<mobile>%s</mobile>" % m for m in recipient_mobiles]))
        postXMLList.append("<msg>%s</msg>" % message)
        postXMLList.append("<concat>%s</concat>" % (1 if concatenate_message else 0))
        postXMLList.append("<message_id>%s</message_id>" % message_id)
        postXMLList.append("<allow_duplicates>%s</allow_duplicates>" % (1 if allow_duplicates else 0))
        postXMLList.append("<allow_invalid_numbers>%s</allow_invalid_numbers>" % (1 if allow_invalid_numbers else 0))
        if reply_path:
            postXMLList.append("<reply_path>%s</reply_path>" % reply_path)

        postXML = '<sms>%s</sms>' % "".join(postXMLList)
        result = self.curl(url, postXML)

        status = result.get("status", None)
        if status and int(status) in [0, 1, 2]:
            return result
        else:
            raise AmbientSMSError, int(status)

    def curl(self, url, post):
        """
        Inteface for sending web requests to the AmbientSMS API Server
        """
        try:
            req = urllib2.Request(url)
            req.add_header( "Content-type" , "application/xml")
            data = urllib2.urlopen(req, post.encode('utf-8')).read()
        except urllib2.URLError, v:
            raise AmbientSMSError, v
        return dictFromXml(data)


