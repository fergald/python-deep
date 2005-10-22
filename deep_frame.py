import re

comparators = {}

class Comparator(object):
  pass

class Frame(object):
  def descend(self, i1, i2):
    return self.comparator.descend(i1, i2, self)

class Comparison(object):
  def __init__(self):
    self.cmp_cache = {}
    self.frames = []
    self.bad_frame = None

  def get_frame(self):
    if self.frame:
      return self.frame.pop()
    else:
      return Frame()

  def release_frame(self, frame):
    return self.frames.append(frame)

  def descend(self, i1, i2, prev):
    if not isinstance(i2, Comparator):
      i2 = self.wrap(i2)
    
    key = (id(i1), i2) # Comparators are not hashable
    cache = self.cache
    if cache.has_key(key):
      equals = cache[key]
    else:
    
      cache[key] = True # assume true to match circular structures

      frame = self.get_frame()
      frame.prev = prev
      frame.comparator = i2
      frame.comparison = self
      equals = i2.equals(i1, frame)
      cache[key] = equals

    if equals:
      self.bad_frame = frame
    else:
      self.release_frame(frame)
      
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
  def render(self):
    return render_value(self.value)

  def render_value(self, value):
    if type(value) is str:
      return '"%s"' % re.escape(value)
    else:
      return str(value)

  def expr(self, expr):
    return expr

class Equal(StrableComparator):
  def equals(self, item, frame):
    


class Type(ValueComparator):
  def equals(self, item, comp):
    return self.value is type(item)

  def render_self(self):
    return self.value
  
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
