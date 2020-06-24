from suds.client import Client

wsdlUrl = 'http://ws.marblegold.co.za/vend.asmx?WSDL'

client = Client(wsdlUrl)
#print client

result = client.service.authenticate_cashier('27832123780','27832123780','135326')#client.service.get_productlist()
print (result)
token = result.token
if token != None:
    print ("connected = authenticated")
    result = client.service.get_balance(token)
    print (result)

    # reference= 'test'
    # sourcemsisdn='27832123780'
    # msisdn='27810378419'
    # denomination=2.00
    # result = client.service.vend_airtime_pinless(token, reference, sourcemsisdn, msisdn, denomination)
    # print result
    #
    # result = client.service.history_airtimepinless(token,'27832123780')
    # print result
    #
    # result = client.service.get_balance(token)
    # print result

    enum = client.factory.create('ReportTypeEnum')
    print (enum)

    result = client.service.get_salesreport(token, 'DayEndHistoric', [])
    print (result)
