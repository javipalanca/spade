%module stack_thread
 %{
 /* Includes the header in the wrapper code */
 #include "pythread.h"
 %}
 
 /* Parse the header file to generate wrappers */
 %include "pythread.h"

