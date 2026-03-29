#! python 3
import sys
import os
import inspect
import Rhino
import System

PLUGIN_ID = System.Guid("3162308b-a228-431a-831e-a6ba6e442be3")

plugin_path = Rhino.PlugIns.PlugIn.PathFromId(PLUGIN_ID)

if plugin_path:
    script_dir = os.path.dirname(plugin_path)
else:
    try:
        current_file = os.path.abspath(__file__)
    except NameError:
        current_file = inspect.getfile(inspect.currentframe())
    script_dir = os.path.dirname(current_file)

if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from ibis.commands.scale import run_scale_command

if __name__ == "__main__":
    run_scale_command()