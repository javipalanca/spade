all:  pythread.h stack_thread.i stack_thread.c thread_pthread.h 
	swig -python stack_thread.i
	gcc -c stack_thread.c stack_thread_wrap.c -I/usr/include/python2.4
	ld -shared stack_thread.o stack_thread_wrap.o -o _stack_thread.so

clean:
	rm *.pyc *.o *.so *_wrap.c 
