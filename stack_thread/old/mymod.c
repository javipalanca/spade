#include "Python.h"

long creahilo(void *func, void *args, int stacksize) {
	pthread_t th;
        int status;
        pthread_attr_t attrs;
        long th_l;

        //start pyobject conversions
        //void *my_func;
        //void *args;
        //PyArg_Parse(func, "0", &my_func);
        //PyArg_ParseTuple();
        //end pyobject conversions

        //if (!initialized)
        //        _init_thread();

        pthread_attr_init(&attrs);
        if(stacksize>0) pthread_attr_setstacksize(&attrs, stacksize);
	status = pthread_create(&th,
                                 &attrs,
                                 (void* (*)(void *))func,
                                 //(void *)arg
                                 NULL
                                 );

        printf("STATUS: %d\n");
        pthread_attr_destroy(&attrs);

        if (status != 0)
            return -1;

        pthread_detach(th);
	return (long)th;
};

int cosa(int x) {
	++x;
	return x;
};


struct bootstate {
	PyInterpreterState *interp;
	PyObject *func;
	PyObject *args;
	int ssize;
};

static void
t_bootstrap(void *boot_raw)
{
	struct bootstate *boot = (struct bootstate *) boot_raw;
	PyThreadState *tstate;
	PyObject *res;

	tstate = PyThreadState_New(boot->interp);

	PyEval_AcquireThread(tstate);
	res = PyEval_CallObjectWithKeywords(
			boot->func, boot->args, NULL);
	if (res == NULL) {
		if (PyErr_ExceptionMatches(PyExc_SystemExit))
			PyErr_Clear();
		else {
			PyObject *file;
			PySys_WriteStderr(
					"Unhandled exception in thread started by ");
			file = PySys_GetObject("stderr");
			if (file)
				PyFile_WriteObject(boot->func, file, 0);
			else
				PyObject_Print(boot->func, stderr, 0);
			PySys_WriteStderr("\n");
			PyErr_PrintEx(0);
		}
	}
	else
		Py_DECREF(res);
	Py_DECREF(boot->func);
	Py_DECREF(boot->args);
	//Py_DECREF(boot->ssize);
	PyMem_DEL(boot_raw);
	PyThreadState_Clear(tstate);
	PyThreadState_DeleteCurrent();
	PyThread_exit_thread();
}



PyObject *mymod_snt(PyObject *self, PyObject *fargs) {

	PyObject *func, *args = NULL;
	int ssize = 1024;
	struct bootstate *boot;
	long ident;

	if (!PyArg_ParseTuple(fargs, "OO|i:start_new_thread", &func, &args, &ssize))
		return NULL;
	if (!PyCallable_Check(func)) {
		PyErr_SetString(PyExc_TypeError,
				"first arg must be callable");
		return NULL;
	}
	if (!PyTuple_Check(args)) {
		PyErr_SetString(PyExc_TypeError,
				"2nd arg must be a tuple");
		return NULL;
	}
	

	boot = PyMem_NEW(struct bootstate, 1);
	if (boot == NULL)
		return PyErr_NoMemory();
	boot->interp = PyThreadState_GET()->interp;
	boot->func = func;
	boot->args = args;
	boot->ssize = ssize;
	Py_INCREF(func);
	Py_INCREF(args);
	//Py_XINCREF(ssize);
	PyEval_InitThreads(); /* Start the interpreter's thread-awareness */
	ident = creahilo(t_bootstrap, (void *) boot, boot->ssize);
	//ident = PyThread_start_new_thread(t_bootstrap, (void*) boot);
	if (ident == -1) {
		//PyErr_SetString(ThreadError, "can't start new thread\n");
		printf("can't start new thread\n");
		Py_DECREF(func);
		Py_DECREF(args);
		//Py_XDECREF(ssize);
		PyMem_DEL(boot);
		return NULL;
	}
	return PyInt_FromLong(ident);


	
	
};

PyObject *mymod_nada(PyObject *self) {
	puts("NADA");
	Py_INCREF(Py_None);
	return Py_None;
};

PyObject * mymod_test(PyObject *self, PyObject *args) {
	    int x;
	    PyObject *obj;

	    if (! PyArg_ParseTuple(args, "iO", &x, &obj)) {
		    return NULL;
	    };
	    x = cosa(x);
	    printf("X = %d\n", x);
	    
	    return obj;
	    
	    /*puts("Hello!");*/
	    Py_INCREF(Py_None);
	    return Py_None;
}

static PyMethodDef mymod_methods[] = {
	    {"snt", (PyCFunction)mymod_snt, METH_VARARGS, "Prints test string.\n"},
	    {"test", (PyCFunction)mymod_test, METH_VARARGS, "Prints test string.\n"},
	    {"nada", (PyCFunction)mymod_nada, METH_NOARGS, "Prints test string.\n"},
	    {NULL, NULL, 0, NULL}
};

DL_EXPORT(void) initmymod(void)
{
	    Py_InitModule3("mymod", mymod_methods, "Provides a test function.\n");   
}

