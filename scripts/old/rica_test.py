from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
import time, json, sys

rica = {
    "first_names": "Hemant Govan",
    "identification_number": "7203245157089",
    "creation": "2016-10-05 03:43:52.010489",
    "name_verified": 1,
    "code": "2196",
    "owner": "Administrator",
    "city": "SANDTON",
    "surburb": "HURL PARK",
    "modified_by": "Administrator",
    "address_verified_on": "2016-10-05 03:45:51.577884",
    "address_verified": 1,
    "sims_to_rica": [
      {
        "serial_no": "1742410024",
        "modified_by": "Administrator",
        "name": "a438dd5501",
        "parent": "4ef95dff68",
        "to_be_invoiced": 1,
        "creation": "2016-10-05 03:43:52.010489",
        "modified": "2016-10-05 03:46:30.339666",
        "doctype": "Sims To Rica",
        "idx": 1,
        "parenttype": "RICA Submission",
        "owner": "Administrator",
        "docstatus": 0,
        "ricaed": 0,
        "parentfield": "sims_to_rica"
      }
    ],
    "docstatus": 0,
    "is_citizen": 1,
    "identity_number_verified": 1,
    "is_consumer": 1,
    "address1": "F102 Rosewalk Manor",
    "address2": "",
    "address3": "",
    "doctype": "RICA Submission",
    "customer": "V00000379",
    "name": "4ef95dff68",
    "idx": 0,
    "last_names": "Pema",
    "country": "",
    "region": "GAUTENG",
    "modified": "2016-10-05 03:46:30.339666",
    "fullname": "Hemant Govan Pema"
  }


driver = webdriver.PhantomJS()
driver.set_window_size(1120, 550)
driver.get("https://rica.mtn.co.za/PCRLogin.aspx")
# frappe.msgprint(driver.current_url)
driver.find_element_by_id('txtId').send_keys("7203245157089")
driver.find_element_by_id("txtPassword").send_keys("G@ur@ng@!08")
driver.find_element_by_id("btnLogin").click()

if driver.current_url == "https://rica.mtn.co.za/Actions.aspx":
    print ("Login successful")
    result = 'Login successful'
    driver.get("https://rica.mtn.co.za/RegisterNumber.aspx")
    if rica.is_consumer == True:
        driver.find_element_by_id('lstCustType').send_keys("C")
    else:
        driver.find_element_by_id('lstCustType').send_keys("J")

    driver.find_element_by_id('txtFName').send_keys(rica.first_names)
    driver.find_element_by_id('txtSurname').send_keys(rica.last_names)
    if rica.is_citizen == True:
        driver.find_element_by_id('optSA').send_keys("I")
    else:
        driver.find_element_by_id('optSA').send_keys("P")
    driver.find_element_by_id('txtID').send_keys(rica.identification_number)
    driver.find_element_by_id('lstResRegion').send_keys(rica.region)
    time.sleep(1)
    driver.find_element_by_id('txtResCityTown').send_keys(rica.city)
    time.sleep(1)
    driver.find_element_by_id('txtResSuburb').send_keys(rica.surburb)
    driver.find_element_by_id('txtResAddr1').send_keys(rica.address1)
    driver.find_element_by_id('txtResAddr2').send_keys(rica.address2)
    driver.find_element_by_id('txtResAddr3').send_keys(rica.address3)
    driver.find_element_by_id('txtResCode').send_keys(rica.code)

    # self.driver.find_element_by_id('txtMSISDN').send_keys("7203245157089")
    # time.sleep(1)

    driver.find_element_by_id('txtSIM').send_keys(s.serial_no)
    time.sleep(1)
    driver.find_element_by_id("btnAddSIM").click()

    # self.driver.find_element_by_id('txtSIMKit').send_keys("")
    time.sleep(2)
    driver.find_element_by_id("lnkSubmit").click()
    time.sleep(3)
    print (driver)
    try:
        alert = driver.switch_to_alert()
        print (alert.text)
        # result += '\n| %s | %s |' % (frappe.utils.now_datetime().replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S"), alert.text)
        alert.accept()
    except:
        pass
        # driver.get(data.rica_menu_url)
        # time.sleep(2)
        # driver.find_element_by_id('txtMSISDN').send_keys(s.serial_no)#btnSearch
        # driver.find_element_by_id("btnSearch").click()

        print (str(sys.exc_info()[0]))
        # result += "\nFailled"
        # frappe.msgprint(driver.page_source)
        # soup = BeautifulSoup(driver.page_source, 'html.parser')#"lxml")
        # frappe.msgprint(str(soup))
        # trs = soup.find('tr')
        # for tr in trs:
        # 	# print tr
        # 	try:
        # 		result.message = tr.get_text()
        # 	except:
        # 		pass

    if result.lower().find(("successfully RICA'd").lower()) != -1:
        print (result)
    else:
        print ('Failed')

driver.quit()
