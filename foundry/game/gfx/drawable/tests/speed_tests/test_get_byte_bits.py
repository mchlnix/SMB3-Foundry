

import time
from random import randint
from foundry.game.gfx.drawable.get_byte_bits import get_byte_bits as get_byte_bits_python
import pyximport
pyximport.install(inplace=True)
from foundry.game.gfx.drawable.get_byte_bits_cython import get_byte_bits as get_byte_bits_cython


test_count = 1000000
data = [randint(0, 0xFF) for i in range(test_count)]

time_start = time.time()
for byt in data:
    get_byte_bits_python(byt, False, 0, 1)
python_time = time.time() - time_start

time_start = time.time()
for byt in data:
    get_byte_bits_cython(byt, False, 0, 1)
cython_time = time.time() - time_start

print(f"Python: {python_time}", f"Cython: {cython_time}", f"Speed Increase: {python_time / cython_time}")