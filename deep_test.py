#! /usr/bin/python

import myunittest
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

class DeepTest(myunittest.TestCase):
  def runTest(self):
    tests = [[E, 1, 1, "1 == 1"],
             [N, 1, 2, "x", "1", "2", "1 != 2"],
             [E, 1, Is(1), "1 Is 1"],
             [N, 2, Is(1), "x", self.str_id(2), self.str_id(1), "2 ! Is 1"],
             [E, 1, Type(int), "1 Type int"],
             [N, [], Type(int), "type(x)", self.str_id(list), self.str_id(int),
              "[] ! Type int"],
             [E, self, InstanceOf(myunittest.TestCase), "self InstanceOf test"],
             [N, [], InstanceOf(int), "x",
              "instance of <type 'list'>",
              "instance of <type 'int'>",
              "[] ! InstanceOf int"],
             [E, [0,1], IndexedElem(1, 1), "List[1]"],
             [N, [0,1], IndexedElem(0, 1), "x[0]", "0", "1", "List[0]"],
             [E, [0,1], List([0, 1]), "list"],
             [N, [0,1], List([0, 0]), "x[1]", "1", "0", "not list"],
             [E, [0,1], [0, 1], "auto list"],
             [N, [0,1], List([0, 0, 0]), "len(x)", "2", "3", "not list len"],
             [N, 1, List([0, 0, 0]), "x", "instance of <type 'int'>", None, "not list type"],
             [E, [1,0], EqSet([0, 1]), "eqset"],
             [N, [0,1], EqSet([0, 2]), "x as a set (==)",
              "1 matching element(s), extra: [1], missing: [2]",
              "2 matching element(s)",
              "not eqset"],
             [E, {"a" : 0, "b" : 1}, IndexedElem("b", 1), "Dict['a']"],
             [N, {"a" : 0, "b" : 1}, IndexedElem("a", 1), 'x["a"]', "0", "1",
              "Dict['b']"],
             [E, {"a" : 0, "b" : 1}, HasKeys(["a", "b"]), "has keys"],
             [N, {"a" : 0, "b" : 1}, HasKeys(["a", "c"]),
              'x.keys() as a set (==)',
              "1 matching element(s), extra: ['b'], missing: ['c']",
              '2 matching element(s)',
              "! haskeys"],
             [E, {"a" : 0, "b" : 1}, Dict({"a" : 0, "b" : 1}), "Dict"],
             [N, {"a" : 0, "b" : 1}, Dict({"a" : 1, "b" : 1}), 'x["a"]', "0", "1",
              "! Dict"],
             [N, {"a" : 0, "c" : 1}, Dict({"a" : 1, "b" : 1}),
              'x.keys() as a set (==)', None, None, "! Dict keys"],
             [N, 1, Dict({"a" : 1, "b" : 1}),
              'x', "instance of <type 'int'>", None, "! Dict type"],
             [E, {"a" : 0, "b" : 1}, {"a" : 0, "b" : 1}, "auto Dict"],
             [E, o, Attr("an_attr", 1), "attr"],
             [N, o, Attr("an_attr", 0), 'x.an_attr', "1", "0", "! attr"],
             [E, o, Attrs({"an_attr" : 1, "an_attr2" : 2}), "attrs dict"],
             [N, o, Attrs({"an_attr" : 0, "an_attr2" : 2}), 'x.an_attr', "1", "0",
              "! attrs dict "],
             [E, o, Attrs((("an_attr", 1), ("an_attr2", 2))), "attrs list"],
             [N, o, Attrs((("an_attr", 0), ("an_attr2", 2))), 'x.an_attr',
              "1", "0", "! attrs list "],
             [E, o.a_func, Call(6, [3], {"c" : 2}), "call"],
             [N, o.a_func, Call(5, [3], {"c" : 2}), "x(3, c=2)", "6", "5",
              "! call"],
             [E, o, o2, "object"],
             ]

    for t in tests:
      if t[0]:
        self.testEqual(*t[1:])
      else:
        self.testNotEqual(*t[1:])
      
  def str_id(self, item):
    return "%s (id = %i)" % (item, id(item))

  def testEqual(self, i1, i2, name=""):
    c = compare(i1, i2)
    msg = "%s: %s vs %s should be equal" %(name, i1, i2)

    if c:
      msg += "\n" + c.render_full()

    self.failUnless(not c, msg)

  def testNotEqual(self, i1, i2, path="", actual="", expected="", name=""):
    c = compare(i1, i2)
    msg = "%s: %s vs %s should not be equal" %(name, i1, i2)

    if c:
      self.failUnless(True, msg)
      if path:
        self.Eq(path, c.render_path(), "path")
      if expected:
        self.Eq(expected, c.render_expected(), "expected")
      if actual:
        self.Eq(actual, c.render_actual(), "actual")
    else:
      self.failUnless(False, msg)

class DeepExc(myunittest.TestCase):
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
        
