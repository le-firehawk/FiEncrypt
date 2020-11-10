from scapy.all import *
# FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.
# Copyright (C) 2020 le_firehawk

# FiEncrypt is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# FiEncrypt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# To contact the owner of FiEncrypt, use the following:
# Email: firehawk@opayq.net

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>


# Placed above due to import * only working at module level


class ImportStructure:
    """Staggered approach for importing modules by category, can be called at any time"""

    def __init__(self, bracket):
        if bracket == "logic":
            # By declaring modules as global variables, they can be accessed as normal
            global math, time, random, datetime, notification
            import math
            import time
            import random
            import datetime
            from plyer import notification
        elif bracket == "system":
            global os, sys, shutil, subprocess, zipfile, ctypes, hashlib
            import os
            import sys
            import shutil
            import subprocess
            import zipfile
            import ctypes
            import hashlib
        elif bracket == "string":
            global getpass, textwrap
            import getpass
            import textwrap
        elif bracket == "network":
            global urllib, socket, netifaces
            import urllib.request as urllib
            import socket
            try:
                import netifaces
            except:
                pass
        elif bracket == "gui":
            global gui
            import PySimpleGUI as gui


class Colours:
    """Manages application of colour codes for the standard out"""

    def __init__(self, colour, **force_apply):
        force_apply = force_apply.get("force", False)
        self.error, self.reset = "\033[91m", "\033[0m"
        if colour == None:
            self.default_colour = parse_colours("\033[0m")
        else:
            self.default_colour = parse_colours(colour)
            if force_apply and "40" in self.default_colour:
                self.error = True
        apply_colour(self.default_colour, self.error, self.reset)

    def return_default(self):
        """Returns the colour code parsed by parse_colours() to be saved as a variable or be directly applied"""
        return self.default_colour


class Contacts:
    """Allows MAC addresses to be saved locally and referred to when sending messages"""
    # ?Staticmethods are used as no self object is required and because the call stack is disrupted through dynamic classes
    @staticmethod
    def main():
        """Gathers a list of all names of contacts present in the Contacts directory"""
        contact_names = []
        enter_home_directory()
        os.chdir(f"./Contacts")
        for root, dirs, files in os.walk(f"."):
            for name in files:
                contact_names.append(name.replace(".txt", ""))
        return contact_names

    @staticmethod
    def check_for(contact_name):
        """Checks for the name passed as a parameter against all identified names in Contacts directory"""
        contact_names = Contacts.main()
        for contact in contact_names:
            if contact_name.lower() in contact.lower():
                with open(f"./{contact}.txt", "r+") as contact_file:
                    contact_lines = contact_file.readlines()
                if "-" in contact_lines[2]:
                    contact_lines[2] = None
                try:
                    contact_lines[3] = contact_lines[3]
                except IndexError:
                    contact_lines.append("No details provided!")
                return contact_lines[0], contact_lines[1], contact_lines[2], contact_lines[3]
            elif ":" in contact_name:
                with open(f"./{contact}.txt", "r+") as contact_file:
                    contact_lines = contact_file.readlines()
                if contact_name in contact_lines[1]:
                    return contact_lines[0], contact_lines[1], contact_lines[2], contact_lines[3]
        return None, None, None, None

    @staticmethod
    def add_ip(contact_name, ip):
        """Locates a contact's file and appends the ip parameter into the relevant line of said file"""
        enter_home_directory()
        os.chdir(f"./Contacts")
        with open(f"./{contact_name}.txt", "r+") as update_contact:
            contact_lines = update_contact.readlines()
            update_contact.seek(0)
            update_contact.truncate()
            update_contact.write(
                f"{contact_lines[0]}{contact_lines[1]}{ip}\n")
            for i, contact_details in enumerate(contact_lines):
                if i > 2 and contact_details.strip() != "" and contact_details != None:
                    contact_details = contact_details.replace("\n", "")
                    update_contact.write(f"{contact_details}")

    @staticmethod
    def add(contact_name, mac, details):
        """Adds a new contact file into the Contacts directory, with all details being written"""
        enter_home_directory()
        os.chdir(f"./Contacts")
        with open(f"./{contact_name}.txt", "w+") as new_contact:
            new_contact.write(f"{contact_name}\n{mac}\n-\n{details}")

    @staticmethod
    def remove(contact_name):
        """Deletes a contact's file, if the search returns a result"""
        name, mac, ip, details = Contacts.check_for(contact_name)
        if None in [name, mac, ip, details]:
            animated_print(f"Unable to locate contact to delete!")
        else:
            os.remove(f"./{name.strip()}.txt")

    @staticmethod
    def list_all():
        """Lists every contact name found within the Contacts directory"""
        contact_names = Contacts.main()
        if contact_names == []:
            animated_print(f"No contacts found in FiEncrypt directory!")
        else:
            for i, name in enumerate(contact_names):
                animated_print(f"Contact {i+1}: ")
                enter_home_directory()
                os.chdir(f"./Contacts")
                with open(f"./{name}.txt", "r+") as contact:
                    contact_lines = contact.readlines()
                    animated_print(
                        f"Name: {contact_lines[0]}\nMAC Address: {contact_lines[1]}\nLast IP: {contact_lines[2]}\nDetails:")
                    for i, line in enumerate(contact_lines):
                        if i > 2 and line != "\n":
                            spec_print = contact_lines[i].replace("\n", "")
                            animated_print(f"{spec_print}\n")


def display_license():
    """Prints out short form message, outlining the basics of the AGPLv3 license, which is applied to FiEncrypt"""
    print("""FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2020 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>\n""")


def parse_colours(colour):
    """Takes plain text colour reference from the config file and returns the applicable colour code for Python's standard out"""
    if "bold" in colour.lower():
        return "\033[1m"
    elif "faded" in colour.lower():
        return "\033[2m"
    elif "faded_italic" in colour.lower():
        return "\033[3m"
    elif "faded_italic_underline" in colour.lower():
        return "\033[4m"
    elif "faded_italic_underline_highlighted" in colour.lower():
        return "\033[7m"
    elif "highlight_out" in colour.lower():
        return "\033[8m"
    elif "invisible" in colour.lower():
        return "\033[27m"
    elif "dark_grey" in colour.lower():
        return "\033[28m"
    elif "grey" in colour.lower():
        return "\033[29m"
    elif "black" in colour.lower():
        return "\033[30m"
    elif "red" in colour.lower():
        return "\033[31m"
    elif "green" in colour.lower():
        return "\033[32m"
    elif "yellow" in colour.lower():
        return "\033[33m"
    elif "blue" in colour.lower():
        return "\033[34m"
    elif "purple" in colour.lower():
        return "\033[35m"
    elif "teal" in colour.lower():
        return "\033[36m"
    elif "black_background" in colour.lower():
        return "\033[40m"
    elif "red_background" in colour.lower():
        return "\033[41m"
    elif "green_background" in colour.lower():
        return "\033[42m"
    elif "yellow_background" in colour.lower():
        return "\033[43m"
    elif "blue_background" in colour.lower():
        return "\033[44m"
    elif "purple_background" in colour.lower():
        return "\033[45m"
    elif "ocean_background" in colour.lower():
        return "\033[40m"
    elif "teal_background" in colour.lower():
        return "\033[46m"
    elif "white_background" in colour.lower():
        return "\033[47m"
    else:
        return "\033[0m"


def apply_colour(default, error, reset):
    """Prints out the default colour defined within the config file and saves it as a global variable applied_default_colour"""
    global applied_default_colour
    applied_default_colour, error_colour, reset_colour = default, error, reset
    if int(default.replace("\033[", "").replace("m", "")) / 10 != 4:
        print(f"{default}", end="")
    elif error == True:
        raise Exception("Invalid Colour!")
    else:
        pass


def animated_print(string, **speed):
    """Accepts a string to be printed, along with the optional parameter for how long Python should wait before printing the next character"""
    try:
        speed = speed.get('speed', None)
        enter_home_directory()
        with open(f"./config.txt", "r+") as config_file:
            config_lines = config_file.readlines()
            if "print" in config_lines[4] and speed == None and not check_debug_mode():
                printing_speed = config_lines[4].split(" = ")
                printing_speed = printing_speed[1]
            elif check_debug_mode():
                printing_speed = 0
            elif speed == None:
                printing_speed = 0.05
            else:
                printing_speed = speed
        for character in string:
            sys.stdout.write(character)
            sys.stdout.flush()
            time.sleep(float(printing_speed))
        print("")
        time.sleep(0.2)
    except KeyboardInterrupt:
        print("")
        maybe_quit()
        Colours(default_colour)
    except:
        print("\nCRASH! Restarting FiEncrypt!")
        initiate()


def substring(string, search, state):
    """Splits a string with the .partition() attribute, based on a substring character, with the pre-defined index of the result being returned"""
    return string.partition(search)[state]


def check_vars(*args):
    """Checks all variables to ensure they are not blank or None, returning all as a list"""
    new_args = []
    for var in args:
        if var == None or str(var).strip() == "":
            var = None
        new_args.append(var)
    return new_args


def maybe_quit():
    """Prompts used with the option to quit FiEncrypt"""
    quit = ""
    while quit != None and "y" not in quit.lower() and "n" not in quit.lower():
        try:
            quit = privacy_input(
                "\033[5mWould you like to quit? [Y|N]\033[0m", 0)
        except KeyboardInterrupt:
            quit = "y"
    if quit == None:
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
    elif "y" in quit.lower():
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        exit()


def pass_os():
    """Returns sys.platform value"""
    return sys.platform


def pass_user():
    """Obtains user from within the current directory and returns it"""
    home_directory, operating_system, user = enter_home_directory()
    try:
        return user
    except NameError:
        return None


def hide_tree():
    """Applies hidden attribute to all files within the FiEncrypt directory (Windows only)"""
    if sys.platform == "win32":
        subprocess.check_call(
            ["attrib", "+H", f"../FiEncrypt"])
        subprocess.check_call(
            ["attrib", "+H", f"./Contacts"])
        subprocess.check_call(
            ["attrib", "+H", f"./config.txt"])
        subprocess.check_call(
            ["attrib", "+H", f"./logs.txt"])
        subprocess.check_call(
            ["attrib", "+H", f"./code.txt"])
        subprocess.check_call(
            ["attrib", "+H", f"./inbox.txt"])
        subprocess.check_call(
            ["attrib", "+H", f"./messagein.txt"])
        subprocess.check_call(
            ["attrib", "+H", f"./messageout.txt"])
        try:
            subprocess.check_call(
                ["atrib", "+H", f"./anarchy2.ico"])
        except:
            pass
        try:
            subprocess.check_call(
                ["attrib", "+H", f"./anarchy.png"])
        except:
            pass


def set_home_directory(operating_system):
    """Performs a variety of checks, including the drive letter being used, to determine the ideal location for FiEncrypt directory to be created"""
    if operating_system == "win32":
        file_path = sys.argv[0].split(":\\")
        if ".py" in str(file_path):
            file_path[1] = file_path[1].replace("\\\listener.py", "")
            if file_path[1].endswith(f":"):
                file_path[1] = file_path[1].replace(":", "")
        drive_letter = file_path[0]
        if drive_letter.lower() == "c":
            user = substring(file_path[1], "Users\\", 2)
            user = substring(user, "\\", 0)
            path = f"c:/Users/{user}/FiEncrypt"
        else:
            path = f"{drive_letter}:/FiEncrypt"
            user = None
        if os.path.exists(path):
            return path, user
        else:
            os.mkdir(path)
            return path, user
    elif operating_system == "linux":
        file_path = os.getcwd()
        user = substring(file_path, f"home/", 2)
        user = substring(user, f"/", 0)
        path = f"/home/{user}/FiEncrypt"
        if os.path.exists(path):
            return path, user
        else:
            os.mkdir(path)
            return path, user


def enter_home_directory():
    """Changes the current directory to the base level of the FiEncrypt directory, for ease of reference to files within"""
    operating_system = pass_os()
    home_directory, user = set_home_directory(operating_system)
    os.chdir(home_directory)
    return home_directory, operating_system, user


def check_debug_mode():
    """Returns the bool of whether the program should be launched in debug mode"""
    enter_home_directory()
    with open(f"./config.txt", "r+") as config_file:
        config_lines = config_file.readlines()
        if "-" not in config_lines[2]:
            if "true" in config_lines[2].lower():
                debug_mode = True
            else:
                debug_mode = False
            return debug_mode
        else:
            return False


def establish_tree():
    """Creates the FiEncrypt directory, with AGPLv3 license being downloaded and a config file with default settings created"""
    import urllib.request
    from stat import S_IREAD, S_IRGRP, S_IROTH
    display_license()
    with open(f"./config.txt", "w+") as config_file:
        default_config = ["# FiEncrypt", "[config.txt]", "debug_mode = False",
                          "display_initiate = False", "-", "-", "-", "-", "graphic_mode = False", "private_mode = False", "auto_code = False"]
        for line in default_config:
            config_file.write(f"{line}\n")
    with open(f"./code.txt", "w+") as code_file:
        pass
    with open(f"./logs.txt", "w+") as logs_file:
        pass
    with open(f"./messagein.txt", "w+") as message_in_file:
        pass
    with open(f"./messageout.txt", "w+") as message_out_file:
        pass
    with open(f"./CREDENTIALS.txt", "w+") as credientials:
        os.chmod(f"./CREDENTIALS.txt", S_IREAD | S_IRGRP | S_IROTH)
    urllib.request.urlretrieve(
        "https://www.gnu.org/licenses/agpl-3.0.txt", f"./LICENSE")
    os.mkdir(f"./Contacts")
    if sys.platform == "win32":
        hide_tree()


def add_new_user():
    enter_home_directory()
    valid_username, valid_password = False, False
    while not valid_username:
        username = privacy_input("Enter a username here", 0)
        hash_user = username.encode("utf-8")
        hash_user = hashlib.sha256(hash_user).hexdigest()
        with open(f"./CREDENTIALS.txt", "r+") as credentials:
            credential_lines = credentials.readlines()
            if len(credential_lines) == 0:
                valid_username = True
            else:
                for line in credential_lines:
                    if hash_user in line:
                        animated_print(f"Username already taken!")
                        valid_username = False
                        break
                    else:
                        valid_username = True
    password = privacy_input("Enter a password here", 1)
    hash_pass = password.encode("utf-8")
    hash_pass = hashlib.sha256(hash_pass).hexdigest()
    confirm_password = "".encode("utf-8")
    while hash_pass != hashlib.sha256(confirm_password).hexdigest():
        confirm_password = privacy_input("Enter password again", 1).encode("utf-8")
        if hash_pass != hashlib.sha256(confirm_password).hexdigest():
            print(f"Passwords do not match!")
    hash = username + password
    hash = hash.encode("utf-8")
    hash = hashlib.sha256(hash).hexdigest()
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        existing_credentials = credentials.readlines()
        existing_credentials.append(hash_user)
        existing_credentials.append(hash)
        for credential in existing_credentials:
            credential = credential.replace("\n", "")
            credentials.write(f"{credential}\n")
    try:
        os.mkdir(f"./{hash_current_user(username.lower())}_inbox")
    except FileExistsError:
        pass
    os.chdir(f"./{hash_current_user(username.lower())}_inbox")
    with open(f"./messages.txt", "w+") as indox_file:
        pass
    animated_print(f"New user {username} successfully added to FiEncrypt!")


def validate_login(username, password):
    hash_user = username.encode("utf-8")
    hash_user = hashlib.sha256(hash_user).hexdigest()
    hash = username + password
    hash = hash.encode("utf-8")
    hash = hashlib.sha256(hash).hexdigest()
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        for i, line in enumerate(credential_lines):
            if hash_user in line:
                valid_username = True
                if hash in credential_lines[i+1]:
                    valid_password = True
                else:
                    valid_password = False
                if valid_username and valid_password:
                    return True
            else:
                valid_username = False
    return False


def self_terminate(confirm):
    """Deletes FiEncrypt"""
    if confirm:
        enter_home_directory()
        os.remove(sys.argv[0])
        shutil.rmtree(f"../FiEncrypt")


def get_own_ip(print_logs, private_mode):
    """Returns the IP address of the first functional interface"""
    if "linux" in pass_os():
        # ?Linux's @netifaces is considerably more complicated, and the first interface with an IP is used, which may be problematic
        your_ip = gnu_ip_resolve(print_logs, private_mode)
        # *You can enter your IP in manually if one is not found
        if your_ip == "":
            your_ip = privacy_input(
                "Enter your IP in dotted decimal format", private_mode)
    elif "win32" in pass_os():
        your_ip = socket.gethostbyname(socket.gethostname())
    return your_ip


def arp_scan(ip):
    """Sends out ARP requests to the broadcast address of the local network, to gather MAC and IP address pairs for resolving the IP address of a contact"""
    try:
        # ?ff MAC address is the standard broadcast address for the router
        # ?The / between Ether and ARP joins both in their relative state(s)
        request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        # ?Verbose set to 0 to prevent the .* output during ARP scan (does not work on windows!)
        if pass_os() != "win32":
            ans, unans = srp(request, timeout=.5, retry=0, verbose=0)
        else:
            return None
        result = []
        for sent, received in ans:
            # ?Using dictionaries allows the check in @mac_resolve() function to search by 'IP' or 'MAC'
            result.append({'IP': received.psrc, 'MAC': received.hwsrc})
        return result
    except KeyboardInterrupt:
        return None


def mac_resolve(mac, print_logs):
    """Checks for a desired MAC address from an ARP scan of the /16 network"""
    IP = get_own_ip(print_logs, False)
    IP = IP.split(".")
    # ?Runs with a /16 subnet as few networks have larger host portions than that. Can be changed
    submask = "/16"
    scan_ip = f"{IP[0]}.{IP[1]}.0.0{submask}"
    print("")
    if "/" in scan_ip:
        IP_str = scan_ip.split(".")
        IP_str[3] = IP_str[3].replace("/16", "")
        # ?Due to memory restrictions with running arp_scan on /16 or larger network, this loop checks each band and only continues if no results are found
        for i in range(254):
            result = arp_scan(
                f"{IP_str[0]}.{IP_str[1]}.{i}.0/24")
            for mapping in result:
                # ?Strips both results to avoid rampant fucking spaces from affecting the comparison query lol
                if mac == None:
                    return None
                elif mac.strip() in str(mapping['MAC']).strip():
                    return str(format(mapping['IP']))
        if result == None:
            return None
    #!Not allowed to trigger, as MAC resolution is only needed when the IP is not known
    else:
        result = arp_scan(scan_ip)
        for mapping in result:
            if print_logs:
                print(mapping)
            if mac.strip() in str(mapping['MAC']).strip():
                return str(format(mapping['IP']))
    return None


def is_private():
    """Returns 1 or 0 based on whether private mode is enabled, effectively hiding any input under privacy_input() module"""
    enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code = retrieve_config_settings()
    if private_mode:
        return 1
    else:
        return 0


def get_current_user(**new_user):
    """Collects the name of the FiEncrypt user account that is currently logged in and saves it to a global variable"""
    global current_user
    try:
        old_user = current_user
    except:
        pass
    current_user = new_user.get('new_user', None)
    if current_user == None:
        try:
            current_user = old_user
        except UnboundLocalError:
            current_user = None
    return current_user


def get_foreign_user(**new_user):
    """Collects the name of the FiEncrypt user account you are currently communicating with over the network and saves it to a global variable"""
    global foreign_user
    try:
        old_foreign_user = foreign_user
    except:
        pass
    foreign_user = new_user.get('new_user', None)
    if foreign_user == None:
        try:
            foreign_user = old_foreign_user.replace("\n", "")
        except UnboundLocalError:
            foreign_user = None
        except AttributeError:
            foreign_user = None
        return foreign_user
    else:
        return foreign_user.replace("\n", "")


def privacy_input(string, state, **line_break):
    """Custom input function that employs the getpass module to hide user input based on the state paramter"""
    line_break = line_break.get("line_break", None)
    try:
        if state == 1 or "true" in str(state).lower():
            if line_break:
                temp = getpass.getpass(f"{string}: \n")
            else:
                temp = getpass.getpass(f"{string}: ")
        else:
            if line_break:
                temp = input(f"{string}: \n")
            else:
                temp = input(f"{string}: ")
        if temp == None or temp == "EXIT":
            return None
        else:
            return temp.strip()
    except KeyboardInterrupt:
        print("")
        maybe_quit()
        return None
    except UnboundLocalError:
        privacy_input(string, state)


def contact_input(string):
    """Automatic check from the Contacts class for the name passed as input"""
    name = input(f"{string}: ")
    if "." not in name:
        return Contacts().check_for(name)
    else:
        return name


def retrieve_config_settings():
    """Saves all relevant settings from the config file to a series of variables that are all returned"""
    with open(f"./config.txt", "r+") as config_file:
        config_lines = config_file.readlines()
        print_logs = config_lines[2].split(" = ")
        print_logs = print_logs[1]
        if "true" in print_logs.lower():
            print_logs = True
        else:
            print_logs = False
        display_initiate = config_lines[3].split(" = ")
        display_initiate = display_initiate[1]
        if "true" in display_initiate.lower():
            display_initiate = True
        else:
            display_initiate = False
        graphic_mode = config_lines[8].split(" = ")
        graphic_mode = graphic_mode[1]
        if "true" in graphic_mode.lower():
            graphic_mode = True
        else:
            graphic_mode = False
        private_mode = config_lines[9].split(" = ")
        private_mode = private_mode[1]
        if "true" in private_mode.lower():
            private_mode = True
        else:
            private_mode = False
        colour_enabled = config_lines[6].split(" = ")
        try:
            colour_enabled = colour_enabled[1]
            if "true" in colour_enabled.lower():
                colour_enabled = True
                default_colour = config_lines[5].split(" = ")
                default_colour = default_colour[1]
            else:
                colour_enabled = False
        except IndexError:
            colour_enabled = False
            default_colour = None
        auto_code = config_lines[10].split(" = ")
        auto_code = auto_code[1]
        if "true" in auto_code.lower():
            auto_code = True
        else:
            auto_code = False
        return print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code


def log(string, log_type, user, display):
    """Records events in the log file based on paramters passed, also printing them to screen when display paramter is True"""
    username = capitalize_user(get_current_user())
    if username == None:
        username = "Undefined"
    log_entry = f"{datetime.datetime.now()}: {log_type} - {string}, Username: {username}"
    if display:
        animated_print(log_entry)
    enter_home_directory()
    try:
        with open(f"./logs.txt", "r+") as log_file:
            logs = log_file.readlines()
            log_file.write(f"{log_entry}\n")
    except FileNotFoundError:
        establish_tree()


def get_poked(foreign_user, **poke_num):
    """Pokes the user with majestic ASCII art"""
    pokes = poke_num.get('poke_num', 1)
    line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13, line14, line15, line16 = "                                     _______________________", "                                    /                       \\", "                                    \__________              \\", " ______________________________________________|              \\", "/                                                              \\", "\________________________                                       \\", "           ______________/                                       \\", "          /                                                      |", "          \______________                                        |", "           ______________/                                       |", "          /                                                      |", "          \______________                                        |", "           _____________/                             ___________|", "          /                                         /", "          \_____________                           /", "                        \_________________________/"
    if pokes > 10:
        pokes = 10
    for poke in range(pokes):
        for i in range(10):
            print(f"{' '  * (10 - i)}{line1}")
            print(f"{' ' * (10 - i)}{line2}")
            print(f"{' ' * (10 - i)}{line3}")
            print(f"{' ' * (10 - i)}{line4}")
            if 10 - i == 1:
                print(f"\\{line5}")
                print(f"/{line6}")
            else:
                print(f"{' ' * (10 - i)}{line5}")
                print(f"{' ' * (10 - i)}{line6}")
            print(f"{' ' * (10 - i)}{line7}")
            print(f"{' ' * (10 - i)}{line8}")
            print(f"{' ' * (10 - i)}{line9}")
            print(f"{' ' * (10 - i)}{line10}")
            print(f"{' ' * (10 - i)}{line11}")
            print(f"{' ' * (10 - i)}{line12}")
            print(f"{' ' * (10 - i)}{line13}")
            print(f"{' ' * (10 - i)}{line14}")
            print(f"{' ' * (10 - i)}{line15}")
            print(f"{' ' * (10 - i)}{line16}")
            time.sleep(0.05)
            if 10 - i <= 1 and poke == (pokes - 1):
                pass
            else:
                for i in range(16):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
        time.sleep(0.5)
    if capitalize_user(get_current_user()).strip().lower() == foreign_user.strip().lower():
        animated_print(
            f"You have poked yourself... Don't you think that is a little weird?")
    else:
        animated_print(f"Hey {capitalize_user(get_current_user())}...")
        if pokes > 1:
            animated_print(
                f"{foreign_user.capitalize()} has poked you {pokes} times!")
        else:
            animated_print(f"{foreign_user.capitalize()} has poked you!")


def you_are_loved(foreign_user, **hearts):
    """Prints out hearts for the user, when someone is willing to share them around..."""
    hearts = hearts.get("hearts", 1)
    if foreign_user == None:
        foreign_user = "Anonymous"
    line1, line2, line3, line4, line5, line6, line7, line8 = "  ____      ____       ", " /    \____/    \\      ", "|                |     ", "|                |     ", " \              /      ", "   \          /        ", "     \      /          ", "       \__/            "
    if hearts >= 5:
        heart_range = 5
    else:
        heart_range = hearts + 1
    for heart in range(heart_range):
        print(f"\033[35m{line1 * heart}")
        print(f"{line2 * heart}")
        print(f"{line3 * heart}")
        print(f"{line4 * heart}")
        print(f"{line5 * heart}")
        print(f"{line6 * heart}")
        print(f"{line7 * heart}")
        print(f"{line8 * heart}\033[0m")
        time.sleep(0.2)
        if heart_range - heart <= 1:
            pass
        else:
            for j in range(8):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
        time.sleep(0.5)
    if capitalize_user(get_current_user()).strip().lower() == foreign_user.strip().lower():
        animated_print(
            f"Congratulations! You have fallen in love with yourself!")
    else:
        if hearts > 1:
            if hearts == 2:
                animated_print(f"No... those are not boobs! I swear...")
            animated_print(
                f"{foreign_user.capitalize()} loves you {hearts} times over!")
        else:
            animated_print(
                f"{foreign_user.capitalize()} loves you {capitalize_user(get_current_user())}!")


def thumbs(foreign_user, up):
    """Good or bad? You can let the user know!"""
    if foreign_user == None:
        foreign_user = "Anonymous"
    if up:
        # print thumbs up
        lines = ["             _______", "            /       \\", "           /        |", "          |         |", "         /         /", "        /         /____________", " ______/                       \\", "/      |                       /",
                 "|      |                       \\", "|      |                       /", "|      |                       \\", "|      |                       /", "\______|_______                \\", "               \_______________/"]
        for line in lines:
            print(line)
    else:
        # print thumbs down
        lines = ["         ______              __________", "        /      \____________/          \\", "        |       |                      /", "        |       |                      \\", "        |       |                      /", "        |       |                      \\", "        |       |                      /",
                 "        |_______|                      \\", "                \         _____________/", "                 \        \\", "                  \        \\", "                   |        \\", "                   |        |", "                   \        |", "                    \______/"]
        for line in lines:
            print(line)


def capitalize_user(user):
    temp = ""
    if user != None and user.strip() != "":
        for word in user.split():
            temp += f"{word.strip().capitalize()} "
        return temp.strip()
    else:
        return "Anonymous"


def check_secret_code(code):
    """Checks secret code entered by the user against a number of preset codes, dictating which secret function should be executed"""
    accepted_codes = [["c", "E"], ['J', '\x1d', '?', '2', 'G'], ['H', '%']]
    for length, accepted_code in enumerate(accepted_codes):
        if code == accepted_code:
            if length == 0:
                code_func = 1
            elif length == 1:
                code_func = 2
            elif length == 2:
                code_func = 3
            return True, code_func
        else:
            pass
    return False, 0


def create_notification(ip, name):
    """Uses the plyer module to generate a notification for the user, when they recieve a new message"""
    if name == None or name.strip() == "":
        name = "Anonymous"
    enter_home_directory()
    if pass_os() == "win32":
        src = f"./anarchy2.ico"
    elif pass_os() == "linux":
        src = f"./anarchy.png"
    with open(f"./inbox.txt", "r+") as mailbox:
        letters = mailbox.readlines()
    if int(len(letters)) / 2 == 0:
        notification.notify(
            title='New Message!',
            message=f'{name}@{ip} has sent you a message!',
            app_name='FiEncrypt',
            app_icon=src,
            timeout=50
        )
    else:
        notification.notify(
            title='New Message!',
            message=f'You have {int(int(len(letters)) / 2 + 1)} new messages!',
            app_name='FiEncrypt',
            app_icon=src,
            timeout=50
        )


def get_recipient_ip(user, display_initiate, print_logs, default_colour, private_mode, error_colour):
    """Obtains the desired IP, MAC, or contact name that a message is to be sent to. Calls arp_scan() and mac_resolve() modules as appropiate"""
    target_mac, target_name = None, None
    ip = privacy_input(
        "Enter the IP, MAC address or contact name of the recipient", private_mode)
    if ip == None:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif "@" in ip:
        ip = ip.split("@")
        expected_user = ip[0].strip()
        ip = ip[1].strip()
        if "." not in ip:
            target_name, target_mac, target_ip, details = Contacts.check_for(
                ip)
            target_name = target_name.replace("\n", "")
            if target_ip != None:
                ip = target_ip
            else:
                ip = mac_resolve(target_mac, print_logs)
            if ip == None:
                animated_print(
                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                Colours(default_colour)
                connected = False
            else:
                Contacts.add_ip(target_name, ip)
        validated = validate_foreign_user(ip, expected_user)
        if not validated:
            animated_print(
                f"{error_colour}WARNING: Unable to verify if recipient is {expected_user}!")
            Colours(default_colour)
            proceed = privacy_input(
                f"Do you wish to proceed anyway? [Y|N]", private_mode)
            if "y" in proceed.lower():
                pass
            else:
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour)
        time.sleep(8)
    if "." not in ip:
        if ":" in ip:
            temp = ip
            target_name, target_mac, target_ip, details = Contacts.check_for(
                temp)
            target_name = target_name.replace("\n", "")
            if target_ip != None:
                ip = target_ip
            else:
                ip = mac_resolve(target_mac, print_logs)
            if ip == None:
                animated_print(
                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                Colours(default_colour)
                connected = False
            else:
                Contacts.add_ip(target_name, ip)
        else:
            try:
                target_name, mac, target_ip, details = Contacts.check_for(
                    ip)
                target_name = target_name.replace("\n", "")
                if mac.strip() == "":
                    animated_print(
                        f"{error_colour}WARNING: MAC address for contact is blank!")
                    Colours(default_colour)
                    connected = False
                else:
                    target_mac = mac
                    if target_ip != None:
                        ip = target_ip
                    else:
                        ip = mac_resolve(target_mac, print_logs)
                    if ip == None:
                        animated_print(
                            f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                        Colours(default_colour)
                        connected = False
                    else:
                        Contacts.add_ip(target_name, ip)
            except ValueError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact name entered!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour)
            except TypeError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact details!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour)
            except AttributeError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact details!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour)
    valid_vars = check_vars(ip, target_mac, target_name)
    return valid_vars[0], valid_vars[1], valid_vars[2]


def gnu_ip_resolve(print_logs, private_mode):
    print("")
    interfaces = netifaces.interfaces()
    if print_logs:
        for i, interface in enumerate(interfaces):
            print(f"{i}. {interface}")
        chosen_interface = privacy_input("Select one of these", private_mode)
        try:
            chosen_interface = interfaces[int(chosen_interface)]
        except:
            pass
        if chosen_interface == None:
            ip = None
        else:
            ip = str(netifaces.ifaddresses(chosen_interface)[netifaces.AF_INET])
            ip = ip.split()
            ip = ip[1].replace("'", "").replace(",", "")
    else:
        for i in interfaces:
            try:
                ip = str(netifaces.ifaddresses(i)[netifaces.AF_INET])
                ip = ip.split()
                ip = ip[1].replace("'", "").replace(",", "")
            except:
                pass
    return ip


def secretcode(user, current_user, default_colour, print_logs, private_mode, error_colour):
    enter_home_directory()
    secret_code = privacy_input(f"Enter the secret code here", private_mode)
    if secret_code == None:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    completed_code = []
    try:
        if ((int(len(secret_code)) % 2) / 2) != 0:
            animated_print(
                f"{error_colour}WARNING: Code format not valid!")
            Colours(default_colour)
            log("Secret Code Entered! Valid? False",
                "sec_code", user, print_logs)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                       print_logs, private_mode, error_colour)
        else:
            pass
    except ValueError:
        animated_print(
            f"{error_colour}WARNING: Code format not valid!")
        Colours(default_colour)
        log("Secret Code Entered! Valid? False",
            "sec_code", user, print_logs)
        secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                   print_logs, private_mode, error_colour)
    temp = 0
    for i in range(0, len(secret_code), 2):
        temp = secret_code[i:i+2]
        completed_code.append(chr(int(temp)))
    valid, func = check_secret_code(completed_code)
    if not valid:
        animated_print(
            f"{error_colour}WARNING: Incorrect secret code entered!")
        Colours(default_colour)
        log("Secret Code Entered! Valid? False",
            "sec_code", user, print_logs)
        secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                   print_logs, private_mode, error_colour)
    else:
        log("Secret Code Entered! Valid? True",
            "sec_code", user, print_logs)
    if func == 1:
        animated_print("Config editor mode entered! Standby...")
        config_file = open(f"./config.txt", "r+")
        config_data = config_file.read()
        config_lines = config_data.split("\n")
        animated_print("Dumping current config file...")
        lines = []
        for line, content in enumerate(config_lines):
            animated_print(f"{line}. {content}")
            lines.append(content)
        try:
            edit_mode = privacy_input(
                "Would you like to enter overwrite mode (1) or edit mode (2)", 0)
        except ValueError:
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        if edit_mode == 3:
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                       print_logs, private_mode, error_colour)
        config_file.close()
        os.remove(f"./config.txt")
        config_file = open("./config.txt", "w+")
        if edit_mode == 1:
            animated_print(
                f"{error_colour}WARNING: Writing a custom config file can cause the program to break. Delete the FiEncrypt folder if you have any issues! Good Luck!")
            Colours(default_colour)
            new_code = privacy_input(
                "Enter a semi-colon (;) in order for a line break (spaces are NOT necessary)", 0)
            new_code = new_code.split(";")
            if len(new_code) != len(config_lines):
                animated_print(
                    f"{error_colour}WARNING: Number of lines differs from the expected value!")
                Colours(default_colour)
                proceed = input("Do you wish to proceed? (Y/N): ")
                if "y" in proceed.lower():
                    for line in new_code:
                        line = f"{line}\n"
                        config_file.write(line)
                    config_file.close()
                    time.sleep(1)
                    menu(user, None, print_logs, default_colour,
                         private_mode, error_colour, print_speed=0)
                else:
                    secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                               print_logs, private_mode, error_colour)
        elif edit_mode == 2:
            lines[2] = lines[2].split(" = ")
            print(f"Line 2: {lines[2][0]} = ", end="")
            lines[2] = f"{lines[2][0]} = {input('')}"
            lines[3] = lines[3].split(" = ")
            print(f"Line 3: {lines[3][0]} = ", end="")
            lines[3] = f"{lines[3][0]} = {input('')}"
            if "-" not in lines[4]:
                lines[4] = lines[4].split(" = ")
                print(f"Line 4: {lines[4][0]} =", end="")
                lines[4] = f"{lines[4][0]} = {input('')}"
            if "-" not in lines[5]:
                lines[5] = lines[5].split(" = ")
                print(f"Line 5: {lines[5][0]} =", end="")
                lines[5] = f"{lines[5][0]} = {input('')}"
            if "-" not in lines[6]:
                lines[6] = lines[6].split(" = ")
                print(f"Line 6: {lines[6][0]} =", end="")
                lines[6] = f"{lines[6][0]} = {input('')}"
            if "-" not in lines[7]:
                lines[7] = lines[7].split(" = ")
                print(f"Line 7: {lines[7][0]} =", end="")
                lines[7] = f"{lines[7][0]} = {input('')}"
            if "-" not in lines[8]:
                lines[8] = lines[8].split(" = ")
                print(f"Line 8: {lines[8][0]} =", end="")
                lines[8] = f"{lines[8][0]} = {input('')}"
            if "-" not in lines[9]:
                lines[9] = lines[9].split(" = ")
                print(f"Line 9: {lines[9][0]} =", end="")
                lines[9] = f"{lines[9][0]} = {input('')}"
            for line in lines:
                line = f"{line}\n"
                config_file.write(line)
            config_file.close()
            time.sleep(1)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        else:
            animated_print(
                f"{error_colour}WARNING: Invalid mode selection!")
            Colours(default_colour)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                       print_logs, private_mode, error_colour)
    elif func == 2:
        animated_print(
            f"Breadfish Time!")
        line1 = "                         ______________________________________"
        line2 = "                        /                                      \\"
        line3 = "|\\                      \\                                      /"
        line4 = "| \\        _             |                                    |"
        line5 = "\\  \\      | \\            |                                    |"
        line6 = " \\  \\      \\ \\           |                                    |_______"
        line7 = "  \\  \\  ____\\ \\_________/                                             \\"
        line8 = "  |___\\/                                                        ()     \\"
        line9 = "  /                                                                     \\"
        line10 = "  \\___                                                            _____ /"
        line11 = "  |   /\\                                                          |____/"
        line12 = "  /  /  \\___                                                          /"
        line13 = " /  /       \\__     _____                                     _______/"
        line14 = "/  /          /____/    |                                    |"
        line15 = "| /                     |                                    |"
        line16 = "|/                      |                                    |"
        line17 = "                        |____________________________________|"
        line_breaks = 0
        for j in range(3):
            for i in range(30):
                if i < 5:
                    line_breaks += 1
                elif i >= 5 and i < 10:
                    line_breaks -= 1
                elif i >= 10 and i < 15:
                    line_breaks += 1
                elif i >= 15 and i < 20:
                    line_breaks -= 1
                elif i >= 20 and i < 25:
                    line_breaks += 1
                elif i >= 25 and i < 30:
                    line_breaks -= 1
                elif i >= 30 and i < 35:
                    line_breaks += 1
                elif i >= 35 and i < 40:
                    line_breaks -= 1
                elif i >= 40 and i < 45:
                    line_breaks += 1
                elif i >= 45 and i < 50:
                    line_breaks -= 1
                print(line_breaks * '\n')
                print(f"{i * ' '}{line1}")
                print(f"{i * ' '}{line2}")
                print(f"{i * '-'}{line3}")
                print(f"{i * ' '}{line4}")
                print(f"{i * ' '}{line5}")
                print(f"{i * ' '}{line6}")
                print(f"{i * '-'}{line7}")
                print(f"{i * ' '}{line8}")
                print(f"{i * ' '}{line9}")
                print(f"{i * ' '}{line10}")
                print(f"{i * ' '}{line11}")
                print(f"{i * '-'}{line12}")
                print(f"{i * ' '}{line13}")
                print(f"{i * ' '}{line14}")
                print(f"{i * '-'}{line15}")
                print(f"{i * ' '}{line16}")
                print(f"{i * ' '}{line17}")
                for k in range(18 + line_breaks):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
                time.sleep(0.1)
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif func == 3:
        enter_home_directory()
        try:
            os.mkdir(f"./RamRanch")
        except FileExistsError:
            pass
        try:
            os.mkdir(f"./SetVol")
        except FileExistsError:
            pass
        if os.path.exists(f"./SetVol/SetVol.exe"):
            pass
        else:
            urllib.request.urlretrieve(
                "https://6ec1f0a2f74d4d0c2019-591364a760543a57f40bab2c37672676.ssl.cf5.rackcdn.com/SetVol.zip", f"./SetVol/SetVol.zip")
            setvol_zip = zipfile.ZipFile(f'./SetVol/SetVol.zip')
            setvol_zip.extractall(f'./SetVol')
            setvol_zip.close()
            os.remove(f"c:/SetVol/SetVol.zip")
        if os.path.exists(f"./RamRanch/ramranch.mp3"):
            pass
        else:
            urllib.request.urlretrieve(
                "https://archive.org/download/ramranch/Ram%20Ranch.mp3", f"./RamRanch/ramranch.mp3")
            animated_print(f"Download complete! Yeehaw!")
        os.system(f'cmd /c "cd c:/SetVol & start ./SetVol & SetVol 100 unmute & start "" "C:\Program Files\Windows Media Player\wmplayer.exe" "c:/RamRanch/ramranch.mp3"')
        ctypes.windll.user32.LockWorkStation()
    elif func == 4:
        animated_print(f"Enabling graphic mode...")
        if(sys.platform.startswith("win32")):
            os.chdir(f"c:/Users/{user}/FiEncrypt")
        elif(sys.platform.startswith("linux")):
            os.chdir(f"/home/{user}/FiEncrypt")
        config_file = open(f"./config.txt", "r+")
        config_data = config_file.read()
        config_lines = config_data.split("\n")
        config_lines[8] = f"graphic_mode = True"
        for line in config_lines:
            if line != "" or " " or "-":
                line = f"{line}\n"
            config_file.write(line)
        config_file.close()
        animated_print("Done!")


def showcode(user, current_user, private_mode, print_logs, error_colour, default_colour):
    enter_home_directory()
    if sys.platform.startswith("win32"):
        log(f"New Directory: {str(os.getcwd())} OS: Windows",
            "cwdchange", user, print_logs)
    else:
        log(f"New Directory: {str(os.getcwd())} OS: Linux",
            "cwdchange", user, print_logs)
    with open(f"./code.txt", "r+") as temp_file:
        code = temp_file.read()
    if current_user != 1 and current_user != 2:
        animated_print(
            f"This is the current code saved in the code.txt file:")
        if(code == ""):
            animated_print(
                f"{error_colour}WARNING: No code present in the code.txt file! Either it has not been generated or manually overwritten!")
            Colours(default_colour)
        else:
            animated_print(code)
        log(f"Code: {str(code)}", "exicode", user, print_logs)
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif(current_user == 2):
        pass
    else:
        try:
            code = code.split("_")
            timestamp, prefix, code = code[0], code[2], code[1]
            return code, prefix, timestamp
        # TODO: Find a way to bypass the associated errors with not having a code saved in the file
        except:
            animated_print(
                f"{error_colour}WARNING! The latest version of this program requires a encryption code to be generated before any other function can run!")
            Colours(default_colour)
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour)


def even_num():
    num2 = 1
    while (num2 % 2) / 2 != 0:
        num1 = random.randint(4, 100)
        num2 = random.randint(2, int(num1))
    return num2


def random_filler(length, string):
    output, alphabet, number, symbols, new_string = "", ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                                                         "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"], [1, 2, 3, 4, 5, 6, 7, 8, 9], ["!", "@", "#", "$", "%", "^", "&", "*",
                                                                                                                                                              "(", ")", "-", "=", "+", "{", "}", "[", "]", ";", ":", "'", "\"", ",", ".", "<", ">", "/", "?"], ""
    for i in range(int(length)):
        type_select = random.choice(["alphabet", "number", "symbols"])
        if type_select == "alphabet":
            output += random.choice(alphabet)
        elif type_select == "number":
            output += random.choice(str(number))
        else:
            output += random.choice(symbols)
    if "fE" in output or "||" in output:
        random_filler(length, string)
    else:
        for i in range(0, int(len(output)/2)):
            new_string += output[i]
        new_string += string
        for j in range(int(len(output)/2), int(len(output))):
            new_string += output[j]
        return new_string


def decrypt_filler(length, string):
    new_string = ""
    for k, char in enumerate(string):
        if k in range(0, int(int(length)/2)):
            pass
        else:
            new_string += char
    new_string = new_string[:int(f"-{int(int(length)/2)}")]
    return new_string


def randomcode(user, current_user, auto_request, private_mode, print_logs, default_colour, error_colour, **auto_code):
    auto_code = auto_code.get("auto_code", None)
    if auto_code == None:
        auto_code = False
    elif auto_code or "t" in str(auto_code).lower():
        auto_code = True
    else:
        auto_code = False
    timer = str(datetime.datetime.now())
    timer = timer.split("-")
    length = 1
    while (length % 2) / 2 != 0:
        length = random.randint(6, 20)
        code = ""
    for i in range(0, length):
        num = random.randint(0, 10)
        code += str(num)
    try:
        # ?New logic for encryption code compilation
        # *Creating scripts that were as dynamic as possible was my goal, as such very few static numbers were used
        b = f"{random.randint(0,len(code)/2)}{random.randint(len(code)/2,len(code))}fE{random.randint(0,len(code)/2)}{random.randint(len(code)/2,len(code))}||{random.randrange(2,(94-int(timer[2][6:8])),2)}"
        val = b.split("||")
        val = int(val[1])
        hrs = int(str(timer[2][3:5])) + int(val)
        mns = int(str(timer[2][6:8])) + int(val)
        new_time = str(hrs)[::-1]
        new_time += "A"
        new_time += str(mns)[::-1]
        a = f"{new_time}|{(int(timer[2][0:2]))}{(int(timer[1]))}"
        rand_code = int(code)
    # ?Will call the module from the start if any step above returns an error
    except ValueError:
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_colour, error_colour, auto_code=auto_code)
    if not auto_request:
        lazy = privacy_input(
            f"Would you like to have a UUID code generated for you? (Y/N)", 0)
    else:
        lazy = "y"
    if lazy == None:
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_colour, error_colour, auto_code=auto_code)
    elif "y" in lazy.lower() and not auto_code:
        temp_string = str(f"Current code as of "+str(datetime.datetime.now()
                                                     )+" is $"+str(a)+"_"+str(rand_code)+"_$"+b+"#")
        animated_print(temp_string)
    elif "y" in lazy.lower():
        pass
    else:
        try:
            # ?The user can input a code of their own, which will be combined with the prefix and timestamp that were automatically generated
            rand_code = privacy_input(
                f"Enter the code you wish to set (or leave this blank to leave code empty)", private_mode)
            if rand_code == None or rand_code.strip() == "":
                animated_print("No code entered!")
                randomcode(user, current_user, auto_request, private_mode,
                           print_logs, default_colour, error_colour, auto_code=auto_code)
        except ValueError:
            animated_print(
                f"{error_colour}WARNING: With no code saved locally, auto-generated key functions will not work! {Colours(default_colour)}")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    try:
        new_string = f"${str(a)}_{str(rand_code)}_${str(b)}#"
        if lazy == None:
            randomcode(user, current_user, auto_request, private_mode,
                       print_logs, default_colour, error_colour, auto_code=auto_code)
        if "y" in lazy.lower():
            if sys.platform.startswith("win32"):
                log(f"New Directory: {str(os.getcwd())} OS: Windows",
                    "cwdchange", user, print_logs)
            else:
                log(f"New Directory: {str(os.getcwd())} OS: Linux",
                    "cwdchange", user, print_logs)
        else:
            animated_print(str(
                f"Current code as of {str(datetime.datetime.now())} is ${str(a)}_{str(rand_code)}_${b}#"))
        enter_home_directory()
        with open("./code.txt", "w+") as code_file:
            code_file.seek(0)
            code_file.truncate()
            code_file.write(new_string)
        log(f"New File: {str(code_file)} Type: Text File Access: Read & Write",
            "newfile", user, print_logs)
        log(f"Success?: Y. New Code: {str(new_string)}. Files updated: 1",
            "newcode", user, print_logs)
        enter_home_directory()
        hide_tree()
        if not auto_code:
            animated_print(f"New code successfully written to code.txt file")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        else:
            pass
    except UnboundLocalError:
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_colour, error_colour, auto_code=auto_code)


def newmessage(code, user, recipient_ip, link, prefix, date, talking_to_self, error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, auto_code, **poked):
    previous_message, poked = poked.get("message", ""), poked.get("poked", False)
    manual = False
    enter_home_directory()
    os.remove("./messageout.txt")
    with open("./messageout.txt", "w+") as message_file:
        pass
    with open("./config.txt", "r+") as config_file:
        config_lines = config_file.readlines()
        if "true" in config_lines[7].lower():
            conversation_mode = True
        else:
            conversation_mode = False
            recipient_ip = ""
    try:
        code2 = code
    except:
        code2 = ""
    try:
        recipient_ip = recipient_ip
    except:
        recipient_ip = ""
    if recipient_ip == "" or code2 == "":
        #!Currently not functioning for extended encryption codes!
        code2 = privacy_input(
            f"Enter the encryption code for the message here! Or, leave it blank for the auto-generated key", private_mode)
        if code2 == "EXIT" or code2 == None:
            Colours(default_colour)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        if code2 == "":
            if code != "":
                code2 = code
            else:
                animated_print(
                    f"{error_colour}WARNING: Unable to retrieve auto-generated key! Make sure the key is in the code.txt file")
                Colours(default_colour)
            manual = False
        else:
            manual = True
    backup_code = code2
    poke = False
    love_sent = False
    if len(code2) == 4:
        code3 = f"{int(code2[0:2])}{int(code2[2:4])}"
        code2 = code3
    elif len(code2) == 2:
        code2 = int(code2)
    else:
        # ?You may see warnings about prefix not being defined, don't worry, it always is before this gets run
        backup_prefix = prefix
        try:
            prefix = prefix.split("fE")
        except:
            pass
        try:
            filler_length = prefix[1].split("||")
            filler_length = filler_length[1].replace("#", "")
            prefix[1] = prefix[1].split("||")
        except:
            filler_length = 0
        try:
            prefix[0] = prefix[0].replace("$", "")
        except:
            pass
        timer = str(datetime.datetime.now())
        timer = timer.split("-")
        hrs = int(str(timer[2][3:5])) + int(prefix[1][1].replace("#", ""))
        mns = int(str(timer[2][6:8])) + int(prefix[1][1].replace("#", ""))
        new_time = str(hrs)
        new_time += "A"
        new_time += str(mns)
        date = f"{int(timer[1])}{int(timer[2][0:2])}"
        timestamp = f"${new_time}|{date}"
        # ?You may notice some scripts are better run than others, that's because this program really grew with my knowledge, and I'm too lazy to refine everything
        enter_home_directory()
        if not auto_code:
            with open(f"./code.txt", "r+") as update_file:
                update_code = update_file.read()
                update_file.seek(0)
                update_file.truncate()
                old_code = update_code.split("_")
                old_code = old_code[0]
                new_code = update_code.replace(old_code, timestamp)
                update_file.write(new_code)
        try:
            if len(prefix[0]) == 2:
                code_seg1 = code2[int(prefix[0][0]):int(prefix[0][1])]
            elif len(prefix[0]) == 3:
                code_seg1 = code2[int(prefix[0][0]):int(prefix[0][1:3])]
            elif len(prefix[0]) == 4:
                code_seg1 = code2[int(prefix[0][0:2]):int(prefix[0][1:3])]
            code_seg1 = list(code_seg1)
            code_seg1 = sum(map(int, code_seg1))
            if len(prefix[1][0]) == 2:
                code_seg2 = code2[int(prefix[1][0][0]):int(prefix[1][0][1])]
            elif len(prefix[1][0]) == 3:
                code_seg2 = code2[int(prefix[1][0][0]):int(prefix[1][0][1:3])]
            elif len(prefix[1][0]) == 4:
                code_seg2 = code2[int(prefix[1][0][0:2]):int(prefix[1][0][1:3])]
            code_seg2 = list(code_seg2)
            code_seg2 = sum(map(int, code_seg2))
            code3 = code2
            Colours(default_colour, force=True)
        except:
            code_seg1 = str(code_seg1)[::-1]
            temp = code_seg2
            code_seg2 = int(code_seg1)
            code_seg1 = temp
            Colours(default_colour)
    if conversation_mode and recipient_ip != "" and poked:
        try:
            message_text = privacy_input(
                f"How do you feel", private_mode, line_break=True)
            if message_text == None:
                Colours(default_colour)
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            while message_text.strip() == "" or message_text.strip() == " ":
                animated_print(
                    f"{error_colour}WARNING: No message was entered!")
                Colours(default_colour)
                message_text = privacy_input(
                    f"Enter a reply here", private_mode)
            if message_text == None:
                try:
                    link = socket.socket()
                    link.connect((recipient_ip, 15753))
                    link.send(str("\\exit").encode())
                    try:
                        link.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    link.close()
                except:
                    pass
                newmessage(code, user, "", link, prefix, date, talking_to_self,
                           error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, message=previous_message)
        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                link = socket.socket()
                link.connect((recipient_ip, 15753))
                link.send(str("\\exit").encode())
                try:
                    link.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                link.close()
            except:
                pass
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip != "":
        try:
            message_text = privacy_input(
                f"Enter a reply here", private_mode, line_break=True)
            if message_text == None:
                Colours(default_colour)
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            while message_text.strip() == "" or message_text.strip() == " ":
                animated_print(
                    f"{error_colour}WARNING: No message was entered!")
                Colours(default_colour)
                message_text = privacy_input(
                    f"Enter a reply here", private_mode)
            if message_text == None:
                try:
                    link = socket.socket()
                    link.connect((recipient_ip, 15753))
                    link.send(str("\\exit").encode())
                    try:
                        link.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    link.close()
                except:
                    pass
                newmessage(code, user, "", link, prefix, date, talking_to_self,
                           error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, message=previous_message)
        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                link = socket.socket()
                link.connect((recipient_ip, 15753))
                link.send(str("\\exit").encode())
                try:
                    link.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                link.close()
            except:
                pass
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    else:
        message_text = privacy_input(
            f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colours(default_colour)
            menu(user, display_initiate, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        while message_text.strip() == "" or message_text.strip() == " ":
            animated_print(
                f"{error_colour}WARNING: No message was entered!")
            Colours(default_colour)
            message_text = privacy_input(
                f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colours(default_colour)
            animated_print(f"Returning to menu...")
            menu(user, display_initiate, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    if message_text.strip() == "\\exit" and recipient_ip != "":
        skip = True
        mailbox = False
    else:
        skip = False
    if message_text.count("\"\"") >= 2:
        temp_message_text = message_text.split("\"\"")
        if message_text.count("\"\"") == 2:
            if temp_message_text[1].replace("\"\"", "") in previous_message:
                message_text = f"YOU ({get_foreign_user().capitalize()}): {temp_message_text[1].strip()} -> {temp_message_text[0].strip()} {temp_message_text[2].strip()}"
        else:
            message_text = f"{temp_message_text[0].strip()}"
            for i in range(2, len(temp_message_text), 2):
                message_text += f"YOU ({get_foreign_user().capitalize()}): {temp_message_text[i-1].strip()} -> {temp_message_text[i].strip()}"
    if not skip:
        decrypted_message = []
        decrypted_current_user = []
        passs2 = 0
        passs = 0
        output_phrase = ''
        encrypted_current_user = ''
        for i, k in enumerate(message_text):
            if i < len(message_text) / 2 and len(str(code3)) >= 4:
                if len(str(code3)) > 4:
                    code2 = code_seg1
                else:
                    code3 = str(code2)[0:2]
                    code2 = int(code3)
            elif len(str(code3)) >= 4:
                if len(str(code3)) > 4:
                    code2 = code_seg2
                else:
                    code3 = str(code2)[2:4]
                    code2 = int(code3)
            decrypted_message.append(k)
            decrypted_message[passs] = ord(k)
            decrypted_message[passs] = int(
                decrypted_message[passs]) + int(code2)
            if decrypted_message[passs] < 32:
                decrypted_message[passs] = int(
                    decrypted_message[passs]) + 95
            elif decrypted_message[passs] > 126:
                decrypted_message[passs] = int(
                    decrypted_message[passs]) - 95
            passs += 1
        for i, k in enumerate(current_user):
            if i < len(current_user) / 2 and len(str(code3)) >= 4:
                if len(str(code3)) > 4:
                    code2 = code_seg1
                else:
                    code3 = str(code2)[0:2]
                    code2 = int(code3)
            elif len(str(code3)) >= 4:
                if len(str(code3)) > 4:
                    code2 = code_seg2
                else:
                    code3 = str(code2)[2:4]
                    code2 = int(code3)
            decrypted_current_user.append(k)
            decrypted_current_user[passs2] = ord(k)
            decrypted_current_user[passs2] = int(
                decrypted_current_user[passs2]) + int(code2)
            passs2 += 1
        for k in decrypted_message:
            output_phrase += chr(k)
        for l in decrypted_current_user:
            encrypted_current_user += chr(l)
        if private_mode:
            encrypted_current_user = ""
        animated_print(f"Encrypting...")
        temp_message_text = textwrap.fill(message_text, width=50)
        # Used to print unencrypted message, but presented too many issues with printing flow
        # print(f"{temp_message_text}")
        if len(str(code3)) != 2:
            scrambled_output_phrase = random_filler(filler_length, output_phrase)
        else:
            scrambled_output_phrase = output_phrase
        temp_output_phrase = textwrap.fill(output_phrase, width=60)
        temp_scrambled_output_phrase = textwrap.fill(
            scrambled_output_phrase, width=60)
        if len(message_text) < 1000:
            line_breaks = len(message_text) / 50
            if sys.platform.startswith("win32"):
                log(
                    f"New Directory: {str(os.getcwd())} OS: Windows", "cwdchange", user, print_logs)
                # time.sleep(0.2)
                # for k in range(1, int(line_breaks) + 2):
                #    sys.stdout.write("\033[F")
                # time.sleep(0.2)
                animated_print(f"{temp_output_phrase}")
            else:
                log(
                    f"New Directory: {str(os.getcwd())} OS: Linux", "cwdchange", user, print_logs)
                # sys.stdout.write("\033[K")
                # for k in range(1, int(line_breaks) + 2):
                #    sys.stdout.write("\033[F")
            if print_logs:
                animated_print(
                    f"{temp_output_phrase}{' ' * int(len(temp_output_phrase) / 60)}")
                animated_print(f"Scrambling...")
                animated_print(f"{scrambled_output_phrase}")
            else:
                animated_print(f"{temp_scrambled_output_phrase}")
        else:
            animated_print(f"{scrambled_output_phrase}")
        sys.stdout.write("\033[K")
        output_file = open("./messageout.txt", "r+")
        log(f"New File: {str(output_file)} Type: Text File",
            "newfile", user, print_logs)
        for i in range(len(message_text)):
            if message_text[i] == output_phrase[i]:
                if message_text[i].strip() != "" and output_phrase[i].strip() != "":
                    # ?It is really difficult to nail down what causes either @code_seg1 or 2 to equal zero, so I added this catcher instead
                    animated_print(
                        f"{error_colour}WARNING: Faulty encryption code! Reloading...")
                    output_file.close()
                    Colours(default_colour)
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_colour, error_colour, auto_code=True)
                    code, prefix, timestamp = showcode(
                        user, 1, private_mode, print_logs, error_colour, default_colour)
                    newmessage(code, user, recipient_ip, link, prefix, date, talking_to_self, error_colour,
                               default_colour, private_mode, print_logs, mailing, display_initiate, True)
            else:
                pass
        else:
            output_file.write(scrambled_output_phrase)
            output_file.close()
            log(f"New Encrypted Message! Success?: Y. Files created: 1",
                "encrypt", user, print_logs)
            decrypt_code = showcode(
                user, 2, private_mode, print_logs, error_colour, default_colour)
        try:
            output_file.close()
        except:
            pass
    try:
        # *This currently only works over LAN, although there seems to be no reason it won't go on the internet
        # TODO: Figure out what port forwarding or VPN needs to be set up to enable the communication network
        if recipient_ip == "" or not conversation_mode and not skip:
            host = ""
            while host == None or "y" not in host.lower() and "n" not in host.lower():
                try:
                    host = privacy_input(
                        "Send message? (Y/N)", 0)
                except KeyboardInterrupt:
                    maybe_quit()
                    Colours(default_colour)
                if host == None:
                    host = ""
        else:
            host = "y"
    except NameError:
        host = privacy_input(
            "Send message? (Y/N)", 0)
        recipient_ip = ""
    if host == None:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif "y" in host:
        link = socket.socket()
        connected = False
        talking_to_self = False
        while not connected:
            try:
                if conversation_mode and recipient_ip != "":
                    ip = recipient_ip
                elif recipient_ip == "":
                    ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                   default_colour, private_mode, error_colour)
                ip = ip.strip().replace("\n", "")
                if recipient_ip != None:
                    recipient_ip = ip.strip().replace("\n", "")
                your_ip = get_own_ip(print_logs, private_mode)
                if recipient_ip == your_ip or recipient_ip == "127.0.0.1":
                    foreign_user = get_foreign_user(new_user=get_current_user())
                    enter_home_directory()
                    with open("./messagein.txt", "r+") as self_talk:
                        self_talk.seek(0)
                        self_talk.truncate()
                        self_talk.write(scrambled_output_phrase)
                    talking_to_self = True
                    connected = True
                    log(f"New message from {user} sent to {user}! Crazy? True",
                        "encrypt", user, print_logs)
                    if len(str(code2)) != 2 and not manual:
                        retrievemessage(
                            code, user, 2, backup_prefix, recipient_ip, link, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                    elif manual != None and manual:
                        retrievemessage(
                            code2, user, 2, None, recipient_ip, link, None, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                    else:
                        retrievemessage(
                            code, user, 2, backup_prefix, recipient_ip, link, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                else:
                    link.connect((recipient_ip, 15753))
                    connected = True
                    mailbox = False
            except ConnectionRefusedError:
                connected = False
                try:
                    link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            Contacts.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except UnboundLocalError:
                        animated_print(
                            f"{error_colour}WARNING: Unable to reach the host! Try a different address!")
                        Colours(default_colour)
                        ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour)
                        if ip == None or ip.strip() == "":
                            menu(user, None, print_logs, default_colour,
                                 private_mode, error_colour, print_speed=0)
                        elif "." not in ip:
                            if ":" in ip:
                                if ip == None:
                                    menu(user, None, print_logs, default_colour,
                                         private_mode, error_colour, print_speed=0)
                                temp = ip
                                target_name, target_mac, target_ip, details = Contacts.check_for(
                                    temp)
                                target_name = target_name.replace("\n", "")
                                if target_ip != None:
                                    ip = target_ip
                                else:
                                    ip = mac_resolve(target_mac, print_logs)
                                if ip == None:
                                    animated_print(
                                        f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                    Colours(default_colour)
                                    connected = False
                                else:
                                    Contacts.add_ip(target_name, ip)
                            else:
                                try:
                                    target_name, mac, target_ip, details = Contacts.check_for(
                                        ip)
                                    target_name = target_name.replace("\n", "")
                                    if mac.strip() == "":
                                        animated_print(
                                            f"{error_colour}WARNING: MAC address for contact is blank!")
                                        Colours(default_colour)
                                        connected = False
                                    else:
                                        target_mac = mac
                                        if target_ip != None:
                                            ip = target_ip
                                        else:
                                            ip = mac_resolve(
                                                target_mac, print_logs)
                                        if ip == None:
                                            animated_print(
                                                f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                            Colours(default_colour)
                                            connected = False
                                        else:
                                            Contacts.add_ip(target_name, ip)
                                except ValueError:
                                    animated_print(
                                        f"{error_colour}WARNING: Invalid contact name entered!")
                                    Colours(default_colour)
                                    connected = False
                                except TypeError:
                                    animated_print(
                                        f"{error_colour}WARNING: Invalid contact details!")
                                    Colours(default_colour)
                                    connected = False
                                except AttributeError:
                                    animated_print(
                                        f"{error_colour}WARNING: Invalid contact details!")
                                    Colours(default_colour)
                                    connected = False
                        recipient_ip = ip.strip().replace("\n", "")
            # ?Linux had some issues with their timeout being some huge value, so @KeyboardInterrupt also does the same
            except KeyboardInterrupt:
                connected = False
                animated_print(
                    f"{error_colour}WARNING: Keyboard Interrupt! Attempting to deliver message!")
                Colours(default_colour)
                try:
                    link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            Contacts.add_ip(target_name, "-")
                    except:
                        animated_print(f"Aborting...")
                        menu(user, None, print_logs, default_colour,
                             private_mode, error_colour, print_speed=0)
            except TimeoutError:
                connected = False
                try:
                    link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except KeyboardInterrupt:
                    try:
                        if target_name != None and target_name.strip() != "":
                            Contacts.add_ip(target_name, "-")
                    except:
                        pass
                    animated_print(f"Aborting...")
                    menu(user, None, print_logs, default_colour,
                         private_mode, error_colour, print_speed=0)
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            Contacts.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except:
                        animated_print(
                            f"{error_colour}WARNING: Unable to reach the host! Try a different address!")
                    Colours(default_colour)
                    try:
                        if ip:
                            pass
                    except UnboundLocalError:
                        ip = None
                    if ip == None or ip.strip() == "":
                        ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour)
                    else:
                        Contacts.add_ip(target_name, ip)
                    if "." not in ip:
                        if ":" in ip:
                            if ip == None:
                                menu(user, None, print_logs, default_colour,
                                     private_mode, error_colour, print_speed=0)
                            temp = ip
                            target_name, target_mac, target_ip, details = Contacts.check_for(
                                temp)
                            target_name = target_name.replace("\n", "")
                            if target_ip != None:
                                ip = target_ip
                            else:
                                ip = mac_resolve(target_mac, print_logs)
                            if ip == None:
                                animated_print(
                                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                Colours(default_colour)
                                connected = False
                            else:
                                Contacts.add_ip(target_name, ip)
                        else:
                            try:
                                target_name, mac, target_ip, details = Contacts.check_for(
                                    ip)
                                target_name = target_name.replace("\n", "")
                                if mac.strip() == "":
                                    animated_print(
                                        f"{error_colour}WARNING: MAC address for contact is blank!")
                                    Colours(default_colour)
                                    connected = False
                                else:
                                    target_mac = mac
                                    if target_ip != None:
                                        ip = target_ip
                                    else:
                                        ip = mac_resolve(
                                            target_mac, print_logs)
                                    if ip == None:
                                        animated_print(
                                            f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                        Colours(default_colour)
                                        connected = False
                                    else:
                                        Contacts.add_ip(target_name, ip)
                            except ValueError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact name entered!")
                                Colours(default_colour)
                                connected = False
                            except TypeError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact details!")
                                Colours(default_colour)
                                connected = False
                            except AttributeError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact details!")
                                Colours(default_colour)
                                connected = False
                    if recipient_ip != None:
                        recipient_ip = ip.strip().replace("\n", "")
            except OSError:
                connected = False
                if ip == None:
                    pass
                else:
                    ip = ip.replace("\n", "")
                try:
                    link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except KeyboardInterrupt:
                    animated_print(f"\nAborting communication!")
                    menu(user, None, print_logs, default_colour,
                         private_mode, error_colour, print_speed=0)
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            Contacts.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except:
                        animated_print(
                            f"{error_colour}WARNING: Unable to reach the host! Try a different address!")
                    Colours(default_colour)
                    if ip == None or ip.strip() == "":
                        ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour)
                    else:
                        try:
                            Contacts.add_ip(target_name, ip)
                        except UnboundLocalError:
                            pass
                    if "." not in ip:
                        if ":" in ip:
                            temp = ip
                            target_name, target_mac, target_ip, details = Contacts.check_for(
                                temp)
                            target_name = target_name.replace("\n", "")
                            if target_ip != None:
                                ip = target_ip
                            else:
                                ip = mac_resolve(target_mac, print_logs)
                            if ip == None:
                                animated_print(
                                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                Colours(default_colour)
                                connected = False
                            else:
                                Contacts.add_ip(target_name, ip)
                        else:
                            try:
                                target_name, mac, target_ip, details = Contacts.check_for(
                                    ip)
                                target_name = target_name.replace("\n", "")
                                if mac.strip() == "":
                                    animated_print(
                                        f"{error_colour}WARNING: MAC address for contact is blank!")
                                    Colours(default_colour)
                                    connected = False
                                else:
                                    target_mac = mac
                                    if target_ip != None:
                                        ip = target_ip
                                    else:
                                        ip = mac_resolve(
                                            target_mac, print_logs)
                                    if ip == None:
                                        animated_print(
                                            f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                                        Colours(default_colour)
                                        connected = False
                                    else:
                                        Contacts.add_ip(target_name, ip)
                            except ValueError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact name entered!")
                                Colours(default_colour)
                                connected = False
                            except TypeError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact details!")
                                Colours(default_colour)
                                connected = False
                            except AttributeError:
                                animated_print(
                                    f"{error_colour}WARNING: Invalid contact details!")
                                Colours(default_colour)
                                connected = False
                    recipient_ip = ip.strip().replace("\n", "")
        if not skip:
            enter_home_directory()
            content = open(f"./messageout.txt", "rb")
            decrypt_code = user, 2
            if code3 == "" and decrypt_code == "":
                decrypt_code, out_file = randomcode(
                    user, user, True, private_mode, print_logs, default_colour, error_colour)
            elif code3 != "":
                try:
                    decrypt_code = f"{timestamp}_{backup_code}_{backup_prefix}"
                except UnboundLocalError:
                    decrypt_code = int(code2)
            message = content.read()
            packet = f"{message} |||| {str(decrypt_code)} | {encrypted_current_user}"
            content.close()
        elif mailbox:
            if sys.platform.startswith("linux"):
                ip = gnu_ip_resolve(print_logs, private_mode)
                if your_ip == "":
                    your_ip = privacy_input(
                        "Enter your IP in dotted decimal format", private_mode)
            elif sys.platform.startswith("win32"):
                your_ip = socket.gethostbyname(socket.gethostname())
            enter_home_directory()
            content = open(f"./messageout.txt", "rb")
            decrypt_code = (user, 2)
            if code3 == "" and decrypt_code == "":
                decrypt_code, out_file = randomcode(
                    user, user, True, private_mode, print_logs, default_colour, error_colour)
            elif code3 != "":
                try:
                    decrypt_code = f"{timestamp}_{backup_code}_{backup_prefix}"
                except UnboundLocalError:
                    decrypt_code = int(code2)
            message = content.read()
            packet = f"Request:False | Source_IP:{your_ip} | Name:{encrypted_current_user} |||| {message} |||| {str(decrypt_code)}"
            content.close()
        else:
            packet = message_text
        link.send(packet.encode())
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        link.close()
        if not skip and print_logs:
            animated_print(
                f"Message {message.decode()} with decryption code {decrypt_code} successfully sent to {ip}!")
        elif mailbox and print_logs:
            animated_print(
                f"Message {message.decode()} with decryption code {decrypt_code} sent to {ip}'s mailbox!")
        elif conversation_mode and recipient_ip.strip() != "" and message_text.strip().endswith("\\exit"):
            animated_print(
                f"Message sent! Exiting conversation with {get_foreign_user().capitalize()}")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        elif not skip:
            animated_print(f"Message sent!")
        elif mailbox and conversation_mode:
            if get_foreign_user() != None:
                animated_print(
                    f"{get_foreign_user().capitalize()} is not available! Message left in their mailbox!")
            else:
                animated_print(f"Message left!")
        elif mailbox:
            animated_print(f"Message left!")
        elif poke:
            animated_print(f"Poke sent!")
        else:
            animated_print(
                f"Leaving conversation with {foreign_user.capitalize()}!")
    elif host != "":
        # *Informs the user of the decryption code, as it is EXTREMELY rare for the same code to be generated by two different computers
        animated_print(
            f"Send this code to the recipient of the message! {backup_code}")
    if conversation_mode and "y" in host and not skip:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_colour, default_colour)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        server_recieve(user, code, user, link, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    elif poke and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_colour, default_colour)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        server_recieve(user, code, user, link, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    elif love_sent and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_colour, default_colour)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        server_recieve(user, code, user, link, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    else:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)


def hash_current_user(user):
    hash_user = user.encode("utf-8")
    hash_user = hashlib.sha256(hash_user).hexdigest()
    return hash_user


def decode_foreign_user(code, prefix, user, default_colour):
    passs, code3, encrypted_foreign_user, decrypted_foreign_user, prefix = 0, code, [
    ], '', prefix.split("fE")
    prefix[1] = prefix[1].split("||")
    prefix[0] = prefix[0].replace("$", "")
    try:
        if len(prefix[0]) == 2:
            code_seg1 = code[int(prefix[0][0]): int(prefix[0][1])]
        elif len(prefix[0]) == 3:
            code_seg1 = code[int(prefix[0][0]): int(prefix[0][1:3])]
        elif len(prefix[0]) == 4:
            code_seg1 = code[int(prefix[0][0:2]): int(prefix[0][1:3])]
        code_seg1 = list(code_seg1)
        code_seg1 = sum(map(int, code_seg1))
        if len(prefix[1][0]) == 2:
            code_seg2 = code[int(prefix[1][0][0]): int(prefix[1][0][1])]
        elif len(prefix[1][0]) == 3:
            code_seg2 = code[int(prefix[1][0][0]): int(prefix[1][0][1:3])]
        elif len(prefix[1][0]) == 4:
            code_seg2 = code[int(prefix[1][0][0:2]): int(prefix[1][0][1:3])]
        code_seg2 = list(code_seg2)
        code_seg2 = sum(map(int, code_seg2))
        Colours(default_colour, force=True)
    except:
        temp = code_seg2
        code_seg2 = int(str(code_seg1)[::-1])
        code_seg1 = temp
        Colours(default_colour)
    for i, k in enumerate(user):
        if i < len(user) / 2 and len(str(code3)) >= 4:
            if len(str(code3)) > 4:
                code = code_seg1
            else:
                code3 = str(code)[0: 2]
                code = int(code3)
        elif len(str(code3)) >= 4:
            if len(str(code3)) > 4:
                code = code_seg2
            else:
                code3 = str(code)[2: 4]
                code = int(code3)
        encrypted_foreign_user.append(k)
        encrypted_foreign_user[passs] = ord(k)
        encrypted_foreign_user[passs] = int(
            encrypted_foreign_user[passs] - code)
        if encrypted_foreign_user[passs] < 32:
            encrypted_foreign_user[passs] = int(
                encrypted_foreign_user[passs]) + 95
        elif encrypted_foreign_user[passs] > 126:
            encrypted_foreign_user[passs] = int(
                encrypted_foreign_user[passs]) - 95
        passs += 1
    for k in encrypted_foreign_user:
        decrypted_foreign_user += chr(k)
    return decrypted_foreign_user


def validate_foreign_user(ip, expected_user):
    reply_link = socket.socket()
    try:
        reply_link.connect((ip.strip(), 15753))
    except ConnectionRefusedError:
        return False
    reply_link.send(
        f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
    reply_link.shutdown(socket.SHUT_RDWR)
    reply_link.close()
    validate_link = socket.socket()
    validate_link.bind((get_own_ip(False, False), 15754))
    validate_link.listen(10)
    sc, address = validate_link.accept()
    info = sc.recv(1024)
    info = info.decode()
    sc.close()
    validate_link.shutdown(socket.SHUT_RDWR)
    validate_link.close()
    if "true" in info.lower():
        return True
    else:
        reply_link = socket.socket()
        try:
            reply_link.connect((ip.strip(), 19507))
        except ConnectionRefusedError:
            return False
        reply_link.send(
            f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
        reply_link.shutdown(socket.SHUT_RDWR)
        reply_link.close()
        validate_link = socket.socket()
        validate_link.bind((get_own_ip(False, False), 15754))
        validate_link.listen(10)
        sc, address = validate_link.accept()
        info = sc.recv(1024)
        info = info.decode()
        sc.close()
        validate_link.shutdown(socket.SHUT_RDWR)
        validate_link.close()
        if "true" in info.lower():
            return True
        else:
            return False


def get_auto_code():
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code = retrieve_config_settings()
    return auto_code


def retrievemessage(old_code, user, current_user, prefix, recipient_ip, link, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, index, display_initiate):
    # ?Names such as @old_code are used to seperate the various states the string is put into during decryption
    try:
        prefix = prefix
    except:
        prefix = ""
    background_colour = "\033[41m"
    enter_home_directory()
    with open("./messagein.txt", "r+") as message_file:
        message_text = message_file.read()
    with open("./config.txt", "r+") as config_file:
        config_lines = config_file.readlines()
        if "true" in config_lines[7].lower():
            # ?Conversation mode attempts to create a flow when talking over LAN/WLAN, automating all the usual input questions
            conversation_mode = True
        else:
            conversation_mode = False
    decrypted_message, poked, love_sent, thumb, code2, allow_message_input = [], False, False, None, "", False
    if old_code != "":
        code2 = old_code
        manual = False
    # ?None of these conditions trigger during conversation mode
    # *@code2 is blank unless old_code carries a value, which is does during conversation and self-talk modes
    while code2 == "" or old_code == "" or current_user != 2:
        code2 = privacy_input(
            f"Enter the encryption code for the message here! Or, leave it blank for the auto-generated key", private_mode)
        # ?All caps EXIT is the standard escape phrase for inputs in this program
        if code2 == None:
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        # *Checks multiple variable before concluding there is no encryption code present
        if code2 == "":
            if old_code != "":
                code2 = old_code
                #!Manual is set to False by default
                break
            else:
                if old_code == "":
                    animated_print(
                        f"{error_colour}WARNING: Unable to retrieve auto-generated key! Make sure the key is in the code.txt file")
                    Colours(default_colour)
                else:
                    code2 = old_code
                    break
            manual = False
        elif len(code2) != 4 and len(code2) != 2:
            manual = True
            # ?The 'prefix delegations' refer to the two sets of numbers within the code that dictate what portions of the code are used to encrypt the input text
            prefix = privacy_input(
                f"Enter the two prefix delegation numbers joined by a colon", private_mode)
            break
        else:
            manual = True
            break
    #!Largely depreciated, as @old_code and @code2 would have interchanged values in the condition(s) above
    if not manual:
        old_code = code2
    # ?This is a specially designed segment for producing the correct code segment variables with the manually entered code.
    # *Manual decryption does not support decryption of the timestamp typical generated with messages
    elif len(code2) != 4 and len(code2) != 2:
        prefix = prefix.split(":")
        # ?Advanced index calling, finding two portions of the main encryption code that will be summed into a two-digit ASCII offset value
        # TODO: Make tweaks to improve the security of this method. Traditionally ASCII offset encryption is not secure, but by taking random parts of a longer string and extracing two different values, applying the encryption to the text as halves, requires a hacker to thoroughly understand the methodology to make even a brute-force effective enough to decrypt the whole message. Yeah yeah 0-94, I know...
        if len(prefix[0]) == 2:
            code_seg1 = code2[int(prefix[0][0]): int(prefix[0][1])]
        elif len(prefix[0]) == 3:
            code_seg1 = code2[int(prefix[0][0]): int(prefix[0][1:3])]
        elif len(prefix[0]) == 4:
            code_seg1 = code2[int(prefix[0][0:2]): int(prefix[0][1:3])]
        if len(prefix[1]) == 2:
            code_seg2 = code2[int(prefix[1][0]): int(prefix[1][1])]
        elif len(prefix[1]) == 3:
            code_seg2 = code2[int(prefix[1][0]): int(prefix[1][1:3])]
        elif len(prefix[1]) == 4:
            code_seg2 = code2[int(prefix[1][0:2]): int(prefix[1][1:3])]
        code_seg1 = sum(map(int, list(code_seg1)))
        code_seg2 = sum(map(int, list(code_seg2)))
        code3 = code2
    # *The old and far less secure method of using 4-digit keys that were split into two values, still supported for decryption
    if len(str(code2)) == 4:
        code3 = f"{int(code2[0:2])}{int(code2[2:4])}"
        code2 = code3
        allow_message_input = True
    # *If the code is two digits long, the program assumes it was given a raw ASCII offset value
    elif len(str(code2)) == 2:
        code3 = int(code2)
        code2 = code3
        allow_message_input = True
    elif not manual:
        backup_prefix = prefix
        prefix = prefix.split("fE")
        filler_length = prefix[1].split("||")
        filler_length = filler_length[1].replace("#", "")
        prefix[1] = prefix[1].split("||")
        prefix[0] = prefix[0].replace("$", "")
        time_decode = int(prefix[1][1].replace("#", ""))
        try:
            if len(prefix[0]) == 2:
                code_seg1 = code2[int(prefix[0][0]): int(prefix[0][1])]
            elif len(prefix[0]) == 3:
                code_seg1 = code2[int(prefix[0][0]): int(prefix[0][1:3])]
            elif len(prefix[0]) == 4:
                code_seg1 = code2[int(prefix[0][0:2]): int(prefix[0][1:3])]
            code_seg1 = list(code_seg1)
            code_seg1 = sum(map(int, code_seg1))
            if len(prefix[1][0]) == 2:
                code_seg2 = code2[int(prefix[1][0][0]): int(prefix[1][0][1])]
            elif len(prefix[1][0]) == 3:
                code_seg2 = code2[int(prefix[1][0][0]): int(prefix[1][0][1:3])]
            elif len(prefix[1][0]) == 4:
                code_seg2 = code2[int(prefix[1][0][0:2]): int(prefix[1][0][1:3])]
            code_seg2 = list(code_seg2)
            code_seg2 = sum(map(int, code_seg2))
            Colours(default_colour, force=True)
        except:
            temp = code_seg2
            code_seg2 = int(str(code_seg1)[::-1])
            code_seg1 = temp
            Colours(default_colour)
        times = []
        date = timestamp.split("|")
        date = date[1]
        # ?The timestamp user backwards values on top of ASCII offsets to increase their security
        if len(date) == 3:
            if date[1] == "0":
                date = f"{date[2:3]}/{date[0:2]}"
            else:
                date = f"{date[1:3]}/{date[0][::-1]}"
        elif len(date) == 4:
            if date[1] == "0":
                date = f"{date[2:4]}/{date[0:2]}"
            else:
                date = f"{date[2:4]}/{date[0:2][::-1]}"
        elif len(date) == 2:
            date = f"{date[1]}/{date[0][::-1]}"
        timestamp = timestamp.split("A")
        timestamp[0] = timestamp[0].replace("$", "")
        timestamp[1] = timestamp[1].split("|")
        timestamp[1] = timestamp[1][0]
        try:
            hrs = int(timestamp[0]) - int(time_decode)
            mins = int(timestamp[1]) - int(time_decode)
        except ValueError:
            hrs = int(timestamp[0][:: -1]) - int(time_decode)
            mins = int(timestamp[1][:: -1]) - int(time_decode)
        if int(hrs) <= 9:
            try:
                hrs = str(hrs).replace("-", "")
                hrs = int(f"0{hrs}")
            except ValueError:
                # ? Sometimes the @time_decode value is poorly generated and exceeds the value of the encrypted timestamp, so this warning is displayed before the program attempts to decrypt the time after reversing the string
                animated_print(
                    f"{error_colour}WARNING: Irregularity detected in the decrypted timestamp! It may be wrong!")
                Colours(default_colour)
                hrs = int(timestamp[0][:: -1]) - int(time_decode)
                hrs = int(f"0{hrs}")
        if int(hrs) <= 12:
            suffix = "AM"
        else:
            suffix = "PM"
            hrs = int(hrs) - 12
        if len(str(mins)) < 2:
            try:
                mins = f"0{mins}"
            except ValueError:
                mins = int(timestamp[1][:: -1]) - int(time_decode)
                mins = f"0{mins}"
        else:
            try:
                if mins < 0:
                    mins = int(timestamp[1][:: -1]) - int(time_decode)
                else:
                    mins = int(mins)
            except ValueError:
                mins = int(timestamp[1][:: -1]) - int(time_decode)
        timestamp = f"{date} - {hrs}:{mins}{suffix}"
        code3 = code2
    passs = 0
    output_phrase = ''
    files = 0
    if allow_message_input:
        message_text = privacy_input(f"Enter message to be decrypted", private_mode)
    if len(message_text) == 0:
        if not allow_message_input:
            animated_print(
                f"{error_colour}WARNING: Message cannot be blank!")
            Colours(default_colour)
            menu(user, current_user, None, default_colour,
                 private_mode, error_colour, print_speed=0)
        else:
            while len(message_text) == 0:
                animated_print(
                    f"{error_colour}WARNING: Message cannot be blank!")
                Colours(default_colour)
                message_text = privacy_input(f"Enter message to be decrypted", private_mode)
    for i, k in enumerate(message_text):
        # ?The first half of the message(determined by len() attribute) is decrypted with @code_seg1
        if i < len(message_text) / 2 and len(str(code3)) >= 4:
            if len(str(code3)) > 4:
                code2 = code_seg1
            else:
                code3 = str(code2)[0: 2]
                code2 = int(code3)
        # ?Avoids using else so that errors are properly caught
        elif len(str(code3)) >= 4:
            if len(str(code3)) > 4:
                code2 = code_seg2
            else:
                code3 = str(code2)[2: 4]
                code2 = int(code3)
        decrypted_message.append(k)
        decrypted_message[passs] = ord(k)
        decrypted_message[passs] = int(decrypted_message[passs] - code2)
        # *This validity check was only dones as some ASCII characters are longer than 1 digit, which would break the decryption process
        if(decrypted_message[passs] < 32):
            decrypted_message[passs] = int(decrypted_message[passs]) + 95
        elif(decrypted_message[passs] > 126):
            decrypted_message[passs] = int(decrypted_message[passs]) - 95
        passs += 1
    for k in decrypted_message:
        output_phrase += chr(k)
    if len(str(code3)) > 4:
        filler_length = int(filler_length.strip())
        output_phrase = decrypt_filler(filler_length, output_phrase)
        placeholder = decrypt_filler(filler_length, message_text)
    # ?Text wrapping to keep the plain text and encrypted output from falling out of sync
    animated_print(f"Decrypting...")
    if not manual and timestamp != None:
        print(timestamp)
    elif not manual:
        print("Date/time not saved!")
    if "<3" in output_phrase.strip() or "\\heart" in output_phrase.strip():
        love_sent = True
        hearts = output_phrase.strip().count("<3")
        hearts += output_phrase.strip().count("\\heart")
    time.sleep(0.2)
    if output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip() and love_sent:
        pokes = output_phrase.count("\\poke")
        temp_output_phrase = output_phrase.replace("\\poke", "").replace(
            "\\exit", "").replace("\\heart", "").strip()
        poked = True
    elif output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip():
        pokes = output_phrase.count("\\poke")
        temp_output_phrase = output_phrase.replace(
            "\\poke", "").replace("\\exit", "").strip()
        poked = True
    elif output_phrase.strip().endswith("\\exit") and love_sent:
        temp_output_phrase = output_phrase.replace("\\exit", "").strip()
    elif "\\poke" in output_phrase.strip() and love_sent:
        pokes = output_phrase.count("\\poke")
        temp_output_phrase = output_phrase.replace("\\poke", "").strip()
        poked = True
    elif output_phrase.strip().endswith("\\exit"):
        temp_output_phrase = output_phrase.replace("\\exit", "").strip()
    elif "\\poke" in output_phrase.strip():
        pokes = output_phrase.count("\\poke")
        temp_output_phrase = output_phrase.replace("\\poke", "").strip()
        poked = True
    elif love_sent:
        temp_output_phrase = output_phrase.replace("\\heart", "").strip()
    else:
        temp_output_phrase = output_phrase.strip()
    if "\\thumbs_up" in temp_output_phrase.strip():
        temp_output_phrase = temp_output_phrase.replace(
            "\\thumbs_up", "").strip()
        thumb = True
    if "\\thumbs_down" in temp_output_phrase.strip():
        temp_output_phrase = temp_output_phrase.replace(
            "\\thumbs_down", "").strip()
        thumb = False
    if temp_output_phrase.strip().count("$") >= 2:
        try:
            cached_output_phrase = temp_output_phrase
            temp_output_phrase_list = temp_output_phrase.split("$")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[9m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                del(temp_output_phrase_list[0])
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[9m"
                else:
                    temp_output_phrase = f"\033[9m"
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[9m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                temp_output_phrase = f"\033[9m"
                next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[9m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("_") >= 2:
        try:
            temp_output_phrase_list = temp_output_phrase.split("_")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[4m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[4m"
                else:
                    temp_output_phrase = f"\033[4m"
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[4m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[4m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[4m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[4m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("~") >= 2:
        try:
            temp_output_phrase_list = temp_output_phrase.split("~")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[3m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[3m"
                else:
                    temp_output_phrase = f"\033[3m"
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[3m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[3m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[3m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[3m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("*") >= 2:
        try:
            temp_output_phrase_list = temp_output_phrase.split("*")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[1m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[1m"
                else:
                    temp_output_phrase = f"\033[1m"
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[1m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[1m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[1m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[1m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("^") >= 2:
        try:
            temp_output_phrase_list = temp_output_phrase.split("^")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[5m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "^", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[5m"
                else:
                    temp_output_phrase = f"\033[5m"
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[5m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "^", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[5m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[5m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_colour}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_colour}":
                        next_format = "\033[5m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_colour}"
                temp_output_phrase = temp_output_phrase.replace(
                    "^", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if "YOU" in temp_output_phrase.strip() and "->" in temp_output_phrase.strip():
        try:
            reply_output_phrase = temp_output_phrase.split("->")
            if temp_output_phrase.count("YOU") >= 2:
                for i in range(1, len(reply_output_phrase), 2):
                    reply_output_phrase[i] = reply_output_phrase[i].split(
                        "YOU")
                    reply_output_phrase.insert(
                        i+1, f"YOU{reply_output_phrase[i][1]}")
                    reply_output_phrase[i] = reply_output_phrase[i][0]
                for i in range(0, len(reply_output_phrase), 2):
                    temp_reply_output_phrase = reply_output_phrase[i]
                    temp_reply_output_phrase = temp_reply_output_phrase.split(
                        ": ", 1)
                    temp_reply_output_phrase[1] = f" \"{temp_reply_output_phrase[1]}"
                    temp_reply_output_phrase = f"{temp_reply_output_phrase[0]}:{temp_reply_output_phrase[1]}"
                    if reply_output_phrase[i+1].strip().startswith(">"):
                        reply_output_phrase[i +
                                            1] = reply_output_phrase[i+1].replace(">", "")
                    animated_print(
                        f"\033[3m\033[43m{temp_reply_output_phrase.strip()}\"\033[0m{applied_default_colour} -> \033[41m{reply_output_phrase[i+1].strip()}\033[0m")
                    Colours(default_colour)
            else:
                temp_output_phrase = reply_output_phrase[1].strip()
                reply_output_phrase = reply_output_phrase[0].strip()
                reply_output_phrase = reply_output_phrase.split(": ", 1)
                reply_output_phrase[1] = f" \"{reply_output_phrase[1]}"
                reply_output_phrase = f"{reply_output_phrase[0]}:{reply_output_phrase[1]}"
                animated_print(
                    f"\033[3m\033[43m{reply_output_phrase}\"\033[0m{applied_default_colour} -> \033[41m{temp_output_phrase}\033[0m")
            cached_output_phrase = temp_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    else:
        animated_print(f"\033[41m{temp_output_phrase}\033[0m")
    Colours(default_colour)
    # *@recipient_ip needs to be defined for the below if statement, if it is not, it gets set to blank
    try:
        recipient_ip = recipient_ip
    except NameError:
        recipient_ip = ""
    # ?The @mailing variable is set in the @check_mailbox() module, and remains true if there are unread messages present
    # *Calls the @check_mailbox() module if there are unread messages, which will send the next message back by calling this module again
    if thumb != None:
        thumbs(get_foreign_user(), thumb)
    if mailing:
        # check_mailbox(user, 2, index, mailing, timestamp, error_colour,
        #              default_colour, display_initiate, print_logs, private_mode)
        if love_sent and poked:
            you_are_loved(get_foreign_user(), hearts=hearts)
            Colours(default_colour)
            get_poked(get_foreign_user(), poke_num=pokes)
        elif love_sent:
            you_are_loved(get_foreign_user(), hearts=hearts)
            Colours(default_colour)
        elif poked:
            get_poked(get_foreign_user(), poke_num=pokes)
        else:
            pass
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip() and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colours(default_colour)
        get_poked(get_foreign_user(), poke_num=pokes)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip():
        get_poked(get_foreign_user(), poke_num=pokes)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colours(default_colour)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and "\\poke" in output_phrase.strip() and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colours(default_colour)
        get_poked(get_foreign_user(), poke_num=pokes)
        newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                   error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), poked=True, message=temp_output_phrase)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit"):
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colours(default_colour)
        if not talking_to_self:
            newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)
        else:
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    elif "\\poke" in output_phrase.strip() and not conversation_mode:
        pass
    elif love_sent and not conversation_mode:
        pass
    elif not conversation_mode or recipient_ip == "" or talking_to_self:
        if poked and talking_to_self:
            get_poked(capitalize_user(get_current_user()), poke_num=pokes)
            newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)
        elif talking_to_self:
            newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)
        else:
            success = privacy_input(f"Was the decryption successful? (Y/N)", 0)
            if success == None:
                menu(user, None, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            elif "y" in success.lower():
                enter_home_directory()
                code_file = open("./code.txt", "r")
                # ?Logs event for when one of the key files is accessed. Values for this entry are static and send to the @log module
                log(
                    f"New File: {str(code_file)} Type: Text File.  Access: Read-Only", "newfile", user, print_logs)
                lines = code_file.readlines()
                if not manual:
                    text = code_file.read()
                    # TODO: Check all files that are used get properly closed as such
                    code_file.close()
                    code_file = open("./code.txt", "r+")
                    log(
                        f"New File: {str(code_file)} Type: Text File.  Access: Write", "newfile", user, print_logs)
                    code_file.seek(0)
                    for line in text.split('\n'):
                        if line != old_code.strip():
                            code_file.write(line + '\n')
                    code_file.truncate()
                    files += 1
                    code_file.close()
                    log(
                        f"Success?: {str(success.upper())}. Files removed: {str(files)}", "decrypt", user, print_logs)
                    animated_print(
                        f"The code used to decrypt this message will be deleted from local storage, for your security")
                else:
                    animated_print(
                        f"Manual code decryption concluded. It is not recommended that you use this code again!")
                    time.sleep(2)
                    menu(user, None, print_logs, default_colour,
                         private_mode, error_colour, print_speed=0)
            else:
                log(
                    f"Success?: {str(success.upper())}. Files removed: {str(files)}", "decrypt", user, print_logs)
                animated_print(
                    f"That is unfortunate :( We will launch the encryption assistant momentarily")
                #!Current unreliable
                helper("decrypt", user, current_user)
    # *Called if in conversation mode
    else:
        if poked:
            get_poked(get_foreign_user(), poke_num=pokes)
            newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), poked=True, message=temp_output_phrase)
        else:
            newmessage(old_code, user, recipient_ip, link, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)


def server_recieve(user, code, current_user, link, recipient_ip, timestamp, prefix, date, default_colour, print_logs, private_mode, error_colour, display_initiate):
    print("Server warming up... ", end="")
    enter_home_directory()
    if sys.platform.startswith("linux"):
        ip = gnu_ip_resolve(print_logs, private_mode)
        if ip == "":
            animated_print(
                f"{error_colour}WARNING: Unable to determine IP address!")
            Colours(default_colour)
            ip = privacy_input(
                "Enter your IP in dotted decimal format", private_mode)
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    try:
        print("Done!")
        try:
            link.shutdown(socket.SHUT_RDWR)
            link.close()
        except:
            pass
        link = socket.socket()
        animated_print("Socket opened... ")
        link.bind((ip, 15753))
        time.sleep(1)
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[F")
        animated_print("Socket bound... ")
        link.listen(10)
        time.sleep(2)
        sys.stdout.write("\033[F")
        animated_print(f"Socket bound... {ip}:15753")
        # ?'serv1' refers to the log code for an inbound server being started, see @logs() module for more
        log(f"Server started on {ip}:15753", "server_start",
            user, print_logs)
        animated_print("Listening on socket... ")
        sc, address = link.accept()
    except KeyboardInterrupt:
        animated_print("\nServer Terminated!")
        try:
            sc.close()
        except:
            pass
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        link.close()
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    sys.stdout.write("\033[K")
    sys.stdout.write("\033[F")
    print("Connection established!")
    try:
        info = sc.recv(1024)
    except ConnectionResetError:
        animated_print(
            f"{error_colour}Connection reset by peer!")
        Colours(default_colour)
        menu(user, display_initiate, print_logs,
             default_colour, private_mode, error_colour, print_speed=0)
    print("Recieving information... ", end="\n\n")
    for i in range(1, 6):
        sys.stdout.write("\033[F")
        print(f"{'-'*(i*2)}> {i*20}%")
        time.sleep(0.5)
    info = info.decode()
    message = info.split(" |||| ")
    if "\\user_confirm" in message[0]:
        message[0] = message[0].split("=")
        expected_user = message[0][1]
        message[0] = message[0][0]
        reply_ip = message[1]
        if expected_user.strip().lower() == capitalize_user(get_current_user()).strip().lower():
            verify_link = socket.socket()
            verify_link.connect((reply_ip.strip(), 15754))
            verify_link.send(str(True).encode())
            verify_link.shutdown(socket.SHUT_RDWR)
            verify_link.close()
            link.shutdown(socket.SHUT_RDWR)
            link.close()
            sc.close()
            animated_print(f"Foreign user validated!")
            server_recieve(user, code, current_user, link, recipient_ip, timestamp, prefix,
                           date, default_colour, print_logs, private_mode, error_colour, display_initiate)
        else:
            verify_link = socket.socket()
            verify_link.connect((reply_ip.strip(), 15754))
            verify_link.send(str(False).encode())
            verify_link.shutdown(socket.SHUT_RDWR)
            verify_link.close()
            link.shutdown(socket.SHUT_RDWR)
            link.close()
            sc.close()
            animated_print(
                f"{error_colour}WARNING: Foreign user validation failed!")
            Colours(default_colour)
            server_recieve(user, code, current_user, link, recipient_ip, timestamp, prefix,
                           date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    else:
        try:
            if "\\exit" in message or "\\poke" in message:
                pass
            else:
                info = message[1]
            message = message[0]
        except IndexError:
            animated_print(
                f"{error_colour}WARNING: {message} recieved but not valid! Restarting Server!")
            Colours(default_colour)
            server_recieve(user, code, current_user, link, recipient_ip, timestamp, prefix,
                           date, default_colour, print_logs, private_mode, error_colour, display_initiate)
        print("Done!")
    sc.close()
    try:
        link.shutdown(socket.SHUT_RDWR)
    except:
        pass
    link.close()
    info = info.split(" | ")
    try:
        message = message.decode()
    except AttributeError:
        pass
    try:
        foreign_user = info[1]
        info[0] = info[0].split("|")
        info[0][1] = info[0][1].split("_")
        date = info[0][1][0]
    except IndexError:
        if "\\exit" in message or "\\poke" in message:
            pass
        else:
            print(info)
            animated_print(
                f"{error_colour}WARNING: Error with date formatting! Returning to menu!")
            Colours(default_colour)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    if "\\exit" in message:
        skip = True
        if get_foreign_user() == None:
            foreign_user = "Anonymous"
        else:
            foreign_user = get_foreign_user()
        animated_print(
            f"{foreign_user.capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        backup_current_user = user
    # ?Removes any remnants of the .encode() attribute added to messages before they are sent
    elif message.startswith("b'") or message.startswith("b\""):
        message = message[2: int(len(message))]
        message = message[0: int(len(message)-1)]
        skip = False
    else:
        # ?These kind of scripts address specific issues I encountered during development. For some reason, an extra backslash used to randomly appear and distort messages being decrypted
        skip = False
    if not skip:
        message = message.replace('"', '\"').replace("'", "\'")
        timer = str(datetime.datetime.now())
        timer = timer.split("-")
        if "\\'" in message:
            message = message.replace("\\'", "'")
        enter_home_directory()
        os.remove(f"./messagein.txt")
        with open(f"./messagein.txt", "w+") as output_file:
            output_file.write(message)
        # Manually replace binary encapsulation due to imutability being given during split process
        code = info[0][1][1].replace("'", "")
        recipient_ip = address[0]
        if print_logs:
            animated_print(
                f"Message {message} successfully recieved from {address[0]} and written to messagein.txt!")
        else:
            if foreign_user != None and foreign_user.strip() != "":
                temp_foreign_user = ""
                for i in foreign_user:
                    if i.strip() == "":
                        pass
                    else:
                        temp_foreign_user += i
                temp_foreign_user = temp_foreign_user.replace("\033[F", "").replace("\033[K", "")
                animated_print(f"Message from {temp_foreign_user} received!")
            else:
                foreign_user = "Anonymous"
        prefix = info[0][1][2]
        if info[0][2].strip() != "":
            prefix = f"{prefix}||{info[0][2]}"
            hrs = int(str(timer[2][3: 5])) + int(info[0][2].replace("#", ""))
            mns = int(str(timer[2][6: 8])) + int(info[0][2].replace("#", ""))
        else:
            prefix = f"{prefix}||{info[0][3]}"
            hrs = int(str(timer[2][3: 5])) + int(info[0][3].replace("#", ""))
            mns = int(str(timer[2][6: 8])) + int(info[0][3].replace("#", ""))
        # timestamp = info[0][0]
        # timestamp = f"{timestamp}|{date}"
        # ?The old method of retrieving the timestamp has been replaced with a new timestamp made when the server recieves the message
        new_time = str(hrs)
        new_time += "A"
        new_time += str(mns)
        date = f"{int(timer[1])}{int(timer[2][0:2])}"
        timestamp = f"{new_time}|{date}"
        log("Message recieved over LAN/WLAN! Downloaded: True",
            "mess_in", user, print_logs)
        try:
            try:
                create_notification(recipient_ip)
            except:
                pass
            if "Anonymous" not in foreign_user:
                foreign_user = decode_foreign_user(code, prefix, foreign_user, default_colour)
            sys.stdout.write("\033[F")
            if get_foreign_user() != None and foreign_user.strip().lower() != get_foreign_user().strip().lower():
                animated_print(
                    f"{error_colour}WARNING: The user sending the message has changed!")
                Colours(default_colour)
            animated_print(
                f"Message from {foreign_user.capitalize()} recieved!")
            foreign_user = get_foreign_user(new_user=foreign_user)

            retrievemessage(code, user, 2, prefix, recipient_ip, link, timestamp, False, False,
                            default_colour, print_logs, private_mode, error_colour, None, display_initiate)
        except KeyboardInterrupt:
            menu(user, display_initiate, print_logs,
                 default_colour, private_mode, error_colour, print_speed=0)
    else:
        menu(user, display_initiate, print_logs,
             default_colour, private_mode, error_colour, print_speed=0)


def send_conversation_invite(user, current_user, default_colour, private_mode, error_colour, print_logs, display_initiate):
    if sys.platform.startswith("linux"):
        ip = gnu_ip_resolve(print_logs, private_mode)
        if ip == "":
            ip = privacy_input(
                "Enter your IP in dotted decimal format", private_mode)
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    try:
        dest_ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                            default_colour, private_mode, error_colour)
        dest_ip = dest_ip.strip()
    except KeyboardInterrupt:
        print("")
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    link = socket.socket()
    connected = False
    while not connected:
        try:
            link.connect((dest_ip, 19507))
            connected = True
        except ConnectionRefusedError:
            connected = False
            animated_print(
                f"{error_colour}WARNING: Connection to recipient unexpectedly terminated! Try again!")
            Colours(default_colour)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        except TimeoutError:
            connected = False
            animated_print(
                f"{error_colour}WARNING: Unable to obtain a response from recipient address! Try again!")
            Colours(default_colour)
            send_conversation_invite(user, current_user, default_colour,
                                     private_mode, error_colour, print_logs, display_initiate)
        except OSError:
            connected = False
            animated_print(
                f"{error_colour}WARNING: Unable to obtain a response from recipient address! Try again!")
            Colours(default_colour)
            send_conversation_invite(user, current_user, default_colour,
                                     private_mode, error_colour, print_logs, display_initiate)
        except KeyboardInterrupt:
            animated_print(f"\nAborting!")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    log(f"Conversation invite sent to {dest_ip}",
        "conv", user, print_logs)
    content = f"Request:True Source_IP:{ip} Name:{current_user}"
    packet = content.encode()
    link.send(packet)
    try:
        link.shutdown(socket.SHUT_RDWR)
    except:
        pass
    link.close()
    # *The code 1 will tell listener.py that it is recieving a conversation request, not a message
    code, prefix, timestamp = showcode(user, 1, private_mode,
                                       print_logs, error_colour, default_colour)
    date = timestamp.split("|")
    date = date[1]
    animated_print(f"{dest_ip} has been invited!")
    start_server = privacy_input(f"Start server? [Y|N]", private_mode)
    if start_server == None:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif "y" in start_server.lower():
        server_recieve(user, code, user, current_user, dest_ip, timestamp,
                       prefix, date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    else:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)


def check_mailbox(user, current_user, index, mailing, timestamp, error_colour, default_colour, display_initiate, print_logs, private_mode):
    enter_home_directory()
    if current_user != 2:
        os.chdir(f"./{hash_current_user(get_current_user().strip().lower())}_inbox")
        with open(f"./messages.txt", "r+") as mailbox:
            letters = mailbox.readlines()
        for i, letter in enumerate(letters):
            try:
                letter = int(letter)
            except ValueError:
                pass
        # ?Due to the formatting of the mailbox entries made by listener.py, each message uses two lines, so the printed value is half the length
        animated_print(f"You have {int(len(letters)/2)} unread messages!\n")
        log(f"Mailbox accessed! Unread messages: {int(len(letters)/2)}",
            "mail_check", user, print_logs)
        loop = 1
        index = [0]
        for i in range(1, len(letters), 2):
            index.append(letters[i])
            loop += 1
    mailing = True
    for i, message in enumerate(index):
        if i != 0:
            message = message.split(" - ")
            # *Places the message into the messagein.txt file, one at a time, deleting them as @retrievemessage() module is called
            with open("./messagein.txt", "r+") as message_file:
                message_file.seek(0)
                message_file.truncate()
                message_file.write(message[0])
            message[1] = message[1].split(" From: ")
            old_code = message[1][0].split("_")
            try:
                timestamp = old_code[0]
                prefix = old_code[2]
                old_code = old_code[1]
                message[1][1] = message[1][1].split("@")
                if message[1][1][0] != None and message[1][1][0].strip() != "" and "anonymous" not in message[1][1][0].lower():
                    message[1][1][0] = decode_foreign_user(
                        old_code, prefix, message[1][1][0].strip(), default_colour)
                else:
                    message[1][1][0] = "Anonymous"
                message[1][1][0] = get_foreign_user(new_user=message[1][1][0])
                animated_print(f"Message from {message[1][1][0].capitalize()}")
            except IndexError:
                animated_print(
                    f"{error_colour}WARNING: Message {i} contains corrupted format! This message will be removed!")
                Colours(default_colour)
            del(index[i])
            enter_home_directory()
            os.chdir(f"./{hash_current_user(get_current_user().strip().lower())}_inbox")
            with open(f"./messages.txt", "w+") as inbox:
                inbox.seek(0)
                inbox.truncate()
                try:
                    inbox.write(f"{i}\n{index[i]}")
                except IndexError:
                    pass
            try:
                retrievemessage(old_code, user, 2, prefix, message[1][1], None, timestamp,
                                True, False, default_colour, print_logs, private_mode, error_colour, index, display_initiate)
                Colours(default_colour)
                reply = privacy_input(
                    f"Would you like to send a reply? [Y|N]", private_mode)
                if "y" in reply.lower():
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_colour, default_colour)
                    newmessage(code, user, message[1][1][1], None, prefix, None,
                               False, error_colour, default_colour, private_mode, print_logs, False, display_initiate, False)
                else:
                    check_mailbox(user, 2, index, mailing, timestamp, error_colour,
                                  default_colour, display_initiate, print_logs, private_mode)
            except UnboundLocalError:
                pass
    # ?File is deleted once all messages are read, and then re-created
    hide_tree()
    mailing = False
    menu(user, display_initiate, print_logs,
         default_colour, private_mode, error_colour, print_speed=0)


def config_settings(user, current_user, default_colour, print_logs, private_mode, error_colour):
    master_printing_speed = None
    animated_print(f"Loading special options...")
    enter_home_directory()
    config_file = open(f"./config.txt", "r+")
    config_data = config_file.read()
    config_lines = config_data.split("\n")
    escape = False
    while not escape:
        if master_printing_speed == None:
            try:
                master_printing_speed = printing_speed
            except UnboundLocalError:
                master_printing_speed = None
        if "debug" in config_lines[2].lower():
            debug_mode = config_lines[2].split(" = ")
            debug_mode = debug_mode[1]
        else:
            debug_mode = False
        if "display" in config_lines[3].lower():
            display_initiate = config_lines[3].split(" = ")
            display_initiate = display_initiate[1]
        else:
            display_initiate = False
        if "printing" in config_lines[4].lower():
            printing_speed = config_lines[4].split(" = ")
            printing_speed = printing_speed[1]
        else:
            printing_speed = 0.05
        if "default" in config_lines[5].lower():
            display_colour = config_lines[5].split(" = ")
            display_colour = display_colour[1]
        else:
            display_colour = "White (default)"
        if "custom" in config_lines[6].lower():
            custom_scheme = config_lines[6].split(" = ")
            custom_scheme = custom_scheme[1]
        else:
            custom_scheme = False
        if "conversation" in config_lines[7].lower():
            conversation_mode = config_lines[7].split(" = ")
            conversation_mode = conversation_mode[1]
        else:
            conversation_mode = False
        if "graphic" in config_lines[8].lower():
            graphic_mode = config_lines[8].split(" = ")
            graphic_mode = graphic_mode[1]
        else:
            graphic_mode = False
        if "private" in config_lines[9].lower():
            private_mode = config_lines[9].split(" = ")
            private_mode = private_mode[1]
        else:
            private_mode = False
        if "auto" in config_lines[10].lower():
            auto_code = config_lines[10].split(" = ")
            auto_code = auto_code[1]
        else:
            auto_code = False
        animated_print(
            f"1. Debug mode: {debug_mode}", speed=master_printing_speed)
        animated_print(
            f"2. Display initiate: {display_initiate}", speed=master_printing_speed)
        animated_print(
            f"3. Print speed: {printing_speed}", speed=master_printing_speed)
        animated_print(
            f"4. Enable custom colour scheme: {custom_scheme}", speed=master_printing_speed)
        if custom_scheme:
            animated_print(
                f"5. Custom colour: {display_colour}", speed=master_printing_speed)
            animated_print(
                f"6. Conversation mode: {conversation_mode}", speed=master_printing_speed)
            animated_print(
                f"7. Graphic mode: {graphic_mode}", speed=master_printing_speed)
            animated_print(
                f"8. Privacy mode: {private_mode}", speed=master_printing_speed)
            animated_print(
                f"9. Auto code: {auto_code}", speed=master_printing_speed)
            animated_print(f"10. Create new user...", speed=master_printing_speed)
        else:
            animated_print(
                f"5. Conversation mode: {conversation_mode}", speed=master_printing_speed)
            animated_print(
                f"6. Graphic mode: {graphic_mode}", speed=master_printing_speed)
            animated_print(
                f"7. Privacy mode: {private_mode}", speed=master_printing_speed)
            animated_print(
                f"8. Auto code: {auto_code}", speed=master_printing_speed)
            animated_print(f"9. Create new user...", speed=master_printing_speed)
        choice = privacy_input(
            f"What setting would you like to modify", private_mode)
        if choice == None:
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        elif choice == "1":
            debug_mode = privacy_input(f"True/False", private_mode)
            if "t" in debug_mode.lower():
                debug_mode = True
            else:
                debug_mode = False
            config_lines[2] = f"debug_mode = {debug_mode}"
        elif choice == "2":
            display_initiate = privacy_input(f"True/False", private_mode)
            if "t" in display_initiate.lower():
                display_initiate = True
            else:
                display_initiate = False
            config_lines[3] = f"display_initiate = {display_initiate}"
        elif choice == "3":
            new_print_speed = privacy_input(
                f"Enter print speed (as float)", private_mode)
            config_lines[4] = f"printing_speed = {float(new_print_speed)}"
        elif choice == "4":
            true_false = privacy_input(f"True/False", private_mode)
            if "t" in true_false.lower():
                true_false = True
            else:
                true_false = False
            config_lines[6] = f"custom_scheme = {true_false}"
        elif choice == "5":
            if custom_scheme:
                new_colour = privacy_input(
                    f"Enter colour (in plain text)", private_mode)
                animated_print(
                    f"{error_colour}WARNING: Program restart will be required for colour change!")
                Colours(default_colour)
                config_lines[5] = f"default_colour = {new_colour}"
            elif conversation_mode or not conversation_mode:
                conversation_mode = privacy_input(
                    f"True/False", private_mode)
                if "t" in conversation_mode.lower():
                    conversation_mode = True
                else:
                    conversation_mode = False
                config_lines[7] = f"conversation_mode = {conversation_mode}"
        elif choice == "6":
            if custom_scheme:
                conversation_mode = privacy_input(
                    f"True/False", private_mode)
                if "t" in conversation_mode.lower():
                    conversation_mode = True
                else:
                    conversation_mode = False
                config_lines[7] = f"conversation_mode = {conversation_mode}"
            else:
                graphic_mode = privacy_input(f"True/False", private_mode)
                if "t" in graphic_mode.lower():
                    graphic_mode = True
                else:
                    graphic_mode = False
                config_lines[8] = f"graphic_mode = {graphic_mode}"
        elif choice == "7":
            if custom_scheme:
                graphic_mode = privacy_input(f"True/False", private_mode)
                if "t" in graphic_mode.lower():
                    graphic_mode = True
                else:
                    graphic_mode = False
                config_lines[8] = f"graphic_mode = {graphic_mode}"
            else:
                private_mode = privacy_input(f"True/False", private_mode)
                animated_print(
                    f"{error_colour}WARNING: Program restart will be required for privacy mode change!")
                Colours(default_colour)
                if "t" in private_mode.lower():
                    private_mode = True
                else:
                    private_mode = False
                config_lines[9] = f"private_mode = {private_mode}"
        elif choice == "8":
            if custom_scheme:
                private_mode = privacy_input(f"True/False", private_mode)
                if "t" in private_mode.lower():
                    private_mode = True
                else:
                    private_mode = False
                config_lines[9] = f"private_mode = {private_mode}"
            else:
                auto_code = privacy_input(f"True/False", private_mode)
                if "t" in auto_code.lower():
                    auto_code = True
                else:
                    auto_code = False
                config_lines[10] = f"auto_code = {auto_code}"
        elif choice == "9":
            if custom_scheme:
                auto_code = privacy_input(f"True/False", private_mode)
                if "t" in auto_code.lower():
                    auto_code = True
                else:
                    auto_code = False
                config_lines[10] = f"auto_code = {auto_code}"
            else:
                add_new_user()
        elif choice == "10":
            if custom_scheme:
                add_new_user()
            else:
                pass
        config_file.close()
        os.remove(f"./config.txt")
        with open("./config.txt", "w+") as file:
            pass
        config_file = open("./config.txt", "r+")
        for line in config_lines:
            if line.strip() != "" and line != "-":
                line = f"{line}\n"
            config_file.write(line)
        config_file.close()
        master_printing_speed = 0


def menu(user, display_initiate, print_logs, default_colour, private_mode, error_colour, **print_speed):
    temp_print_speed = print_speed.get("print_speed", None)
    auto_code = print_speed.get("auto_code", False)
    print_speed = temp_print_speed
    mailing = False
    talking_to_self = False
    recipient_ip = ""
    if user != "":
        backup_user = user
    if display_initiate == None:
        display_initiate = False
    # ?@func is set to 0 as it will always trigger the while loop below
    func = 0
    animated_print(f"1. Encrypt New Message", speed=print_speed)
    animated_print(f"2. Decrypt Message", speed=print_speed)
    animated_print(f"3. Show Current Code", speed=print_speed)
    animated_print(f"4. Request Random Code", speed=print_speed)
    # ?Until function option 5, there was no variability, however as 'Initiate Filesystem' is not always shown, there are two different conditions
    if display_initiate:
        animated_print(f"5. Initiate Filesystem", speed=print_speed)
        animated_print(
            f"^ This must be run before any other functions will work!", speed=print_speed)
        animated_print(f"6. Launch Encryption Helper", speed=print_speed)
        animated_print(f"7. Secret Code", speed=print_speed)
        animated_print(f"8. Open Inbound Server", speed=print_speed)
        animated_print(f"9. Invite to Conversation", speed=print_speed)
        animated_print(f"10. Check Mailbox", speed=print_speed)
        animated_print(f"11. Manage Contacts", speed=print_speed)
        animated_print(f"12. Config Settings", speed=print_speed)
        animated_print(f"13. Reload", speed=print_speed)
        animated_print(f"14. Quit", speed=print_speed)
    else:
        animated_print(f"5. Encryption Helper", speed=print_speed)
        animated_print(f"6. Secret Code", speed=print_speed)
        animated_print(f"7. Open Inbound Server", speed=print_speed)
        animated_print(f"8. Invite to Conversation", speed=print_speed)
        animated_print(f"9. Check Mailbox", speed=print_speed)
        animated_print(f"10. Manage Contacts", speed=print_speed)
        animated_print(f"11. Config Settings", speed=print_speed)
        animated_print(f"12. Reload", speed=print_speed)
        animated_print(f"13. Quit", speed=print_speed)
    # *While loop to force the user to enter correct function num
    while func not in range(1, 14):
        try:
            func = input(f"Select one of these functions: ")
        except KeyboardInterrupt:
            print("")
            maybe_quit()
            Colours(default_colour)
            func = 0
        try:
            func = int(func)
        except ValueError:
            new_func = ""
            for char in func:
                try:
                    char = int(char)
                except:
                    pass
                if 'str' not in str(type(char)):
                    new_func += str(char)
            func = int(new_func)
        log(f"Function run: {func} Valid? {func in range(1,14)}",
            "execute_function", user, print_logs)
        # *Calls the appropiate function
        if func == 4:
            code, temp_file = randomcode(
                user, capitalize_user(get_current_user()), False, private_mode, print_logs, default_colour, error_colour)
            try:
                backup_code = code
            except:
                pass
        elif func == 1:
            # ?Sometimes @backup_code is not defined, and if it is, @showcode() module will be called, returning the @code to be used for the module being called
            try:
                newmessage(code, user, recipient_ip, None, prefix, None,
                           talking_to_self, error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, auto_code)
            except UnboundLocalError:
                code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                   print_logs, error_colour, default_colour)
                newmessage(code, user, recipient_ip, None, prefix, None,
                           talking_to_self, error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, auto_code)
        elif func == 2:
            try:
                retrievemessage(backup_code, user, capitalize_user(get_current_user()), prefix, recipient_ip, None, timestamp,
                                None, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
            except UnboundLocalError:
                code, prefix, timestamp = showcode(user, 1, private_mode,
                                                   print_logs, error_colour, default_colour)
                retrievemessage(code, user, capitalize_user(get_current_user()), prefix, recipient_ip, None, timestamp,
                                None, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
        elif func == 3:
            showcode(user, capitalize_user(get_current_user()), private_mode,
                     print_logs, error_colour, default_colour)
        # ?If display_initiate is set to true, the user will see this option, although it should only need to be run once
        elif func == 5:
            # *The same number will perform differently based on this condition
            if display_initiate:
                establish_tree()
            else:
                helper("all", backup_user)
        elif func == 6:
            if display_initiate:
                helper("all", backup_user)
            else:
                secretcode(user, capitalize_user(get_current_user()), default_colour,
                           print_logs, private_mode, error_colour)
        elif func == 7:
            if display_initiate:
                secretcode(user, capitalize_user(get_current_user()), default_colour,
                           print_logs, private_mode, error_colour)
            else:
                code, prefix, timestamp = showcode(
                    user, 1, private_mode, print_logs, error_colour, default_colour)
                date = timestamp.split("|")
                date = date[1]
                server_recieve(user, code, capitalize_user(get_current_user()), None, recipient_ip, timestamp, prefix,
                               date, default_colour, print_logs, private_mode, error_colour, display_initiate)
        elif func == 8:
            if display_initiate:
                code, prefix, timestamp = showcode(
                    user, 1, private_mode, print_logs, error_colour, default_colour)
                date = timestamp.split("|")
                date = date[1]
                server_recieve(user, code, capitalize_user(get_current_user()), None, recipient_ip, timestamp, prefix,
                               date, default_colour, print_logs, private_mode, error_colour, display_initiate)
            else:
                send_conversation_invite(
                    user, capitalize_user(get_current_user()), default_colour, private_mode, error_colour, print_logs, display_initiate)
        elif func == 9:
            if display_initiate:
                send_conversation_invite(
                    user, capitalize_user(get_current_user()), default_colour, private_mode, error_colour, print_logs, display_initiate)
            else:
                try:
                    check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                                  error_colour, default_colour, display_initiate, print_logs, private_mode)
                except UnboundLocalError:
                    code, prefix, timestamp = showcode(user, 1, private_mode,
                                                       print_logs, error_colour, default_colour)
                    check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                                  error_colour, default_colour, display_initiate, print_logs, private_mode)
        elif func == 10:
            if display_initiate:
                check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                              error_colour, default_colour, display_initiate, print_logs, private_mode)
            else:
                contact_func = 0
                animated_print(f"Contact manager:")
                animated_print(f"1. Add Contact")
                animated_print(f"2. Remove Contact")
                animated_print(f"3. Search For Contact")
                animated_print(f"4. List All Contacts")
                animated_print(f"5. Return To Main Menu")
                while contact_func not in range(1, 6):
                    try:
                        contact_func = input(f">> ")
                    except KeyboardInterrupt:
                        print("")
                        menu(user, display_initiate, print_logs,
                             default_colour, private_mode, error_colour, print_speed=0)
                    try:
                        contact_func = int(contact_func)
                    except ValueError:
                        if contact_func == None:
                            menu(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour, print_speed=0)
                        else:
                            contact_func = 0
                    if contact_func == 1:
                        new_name = privacy_input(
                            f"Enter contact name here", private_mode)
                        new_ip = privacy_input(
                            f"Enter MAC address here (or leave blank)", private_mode)
                        new_details = privacy_input(
                            f"Enter any additional details here", private_mode)
                        Contacts.add(new_name, new_ip, new_details)
                        contact_func = 0
                    elif contact_func == 2:
                        target_name = privacy_input(
                            f"Enter name of contact to be removed", private_mode)
                        Contacts.remove(target_name)
                        contact_func = 0
                    elif contact_func == 3:
                        search = privacy_input(
                            f"Enter the contact name here", private_mode)
                        result = Contacts.check_for(search)
                        if result != None:
                            animated_print(result)
                        else:
                            animated_print(
                                f"No contact matching {search} found!")
                        contact_func = 0
                    elif contact_func == 4:
                        Contacts.list_all()
                        contact_func = 0
                    elif contact_func == 5:
                        menu(user, display_initiate, print_logs,
                             default_colour, private_mode, error_colour, print_speed=0)
                    else:
                        animated_print(
                            f"Inavlid option selected!")
        elif func == 11:
            if display_initiate:
                contact_func = 0
                animated_print(f"Contact manager:")
                animated_print(f"1. Add Contact")
                animated_print(f"2. Remove Contact")
                animated_print(f"3. Search For Contact")
                animated_print(f"4. List All Contacts")
                animated_print(f"5. Return To Main Menu")
                while contact_func not in range(1, 6):
                    try:
                        contact_func = input(f">> ")
                    except KeyboardInterrupt:
                        print("")
                        menu(user, display_initiate, print_logs,
                             default_colour, private_mode, error_colour, print_speed=0)
                    try:
                        contact_func = int(contact_func)
                    except ValueError:
                        if contact_func == None:
                            menu(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour, print_speed=0)
                        else:
                            contact_func = 0
                    if contact_func == 1:
                        new_name = privacy_input(
                            f"Enter contact name here", private_mode)
                        new_ip = privacy_input(
                            f"Enter MAC address here (or leave blank)", private_mode)
                        new_details = privacy_input(
                            f"Enter any additional details here", private_mode)
                        Contacts.add(new_name, new_ip, new_details)
                        contact_func = 0
                    elif contact_func == 2:
                        target_name = privacy_input(
                            f"Enter name of contact to be removed", private_mode)
                        Contacts.remove(target_name)
                        contact_func = 0
                    elif contact_func == 3:
                        search = privacy_input(
                            f"Enter the contact name here", private_mode)
                        result = Contacts.check_for(search)
                        if result != None:
                            animated_print(result)
                        else:
                            animated_print(
                                f"No contact matching {search} found!")
                        contact_func = 0
                    elif contact_func == 4:
                        Contacts.list_all()
                        contact_func = 0
                    elif contact_func == 5:
                        menu(user, display_initiate, print_logs,
                             default_colour, private_mode, error_colour, print_speed=0)
                    else:
                        animated_print(
                            f"Inavlid option selected!")
            else:
                config_settings(user, capitalize_user(get_current_user()), default_colour,
                                print_logs, private_mode, error_colour)
        elif func == 12:
            if display_initiate:
                config_settings(user, capitalize_user(get_current_user()), default_colour,
                                print_logs, private_mode, error_colour)
            else:
                initiate()
        elif func == 13:
            if display_initiate:
                initiate()
            else:
                exit()
        elif func == 14:
            if display_initiate:
                exit()
        else:
            animated_print(f"Invalid Fuction!")


def login(display_initiate, user_account_name, error_colour, default_colour, print_logs, private_mode, auto_code):
    access, attempts, username_input, password_input = False, 3, "", ""
    animated_print(
        f"Welcome to FiEncrypt! Enter your credientials below!")
    while not access:
        while username_input == None or username_input.strip() == "":
            username_input = privacy_input(f"Username", is_private())
            if username_input == None or username_input.strip() == "":
                animated_print(
                    f"{error_colour}WARNING: Username cannot be blank!")
                Colours(default_colour)
        while password_input == None or password_input.strip() == "":
            password_input = privacy_input(f"Password", 1)
            if password_input == None or password_input.strip() == "":
                animated_print(
                    f"{error_colour}WARNING: Password cannot be blank!")
                Colours(default_colour)
        # table = set_credentials()
        # password_table = validate(username_input, password_input)
        access = validate_login(username_input, password_input)
        if attempts == 0:
            animated_print(f"0 Attempts left! Game over brother!")
            self_terminate(True)
        elif access:
            if private_mode:
                animated_print(f"Access granted! Welcome @Anonymous!")
            else:
                animated_print(f"Access granted! Welcome @{capitalize_user(username_input)}")
            current_user = get_current_user(new_user=username_input)
            menu(pass_user(), display_initiate, print_logs,
                 default_colour, private_mode, error_colour, auto_code=auto_code)
        elif not access:
            current_user = username_input
            username_input, password_input = None, None
            animated_print(
                f"Incorrect Login! {attempts} attempts left! Try again!")
            log(f"User: {str(current_user)} Success?: N. Attempts left: {str(attempts)}",
                "login", current_user, print_logs)
            attempts -= 1


def initiate():
    ImportStructure("logic")
    ImportStructure("system")
    log("--== FiEncrypt Warming Up! ==--", "", pass_user(), False)
    log("Logic modules imported!", "module_start", pass_user(), False)
    log("System modules imported!", "module_start", pass_user(), False)
    ImportStructure("string")
    log("String modules imported!", "module_start", pass_user(), False)
    ImportStructure("network")
    log("Network modules imported!", "module_start", pass_user(), False)
    home_directory, operating_system, user = enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code = retrieve_config_settings()
    error_colour = "\033[91m"
    if colour_enabled:
        Colours(default_colour)
    else:
        Colours(None)
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        if len(credential_lines) < 2:
            animated_print(
                f"Welcome to FiEncrypt! Please create a user account by entering a username and password below!")
            add_new_user()
    login(display_initiate, user, error_colour,
          default_colour, print_logs, private_mode, auto_code)


initiate()
