import importlib

def trend_import(model):
    return importlib.import_module("api_util.%s"%model)