import json
import sys
import os
from shutil import copyfile
system_paths = ['C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands', 'C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands', 'C:\\Users\\kasymzhan.asimov\\Desktop\\rg.avr\\Resources\\python-3\\python39.zip', 'C:\\Users\\kasymzhan.asimov\\Desktop\\rg.avr\\Resources\\python-3\\DLLs', 'C:\\Users\\kasymzhan.asimov\\Desktop\\rg.avr\\Resources\\python-3\\lib', 'C:\\Users\\kasymzhan.asimov\\Desktop\\rg.avr\\Resources\\python-3', 'C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands\\venv', 'C:\\Users\\kasymzhan.asimov\\PycharmProjects\\1cbrands\\venv\\lib\\site-packages']


def get_params():
    data = sys.stdin
    params = json.load(data)
    return params


def print_params(params, path='params_print.txt'):
    f = open(path, "w")
    f.write(json.dumps(params))
    f.close()


if __name__ == '__main__':
    with open(__file__) as f:
        lines = f.readlines()
    print(lines)
    for i in range(len(lines)):
        if 'system_paths =' in lines[i][0:15]:
            lines[i] = f'system_paths = {str(sys.path)}\n'
    with open(__file__, "w") as f:
        f.write("".join(lines))
    for each in system_paths:
        if each.endswith("\\site-packages"):
            copyfile(each + '\\pywin32_system32\\pythoncom37.dll', each + '\\win32\\lib\\pythoncom37.dll')
            copyfile(each + '\\pywin32_system32\\pywintypes37.dll', each + '\\win32\\lib\\pywintypes37.dll')

else:
    # for path in system_paths:
    #     if path not in sys.path:
    #         sys.path.append(path)
    if not str(os.getcwd()).endswith('Core_Agent'):
        sys.path = system_paths
    # f = open(r"C:\Users\Administrator\Desktop\RPA_Robot\Robot\EnbekRobot\Files\demofile3.txt", "w")
    # f.write(str(system_paths))
    # f.close()
