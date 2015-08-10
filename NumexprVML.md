# Introduction #

Numexpr has support for Intel's VML in order to accelerate the evaluation of transcendental functions on Intel CPUs.  Here it is a small example on the kind of improvement you may get by using it.

# Some benchmarks #

Numexpr & VML can both use several threads for doing computations.  Let's see how performance improves by using 1 or 2 threads on a 2-core Intel CPU (Core2 E8400 @ 3.00GHz).

## Using 1 thread ##

Here we have some benchmarks on the improvement of speed that Intel's VML can achieve.  First, look at times by some easy expression containing sine and cosine operations **without** using VML:

```
In [17]: ne.use_vml
Out[17]: False

In [18]: x = np.linspace(-1, 1, 1e6)

In [19]: timeit np.sin(x)**2+np.cos(x)**2
10 loops, best of 3: 43.1 ms per loop

In [20]: ne.set_num_threads(1)
Out[20]: 2

In [21]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
10 loops, best of 3: 29.5 ms per loop
```


and now using VML:

```
In [37]: ne.use_vml
Out[37]: True

In [38]: x = np.linspace(-1, 1, 1e6)

In [39]: timeit np.sin(x)**2+np.cos(x)**2
10 loops, best of 3: 42.8 ms per loop

In [40]: ne.set_num_threads(1)
Out[40]: 2

In [41]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 19.8 ms per loop
```

Hey, VML can accelerate computations by a 50% using a single CPU.  That's great!

## Using 2 threads ##

First, look at the time of the non-VML numexpr when using 2 threads:

```
In [22]: ne.set_num_threads(2)
Out[22]: 1

In [23]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 15.3 ms per loop
```

OK.  We've got an almost perfect 2x improvement in speed with regard to the 1 thread case.  Let's see about the VML-powered numexpr version:

```
In [43]: ne.set_num_threads(2)
Out[43]: 1

In [44]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 12.2 ms per loop
```

Ok, that's about 1.6x improvement over the 1 thread VML computation, and still a 25% of improvement over the non-VML version.  Good, native numexpr multithreading code really looks very efficient!

## Numexpr native threading code vs VML's one ##

You may already know that both numexpr and Intel's VML do have support for multithreaded computations, but you might be curious about which one is more efficient, so here it goes a hint.  First, using the VML multithreaded implementation:

```
In [49]: ne.set_vml_num_threads(2)

In [50]: ne.set_num_threads(1)
Out[50]: 1

In [51]: ne.set_vml_num_threads(2)

In [52]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 16.8 ms per loop
```

and now, using the native numexpr threading code:

```
In [53]: ne.set_num_threads(2)
Out[53]: 1

In [54]: ne.set_vml_num_threads(1)

In [55]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 12 ms per loop
```

This means that numexpr's native multithreaded code is about 40% faster than VML's for this case.  So, in general, you should use the former with numexpr (and this is the default actually).

## Mixing numexpr's and VML multithreading capabilities ##

Finally, you might be tempted to use both multithreading codes at the same time, but you will be deceived about the improvement in performance:

```
In [57]: ne.set_vml_num_threads(2)

In [58]: timeit ne.evaluate('sin(x)**2+cos(x)**2')
100 loops, best of 3: 17.7 ms per loop
```

Your code actually performs much worse.  That's normal too because you are trying to run 4 threads on a 2-core CPU.  For CPUs with many cores, you may want to try with different threading configurations, but as a rule of thumb, numexpr's one will generally win.