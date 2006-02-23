# Copyright 2006 Fergal Daly <fergal@esatclear.ie>

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

import unittest

from deep import *
import re

E=True
N=False

class mess(object):
  def __init__(self):
    self.an_attr = 1
    self.an_attr2 = 2
  def a_func(self, a, b=1, c=0):
    return a + b + c

o = mess()
o2 = mess()
noto = mess()
noto.an_attr2 = 7


class TestEqual(object):
  def __init__(self, i1, i2, name=""):
    self.i1 = i1
    self.i2 = i2
    self.name = name

  def test(self, case):
    c = compare(self.i1, self.i2)
    msg = "%s: %s vs %s should be equal" %(self.name, self.i1, self.i2)

    if c:
      msg += "\n" + c.render_full()

    case.failUnless(not c, msg)

class TestNotEqual(object):
  def __init__(self, i1, i2, path="", actual="", expected="", name=""):
    self.i1 = i1
    self.i2 = i2
    self.path = path
    self.actual = actual
    self.expected = expected
    self.name = name

  def test(self, case):
    c = compare(self.i1, self.i2)
    msg = "%s: %s vs %s should not be equal" %(self.name, self.i1, self.i2)

    if c:
      case.failUnless(True, msg)
      if self.path:
        case.assertEquals(self.path, c.render_path())
      if self.expected:
        case.assertEquals(self.expected, c.render_expected())
      if self.actual:
        case.assertEquals(self.actual, c.render_actual())
    else:
      case.failUnless(False, msg)

E = TestEqual
N = TestNotEqual

class DeepTest(unittest.TestCase):
  def runTest(self):
    tests = [E(1, 1, "1 == 1"),
             N(1, 2, "x", "1", "2", "1 != 2"),
             E((1,2), (1,2), "tuple compare"),
             N((1,3), (1,2), "x[1]", "3", "2", "tuple compare"),
             E(1, Is(1), "1 Is 1"),
             N(2, Is(1), "x", self.str_id(2), self.str_id(1), "2 ! Is 1"),
             E(1, Type(int), "1 Type int"),
             N([], Type(int), "type(x)", self.str_id(list), self.str_id(int),
               "[] ! Type int"),
             E(self, InstanceOf(unittest.TestCase), "self InstanceOf test"),
             N([], InstanceOf(int), "x",
               "instance of <type 'list'>",
               "instance of <type 'int'>",
               "[] ! InstanceOf int"),
             E([0,1], IndexedElem(1, 1), "List[1]"),
             N([0,1], IndexedElem(0, 1), "x[0]", "0", "1", "List[0]"),
             E([0,1], List([0, 1]), "list"),
             N([0,1], List([0, 0]), "x[1]", "1", "0", "not list"),
             E([0,1], [0, 1], "auto list"),
             N([0,1], List([0, 0, 0]), "len(x)", "2", "3", "not list len"),
             N(1, List([0, 0, 0]), "x", "instance of <type 'int'>", None, "not list type"),
             E([1,0], EqSet([0, 1]), "eqset"),
             N([0,1], EqSet([0, 2]), "x as a set (==)",
               "1 matching element(s), extra: [1], missing: [2]",
               "2 matching element(s)",
               "not eqset"),
             E({"a" : 0, "b" : 1}, IndexedElem("b", 1), "Dict['a']"),
             N({"a" : 0, "b" : 1}, IndexedElem("a", 1), "x['a']", "0", "1",
               "Dict['b']"),
             E({"a" : 0, "b" : 1}, HasKeys(["a", "b"]), "has keys"),
             N({"a" : 0, "b" : 1}, HasKeys(["a", "c"]),
               'x.keys() as a set (==)',
               "1 matching element(s), extra: ['b'], missing: ['c']",
               '2 matching element(s)',
               "! haskeys"),
             E({"a" : 0, "b" : 1}, Dict({"a" : 0, "b" : 1}), "Dict"),
             N({"a" : 0, "b" : 1}, Dict({"a" : 1, "b" : 1}), "x['a']", "0", "1",
               "! Dict"),
             N({"a" : 0, "c" : 1}, Dict({"a" : 1, "b" : 1}),
              'x.keys() as a set (==)', None, None, "! Dict keys"),
             N(1, Dict({"a" : 1, "b" : 1}),
               'x', "instance of <type 'int'>", None, "! Dict type"),
             E({"a" : 0, "b" : 1}, {"a" : 0, "b" : 1}, "auto Dict"),
             E(o, HasAttr("an_attr"), "attr"),
             N(o, HasAttr("another_attr"), "hasattr(x, 'another_attr')", "False", "True", "! attr"),
             E(o, Attr("an_attr", 1), "attr"),
             N(o, Attr("an_attr", 0), 'x.an_attr', "1", "0", "! attr"),
             E(o, Attrs({"an_attr" : 1, "an_attr2" : 2}), "attrs dict"),
             N(o, Attrs({"an_attr" : 0, "an_attr2" : 2}), 'x.an_attr', "1", "0",
               "! attrs dict "),
             E(o, Attrs((("an_attr", 1), ("an_attr2", 2))), "attrs list"),
             N(o, Attrs((("an_attr", 0), ("an_attr2", 2))), 'x.an_attr',
               "1", "0", "! attrs list "),
             E(o, Attrs(an_attr=1, an_attr2=2), "attrs dict"),
             N(o, Attrs(an_attr=0, an_attr2=2), 'x.an_attr', "1", "0",
               "! attrs dict "),
             N(o, Attr("no_attr", 0), "hasattr(x, 'no_attr')", "False", "True", "no attr"),
             N((1,2), Attr("no_attr", 0), "hasattr(x, 'no_attr')", "False", "True", "tuple, no attr"),
             E(o.a_func, Call(6, [3], {"c" : 2}), "call"),
             N(o.a_func, Call(5, [3], {"c" : 2}), "x(3, c=2)", "6", "5",
               "! call"),
             E(o, o2, "object"),
             N(o, noto, "x.__dict__['an_attr2']", "2", "7", "! object"),
             E(o, And(Attr("an_attr", 1), Attr("an_attr2", 2)), "and"),
             N(o, And(Attr("an_attr", 0), Attr("an_attr2", 2)), 'x.an_attr', "1", "0", "! and 1"),
             N(o, And(Attr("an_attr", 1), Attr("an_attr2", 3)), 'x.an_attr2', "2", "3", "! and 2"),
             E([1, 2], [Ignore(), 2], "ignore"),
             ]

    # for t in (tests[-1],):
    for t in tests:
      t.test(self)
      
  def str_id(self, item):
    return "%s (id = %i)" % (item, id(item))

class DeepExc(unittest.TestCase):
  def runTest(self):
    ex = None
    try:
      compare([0, 1], IndexedElem(2, None))
    except Exception, e:
      ex = e

    for pat in (r"examining x\[2\]", "IndexError"):
      if not re.search(pat, str(ex)):
        self.fail("exception didn't match '%s':\n%s" % (pat, ex))


if __name__ == '__main__':
  suite = unittest.TestSuite()
  suite.addTests([ DeepTest(),
                   DeepExc(),
                  ]
                )
  unittest.TextTestRunner(verbosity=3).run(suite)
        
