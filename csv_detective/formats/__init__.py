import importlib
import os

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and not file.startswith("_"):
        module_name = file[:-3]
        module = importlib.import_module(f"csv_detective.formats.{module_name}")
        globals()[module_name] = module
        del module
