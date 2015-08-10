# IMPORTANT NOTICE #

**Please be aware that the numexpr project has been migrated to [GitHub](https://github.com/pydata/numexpr).  This site has been declared unmaintained as of 2014-01-21.  Sorry for the inconveniences.**

-- Francesc Alted

## What It Is ##

The `numexpr` package evaluates multiple-operator array expressions
many times faster than [NumPy](http://numpy.scipy.org/) can.  It
accepts the expression as a string, analyzes it, rewrites it more
efficiently, and compiles it on the fly into code for its internal virtual machine (VM).
Due to its integrated just-in-time (JIT) compiler, it does not
require a compiler at runtime.

Also,`numexpr` implements support for multi-threading
computations straight into its internal virtual machine, written in C.
This allows to bypass the GIL in Python, and allows near-optimal parallel
performance in your vector expressions, most specially on CPU-bounded
operations (memory-bounded ones were already the strong point of `numexpr`).
See [MultiThreadVM](http://code.google.com/p/numexpr/wiki/MultiThreadVM)
for more info on this.

It is also interesting to note that, as of version 2.0, numexpr uses the new iterator introduced in NumPy 1.6 so as to achieve better performance in a broader range of data arrangements.  For details, see [NewVM](http://code.google.com/p/numexpr/wiki/NewVM).

Finally,  `numexpr` has support for the Intel VML (Vector Math Library)
-- integrated in [Intel MKL (Math Kernel Library)](http://software.intel.com/en-us/intel-mkl/) --, allowing nice speed-ups when computing transcendental functions (like
trigonometrical, exponentials...) on top of Intel-compatible platforms.
MKL also allows to use multiple cores in your computations (although the native multi-threading implementation is preferred because its higher efficiency).  See [NumexprVML](http://code.google.com/p/numexpr/wiki/NumexprVML) for some benchmarks.

## Examples of Use ##

Using it is simple:

```
>>> import numpy as np
>>> import numexpr as ne

>>> a = np.arange(1e6)
>>> b = np.arange(1e6)

>>> ne.evaluate("a + 1")   # a simple expression
array([  1.00000000e+00,   2.00000000e+00,   3.00000000e+00, ...,
         9.99998000e+05,   9.99999000e+05,   1.00000000e+06])

>>> ne.evaluate('a*b-4.1*a > 2.5*b')   # a more complex one
array([False, False, False, ...,  True,  True,  True], dtype=bool)
```

and fast... (specially if using its multi-threading capabilities on multicore machines :-)

```
>>> timeit a**2 + b**2 + 2*a*b
10 loops, best of 3: 21.5 ms per loop

# numexpr w/ 16 threads (default for 8-core, with hyperthreading)
>>> timeit ne.evaluate("a**2 + b**2 + 2*a*b")
100 loops, best of 3: 2.14 ms per loop  # 10x faster than NumPy

>>> ne.set_num_threads(8)  # using just 8 threads
>>> timeit ne.evaluate("a**2 + b**2 + 2*a*b")
100 loops, best of 3: 3.15 ms per loop  # 6.8x faster than NumPy

>>> ne.set_num_threads(1)  # using just 1 thread
>>> timeit ne.evaluate("a**2 + b**2 + 2*a*b")
100 loops, best of 3: 7.58 ms per loop  # 2.8x faster than NumPy

```

The above example shows how `numexpr` can frequently reach the memory bandwidth limit of the machine (the working set for this case is `8 MB * 3 = 24 MB`, processed in 2.14 ms, which accounts for a total throughput of ~11 GB/s, the practical memory bandwidth of this machine).

## User's Guide ##

For instructions on how to install the package, the complete list of functions you
can use and the types supported, please check the UsersGuide.

## Why It Works ##

There are two extremes to array expression evaluation.  Each binary
operation can run separately over the array elements and return a
temporary array.  This is what NumPy does: `2*a + 3*b` uses three
temporary arrays as large as `a` or `b`.  This strategy wastes memory
(a problem if the arrays are large).  It is also not a good use of CPU
cache memory because the results of `2*a` and `3*b` will not be in
cache for the final addition if the arrays are large.

The other extreme is to loop over each element:

```
for i in xrange(len(a)):
    c[i] = 2*a[i] + 3*b[i]
```

This conserves memory and is good for the cache, but on each iteration
Python must check the type of each operand and select the correct
routine for each operation.  All but the first such checks are wasted,
as the input arrays are not changing.

`numexpr` uses an in-between approach.  Arrays are handled in chunks (the first pass uses 1024 elements, or 4096, if using VML).  As Python code, it looks something like this:

```
for i in xrange(0, len(a), 256):
    r0 = a[i:i+256]
    r1 = b[i:i+256]
    multiply(r0, 2, r2)
    multiply(r1, 3, r3)
    add(r2, r3, r2)
    c[i:i+256] = r2
```

The 3-argument form of `add()` stores the result in the third
argument, instead of allocating a new array.  This achieves a good
balance between cache and branch prediction.  The virtual machine is
written entirely in C, which makes it faster than the Python above.

For more info about `numexpr`, read the
[Numexpr's Overview](http://code.google.com/p/numexpr/wiki/Overview)
written by the original author (David M. Cooke).  This [lecture](https://python.g-node.org/python-autumnschool-2010/materials/starving_cpus) also offers a nice overview about `numexpr` and how it works.  Finally, reading this [article](http://www.pytables.org/docs/CISE-12-2-ScientificPro.pdf) may help you understand why memory access is such a big problem nowadays.