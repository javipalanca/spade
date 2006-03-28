#include "Python.h"

long creahilo(void *func, int stacksize) {
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

PyObject *mymod_snt(PyObject *self, PyObject *args) {
	long sz;
	PyObject *obj;
	PyObject *tupla;

	if (! PyArg_ParseTuple(args, "O", &obj)) {
		Py_INCREF(Py_None);
		return Py_None;
	};
	
	sz = creahilo((void *)obj, 1024);
	printf("sz = %d\n", sz);
	Py_INCREF(Py_None);
	return Py_None;
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

