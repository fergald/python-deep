import re

comparators = {}

class Comparator(object):
  pass

pending = Pending()

class Comparison(object):
  def __init__(self):
    self.cmp_cache = {}
    self.wrap_cache = {}
    self.stack = []

  def descend(self, i1, i2):
    if not isinstance(i2, Comparator):
      i2 = self.wrap(i2)
    
    key = (i1, i2)
    cache = self.cache
    if cache.has_key(key):
      return cache[key]
    
    cache[key] = True # assume true to match circular structures
    stack = self.stack
    stack.append(i1, i2)
    value = i2.equals(i1, self)
    if value:
      stack.pop()
    cache[key] = value
    return value

  def wrap(self, item):
    t = type(item)
    if t in (str, int):
      return Scalar(item)
    if t in (str, int, list, tuple):
      return 
    
class NotSupplied():
  pass

class ValueComparator(Comparator):
  def __init__(self, value):
    self.value = value

  def render(self, value=NotSupplied):
    if value is NotSupplied:
      value = self.value

    return self.render_any(value)
class StrableComparator(Comparator):
  def render(self, value=NotSupplied):
    if type(value) is str:
      return '"%s"' % re.escape(value)
    else:
      return str(value)

class Type(ValueComparator):
  def equals(self, i2, comp):
    return self.value is type(i2)

  def render(self, value=NotSupplied):
    return "type(%s)"
  
  def expr(self, expr):
    return "type(%s)" % expr
  
class Scalar(ValueComparator):
  def equals(self, i2, comp):
    return self.value == i2

class DoesNotExist(object):
  def render(self, value=NotSupplied):
    if value is NotSupplied:
      return "Does Not Exist"
    else:
      return str(value)
    

DNE = DoesNotExist()

class Iterable(ValueComparator):
  def equals(self, i2, comp):
    value = self.value

    for i1 in 
    return self.value == i2

class Len(ValueComparator):
  def equals(self, i2, comp):
    value = self.value
    
    return self.value == len(i2)

  def expr(self, expr):
    return "len(%s)" % expr
