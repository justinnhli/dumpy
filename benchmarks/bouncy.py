#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from demos.bouncy import Bouncy


def main():
    bouncy = Bouncy(20)
    bouncy.prestart()
    num_frames = 250
    for _ in range(num_frames):
        bouncy.dispatch_tick(40)


if __name__ == '__main__':
    main()
