from selenium import webdriver
from bs4 import BeautifulSoup
from scripts.frappeclient import FrappeClient
import time, json. sys

class RicaService(object):
    def __init__(self):
        accessDetails = open('/home/hemant/access.txt')
        aD = json.loads(accessDetails.read())
        self.client = FrappeClient(aD['url'],aD['username'],aD['password'])
        self.settingObj = self.client.get_api("varmani.getMTNServiceSettings")
        self.driver = webdriver.PhantomJS()
        self.login()

        #self.driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.logout()

    def login(self):
        self.driver.set_window_size(1120, 550)
        self.driver.get(self.settingObj['rica_login_url'])
        self.driver.find_element_by_id('txtId').send_keys(self.settingObj['rica_username'])
        self.driver.find_element_by_id("txtPassword").send_keys(self.settingObj['rica_password'])
        self.driver.find_element_by_id("btnLogin").click()
        #"""
        if self.driver.current_url == self.settingObj['rica_register_url']:
            return True
        else:
            return False

    def logout(self):
        self.driver.quit()

    def register(self, doc):
        result = {}
        self.driver.get(self.settingObj['rica_register_url'])
        if doc['is_consumer'] == True:
            self.driver.find_element_by_id('lstCustType').send_keys("C")
        else:
            self.driver.find_element_by_id('lstCustType').send_keys("J")

        self.driver.find_element_by_id('txtFName').send_keys(doc['first_names'])
        self.driver.find_element_by_id('txtSurname').send_keys(doc['last_names'])
        if doc['is_citizen'] == True:
            self.driver.find_element_by_id('optSA').send_keys("I")
        else:
            self.driver.find_element_by_id('optSA').send_keys("P")
        self.driver.find_element_by_id('txtID').send_keys(doc['identification_number'])
        self.driver.find_element_by_id('lstResRegion').send_keys(doc['region'])
        time.sleep(1)
        self.driver.find_element_by_id('txtResCityTown').send_keys(doc['city'])
        time.sleep(1)
        self.driver.find_element_by_id('txtResCityTown').send_keys(doc['city'])
        self.driver.find_element_by_id('txtResSuburb').send_keys(doc['surburb'])
        self.driver.find_element_by_id('txtResAddr1').send_keys(doc['address1'])
        self.driver.find_element_by_id('txtResAddr2').send_keys(doc['address2'])
        self.driver.find_element_by_id('txtResAddr3').send_keys(doc['address3'])
        self.driver.find_element_by_id('txtResCode').send_keys(doc['code'])

        #self.driver.find_element_by_id('txtMSISDN').send_keys("7203245157089")
        #time.sleep(1)

        self.driver.find_element_by_id('txtSIM').send_keys(doc['serial_number'])
        time.sleep(1)
        self.driver.find_element_by_id("btnAddSIM").click()

        #self.driver.find_element_by_id('txtSIMKit').send_keys("")
        time.sleep(2)
        self.driver.find_element_by_id("lnkSubmit").click()
        time.sleep(2)
        try:
            alert = self.driver.switch_to_alert()
            result.message = alert.text
            alert.accept()
        except:
            print ("no alert to accept")
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            #print soup._all_strings
            trs = soup.find('tr')
            for tr in trs:
                #print tr
                try:
                    self.result.message = tr.get_text()
                except:
                    pass


        if "successfully RICA'd" in result.message:
            result.processed= True
        else:
            result.processed = False

        return result

    def deregister(self, doc):
        result = {}
        self.driver.get(self.settingObj['rica_deregister_url'])

        self.driver.find_element_by_id('optSearchType_1').click()
        time.sleep(1)

        self.driver.find_element_by_id('txtSIM').send_keys(doc['serial_number'])
        if doc['is_citerzen'] == True:
            self.driver.find_element_by_id('optIDType_0').click()
            self.driver.find_element_by_id('txtID').send_keys(doc['identification_number'])
        else:
            self.driver.find_element_by_id('optIDType_').click()
            self.driver.find_element_by_id('lstCounty').send_keys(doc['country'])
            self.driver.find_element_by_id('txtPassport').send_keys(doc['identification_number'])
        time.sleep(1)
        self.driver.find_element_by_id("lnkSubmit").click()
        time.sleep(2)
        try:
            alert = self.driver.switch_to_alert()
            result.message = alert.text
            alert.accept()
        except:
            print ("no alert to accept")
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            #print soup._all_strings
            trs = soup.find('tr')
            for tr in trs:
                #print tr
                try:
                    self.result.message = tr.get_text()
                except:
                    pass


        if "successfuly deregistered" in result.message:
            result.processed= True
        else:
            result.processed = False

        return result
