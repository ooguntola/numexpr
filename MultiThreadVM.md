# Multi-thread Virtual Machine in `numexpr` #

Starting from version 1.4, `numexpr` wears a new multi-threaded implementation of its internal virtual machine.  This virtual machine is in charge of performing the computations of vectors and, for efficiency, it is made in pure C.  The parallelization (using the POSIX pthreads library) of such a virtual machine allows to accelerate all the operations that are bounded by CPU, like those using transcendental functions (trigonometrical, `log`, `exp`, `sqrt`..).

Last but not least, it also contributes to reduce (and, if the computing machine has cores enough, even to completely remove) the overhead of the virtual machine for memory-bound computations.

# Implementation details #

Threading in C provides the best parallel performance in nowadays multi-core machines (much better than message-passing paradigms).  In addition, the new C code avoids the GIL that hampers performance in many Python apps.  FInally, it uses a pool of threads in order to remove the overhead of creating/finishing the thread process for each run (incidentally, the implementation is based on the same parallel engine that powers the [Blosc](http://www.blosc.org) compressor).

This internal parallel virtual machine can also be used in combination with Intel's VML in order to leverage its serial features, like computations using different precisions or fine-tuned implementations of functions.  More specificaly, when `numexpr` is linked against VML, the default is to use `numexpr`'s own parallel engine, but the user may still select the parallel engine in VML instead by playing with the `set_num_threads()` and `set_vml_num_threads()` functions.  However, `numexpr`'s parallel implementation is efficient enough for most of situations (and in fact, somewhat better for large arrays).

# Some benchmarks #

Just to give you an idea on the kind of performance here they are some speed-ups achieved in different scenarios.  The figures below have been collected on a Windows 64 box wearing a 6-core processor (AMD Phenom II X6 @ 3.2 GHz) and 8 GB of RAM (DDR3 @ 1.2 GHz).

## Computing a CPU-bounded expression ##

Results for evaluating an expression with transcendental functions like `(sin(x)**2+cos(x)**2)`:

```
Time numpy: 0.630
Time numexpr with 1 threads: 0.467
Time numexpr with 2 threads: 0.234
Time numexpr with 3 threads: 0.161
Time numexpr with 4 threads: 0.123
Time numexpr with 5 threads: 0.101
Time numexpr with 6 threads: 0.089
```

That is, more than a 5x speed-up with respect to using 1 core and more than 7x with respect to plain NumPy.

## Computing a memory-bounded expression ##

For memory-bounded computations, the speed-up is not as spectacular, but multi-thread still helps to reduce `numexpr`'s virtual machine overhead.  For example, for computing this polynomial `((.25*x +.75)*x - 1.5)*x - 2`, the timings are:

```
Time numpy: 0.411
Time numexpr with 1 threads: 0.112
Time numexpr with 2 threads: 0.070
Time numexpr with 3 threads: 0.060
Time numexpr with 4 threads: 0.053
Time numexpr with 5 threads: 0.047
Time numexpr with 6 threads: 0.046
```

This time, the speed-up is around 2.4x wrt `numexpr` using 1 core, and almost 9x with respect to plain NumPy.  It is worth noting that a pure C program took 48 ms for doing the same computation (which is pretty close to the fundamental limit imposed by the memory bandwidth for this machine).

## General boolean expressions ##

Finally, using a general recollection of different functions that are in  `bench/boolean_timing.py` (these are very important for in-kernel queries in [PyTables](http://www.pytables.org) database), the speed-ups are very nice too.

When using 1 thread:

```
*************** Numexpr vs NumPy speed-ups *******************
Contiguous case:         2.2 (mean), 0.85 (min), 6.09 (max)
Strided case:            2.56 (mean), 0.98 (min), 7.74 (max)
Unaligned case:          3.74 (mean), 1.19 (min), 8.44 (max)
```

and when using 6 threads:

```
*************** Numexpr vs NumPy speed-ups *******************
Contiguous case:         8.42 (mean), 1.3 (min), 25.19 (max)
Strided case:            11.43 (mean), 1.92 (min), 35.23 (max)
Unaligned case:          16.13 (mean), 6.58 (min), 44.06 (max)
```

So, when using 6 threads, this accounts for a mean speed-up of around 4x wrt 1 thread, and up to 16x (mean) faster than NumPy.  The maximum speed case is a huge 44x over NumPy (evaluating the expression `(f3+1)**50 > i2` for unaligned arrays).