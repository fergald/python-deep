http://code.google.com/p/python-deep/

This module allows easy and flexible deep comparisons of
datastructures. It's not well documented yet but it's a port to python
of Test::Deep which is well documented
(http://search.cpan.org/~fdaly/Test-Deep/). It is most useful for unit
testing (it comes with deep/test.py to use with unittest.py) but it is
a general comparison framework so can be used for argument
verification for example.

It allows easy comparison of objects - it just checks that
they're in the same class and have the same __dict__.

It allows set-wise comparison of lists or tuples (actually, that's on
in the Perl version at the moment).

Most importantly it allows aribitrary nesting of the various
comparisons and embedding of them inside other datastructures and
objects. This makes it easy to perform comparisons that would
otherwise have been tedious.

Run examples.py and have a look around it for more info.
