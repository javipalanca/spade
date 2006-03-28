all:  pythread.h stack_thread.i stack_thread.c thread_pthread.h 
	@#swig -python stack_thread.i
	@#gcc -c stack_thread.c stack_thread_wrap.c -I/usr/include/python2.4
	@#gcc -shared -I /usr/include/python2.4/ stack_thread.c -o stack_thread.so
	@#gcc -shared -I /usr/include/python2.4/ mymod.c -o mymod.so
	gcc -shared -I /usr/include/python2.4/ threadmodule.c -o stack_thread.so
	@#ld -shared stack_thread.o stack_thread_wrap.o -o _stack_thread.so

clean:
	rm -f *.pyc *.o *.so *_wrap.c 
