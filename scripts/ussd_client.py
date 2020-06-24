import sys, json, requests, datetime, time
import xml.etree.ElementTree as ET
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol, ReconnectingClientFactory
from frappeclient import FrappeClient
from threading import Thread
from messageService import MessageSerice
from emailService import EmailService

class EchoClientProtocol(Protocol):
    def dataReceived(self, data):
        root = ET.fromstring(data)
        for datablock in root.findall('datablock'):
            # lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
            sessionid = datablock.find('sessionid').text
            msisdn = datablock.find('msisdn').text
            rootMsg = datablock.find('svcCode').text
            requestMsg = datablock.find('message').text.replace('*130*826*', '').replace('#', '')
            msgType = datablock.find('type').text
            localtime = time.asctime(time.localtime(time.time()))
            # ranNow = datetime.datetime.now().replace(microsecond=0)
            # saveTime = "timeRec=" + ranNow.strftime("%Y-%m-%d %H:%M:%S")
            log.msg(
                 localtime + " | " + sessionid + " | " + msisdn + " | " + rootMsg + " | " + requestMsg + " | " + msgType)

            # lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

            t = Thread(target=self.process_message, args=(sessionid,msisdn,rootMsg,requestMsg,msgType,))
            t.start()

            # try:
            #     lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
            #     self.client.post_api("varmani.setLastTime", saveTime)
            #
            # except Exception as e:
            #     log.msg("Unexpected error:" + str(e))

    def connectionMade(self):
        accessDetails = open('/home/hemant/access.txt')
        self.aD = json.loads(accessDetails.read())
        self.client = FrappeClient(self.aD['url'], self.aD['username'], self.aD['password'])
        self.settingObj = self.client.get_api("varmani.getMTNServiceSettings")

        getLoginMessage = "<usereq USERNAME='" + self.settingObj['ussd_username'] + "' PASSWORD='" + self.settingObj[
            'ussd_password'] + "' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='\*'/></usereq>END"

        data = getLoginMessage
        self.transport.write(data.encode())
        log.msg('Data sent {}'.format('MTN logging message'))

        myMessenger = EmailService()  # MessageSerice()
        mySMSer = MessageSerice()
        localtime = time.asctime(time.localtime(time.time()))
        myMessenger.sendMessage("USSD Service started", "USSD Service started on " + localtime, "hem@varmani.co.za")
        #mySMSer.sendSMS('27810378419', "USSD Service started on " + localtime)

    def connectionLost(self, reason):
        log.msg('Lost connection because {}'.format(reason))

    def process_message(self,sessionId, msisdn, rootMsg, requestMsg, msgType):
        self.client = FrappeClient(self.aD['url'], self.aD['username'], self.aD['password'])
        # lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
        session = self.record_message(sessionId, msisdn, rootMsg, requestMsg, msgType, '', "1")
        try:
            banned = self.client.get_api("varmani.isBanned", "msisdn=" + msisdn)
        except:
            banned = False

        message_type = 'USER_REQUEST'
        if (banned != True or banned == None):
            # print 'NOT banned'
            try:
                customer = self.client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.get_customer",
                                          "msisdn=" + msisdn)  # returns varmani network node
                if customer not None:
                    req_msg = requestMsg.split('*130*826')
                    # print req_msg
                    # print req_msg[len(req_msg)-1]
                    if rootMsg != '*130*826#':  # Speed dials
                        options = requestMsg.split('*')
                        # print str(options)
                        if options[0] == '0':  # Buy products
                            pass
                        elif options[0] == '1':  # Refer - *ID*SERIALNUMBER
                            try:
                                id = options[1]
                            # print id
                            except:
                                id = None
                                message = 'ID Number not provided or invalid'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'ERROR'
                            try:
                                serial_number = options[2]
                            # print serial_number
                            except:
                                serial_number = None
                                message = 'ID Number not provided or invalid'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'ERROR'
                            if id != None and serial_number != None:
                                # print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
                                result = self.client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.referral",
                                                        "id=%s&serial=%s&referrer=%s" % (
                                                        options[1], options[2], customer['name']))
                                message = result['message']
                                message_type = result['message_type']
                                next_command = result['next_command']

                        elif options[0] == '01':  # Opt in - *ID
                            try:
                                id = options[1]
                            # print id
                            except:
                                id = None
                                message = 'ID Number not provided or invalid'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'ERROR'

                            if id != None:
                                result = self.client.get_api(
                                    "varmani.varmani.doctype.varmani_network.varmani_network.opt_in",
                                    "id=%s&msisdn=%s" % (
                                        options[1], msisdn))
                                message = result['message']
                                message_type = result['message_type']
                                next_command = result['next_command']
                                customer = self.client.get_api(
                                    "varmani.varmani.doctype.varmani_network.varmani_network.get_customer",
                                    "msisdn=" + msisdn)  # returns varmani network node
                                # print customer
                        elif options[0] == '2':  # Get a new sim
                            try:
                                requester = options[1]
                            # print id
                            except:
                                requester = None
                                message = 'Sim Number not provided or invalid'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'ERROR'
                            if requester != None:
                                # print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
                                result = self.client.get_api("varmani.varmani.doctype.varmani_network.varmani_network.new_sim",
                                                        "requester=%s&serial=%s" % (
                                                            customer['name'], options[1]))
                                message = result['message']
                                message_type = result['message_type']
                                next_command = result['next_command']

                        elif options[0] == '202':  # new sim
                            # print str(options[1])
                            result = self.client.get_api(
                                "varmani.varmani.doctype.varmani_network.varmani_network.is_this_a_varmani_sim",
                                "serial_no=%s" % (str(options[1])))
                            # print str(result)
                            if result == None:
                                message = "You have not provided a Varmani Sim."
                            else:
                                result = self.client.get_api(
                                    "varmani.varmani.doctype.varmani_network.varmani_network.is_this_sim_sold",
                                    "serial_no=%s" % (str(options[1])))
                                # print str(result)
                                if result == None:
                                    message = 'Sim is available'
                                else:
                                    message = 'Sim already sold'
                            message_type = 'PULL_REQ_CONFIRM'
                            next_command = 'INTERNAL'

                        elif options[0] == '3':  # Balance
                            debt = self.client.get_api("erpnext.accounts.utils.get_balance_on",
                                                  "party_type=Customer&party=" + customer[
                                                      "customer"])  # +"&account=Debtors - VAR")
                            message = 'Your balance is ' + str(debt * -1)
                            message_type = 'PULL_REQ_CONFIRM'
                            next_command = 'BALANCE'
                        elif options[0] == '33':
                            pass
                        elif options[0] == '4':  # Reset Pin
                            pass
                        elif options[0] == '111':  # Sell a new sim to a Varmani Customer
                            pass
                        elif options[0] == '99':  # Special option for internal use only
                            pass
                        elif options[0] == '911':  # Helpdesk request by Varmani Customer
                            pass
                        else:
                            message = 'Unknown request: ' + requestMsg
                            message_type = 'PULL_REQ_CONFIRM'
                            next_command = 'ERROR'
                    else:
                        if session['command'] == '':
                            debt = self.client.get_api("erpnext.accounts.utils.get_balance_on",
                                                  "party_type=Customer&party=" + customer[
                                                      "customer"])  # +"&account=Debtors - VAR")
                            message = 'Welcome ' + customer["full_name"] + ', please provide your pin.'
                            message_type = 'USER_REQUEST'
                            next_command = 'PIN'
                        if session['command'] == 'PIN':
                            # print 'msisdn="%s"&pin="%s"' %(msisdn, requestMsg)
                            pin_verified = self.client.get_api(
                                "varmani.varmani.doctype.varmani_network.varmani_network.verify_varmani_customer_pin",
                                'msisdn=%s&pin=%s' % (msisdn, requestMsg))
                            # print pin_verified
                            if pin_verified == True:
                                message = 'Menu\n0- Buy a Varmani Product\n1- Refer Others\n2- Add a new sim to your account\n3- My Account Balance\n4- Reset your pin\nNeed Help? Dial *130*826*911#'
                                message_type = 'USER_REQUEST'
                                next_command = 'BUY'
                            else:
                                message = 'Pin NOT verify, please try again.'
                                message_type = 'USER_REQUEST'
                                next_command = 'PIN'

                        elif session['command'] == 'BUY':
                            if requestMsg == '0':  # buy product
                                message = 'Which product would you like to buy\n1) Airtime\n2) Electricity (Coming Soon)\nNeed Help? Dial *130*826*911#'
                                message_type = 'USER_REQUEST'
                                next_command = 'BUY'
                            elif requestMsg == '1':  # refer
                                message = 'You are buying\n Airtime\nNeed Help? Dial *130*826*911#'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'SELECT'
                            elif requestMsg == '2':  # new sim
                                message = 'You are buying\n Electricity (Coming Soon)\nNeed Help? Dial *130*826*911#'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'SELECT'
                            elif requestMsg == '3':  # balance
                                debt = self.client.get_api("erpnext.accounts.utils.get_balance_on",
                                                      "party_type=Customer&party=" + customer[
                                                          "customer"])  # +"&account=Debtors - VAR")
                                message = 'Your balance is ' + str(debt * -1)
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'MENU'
                            elif requestMsg == '4':  # reset pin
                                pass
                            elif requestMsg == '99':  # only for varmani
                                pass
                        elif session['command'] == 'ID_TYPE':
                            pass
                        elif session['command'] == 'ID_NUMBER':
                            pass
                        elif session['command'] == 'SIMNUM':
                            pass
                        elif session['command'] == 'SELECT':
                            pass
                        elif session['command'] == 'SENDTO':
                            pass
                        elif session['command'] == 'LOADTO':
                            pass
                        elif session['command'] == ' AMOUNT':
                            pass
                        elif session['command'] == 'CONFIRM_VEND':
                            message_type = 'PULL_REQ_CONFIRM'
                            # print customer
                            # print customer["full_name"]

                            # print message
                            # print message_type
                            # print next_command

                    # print message
                    # print message_type
                    # print next_command

                    self.send_ussd(sessionId, msisdn, message, message_type)  # 'USER_REQUEST')PULL_REQ_CONFIRM
                    self.record_message(sessionId, msisdn, rootMsg, message, message_type, next_command, "0")
                else:
                    req_msg = requestMsg.split('*130*826')
                    # print req_msg
                    # print req_msg[len(req_msg)-1]
                    if rootMsg != '*130*826#':  # Speed dials
                        options = requestMsg.split('*')
                        if options[0] == '01':  # opt in - *ID
                            try:
                                id = options[1]
                            # print id
                            except:
                                id = None
                                message = 'ID Number not provided or invalid'
                                message_type = 'PULL_REQ_CONFIRM'
                                next_command = 'ERROR'

                            if id != None:
                                customer = self.client.get_api(
                                    "varmani.varmani.doctype.varmani_network.varmani_network.get_customer",
                                    "id=" + id)  # returns varmani network node
                                # print customer
                                if customer <> None:
                                    # print 'got here: ' +"id=%s&serial=%s" % (options[1],options[2])
                                    result = self.client.get_api(
                                        "varmani.varmani.doctype.varmani_network.varmani_network.opt_in",
                                        "id=%s&msisdn=%s" % (
                                            options[1], msisdn))
                                    message = result['message']
                                    message_type = result['message_type']
                                    next_command = result['next_command']

                                    self.send_ussd(sessionId, msisdn, message, message_type)  # 'USER_REQUEST')PULL_REQ_CONFIRM
                                    self.record_message(sessionId, msisdn, rootMsg, message, message_type, next_command, "0")
                                else:
                                    # print 'No customer with msisdn=' + msisdn + ' found.'
                                    self.record_message(sessionId, msisdn, rootMsg,
                                                  'No customer with msisdn=' + msisdn + ' found.',
                                                  msgType, '', "0")
                            else:
                                # print 'No customer with msisdn=' + msisdn + ' found.'
                                self.record_message(sessionId, msisdn, rootMsg, 'No customer with msisdn=' + msisdn + ' found.',
                                              msgType, '', "0")
            except:
                # send_ussd(sessionId,msisdn,'Not Authorised!','PULL_REQ_CONFIRM')
                # print(sys.exc_info()[0])
                self.record_message(sessionId, msisdn, rootMsg, 'Not Authorised!', msgType, '', "0")

            # localtime = time.asctime(time.localtime(time.time()))
            # current = datetime.datetime.now().replace(microsecond=0)
            # diff = current - ranNow
            # seconds = diff.total_seconds()
            # lastTimeCheck = datetime.datetime.now().replace(microsecond=0)
            seconds = 0

        # currentTime = datetime.datetime.now()
        # diffTime = currentTime - lastTimeCheck
        # secondsTime = diffTime.total_seconds()
        # print 'sending message',secondsTime

        # lastTimeCheck = datetime.datetime.now().replace(microsecond=0)

        # currentTime = datetime.datetime.now()
        # diffTime = currentTime - lastTimeCheck
        # secondsTime = diffTime.total_seconds()
        # print 'Storing sessiong message', secondsTime
        else:
            # send_ussd(sessionId,msisdn,'Not Authorised!','PULL_REQ_CONFIRM')
            self.record_message(sessionId, msisdn, rootMsg, 'Banned!', msgType, '', "0")

    def send_ussd(self, sessionId, msisdn, msg, msgType):
        responseMeg = "<usareq NODE='" + self.settingObj['ussd_node'] + "' TRANSFORM='USSD' USERNAME='" + self.settingObj[
            'ussd_username'] + "' PASSWORD='" + self.settingObj[
                          'ussd_password'] + "' VERBOSITY='2'><command><ussd_response><sessionid>" + sessionId + "</sessionid><type>" + msgType + "</type><msisdn>" + msisdn + "</msisdn><message>" + msg + "</message></ussd_response></command></usareq>"
        r = requests.post(self.settingObj['message_url'], data={'command': responseMeg})

    def record_message(self,sessionid, msisdn, rootMsg, requestMsg, msgType, last_command, direction):
        # self.client = FrappeClient("https://www.varmani.co.za","administrator","gauranga")
        # print last_command
        try:
            nameMSISDN = self.client.get_value("MSISDN Communications", "name", {"msisdn": msisdn})
            if nameMSISDN:
                docMSISDN = self.client.get_doc("MSISDN Communications", nameMSISDN["name"])
            else:
                docMSISDN = {"doctype": "MSISDN Communications"}

            name = self.client.get_value("USSD Session", "name", {"ussd_sessionid": sessionid})
            if name:
                doc = self.client.get_doc("USSD Session", name["name"])
                # oldmessages = doc["messages"]
                doc["messages"] += "|- %s -|- %s -|- %s -|- %s -|- %s -|\n" % (
                datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), direction, msisdn,
                msgType, requestMsg)
                # doc["messages"] = oldmessages
                if last_command != '':
                    doc['command'] = last_command
            else:
                doc = {"doctype": "USSD Session"}
                doc['command'] = ''
                doc["messages"] = "|- %s -|- %s -|- %s -|- %s -|- %s -|\n" % (
                datetime.datetime.now().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), direction, msisdn,
                msgType, requestMsg)

            docMSISDN["msisdn"] = msisdn
            doc["ussd_sessionid"] = sessionid
            doc["msisdn"] = msisdn
            doc["root_message"] = rootMsg
            localtime = datetime.datetime.now().replace(microsecond=0)
            doc["date"] = localtime.strftime("%Y-%m-%d %H:%M:%S")

            try:
                docMSISDN['ussd_sessions'].append(doc)
            except:
                docMSISDN['ussd_sessions'] = []
                docMSISDN['ussd_sessions'].append(doc)

            # print(docMSISDN)
            # print "this far"
            docMSISDN['session_count'] = self.client.get_api("varmani.USSDMessageCount", "msisdn=" + msisdn)

            if nameMSISDN:
                self.client.update(docMSISDN)
            else:
                self.client.insert(docMSISDN)

            return doc

        except:
            print("something went wrong")
            print(sys.exc_info()[0])

            return None
            # print doc


class EchoClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.')

    def buildProtocol(self, addr):
        log.msg('Connected.')
        self.resetDelay()
        return EchoClientProtocol()

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Lost failed. Reason: {}'.format(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)


def main():
    log.startLogging(sys.stdout)
    log.msg('Start your engines...')

    accessDetails = open('/home/hemant/access.txt')
    aD = json.loads(accessDetails.read())
    client = FrappeClient(aD['url'], aD['username'], aD['password'])
    settingObj = client.get_api("varmani.getMTNServiceSettings")

    # getLoginMessage= "<usereq USERNAME='" + settingObj['ussd_username'] + "' PASSWORD='" + settingObj[
    #         'ussd_password'] + "' VERBOSITY='0'><subscribe NODE='.*' TRANSFORM='USSD' PATTERN='.*'/></usereq>END\nHB"

    reactor.connectTCP(settingObj['ussd_server_socket_ip'], int(settingObj['ussd_server_socket_port']), EchoClientFactory())
    reactor.run()


if __name__ == '__main__':
    main()
