This module allows easy and flexible deep comparisons of
datastructure. It's not well documented yet but it's a port to python
of Test::Deep which is well documented
(http://search.cpan.org/~fdaly/Test-Deep/). It is most useful for
unit testing.

It allows easy comparison of objects - it just checks that
they're in the same class and have the same __dict__.

It allows set-wise comparison of lists or tuples.

Most importantly it allows aribitrary nesting of the various
comparisons and embedding of them inside other datastructures and
object. This makes it easy to perform comparisons that would otherwise
have been tedious.
