import os
import importlib

print([ importlib.import_module(i) for i in os.listdir() if i.endswith(".py") and not i.startswith("test_") ])

exit(0)
