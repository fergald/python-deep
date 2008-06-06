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

import deep
import unittest

main = unittest.main

class TestCaseMix(object):
  """ A mixin class for use with python's unittest framework """
  def DeepEq(self, first, second, msg=""):
    res = deep.diff(first, second)
    if res:
      msg = "%s:\nExpected: %s\nActual  : %s" % (msg, second, first)
      msg += "\nDiffered at " + res.render_full()

    self.failUnless(not res, msg)

class TestCase(unittest.TestCase, TestCaseMix):
  """ A premixed TestCase class """
  pass
