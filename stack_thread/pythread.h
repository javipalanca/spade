
#ifndef Py_PYTHREAD_H
#define Py_PYTHREAD_H

#define NO_EXIT_PROG		/* don't define PyThread_exit_prog() */
				/* (the result is no use of signals on SGI) */

typedef void *PyThread_type_lock;
typedef void *PyThread_type_sema;

#ifdef __cplusplus
extern "C" {
#endif

void _init_thread(void);
PyObject *_start_new_thread(PyObject *, int);
//long _start_new_thread(PyObject *, int);
//long _start_new_thread(PyObject *, PyObject *, int);
//long _start_new_thread(void(*)(void*), void*, int);
void _exit_thread(void);
void __exit_thread(void);
long _get_thread_ident(void);

PyThread_type_lock _allocate_lock(void);
void _free_lock(PyThread_type_lock);
int _acquire_lock(PyThread_type_lock, int);
#define WAIT_LOCK	1
#define NOWAIT_LOCK	0
void _release_lock(PyThread_type_lock);

#ifndef NO_EXIT_PROG
void _exit_prog(int);
void __exit_prog(int);
#endif

#ifdef __cplusplus
}
#endif

#endif /* !Py_PYTHREAD_H */
