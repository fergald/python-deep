# can't remember if this is supposed to work yet or not

class Set(ValueComparator):
  def equals(self, item, comp):
    v = self.value
    c_match = {}
    i_match = {}

    for c in v:
      c_match[id(c)] = {}
    for i in item:
      i_match[id(i)] = {}
    for c in v:
      for i in item:
        if comp.descend(i, c):
          c_match[id(c)][id(i)] = None
          i_match[id(i)][id(c)] = None

    # remove ambiguity by delete all no matches and exact matches
    def no_match(match):
      no_match = []
      for key in match:
        if not key:
          no_match.append(key)
      return no_match

    missing = no_match(c_match)
    del(c_match[missing])
    extra = no_match(i_match)
    del(i_match[extra])

    for c in c_match.keys():
      cm = c_match[c]
      if len(cm) == 1:
        i, = cm
        im = i_match[i]
        if len(im) == 1:
          # totally unambiguous match, remove from both sides
          del(c_match[c])
          del(i_match[i])
      
    # now we need to generate sets of compatible assumptions 
    for (v2, m2) in v_match.keys():
      
    for key in v:
      if extra.has_key(key):
        del extra[key]
      else:
        missing.append(key)

    if extra or missing:
      self.extra = extra.keys()
      self.missing = missing
      return False
    else:
      return True

    def expr(self, expr):
      pass
