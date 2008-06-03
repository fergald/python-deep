#! /usr/bin/python

import deep

examples = [("a failing regex", "feRgal", deep.Re("rga")),
            ("a failing regex inside a list", [1, "feRgal"], [1, deep.Re("rga")]),
            ("a failing regex inside a list inside a dictionary",
             {"key1" : "wibble", "key2" : [1, "feRgal"]},
             {"key2" : [1, deep.Re("rga"), ], "key1" : "wibble"}),
            ]

for e in examples:
  (desc, obj, comp) = e
  d = deep.diff(obj, comp)
  print "###################"
  print desc
  print "###################"
  print d.render_full()
  print
