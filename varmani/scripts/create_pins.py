import json, time
from frappeclient import FrappeClient
import socket, select, string, sys, datetime
from messageService import MessageSerice
import hashlib, time
#from .utils import random_string
import string
from Queue import Queue
from threading import Thread
from random import choice
import MySQLdb as my




#frappe.generate_hash(doctype, 10)

if __name__ == "__main__":

    accessDetails = open('/home/hemant/access.txt')
    aD = json.loads(accessDetails.read())

    current = datetime.datetime.now().replace(microsecond=0)
    #
    # {
    #   "data": {
    #     "modified_by": "Administrator",
    #     "name": "dddfb9bb9a",
    #     "creation": "2016-11-10 14:28:48.729964",
    #     "modified": "2016-11-10 14:28:48.729964",
    #     "item_code": "C10-P",
    #     "doctype": "Bulk Pins",
    #     "vendor": "",
    #     "idx": 0,
    #     "pin": "***",
    #     "serial_number": "34785q",
    #     "owner": "Administrator",
    #     "docstatus": 0
    #   }
    # }

    sql = "INSERT INTO `tabBulk Pins` (name, creation, item_code, serial_number, pin) VALUES (%s, %s, %s, %s, %s)"
    # try:
    client = FrappeClient(aD['url'], aD['username'], aD['password'])
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    items = client.get_api('varmani.varmani.doctype.bulk_pins.bulk_pins.get_items')
    # print items
    counter = 0

    def random_string(length):
        """generate a random string"""
        import string
        from random import choice
        return ''.join([choice(string.letters + string.digits) for i in range(length)])


    def do_stuff(q,i):
        while True:
            p= q.get()
            # client.get_api("varmani.varmani.doctype.bulk_pins.bulk_pins.load_pin", "serial=%s&item=%s" % (str(p[0]),str(p[1])))
            # print p
            db = my.connect(host=aD['mysql_server'], user='root', passwd=aD['mysql_password'], db=aD['mysql_database'])
            cursor = db.cursor()
            number_of_rows = cursor.executemany(sql,p)
            db.commit()
            db.close()
            q.task_done()
        # print 'Thread ' + i + ' done'

    q = Queue(maxsize=0)
    num_threads = 50
     # print "Batch " + str(i) + " Done"

    for i in range(num_threads):
      worker = Thread(target=do_stuff, args=(q,i),)
      worker.setDaemon(True)
      worker.start()

    data = []
    for y in range(150000):
        for i in items:
            digest = hashlib.sha224('Bulk Pins' + repr(time.time()) + repr(random_string(8))).hexdigest()
            # print digest
            counter = counter + 1
            load = (digest[:15], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), i['name'], counter, "123456")
            data.append(load)
            # print load
            if (counter % 250) == 0:
                q.put(data)
                print counter
                data = []
        q.join()


    print 'exited'
    diff = datetime.datetime.now().replace(microsecond=0) - current
    print current, diff.total_seconds() / 60