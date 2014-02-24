import random, urllib2, urllib, sys, os, Queue, threading, socket, re, time, uuid

queue = Queue.Queue()
out_queue = Queue.Queue()
n = 0
#fbinput
fbinput = raw_input('input filename (fblink.txt): ')
if not fbinput: fbinput = 'fblink.txt'  
try:
    fbfile = open(fbinput)
except Exception:
    print "File %s does not exist." % fbinput
    fbinput = raw_input('input filename (fblink.txt): ')
#fboutput   
fboutput = raw_input('output folder (fbpages): ')
if not fboutput: fboutput = 'fbpages'
if not os.path.exists(fboutput): os.makedirs(fboutput)
#proxyfile
proxyfile = raw_input('proxyfile or no(fbproxy.txt): ')
if not proxyfile: proxyfile = 'fbproxy.txt'
# threadcount 
threadcount = raw_input('input thread count (default 5): ')
if threadcount: threadcount = int(threadcount)
if not threadcount: threadcount = 5
        
        
class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    global fboutput
    global proxyfile
    global fbinput
    
    
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            fblink = self.queue.get()
            #fb = fblink.split(',')
            uid = str(uuid.uuid4())
            if proxyfile != 'no':
                rawproxy = random.choice(list(open(proxyfile)))
                rawproxy = rawproxy.strip()
                proxy = urllib2.ProxyHandler({'http': rawproxy})
                auth = urllib2.HTTPBasicAuthHandler()
                opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
            else:
                opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib2.install_opener(opener)
            try:
                conn = urllib2.urlopen(fblink)
                return_str = conn.read()
                if 'facebook' in fblink:
                    return_str = re.sub('<code class="hidden_elem" id=".*?"><!-- ','',return_str)
                    return_str = re.sub(' --></code>','',return_str)
                file = open(fboutput + '/' + uid + '.html', 'w+')
                file.write(uid + ',' + fblink)
                file.write(return_str)
                file.close()
                global n
                n += 1
                if n % 20 == 0: print str(n) + ' completed'
                print 'success: ' + str(n) + ', ' + fblink
            except Exception:
                print 'fail: ' + fblink
                f = open(fbinput + '_failed.txt', 'a')
                f.write(fblink + '\n')
                f.close()
                
            self.queue.task_done()

            
start = time.time()
           
def main(): 
    
    #spawn a pool of threads, and pass them queue instance    
    for i in range(threadcount):
        t = ThreadUrl(queue, out_queue)
        t.setDaemon(True)
        t.start()
        
    #populate queue with data
    for fblink in fbfile:
        fblink = fblink.strip()
        queue.put(fblink)
            
    #wait on the queue until everything has been processed
    queue.join()
    out_queue.join()
main()

lines = open(fbinput + '_failed.txt', 'r').readlines()
#lines[0] = "This is the new first line \n"
file = open(fbinput + '_failed.txt', 'w')
for line in lines:
    file.write(line)
file.close()

print "finished: %s" % (time.time() - start)
raw_input()

