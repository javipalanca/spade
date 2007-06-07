# This file was created automatically by SWIG 1.3.27.
# Don't modify this file, modify the SWIG interface instead.

import _stack_thread

# This file is compatible with both classic and new-style classes.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name) or (name == "thisown"):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types



_init_thread = _stack_thread._init_thread

_start_new_thread = _stack_thread._start_new_thread

_exit_thread = _stack_thread._exit_thread

__exit_thread = _stack_thread.__exit_thread

_get_thread_ident = _stack_thread._get_thread_ident

_allocate_lock = _stack_thread._allocate_lock

_free_lock = _stack_thread._free_lock

_acquire_lock = _stack_thread._acquire_lock
WAIT_LOCK = _stack_thread.WAIT_LOCK
NOWAIT_LOCK = _stack_thread.NOWAIT_LOCK

_release_lock = _stack_thread._release_lock


