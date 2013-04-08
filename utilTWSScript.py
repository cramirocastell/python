import requests
import time
import csv
import sys
import json
import re
from optparse import OptionParser

protocol = 'http'
verify = False
delay = 10
cont = 0
contfile = 0

parserArg = OptionParser(usage="usage: %prog [options]")
parserArg.add_option("-a", "--assign", dest="assign_flag", action="store_true", help="assign cards.")
parserArg.add_option("-r", "--register", dest="register", action="store_true", help="register users")
parserArg.add_option("-z", "--remove", dest="remove_user", action="store_true", help="remove users")
parserArg.add_option("-s", "--ssl", dest="ssl_flag", action="store_true", help="use ssl protocol for connection")
parserArg.add_option("-d", "--delay", dest="delay_time", help="delay between each request in milliseconds (Default=10)")
parserArg.add_option("-m", "--msisdn", dest="msisdn", help="msisdn of user")
parserArg.add_option("-c", "--serviceid", dest="serviceid", help="card serviceid. If -f, script automatically replaces given uniqueId with msisdn")
parserArg.add_option("-e", "--aid", dest="aid", help="card aid")
parserArg.add_option("-f", "--filename", dest="filename", help="filename that contains msisdn list")
parserArg.add_option("-i", "--host", dest="server_host", help="server host to connect (Example: 10.95.55.13:8080")
opts, args = parserArg.parse_args()	
if opts.ssl_flag:
    verify = True
    protocol = 'https'
if opts.delay_time:
    delay = float(opts.delay_time) / 1000
if opts.assign_flag and opts.register:
    parserArg.error("could not perform both operations at the same time")
if not opts.assign_flag and not opts.register and not opts.remove_user:
    parserArg.error("-a, -r or -z options are mandatory")
if not opts.server_host:
    parserArg.error("server host is mandatory")


if opts.assign_flag:
    if not opts.aid and not opts.serviceid:
        parserArg.error("-a flag must be combined with [-m -c -e] or [-c -e -f] options")

if opts.register:
    if not opts.filename and not opts.msisdn:
        parserArg.error("-r flag must be combined with -m or -f options")



serviceid = opts.serviceid
if serviceid:
    serviceid_split = re.split('\.', serviceid)
    if not len(serviceid_split) == 5:
        parserArg.error("wrong serviceid lenth")


def sendRemoveUser(msisdn):
    global cont
    cadena = ''.join([protocol, '://', opts.server_host, '/cms/subscribers/', msisdn])
    print "Remove:", cadena
    headers = {"Accept": "text/html", "Accept-Charset": "UTF-8", "Authorization": "Basic U3VwRVI6c1VQZXI="}
    resp = requests.delete(cadena, headers=headers)
    cont += 1
    if resp.status_code not in [200, 201]:
        msg = "sendRemoveUser failed. Response: {0}, expected {1}, text: {2}"
        raise RuntimeError(msg.format(resp, [200, 201], resp.text))
    print resp


def sendAssign(msisdn, aid, serviceid):
    global cont
    cadena = ''.join([protocol, '://', opts.server_host, '/cms/subscribers/', msisdn, '/cards'])
    print "Assign:", cadena
    headers = {"Accept": "text/html", "Accept-Charset": "UTF-8", "Track-ID": ''.join(["util-", msisdn]),
               "Content-Type": "application/json", "Authorization": "Basic U3VwRVI6c1VQZXI="}
    body = {"serviceId": str(serviceid), "cardDetails": {"aid": str(aid)}}
    resp = requests.post(cadena, data=json.dumps(body), headers=headers, timeout=10)
    cont += 1
    if resp.status_code not in [200, 201]:
        msg = "sendAssign failed. Response: {0}, expected {1}, text: {2}"
        raise RuntimeError(msg.format(resp, [200, 201], resp.text))
    print resp


def sendRegistration(msisdn):
    global cont
    cadena = ''.join([protocol, '://', opts.server_host, '/smsagent/DE/LSDP/incomingSMS'])
    print "Register:", cadena
    headers = {"Accept-Encoding": "gzip,deflate", "Content-Type": "text/xml;charset=UTF-8",
               "SOAPAction": "urn:notifySmsReception"}
    registration_body = '''
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:sec="http://www.telefonica.com/wsdl/UNICA/SOAP/common/v1/security_headers"
    xmlns:v1="http://www.telefonica.com/schemas/UNICA/SOAP/common/v1"
    xmlns:loc="http://www.telefonica.com/wsdl/UNICA/SOAP/SMS/v1/local" xmlns:v11="http://www.telefonica.com/schemas/UNICA/SOAP/SMS/v1/">
    <soapenv:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <wsse:UsernameToken>
            <wsse:Username>walletUser</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">walletPassword</wsse:Password>
        </wsse:UsernameToken>
    </wsse:Security>
    <sec:simpleOAuthHeader/></soapenv:Header>
    <soapenv:Body>
        <loc:notifySmsReception>
            <loc:correlator>123123</loc:correlator>
            <loc:message>
                <v11:message>Pruebas de Jose</v11:message>
                <v11:originAddress>
                    <v1:phoneNumber>''' + msisdn + '''</v1:phoneNumber></v11:originAddress>
                <v11:destinationAddress>
                    <v1:phoneNumber>''' + msisdn + '''</v1:phoneNumber></v11:destinationAddress>
            </loc:message>
        </loc:notifySmsReception>
    </soapenv:Body>
    <sec:simpleOAuthHeader/></soapenv:Envelope>'''
    resp = requests.post(cadena, data=registration_body, headers=headers)
    cont += 1
    if resp.status_code not in [200, 201]:
        msg = "sendRegistration failed. Response: {0}, expected {1}, text: {2}"
        raise RuntimeError(msg.format(resp, [200, 201], resp.text))
    print resp


if opts.filename:
    f = csv.reader(open("users.csv"))
    for linea in f:
        if linea:
            contfile += 1
            if opts.assign_flag:
                serviceid = ''.join([serviceid_split[0], '.', serviceid_split[1], '.', serviceid_split[2],
                                     '.',  serviceid_split[3], '.', linea[0]])
                sendAssign(linea[0], opts.aid, serviceid)
            elif opts.register:
                sendRegistration(linea[0])
            elif opts.remove_user:
                sendRemoveUser(linea[0])
            time.sleep(float(delay))
else:
    if opts.assign_flag:
        sendAssign(opts.msisdn, opts.aid, serviceid)
    elif opts.register:
        sendRegistration(opts.msisdn)
    elif opts.remove_user:
        sendRemoveUser(opts.msisdn)

print '\n\n'
if opts.filename:
    print 'File has [' + str(contfile) + '] lines\n'
    if contfile != cont:
        print '\nWARNING!!! Some lines have not be processed'

print 'Processed [' + str(cont) + '] requests'
