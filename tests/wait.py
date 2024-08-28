#! /usr/bin/env python

import sys
import utils as u

assert len(sys.argv) == 4, f"usage: {sys.argv[0]} host port tries"

host, port, tries = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

sys.exit(0 if u.has_service(host, port, tries) else 1)
