
import stack_thread
import thread
import time

def run():
	while 1:
		print "run"
		time.sleep(1)

#print thread.start_new_thread(run,())
print stack_thread._start_new_thread(run,(),1024)

while 1:
	time.sleep(1)
