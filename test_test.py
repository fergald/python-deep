#! /usr/bin/python

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

import deep.test

class DeepTest(deep.test.TestCase):
  def testTest(self):
    self.assertEquals(1, 1)
    self.DeepEq([1], [1], "wibble")

if __name__ == '__main__':
 deep.test.main()
