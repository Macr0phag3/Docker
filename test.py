import time

from toolboxs import tt as tt

print tt.ip

raw_input("> ")
try:
    reload(tt)
except:
    pass

print tt.ip
