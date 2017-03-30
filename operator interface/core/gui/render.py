import subprocess
import os

files = os.listdir(os.curdir)  #files and directories

while True:

    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension == ".ui":
            output_file = filename + ".py"
            command_string = "pyuic5 " + file + " -o " + output_file
            os.system(command_string)
            print("Converted: " + file + " to: " + output_file)