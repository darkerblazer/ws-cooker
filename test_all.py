import os
import importlib

for i in [ importlib.import_module(i[:-3]) for i in os.listdir() if i.endswith(".py") and not i.startswith("test_") ]: globals()[i__name__] = i

# exit(0)
