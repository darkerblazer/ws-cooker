import importlib

def test_one(i="wscooker-gui.py"): importlib.import_module(i[:-3])

def test_two(i="stupid.py"): importlib.import_module(i[:-3])


# exit(0)
