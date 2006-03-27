/* Posix threads interface */

#include <stdlib.h>
#include <string.h>
#if defined(__APPLE__) || defined(HAVE_PTHREAD_DESTRUCTOR)
#define destructor xxdestructor
#endif
#include <pthread.h>
#if defined(__APPLE__) || defined(HAVE_PTHREAD_DESTRUCTOR)
#undef destructor
#endif
#include <signal.h>

/* The POSIX spec says that implementations supporting the sem_*
   family of functions must indicate this by defining
   _POSIX_SEMAPHORES. */   
#ifdef _POSIX_SEMAPHORES
/* On FreeBSD 4.x, _POSIX_SEMAPHORES is defined empty, so 
   we need to add 0 to make it work there as well. */
#if (_POSIX_SEMAPHORES+0) == -1
#define HAVE_BROKEN_POSIX_SEMAPHORES
#else
#include <semaphore.h>
#include <errno.h>
#endif
#endif

#if !defined(pthread_attr_default)
#  define pthread_attr_default ((pthread_attr_t *)NULL)
#endif
#if !defined(pthread_mutexattr_default)
#  define pthread_mutexattr_default ((pthread_mutexattr_t *)NULL)
#endif
#if !defined(pthread_condattr_default)
#  define pthread_condattr_default ((pthread_condattr_t *)NULL)
#endif


/* Whether or not to use semaphores directly rather than emulating them with
 * mutexes and condition variables:
 */
#if defined(_POSIX_SEMAPHORES) && !defined(HAVE_BROKEN_POSIX_SEMAPHORES)
#  define USE_SEMAPHORES
#else
#  undef USE_SEMAPHORES
#endif


/* On platforms that don't use standard POSIX threads pthread_sigmask()
 * isn't present.  DEC threads uses sigprocmask() instead as do most
 * other UNIX International compliant systems that don't have the full
 * pthread implementation.
 */
#if defined(HAVE_PTHREAD_SIGMASK) && !defined(HAVE_BROKEN_PTHREAD_SIGMASK)
#  define SET_THREAD_SIGMASK pthread_sigmask
#else
#  define SET_THREAD_SIGMASK sigprocmask
#endif


/* A pthread mutex isn't sufficient to model the Python lock type
 * because, according to Draft 5 of the docs (P1003.4a/D5), both of the
 * following are undefined:
 *  -> a thread tries to lock a mutex it already has locked
 *  -> a thread tries to unlock a mutex locked by a different thread
 * pthread mutexes are designed for serializing threads over short pieces
 * of code anyway, so wouldn't be an appropriate implementation of
 * Python's locks regardless.
 *
 * The pthread_lock struct implements a Python lock as a "locked?" bit
 * and a <condition, mutex> pair.  In general, if the bit can be acquired
 * instantly, it is, else the pair is used to block the thread until the
 * bit is cleared.     9 May 1994 tim@ksr.com
 */

typedef struct {
	char             locked; /* 0=unlocked, 1=locked */
	/* a <cond, mutex> pair to handle an acquire of a locked lock */
	pthread_cond_t   lock_released;
	pthread_mutex_t  mut;
} pthread_lock;

#define CHECK_STATUS(name)  if (status != 0) { perror(name); error = 1; }

/*
 * Initialization.
 */

#ifdef _HAVE_BSDI
static
void _noop(void)
{
}

static void
__init_thread(void)
{
	/* DO AN INIT BY STARTING THE THREAD */
	static int dummy = 0;
	pthread_t thread1;
	pthread_create(&thread1, NULL, (void *) _noop, &dummy);
	pthread_join(thread1, NULL);
}

#else /* !_HAVE_BSDI */

static void
__init_thread(void)
{
#if defined(_AIX) && defined(__GNUC__)
	pthread_init();
#endif
}

#endif /* !_HAVE_BSDI */

/*
 * Thread support.
 */


PyObject *
//long
//_start_new_thread(void (*func)(void *), void *arg, int stacksize)
//_start_new_thread(PyObject *func, PyObject *arg, int stacksize)
_start_new_thread(PyObject *func, int stacksize)
{
	pthread_t th;
	int status;
	pthread_attr_t attrs;
	long th_l;

	//start pyobject conversions
	void *my_func;
	void *args;
	PyArg_Parse(func, "0", &my_func);
	//PyArg_ParseTuple();
	//end pyobject conversions

	if (!initialized)
		_init_thread();

	pthread_attr_init(&attrs);

	if(stacksize>0)	pthread_attr_setstacksize(&attrs, stacksize);
	
#if defined(PTHREAD_SYSTEM_SCHED_SUPPORTED) && !defined(__FreeBSD__)
        pthread_attr_setscope(&attrs, PTHREAD_SCOPE_SYSTEM);
#endif

	status = pthread_create(&th, 
				 &attrs,
				 (void* (*)(void *))my_func,
				 //(void *)arg
				 NULL
				 );

	printf("STATUS: %d\n");
	pthread_attr_destroy(&attrs);

	if (status != 0)
            return Py_BuildValue("l",-1);

        pthread_detach(th);

	printf("_start_new_thread QUASI FINALIZED\n");

#if SIZEOF_PTHREAD_T <= SIZEOF_LONG
	printf("_start_new_thread PRIMERO\n");
	th_l = (long) th;
	return Py_BuildValue("l", th_l);
	//return (long) th;
#else
	printf("_start_new_thread SEGUNDO\n");
	return (long) *(long *) &th;
#endif
}

/* XXX This implementation is considered (to quote Tim Peters) "inherently
   hosed" because:
     - It does not guarantee the promise that a non-zero integer is returned.
     - The cast to long is inherently unsafe.
     - It is not clear that the 'volatile' (for AIX?) and ugly casting in the
       latter return statement (for Alpha OSF/1) are any longer necessary.
*/
long 
_get_thread_ident(void)
{
	volatile pthread_t threadid;
	if (!initialized)
		_init_thread();
	/* Jump through some hoops for Alpha OSF/1 */
	threadid = pthread_self();
#if SIZEOF_PTHREAD_T <= SIZEOF_LONG
	return (long) threadid;
#else
	return (long) *(long *) &threadid;
#endif
}

static void 
do_exit_thread(int no_cleanup)
{
	if (!initialized) {
		if (no_cleanup)
			_exit(0);
		else
			exit(0);
	}
}

void 
_exit_thread(void)
{
	do_exit_thread(0);
}

void 
__exit_thread(void)
{
	do_exit_thread(1);
}

#ifndef NO_EXIT_PROG
static void 
do_exit_prog(int status, int no_cleanup)
{
	if (!initialized)
		if (no_cleanup)
			_exit(status);
		else
			exit(status);
}

void 
_exit_prog(int status)
{
	do_exit_prog(status, 0);
}

void 
__exit_prog(int status)
{
	do_exit_prog(status, 1);
}
#endif /* NO_EXIT_PROG */

#ifdef USE_SEMAPHORES

/*
 * Lock support.
 */

PyThread_type_lock 
_allocate_lock(void)
{
	sem_t *lock;
	int status, error = 0;

	if (!initialized)
		_init_thread();

	lock = (sem_t *)malloc(sizeof(sem_t));

	if (lock) {
		status = sem_init(lock,0,1);
		CHECK_STATUS("sem_init");

		if (error) {
			free((void *)lock);
			lock = NULL;
		}
	}

	return (PyThread_type_lock)lock;
}

void 
_free_lock(PyThread_type_lock lock)
{
	sem_t *thelock = (sem_t *)lock;
	int status, error = 0;


	if (!thelock)
		return;

	status = sem_destroy(thelock);
	CHECK_STATUS("sem_destroy");

	free((void *)thelock);
}

/*
 * As of February 2002, Cygwin thread implementations mistakenly report error
 * codes in the return value of the sem_ calls (like the pthread_ functions).
 * Correct implementations return -1 and put the code in errno. This supports
 * either.
 */
static int
fix_status(int status)
{
	return (status == -1) ? errno : status;
}

int 
_acquire_lock(PyThread_type_lock lock, int waitflag)
{
	int success;
	sem_t *thelock = (sem_t *)lock;
	int status, error = 0;


	do {
		if (waitflag)
			status = fix_status(sem_wait(thelock));
		else
			status = fix_status(sem_trywait(thelock));
	} while (status == EINTR); /* Retry if interrupted by a signal */

	if (waitflag) {
		CHECK_STATUS("sem_wait");
	} else if (status != EAGAIN) {
		CHECK_STATUS("sem_trywait");
	}
	
	success = (status == 0) ? 1 : 0;

	return success;
}

void 
_release_lock(PyThread_type_lock lock)
{
	sem_t *thelock = (sem_t *)lock;
	int status, error = 0;


	status = sem_post(thelock);
	CHECK_STATUS("sem_post");
}

#else /* USE_SEMAPHORES */

/*
 * Lock support.
 */
PyThread_type_lock 
_allocate_lock(void)
{
	pthread_lock *lock;
	int status, error = 0;

	if (!initialized)
		_init_thread();

	lock = (pthread_lock *) malloc(sizeof(pthread_lock));
	memset((void *)lock, '\0', sizeof(pthread_lock));
	if (lock) {
		lock->locked = 0;

		status = pthread_mutex_init(&lock->mut,
					    pthread_mutexattr_default);
		CHECK_STATUS("pthread_mutex_init");

		status = pthread_cond_init(&lock->lock_released,
					   pthread_condattr_default);
		CHECK_STATUS("pthread_cond_init");

		if (error) {
			free((void *)lock);
			lock = 0;
		}
	}

	return (PyThread_type_lock) lock;
}

void 
_free_lock(PyThread_type_lock lock)
{
	pthread_lock *thelock = (pthread_lock *)lock;
	int status, error = 0;


	status = pthread_mutex_destroy( &thelock->mut );
	CHECK_STATUS("pthread_mutex_destroy");

	status = pthread_cond_destroy( &thelock->lock_released );
	CHECK_STATUS("pthread_cond_destroy");

	free((void *)thelock);
}

int 
_acquire_lock(PyThread_type_lock lock, int waitflag)
{
	int success;
	pthread_lock *thelock = (pthread_lock *)lock;
	int status, error = 0;


	status = pthread_mutex_lock( &thelock->mut );
	CHECK_STATUS("pthread_mutex_lock[1]");
	success = thelock->locked == 0;

	if ( !success && waitflag ) {
		/* continue trying until we get the lock */

		/* mut must be locked by me -- part of the condition
		 * protocol */
		while ( thelock->locked ) {
			status = pthread_cond_wait(&thelock->lock_released,
						   &thelock->mut);
			CHECK_STATUS("pthread_cond_wait");
		}
		success = 1;
	}
	if (success) thelock->locked = 1;
	status = pthread_mutex_unlock( &thelock->mut );
	CHECK_STATUS("pthread_mutex_unlock[1]");

	if (error) success = 0;
	return success;
}

void 
_release_lock(PyThread_type_lock lock)
{
	pthread_lock *thelock = (pthread_lock *)lock;
	int status, error = 0;


	status = pthread_mutex_lock( &thelock->mut );
	CHECK_STATUS("pthread_mutex_lock[3]");

	thelock->locked = 0;

	status = pthread_mutex_unlock( &thelock->mut );
	CHECK_STATUS("pthread_mutex_unlock[3]");

	/* wake up someone (anyone, if any) waiting on the lock */
	status = pthread_cond_signal( &thelock->lock_released );
	CHECK_STATUS("pthread_cond_signal");
}

#endif /* USE_SEMAPHORES */
