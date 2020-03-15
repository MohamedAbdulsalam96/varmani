from Queue import Queue
from threading import Thread

def do_stuff(q,i):
    while True:
        p= q.get()
        print str(i) + ' got ' + str(p)
        q.task_done()
    print 'Thread ' + i + ' done'


q = Queue(maxsize=0)
num_threads = 3

for i in range(num_threads):
  worker = Thread(target=do_stuff, args=(q,i))
  worker.setDaemon(True)
  worker.start()

for y in range (10):
    q.put(y)
q.join()
print "Batch " + str(y) + " Done"

for y in range (10):
    q.put(y)
q.join()
print "Batch " + str(y) + " Done"
