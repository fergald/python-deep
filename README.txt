Flexible comparison of nested python datastrucures and objects.

Composable "regular expressions" for data structures.

This module allows easy and flexible deep comparisons of
datastructures. It's not well documented yet but it's a port to python
of Test::Deep which is well documented
(http://search.cpan.org/~fdaly/Test-Deep/).

It can provide useful output, pin-pointing where 2 items begin to
differ, rather than just returning true or false. This makes it very
useful for unit-testing and deep.test provides classes for use with
unittest.py .

It allows easy comparison of objects - it just checks that
they're in the same class and have the same __dict__.

It allows set-wise comparison of lists or tuples (actually, that's on
in the Perl version at the moment).

Most importantly it allows aribitrary nesting of the various
comparisons and embedding of them inside other datastructures and
objects. This makes it easy to perform comparisons that would
otherwise have been tedious.

It turns what would have involved lots of looping and iffing and
comparing into just putting together a structure that looks like what
you're trying to match.

Examples:

###
# Test that we have a list of objects from the correct classes (yes you
# can do this easily without deep.py).

three_types = [deep.InstanceOf(int),
       deep.InstanceOf(list),
       deep.InstanceOf(dict)]
diff = deep.diff([1, 2, 3], three_types)
if diff:
  diff.print_full()

# Outputs
x[1]:
Expected: instance of <type 'list'>
Actual  : instance of <type 'int'>

###
# Test that we have a list of strings that all match a pattern.

list_of_bings = deep.Elements(deep.Re("^bing "))
diff = deep.diff(["bing bong", "bing crosby", "bin laden"], list_of_bings)
if diff:
  diff.print_full()

# Outputs
x[2]:
Expected: something matching '^bing '
Actual  : 'bin laden'

###

# Test that we have an object who's "wibble" attribute is a dict and
# that this dict has 3 keys "time", "bings" and "things" and
# "time". We want to make sure that "time" is a float and we want to
# reuse the comparisons from the earlier examples for the other 2
# keys.

complex = deep.Attr("wibble", {"time": deep.InstanceOf(float),
                               "bings": list_of_bings,
                               "things": three_types})
class O(object):
  wibble = {"time": 1234.12,
            "bings": ["bing go"],
            "things": [1, [], {}, "hello"]}

diff = deep.diff(O(), complex)
if diff:
  diff.print_full()

# Outputs
len(x.wibble['things']):
  Expected: 3
  Actual  : 4  
