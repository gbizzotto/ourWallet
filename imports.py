import importlib

def auto_import(module_name):
    if importlib.find_loader(module_name) is None:
        if auto_import.install == None:
            x = input("Install missing modules? (Y/n)")
            auto_import.install = x in ("y", "Y", "")
        if auto_import.install:
            from pip._internal import main as pipmain
            pipmain(['install', module_name])
    globals()[module_name] = __import__(module_name)
auto_import.install = None
