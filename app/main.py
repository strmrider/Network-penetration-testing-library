import os
from . import logo, action, menus, style

exit_commands = ['exit', 'q']
CLEAR = 'clear'
RESET = 'rest'
SCAN_OPTIONS = 'scan'
DOS_OPTIONS = 'dos'
MITM_OPTIONS = 'mitm'


def main_screen():
    os.system('clear')
    print(style.fg.darkgrey, logo.SKULL_1)
    print("\n")
    print(style.fg.lightgrey)
    print("Welcome to the Pentesting System.\nType in an option for further details. Type 'reset' to restart the "
          "program." " Type 'exit' or 'q' to quit.")
    print("")
    menus.print_main_menu()
    print("")

def app_flow():
    while True:
        print(style.fg.lightgreen)
        data = input(">>> ")
        if data in exit_commands:
            break
        if data == "clear":
            os.system('clear')
        elif data == "reset":
            main_screen()
        elif data == "scan":
            menus.print_options(menus.scan_options)
        elif data == "dos":
            menus.print_options(menus.dos_options)
        elif data == "mitm":
            menus.print_options(menus.mitm_options)
        else:
            splitted = data.split(' ')
            if not action.scans_handler(splitted):
                if not action.dos_handler(splitted):
                    if not action.mitm_handler(splitted):
                        print ("Command {} is invalid".format(splitted[0]))

def run_app():
    main_screen()
    app_flow()
