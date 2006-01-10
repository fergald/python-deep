import re, sys, traceback

__all__ = ['compare',
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
           ]

DEBUG = 0

class Unspec: pass

def compare(i1, i2, debug=Unspec):
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
  def render_value(self, value):
    if type(value) is str:
      return '"%s"' % re.escape(value)
    else:
      return str(value)

  def expr(self, expr):
    return expr

class DeepException(Exception):
  def __init__(self, einfo, comp):
    Exception.__init__(self)
    self.einfo = einfo
    self.comp = comp

  def __str__(self):
    return "Exception while examining %s\n%s" % (
      self.comp.render_path(),
      "".join(traceback.format_exception(*(self.einfo)))
      )

class Comparison(object):
  def __init__(self):
    self.cache = {}
    self.stack = []

  def debug(self, msg):
    pass

  def descend(self, i1, i2):
    if i1 is i2:
      return True

    if not isinstance(i2, Comparator):
      i2 = self.wrap(i2)
    
    key = (id(i1), i2) # Comparators are not hashable
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
        raise DeepException(sys.exc_info(), self)

      if equals:
        stack.pop()
      
    return equals

  def wrap(self, item):
    t = type(item)

    if t in (str, int, bool):
      return Equal(item)
    elif t in (list, ):
      return List(item)
    elif t in (tuple, ):
      return Tuple(item)
    elif t in (dict, ):
      return Dict(item)
    elif t in (type, ):
      return Is(item)
    else:
      return Object(item)

  def render_path(self):
    path = "x"
    for (i1, i2) in self.stack:
      path = i2.expr(path)

    return path

  def last(self):
    return self.stack[-1]
  def render_expected(self):
    return self.last()[1].render()
  
  def render_actual(self):
    last = self.last()
    return last[1].render_value(last[0])
  
  def render_full(self):
    return "%s:\nExpected: %s\nActual  : %s" % \
           (self.render_path(), self.render_expected(), self.render_actual())
  def print_full(self):
    print self.render_full()

class DebugComparison(Comparison):
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
  def __init__(self, value):
    self.value = value

  def render(self):
    return self.render_value(self.value)

  def __repr__(self):
    return "%s(%s)" % (self.__class__.__name__, `self.value`)

class TransformComparator(ValueComparator):
  def equals(self, item, comp):
    trans = self.transform(item)
    return comp.descend(trans, self.value)

  def transform(self, item):
    pass

  def trans_args(self):
    return ""

  def __repr__(self):
    # import pdb;pdb.set_trace()
    return "%s(%s)==%s" %(self.__class__.__name__, self.trans_args(), `self.value`)

class Equal(ValueComparator):
  def equals(self, item, comp):
    return self.value == item

class Is(ValueComparator):
  def equals(self, item, comp):
    return self.value is item

  def render_value(self, value):
    return "%s (id = %i)" % (super(Is, self).render_value(value), id(value))

class Type(TransformComparator):
  def transform(self, item):
    return type(item)

  def expr(self, expr):
    return "type(%s)" % expr
  
class InstanceOf(ValueComparator):
  def equals(self, item, comp):
    return isinstance(item, self.value)

  def render(self):
    return "instance of %s" % self.value

  def render_value(self, value):
    return "instance of %s" % type(value)

class DoesNotExist(object):
  pass

class IndexedElem(TransformComparator):
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
  def transform(self, item):
    return len(item)

  def expr(self, expr):
    return "len(%s)" % expr

class Listish(ValueComparator):
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
  mytype = list

class Tuple(Listish):
  mytype = tuple

class EqSet(ValueComparator):
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

class HasKeys(TransformComparator):
  def __init__(self, value):
    self.value = EqSet(value)

  def transform(self, item):
    return item.keys()

  def expr(self, expr):
    return "%s.keys()" % expr

      
class Dict(ValueComparator):
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
  def equals(self, item, comp):
    v = self.value

    return comp.descend(item, InstanceOf(v.__class__)) and \
           comp.descend(item, Attr("__dict__", v.__dict__))

class HasAttr(TransformComparator):
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
  def __init__(self, attr, value):
    self.hasattr = HasAttr(attr)
    self.cmpattr = CmpAttr(attr, value)

  def equals(self, item, comp):
    return comp.descend(item, self.hasattr) and \
           comp.descend(item, self.cmpattr)

def QAttrs(**qargs):
  return Attrs(qargs)

class Attrs(ValueComparator):
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

