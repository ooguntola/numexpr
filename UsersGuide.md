## Description ##

The `numexpr` package supplies routines for the fast evaluation of
array expressions elementwise by using a vector-based virtual
machine. It's comparable to SciPy's [weave](http://www.scipy.org/Weave)
package, but doesn't require a separate compile step of C or C++
code.

Using it is simple:

```
>>> import numpy as np
>>> import numexpr as ne
>>> a = np.arange(10)
>>> b = np.arange(0, 20, 2)
>>> c = ne.evaluate("2*a+3*b")
>>> c
array([ 0,  8, 16, 24, 32, 40, 48, 56, 64, 72])
```


## Building ##

`Numexpr` requires [Python](http://python.org/) 2.5 or greater, and
[NumPy](http://numpy.scipy.org/) 1.6 or greater.  It's built in the
standard Python way:

```
$ python setup.py build
$ python setup.py install
```

You can test `numexpr` with:
```
$ python -c "import numexpr; numexpr.test()"
```


### Enabling Intel's VML support ###

Starting from release 1.2 on, numexpr includes support for Intel's VML
library.  This allows for better performance on Intel architectures,
mainly when evaluating transcendental functions (trigonometrical,
exponential...).  It also enables numexpr using several CPU cores.

If you have Intel's MKL (the library that embeds VML), just copy the
`site.cfg.example` that comes in the distribution to `site.cfg` and
edit the latter giving proper directions on how to find your MKL
libraries in your system.  After doing this, you can proceed with the
usual building instructions listed above.  Pay attention to the
messages during the building process in order to know whether MKL has
been detected or not.  Finally, you can check the speed-ups on your
machine by running the `bench/vml_timing.py` script (you can play with
different parameters to the `set_vml_accuracy_mode()` and
`set_vml_num_threads()` functions in the script so as to see how it would
affect performance).


## Usage Notes ##

`Numexpr`'s principal routine is:

```
evaluate(ex, local_dict=None, global_dict=None, optimization='aggressive', truediv='auto')
```

where `ex` is a string forming an expression, like `"2*a+3*b"`.  The
values for `a` and `b` will by default be taken from the calling
function's frame (through the use of `sys._getframe()`).
Alternatively, they can be specified using the `local_dict` or
`global_dict` arguments, or passed as keyword arguments.

The `optimization` parameter can take the values 'moderate' or 'aggressive'.  'moderate' means that no optimization is made that can affect precision at all.  'aggressive' (the default) means that the expression can be rewritten in a way that precision **could** be affected, but normally very little.  For example, in 'aggressive' mode, the transformation 'x3' -> 'x\*x\*x' is made, but not in 'moderate' mode.

The `truediv` parameter specifies whether the division is a 'floor division' (False) or a 'true division' (True).  The default is the value of `__future__.division` in the interpreter.  See PEP 238 for details.

Expressions are cached, so reuse is fast.  Arrays or scalars are
allowed for the variables, which must be of type 8-bit boolean (bool),
32-bit signed integer (int), 64-bit signed integer (long),
double-precision floating point number (float), 2x64-bit,
double-precision complex number (complex) or raw string of bytes
(str).  If they are not in the previous set of types, they will be
properly upcasted for internal use (the result will be affected as
well).  The arrays must all be the same size.


## Datatypes supported internally ##

Numexpr operates internally only with the following types:

  * 8-bit boolean (bool)
  * 32-bit signed integer (int or int32)
  * 64-bit signed integer (long or int64)
  * 32-bit single-precision floating point number (float or float32)
  * 64-bit, double-precision floating point number (double or float64)
  * 2x64-bit, double-precision complex number (complex or complex128)
  * Raw string of bytes (str)

If the arrays in the expression does not match any of these types,
they will be upcasted to one of the above types (following the usual
type inference rules, see below).  Have this in mind when doing
estimations about the memory consumption during the computation of
your expressions.

Also, the types in Numexpr conditions are somewhat stricter than those
of Python.  For instance, the only valid constants for booleans are
`True` and `False`, and they are never automatically cast to integers.


## Casting rules ##

Casting rules in Numexpr follow closely those of NumPy.  However, for
implementation reasons, there are some known exceptions to this rule,
namely:

  * When an array with type `int8`, `uint8`, `int16` or `uint16` is used inside Numexpr, it is internally upcasted to an `int` (or `int32` in NumPy notation).

  * When an array with type `uint32` is used inside Numexpr, it is internally upcasted to a `long` (or `int64` in NumPy notation).

  * A floating point function (e.g. `sin`) acting on `int8` or `int16` types returns a `float64` type, instead of the `float32` that is returned by NumPy functions.  This is mainly due to the absence of native `int8` or `int16` types in Numexpr.

  * In operations implying a scalar and an array, the normal rules of casting are used in Numexpr, in contrast with NumPy, where array types takes priority.  For example, if 'a' is an array of type `float32` and 'b' is an scalar of type `float64` (or Python `float` type, which is equivalent), then 'a\*b' returns a `float64` in Numexpr, but a `float32` in NumPy (i.e. array operands take priority in determining the result type).  If you need to keep the result a `float32`, be sure you use a `float32` scalar too.


## Supported operators ##

`Numexpr` supports the set of operators listed below:

  * Logical operators: `&, |, ~`
  * Comparison operators: `<, <=, ==, !=, >=, >`
  * Unary arithmetic operators: `-`
  * Binary arithmetic operators: `+, -, *, /, **, %`


## Supported functions ##

The next are the current supported set:

  * **where(bool, number1, number2): number** -- number1 if the bool condition is true, number2 otherwise.
  * **{sin,cos,tan}(float|complex): float|complex** -- trigonometric sine, cosine or tangent.
  * **{arcsin,arccos,arctan}(float|complex): float|complex** -- trigonometric inverse sine, cosine or tangent.
  * **arctan2(float1, float2): float** -- trigonometric inverse tangent of float1/float2.
  * **{sinh,cosh,tanh}(float|complex): float|complex** -- hyperbolic sine, cosine or tangent.
  * **{arcsinh,arccosh,arctanh}(float|complex): float|complex** -- hyperbolic inverse sine, cosine or tangent.
  * **{log,log10,log1p}(float|complex): float|complex** -- natural, base-10 and log(1+x) logarithms.
  * **{exp,expm1}(float|complex): float|complex** -- exponential and exponential minus one.
  * **sqrt(float|complex): float|complex** -- square root.
  * **abs(float|complex): float|complex**  -- absolute value.
  * **{real,imag}(complex): float** -- real or imaginary part of complex.
  * **complex(float, float): complex** -- complex from real and imaginary parts.

### Notes ###

  * `abs()` for complex inputs returns a `complex` output too.  This is a departure from NumPy where a `float` is returned instead.  However, Numexpr is not flexible enough yet so as to allow this to happen.  Meanwhile, if you want to mimic NumPy behaviour, you may want to select the real part via the `real` function (e.g. "real(abs(cplx))") or via the `real` selector (e.g. "abs(cplx).real").


More functions can be added if you need them.


## Supported reduction operations ##

The next are the current supported set:

  * **sum(number, axis=None)**: Sum of array elements over a given axis.  Negative axis are not supported.

  * **prod(number, axis=None)**: Product of array elements over a given axis.  Negative axis are not supported.

**Note:** because of internal limitations, reduction operations must appear the last in the stack.  If not, it will be issued an error like:

```
>>> ne.evaluate('sum(1)*(-1)')

RuntimeError: invalid program: reduction operations must occur last
```

## General routines ##

  * **evaluate(expression, local\_dict=None, global\_dict=None, optimization='aggressive', truediv='auto')**:  Evaluate a simple array expression element-wise.  See examples above.

  * **test()**:  Run all the tests in the test suite.

  * **print\_versions()**:  Print the versions of software that numexpr relies on.

  * **set\_num\_threads(nthreads)**: Sets a number of threads to be used in operations.  Returns the previous setting for the number of threads.  See note below to see how the number of threads is set initially in Numexpr.

> If you are using VML, you may want to use **set\_vml\_num\_threads(nthreads)** to perform the parallel job with VML instead.  However, you should get very similar performance with VML-optimized functions, and VML's parallelizer cannot deal with common expressions like `(x+1)*(x-2)`, while Numexpr's one can.

  * **detect\_number\_of\_cores()**: Detects the number of cores on a system.

**Note on the initial number of threads:** The initial number of threads will be set to the number of cores detected in the system or 8, whichever is **lower**. The `NUMEXPR_MUM_THREADS` environment variable is also honored at initialization time and, if defined, the initial number of threads will be set to this value instead.  Because of internal limitations, the number of threads cannot be larger than 4096 (there is an internal protection for this).


## Intel's VML specific support routines ##

When compiled with Intel's VML (Vector Math Library), you will be able
to use some additional functions for controlling its use. These are:

  * **set\_vml\_accuracy\_mode(mode)**:  Set the accuracy for VML operations.

> The `mode` parameter can take the values:

> - 'low': Equivalent to VML\_LA - low accuracy VML functions are called

> - 'high': Equivalent to VML\_HA - high accuracy VML functions are called

> - 'fast': Equivalent to VML\_EP - enhanced performance VML functions are called

> It returns the previous mode.

> This call is equivalent to the `vmlSetMode()` in the VML library.
> See:

> http://www.intel.com/software/products/mkl/docs/webhelp/vml/vml_DataTypesAccuracyModes.html

> for more info on the accuracy modes.

  * **set\_vml\_num\_threads(nthreads)**: Suggests a maximum number of
> > threads to be used in VML operations.


> This function is equivalent to the call
> `mkl_domain_set_num_threads(nthreads, MKL_VML)` in the MKL library.
> See:

> http://www.intel.com/software/products/mkl/docs/webhelp/support/functn_mkl_domain_set_num_threads.html

> for more info about it.

  * **get\_vml\_version()**:  Get the VML/MKL library version.


## Credits ##

`Numexpr` was initially written by David Cooke, and extended to more types by Tim Hochberg.  Francesc Alted contributed support for boolean types, single precision floating point types, efficient strided and unaligned array operations and multi-threading code. Ivan Vilata contributed support for strings.  Gregor Thalhammer implemented the support for Intel VML (Vector Math Library).  Mark Wiebe added support for the new iterator in NumPy, which allows for better performance in more scenarios (like broadcasting, fortran-ordered or non-native byte orderings).  Gaëtan de Menten contributed important bug fixes and speed enhancements.  Antonio Valentino contributed the port for Python 3.


## License ##

Numexpr is distributed under the [MIT](http://www.opensource.org/licenses/mit-license.php) license.