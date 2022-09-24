#! /usr/bin/env python

import sys
import utils as u

host, port = sys.argv[1], int(sys.argv[2])

sys.exit(0 if u.has_service(host, port, 3) else 1)
