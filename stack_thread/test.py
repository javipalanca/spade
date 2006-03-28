
import stack_thread
#import thread
import time
#import mymod

def run():
	while 1:
		print "run"
		time.sleep(1)

#print thread.start_new_thread(run,())
#print stack_thread._start_new_thread(run,(),1024)
#print mymod.snt(run,(), 10204)
print stack_thread.start_new_thread(run,(),1)
print "HOLA DESPUES"

while 1:
	time.sleep(1.0)
