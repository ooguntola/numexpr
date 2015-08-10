# Computed goto branch #

I (david.m.cooke) did some work on replacing the instruction dispatch from a large
case statement to using gcc's [labels-as-values extension](http://gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html). (This is the same technique used in Python 3.1, and the
ocaml bytecode runtime).

The code is in the [computed\_goto](http://code.google.com/p/numexpr/source/browse/#svn/branches/computed_goto) branch. The computed goto's are used if the `USE_COMPUTED_GOTO` preprocessor symbol is defined; I do it like this
```
$ EXTRA_CFLAGS=-DUSE_COMPUTED_GOTO python setup.py build
```

Currently, there does not appear to be much advantage to using this method instead of a case statement: the speed up is negligible. However, the method to produce the interpreter (done by the `generate/genvm.py` program) allows for more flexibility in playing with different techniques.