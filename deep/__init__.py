# Copyright 2008 Fergal Daly <fergal@esatclear.ie>

# This file is part of deep.py.
#
# deep.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2.1 of the License.
#
# deep.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with deep.py; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Flexible comparison of nested python datastrucures and objects.

Composable "regular expressions" for data structures.

This module allows easy and flexible deep comparisons of
datastructure. It's not well documented yet but it's a port to python
of Test::Deep which is well documented
(http://search.cpan.org/~fdaly/Test-Deep/).

It can provide useful output, pin-pointing where 2 items begin to
differ, rather than just returning true or false. This makes it very
useful for unit-testing and deep.test provides classes for use with
unittest.py .

It allows easy comparison of objects - it just checks that
they're in the same class and have the same __dict__.

It allows set-wise comparison of lists or tuples.

Most importantly it allows aribitrary nesting of the various
comparisons and embedding of them inside other datastructures and
object. This makes it easy to perform comparisons that would otherwise
have been tedious.

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

list_of_bings = deep.ArrayValues(deep.Re("^bing "))
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
"""

__author__ = "Fergal Daly <fergal@esatclear.ie>"

import re
import sys
import traceback

__all__ = ['diff',
           'Equal',
           'Is',
           'Type',
           'InstanceOf',
           'IndexedElem',
           'List',
           'Tuple',
           'EqSet',
           'HasKeys',
           'Dict',
           'HasAttr',
           'Attr',
           'Attrs',
           'Call',
           'Object',
           'And',
           'Ignore',
           'Re',
           'Slice',
           'ArrayValues',
           'DictValues',
           ]

DEBUG = 0

class Unspec: pass

def diff(i1, i2, debug=Unspec):
  if debug is Unspec:
    debug = DEBUG
  if debug:
    comp = DebugComparison()
  else:
    comp = Comparison()
  equal = comp.descend(i1, i2)

  if equal:
    return None
  else:
    return comp

class Comparator(object):
  """Base class for all Comparator objects."""
  def render_value(self, value):
    return `value`

  def expr(self, expr):
    return expr

class DeepException(Exception):
  """Exception class, shouldn't ever be used but keeps a stack trace
  to make debugging easier."""
  def __init__(self, comp, einfo=None):
    Exception.__init__(self)
    if not einfo:
      einfo = sys.exc_info()

    self.einfo = einfo
    self.comp = comp

  def __str__(self):
    return "Exception while examining %s\n%s" % (
      self.comp.render_path(),
      "".join(traceback.format_exception(*(self.einfo)))
      )

class Comparison(object):
  """This object holds all the state of a single comparison."""
  def __init__(self):
    self.cache = {}
    self.stack = []

  def debug(self, msg):
    pass

  def descend(self, i1, i2):
    """
    Arguments:
      i1 : any item of data
      i2 : an item to compare with i1, this may be some plain data, an
        object derived from deep.Comparator or a mix of both.
    Returns: A true or false value

    Operation:
      1 Return true if i1 and i2 are the same object (using id()).
      2 If we have compared i1 and i2 before we return the value we
        returned previously, from a cache.
      3 If i2 is not already derived from deep.Comparator, wrap it in an
        appropriate comarator object and call that i2.
      4 Ask the comparator i2 if it considers i1 to be equal.

    Circular structures are handled by stage 2 above and the fact that
    when we encounter a previously unseen pair (i1, i2) we set their cached
    result to true. This is effectively "assume i1 == i2 unless we can prove
    otherwise". Eventually we will come back out of the circular structure
    and if we couldn't find an differences then it really was true.
    """

    if i1 is i2:
      return True

    if not isinstance(i2, Comparator):
      i2 = self.wrap(i2)

    # We don't know whether i1 will be hashable so take it's id
    # Comparators are not hashable so this will be just id()
    key = (id(i1), i2) 
    cache = self.cache
    if cache.has_key(key):
      equals = cache[key]
    else:
      cache[key] = True # assume true to match circular structures
      stack = self.stack
      stack.append((i1, i2))
      equals = False
      try:
        try:
          equals = i2.equals(i1, self)
        finally:
          cache[key] = equals
      except DeepException:
        raise
      except Exception:
        raise DeepException(self)

      if equals:
        stack.pop()
      
    return equals

  def wrap(self, item):
    """Take a python object and return a deep.Comparator object that
    will make the "right" type of comparison"""
    t = type(item)

    # do I cover all the builtin types here?
    # missing Class
    if t in (str, int, bool, float, unicode):
      return Equal(item)
    elif t in (list, ):
      return List(item)
    elif t in (set, ):
      return Set(item)
    elif t in (frozenset, ):
      return Frozenset(item)
    elif t in (tuple, ):
      return Tuple(item)
    elif t in (dict, ):
      return Dict(item)
    elif t in (type, ):
      return Is(item)
    else:
      return Object(item)

  def render_path(self):
    """
    Returns:
      a string which represents the stack
    """
    path = "x"
    for (i1, i2) in self.stack:
      path = i2.expr(path)

    return path

  def last(self):
    return self.stack[-1]

  def render_expected(self):
    """
    Returns:
      The value the last comparator was expecting
    """
    return self.last()[1].render()
  
  def render_actual(self):
    """
    Returns:
      The value the last comparator actually got
    """
    last = self.last()
    return last[1].render_value(last[0])
  
  def render_full(self):
    """
    Returns:
      A "pretty" string including the path, the expected and the actual value
      of the last comparator
    """
    return "%s:\nExpected: %s\nActual  : %s" % \
           (self.render_path(), self.render_expected(), self.render_actual())

  def print_full(self):
    print self.render_full()

class DebugComparison(Comparison):
  """This class is useful if you are debugging a comparison and would like
  output on the progress that is being made at each step."""
  def __init__(self):
    self.depth = 0
    Comparison.__init__(self)

  def debug(self, msg):
    print "%s%s" % ("  " * self.depth, msg)

  def descend(self, i1, i2):
    self.debug("descend(%s, %s)" % (i1, i2))
    self.depth += 1
    res = super(DebugComparison, self).descend(i1, i2)
    self.depth -= 1
    self.debug(res)
    return res

  def wrap(self, item):
    wrapped = super(DebugComparison, self).wrap(item)
    self.debug("%s wrapped as %s" % (`item`, `wrapped`))
    return wrapped

class ValueComparator(Comparator):
  """A base class for comparators that perform a simple comparison
  against a value."""
  def __init__(self, value):
    self.value = value

  def render(self):
    return self.render_value(self.value)

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, `self.value`)

class TransformComparator(ValueComparator):
  """A base class for comparators that transform their inout and then
  perform a simple comparison against a value."""
  def equals(self, item, comp):
    trans = self.transform(item)
    return comp.descend(trans, self.value)

  def transform(self, item):
    """Override this method with the transformation that should be applied."""
    pass

  def trans_args(self):
    return ""

  def __repr__(self):
    return "%s(%s)==%s" %(self.__class__.__name__, self.trans_args(), `self.value`)

class Equal(ValueComparator):
  """Compares using python's == ."""
  def equals(self, item, comp):
    return self.value == item

class Is(ValueComparator):
  """Compares using python's is."""
  def equals(self, item, comp):
    return self.value is item

  def render_value(self, value):
    return "%s (id = %i)" % (super(Is, self).render_value(value), id(value))

class Type(TransformComparator):
  """Takes type(item) and then compares."""
  def transform(self, item):
    return type(item)

  def expr(self, expr):
    return "type(%s)" % expr
  
class InstanceOf(ValueComparator):
  """Compares using python's isinstance()."""
  def equals(self, item, comp):
    return isinstance(item, self.value)

  def render(self):
    return "instance of %s" % self.value

  def render_value(self, value):
    return "instance of %s" % type(value)

class DoesNotExist(object):
  pass

class IndexedElem(TransformComparator):
  """Compares against item[some index]."""
  def __init__(self, index, value):
    self.index = index
    self.value = value

  def transform(self, item):
    return item[self.index]

  def expr(self, expr):
    return "%s[%s]" % (expr, self.render_value(self.index))

  def trans_args(self):
    return "%s" % `self.index`

class Len(TransformComparator):
  """Compares against len(item)."""
  def transform(self, item):
    return len(item)

  def expr(self, expr):
    return "len(%s)" % expr

class Listish(ValueComparator):
  """Base class for comparing against specific collections."""
  def equals(self, item, comp):
    v = self.value

    for c in (InstanceOf(self.mytype), Len(len(v))):
      if not comp.descend(item, c):
        return False

    for i in range(0, len(v)):
      if not comp.descend(item, IndexedElem(i, v[i])):
        return False

    return True

class List(Listish):
  """Compare as a list, element by element."""
  mytype = list

class Tuple(Listish):
  """Compare as a tuple, element by element."""
  mytype = tuple

class EqSet(ValueComparator):
  """Compare as a set (not as a bag!)."""
  def equals(self, item, comp):
    matched = []
    missing = []
    extra = {}

    for i in item:
      extra[i] = None

    for c in self.value:
      found = False
      for i in extra:
        if c == i:
          found = True
          matched.append(i)
          del(extra[i])
          break

      if not found:
        missing.append(c)

    if len(missing) or len(extra):
      self.matched = matched
      self.missing = missing
      self.extra = extra.keys()
      return False
    else:
      return True

  def render(self):
    return "%i matching element(s)" % len(self.value)

  def render_value(self, value):
    return "%i matching element(s), extra: %s, missing: %s" % \
           (len(self.matched), self.extra, self.missing)

  def expr(self, expr):
    return "%s as a set (==)" % expr

class Set(EqSet):
  """Compare to builtin set item."""
  def equals(self, item, comp):
    return (comp.descend(item, InstanceOf(set)) and
            EqSet.equals(self, item, comp))

class Frozenset(EqSet):
  """Compare to builtin frozenset item."""
  def equals(self, item, comp):
    return (comp.descend(item, InstanceOf(frozenset)) and
            EqSet.equals(self, item, comp))

class HasKeys(TransformComparator):
  """Compare item.keys()."""
  def __init__(self, value):
    self.value = EqSet(value)

  def transform(self, item):
    return item.keys()

  def expr(self, expr):
    return "%s.keys()" % expr
      
class Dict(ValueComparator):
  """Check that item is a dict and compare it element by element."""
  def equals(self, item, comp):
    v = self.value

    for c in (InstanceOf(dict), HasKeys(v.keys())):
      if not comp.descend(item, c):
        return False

    for i in item:
      if not comp.descend(item, IndexedElem(i, v[i])):
        return False

    return True

class Object(ValueComparator):
  """Compare to another object. Check that the types match and that the
  attribute dictionaries match."""
  def equals(self, item, comp):
    v = self.value

    return comp.descend(item, InstanceOf(v.__class__)) and \
           comp.descend(item, Attr("__dict__", v.__dict__))

class HasAttr(TransformComparator):
  """Check that item has a given attribute."""
  def __init__(self, attr, value=True):
    self.attr = attr
    self.value = value

  def transform(self, item):
    return hasattr(item, self.attr)

  def expr(self, expr):
    return "hasattr(%s, %s)" % (expr, `self.attr`)

  def trans_args(self):
    return `self.attr`

class CmpAttr(TransformComparator):
  """Compare item.some_attribute."""
  def __init__(self, attr, value):
    self.attr = attr
    self.value = value

  def transform(self, item):
    return getattr(item, self.attr)

  def expr(self, expr):
    return "%s.%s" % (expr, self.attr)

  def trans_args(self):
    return `self.attr`

class Attr(Comparator):
  """Check that item.some_attr exists and compare it to some value."""
  def __init__(self, attr, value):
    self.hasattr = HasAttr(attr)
    self.cmpattr = CmpAttr(attr, value)

  def equals(self, item, comp):
    return comp.descend(item, self.hasattr) and \
           comp.descend(item, self.cmpattr)

class Attrs(ValueComparator):
  """Check that item has certain attributes and compare them to some
  values. This can be created in several ways:
  Attrs(attr1=value1, attr2=value)
  Attrs([(attr1, value1), (attr2, value2)])
  Attrs({attr1 : value1, attr2 : value2 })
  """
  def __init__(self, *args, **qargs):
    if args:
      if qargs:
        raise TypeError("__init__() takes a dict, a tuple or keyword args (args and kwargs given)")
      if len(args) > 1:
        raise TypeError("__init__() takes a dict, a tuple or keyword args (2 args given)")
      value = args[0]
    else:
      value = qargs
    ValueComparator.__init__(self, value)

  def equals(self, item, comp):
    v = self.value
    if isinstance(v, dict):
      items = v.items()
    else:
      items = v
    for (attr, c) in items:
      if not comp.descend(item, Attr(attr, c)):
        return False

    return True

class Call(TransformComparator):
  """Calls item(some, args) and compares the result to some value."""
  def __init__(self, value, args=[], kwargs={}):
    self.value = value
    self.args = args
    self.kwargs = kwargs

  def transform(self, item):
    return item(*self.args, **self.kwargs)

  def expr(self, expr):
    args = []
    args_s = ", ".join(map(self.render_value, self.args))
    if args_s:
      args.append(args_s)
    kwargs_a = [("%s=%s" % (x[0], self.render_value(x[1])))
                for x in self.kwargs.items()]
    if kwargs_a:
      args.append(", ".join(kwargs_a))

    return "%s(%s)" % (expr, ", ".join(args))

class AndA(Comparator):
  """Checks that each of an array of comparators successfully compare against
  item."""
  def __init__(self, conds):
    self.conds = conds

  def equals(self, item, comp):
    for cond in self.conds:
      if not comp.descend(item, cond):
        return False

    return True
    
  def render(self):
    return self.render_value(self.value)

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, `self.conds`)

class And(AndA):
  """As AndA but instead of passing in an array object, the argument list
  to the constructor is turned into an array object."""
  def __init__(self, *conds):
    AndA.__init__(self, conds)

class Ignore(Comparator):
  """This comparator always succeeds."""
  def equals(self, item, comp):
    return True
    
  def __repr__(self):
    return "Ignore"

class Re(Comparator):
  """Check that item matches a regular expression (using re.search)."""
  def __init__(self, regex, flags=0):
    if type(regex) is str:
      self.orig = "%s" % `regex`
      if flags:
        self.orig += " (flags=%d)" % flags
      regex = re.compile(regex, flags)
    else:
      self.orig = `regex`
    self.regex = regex

  def equals(self, item, comp):
    if self.regex.search(item):
      return True
    else:
      return False

  def render(self):
    return "something matching %s" % self.orig

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, self.orig)

class Slice(Comparator):
  """Compare certain indexed elements of item against the value."""
  def __init__(self, value, indices):
    """
    Arguments:
      value: the value to comapre against
      indices: the indices to compare, if None then compare all indices
    """
    self.value = value
    self.indices = indices

  def equals(self, item, comp):
    value = self.value
    indices = self.indices

    for i in indices:
      if not comp.descend(item, IndexedElem(i, value)):
        return False

    return True

  def render(self):
    return self.render_value(self.value)

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, `self.value`)

class ArrayValues(ValueComparator):
  """ Compare each element of an array to the value """
  def equals(self, item, comp):
    return comp.descend(item, Slice(self.value, xrange(0, len(item))))
                        
class DictValues(ValueComparator):
  """ Compare each value in a dictionary to the value """
  def equals(self, item, comp):
    return comp.descend(item, Slice(self.value, item.keys()))
                        
