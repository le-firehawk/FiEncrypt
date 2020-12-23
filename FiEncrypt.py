import contextlib
from scapy import *
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


class ImportStructure:
    """Staggered approach for importing modules by category, can be called at any time"""

    def __init__(self, import_set):
        if import_set == "logic":
            # By declaring modules as global variables, they can be accessed as normal
            global math, time, random, datetime, notification
            import math
            import time
            import random
            import datetime
            from plyer import notification
        elif import_set == "system":
            global os, sys, shutil, subprocess, zipfile, ctypes, hashlib, Image, pyaudio, wave, playsound
            import os
            import sys
            import shutil
            import subprocess
            import zipfile
            import ctypes
            import hashlib
            from PIL import Image
            import pyaudio
            import wave
            from playsound import playsound
        elif import_set == "string":
            global getpass, textwrap
            import getpass
            import textwrap
        elif import_set == "network":
            global urllib, socket, netifaces, tqdm
            import urllib.request as urllib
            import socket
            import tqdm
            try:
                import netifaces
            except:
                pass
        elif import_set == "gui":
            global gui
            import PySimpleGUI as gui


class Colours:
    """Manages application of colour codes for the standard out"""

    def __init__(self, colour, **kwargs):
        force_apply, self.error, self.reset = "\033[91m", "\033[0m", kwargs.get("force", False)
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

    def __init__(self, user, current_user, print_logs, default_colour, error_colour, private_mode):
        """Gathers a list of all names of contacts present in the Contacts directory"""
        self.user, self.current_user, self.print_logs, self.default_colour, self.error_colour, self.private_mode, self.contact_names = user, current_user, print_logs, default_colour, error_colour, private_mode, []
        enter_home_directory(
            next_step=f"./{hash_current_user(current_user.lower().strip())}/contacts")
        for root, dirs, files in os.walk(f"."):
            for name in files:
                self.contact_names.append(name.replace(".txt", ""))

    def check_for(self, contact_name):
        """Checks for the name passed as a parameter against all identified names in Contacts directory"""
        for contact in self.contact_names:
            enter_home_directory()
            os.chdir(f"./{hash_current_user(current_user.lower().strip())}/contacts")
            if contact_name.lower() in contact.lower():
                enter_home_directory()
                os.chdir(f"./{hash_current_user(current_user.lower().strip())}/contacts")
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
                    log(f"Contact Search: {contact_name} - {contact_lines}",
                        "contactManager", self.current_user, self.print_logs)
                    return contact_lines[0], contact_lines[1], contact_lines[2], contact_lines[3]
        log(f"Contact Search: {contact_name} - {[None, None, None, None]}",
            "contactManager", self.current_user, self.print_logs)
        return None, None, None, None

    def add_ip(self, contact_name, ip):
        """Locates a contact's file and appends the ip parameter into the relevant line of said file"""
        enter_home_directory(
            next_step=f"./{hash_current_user(current_user.lower().strip())}/contacts")
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
        log(f"Contact Updated: {contact_name}({contact_lines[1]}) New IP: {ip}",
            "contactManager", self.current_user, self.print_logs)

    def add(self, contact_name, mac, details):
        """Adds a new contact file into the Contacts directory, with all details being written"""
        enter_home_directory(
            next_step=f"./{hash_current_user(current_user.lower().strip())}/contacts")
        with open(f"./{contact_name}.txt", "w+") as new_contact:
            new_contact.write(f"{contact_name}\n{mac}\n-\n{details}")
        log(f"New Contact: {contact_name}({mac})",
            "contactManager", self.current_user, self.print_logs)

    def remove(self, contact_name):
        """Deletes a contact's file, if the search returns a result"""
        enter_home_directory(
            next_step=f"./{hash_current_user(current_user.lower().strip())}/contacts")
        name, mac, ip, details = self.check_for(contact_name)
        if None in [name, mac, ip, details]:
            animated_print(f"Unable to locate contact to delete!")
        else:
            os.remove(f"./{name.strip()}.txt")
            log(f"Contact Removed: {name}({mac})", "contactManager",
                self.current_user, self.print_logs)

    def list_all(self):
        """Lists every contact name found within the Contacts directory"""
        if self.contact_names == []:
            animated_print(f"No contacts found in FiEncrypt directory!")
        else:
            for i, name in enumerate(self.contact_names):
                animated_print(f"Contact {i+1}: ")
                enter_home_directory(
                    next_step=f"./{hash_current_user(current_user.lower().strip())}/contacts")
                with open(f"./{name}.txt", "r+") as contact:
                    contact_lines = contact.readlines()
                    animated_print(
                        f"Name: {contact_lines[0]}\nMAC Address: {contact_lines[1]}\nLast IP: {contact_lines[2]}\nDetails:")
                    for i, line in enumerate(contact_lines):
                        if i > 2 and line != "\n":
                            spec_print = contact_lines[i].replace("\n", "")
                            animated_print(f"{spec_print}\n")
        log(f"Contact Dump: {self.contact_names}",
            "contactManager", self.current_user, self.print_logs)


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
    elif error:
        log("Invalid Colour passed from config file!", "fileManager", get_current_user(), None)
        raise Exception("Invalid Colour!")
    else:
        pass


def animated_print(string, **kwargs):
    """Accepts a string to be printed, along with the optional parameter for how long Python should wait before printing the next character"""
    try:
        speed = kwargs.get('speed', None)
        newline = kwargs.get('newline', False)
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
        if newline:
            print("\n")
        print("")
        time.sleep(0.2)
    except KeyboardInterrupt:
        print("")
        maybe_quit()
        print(applied_default_colour)
    except:
        print("\nCRASH! Restarting FiEncrypt!")
        log("Unknown error during output!", "moduleManager", get_current_user(), None)
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
        sys.stdout.write("\033[F"), sys.stdout.write("\033[K")
    elif "y" in quit.lower():
        sys.stdout.write("\033[F"), sys.stdout.write("\033[K")
        clear_cache()
        log("FiEncrypt shutting down!", "moduleManager", get_current_user(), None)
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
    succes_count = 0
    if sys.platform == "win32":
        subprocess.check_call(
            ["attrib", "+H", f"../FiEncrypt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./Contacts"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./config.txt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./logs.txt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./code.txt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./inbox.txt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./messagein.txt"])
        succes_count += 1
        subprocess.check_call(
            ["attrib", "+H", f"./messageout.txt"])
        succes_count += 1
        try:
            subprocess.check_call(
                ["atrib", "+H", f"./anarchy2.ico"])
            succes_count += 1
        finally:
            try:
                subprocess.check_call(
                    ["attrib", "+H", f"./anarchy.png"])
                succes_count += 1
            finally:
                try:
                    subprocess.check_call(["attrib", "+H", f"./build"])
                    succes_count += 1
                finally:
                    try:
                        subprocess.check_call(["attrib", "+H", f"./cache"])
                        succes_count += 1
                    finally:
                        try:
                            subprocess.check_call(["attrib", "+H", f"./dist"])
                            succes_count += 1
                        finally:
                            try:
                                subprocess.check_call(["attrib", "+H", f"./FiEncrypt.egg-info"])
                                succes_count += 1
                            finally:
                                try:
                                    subprocess.check_call(
                                        ["attrib", "+H", f"./{hash_current_user(get_current_user().lower().strip())}"])
                                    succes_count += 1
                                except:
                                    pass
        log(f"Files hidden ({succes_count}/15)", "fileManager", get_current_user(), None)


def set_home_directory(operating_system):
    """Performs a variety of checks, including the drive letter being used, to determine the ideal location for FiEncrypt directory to be created"""
    if operating_system == "win32":
        file_path = sys.argv[0].split(":\\")
        if ".py" in str(file_path):
            file_path[1] = file_path[1].replace("\\\FiEncrypt.py", "")
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
            #log(f"Existing FiEncrypt directory found!", "fileManager", None, None)
            return path, user
        else:
            os.mkdir(path)
            #log(f"New FiEncrypt directory created!", "fileManager", None, None)
            return path, user
    elif operating_system == "linux":
        file_path = os.getcwd()
        user = substring(file_path, f"home/", 2)
        user = substring(user, f"/", 0)
        path = f"/home/{user}/FiEncrypt"
        if os.path.exists(path):
            #log(f"Existing FiEncrypt directory found!", "fileManager", None, None)
            return path, user
        else:
            os.mkdir(path)
            #log(f"New FiEncrypt directory created!", "fileManager", None, None)
            return path, user


def enter_home_directory(**kwargs):
    """Changes the current directory to the base level of the FiEncrypt directory, for ease of reference to files within"""
    next_step, operating_system = kwargs.get(
        "next_step", None), pass_os()
    home_directory, user = set_home_directory(operating_system)
    os.chdir(home_directory)
    if next_step != None:
        try:
            os.chdir(next_step)
            log(f"Home directory entered, stepped into {next_step}", "fileManager", None, None)
        except:
            pass
    else:
        pass
        #log(f"Home directory entered", "fileManager", None, None)
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
    display_license()
    with open(f"./config.txt", "w+") as config_file:
        default_config = ["# FiEncrypt", "[config.txt]", "debug_mode = False",
                          "display_initiate = False", "-", "-", "-", "-", "graphic_mode = False", "private_mode = False", "auto_code = False", "voice_message = 15s"]
        for line in default_config:
            config_file.write(f"{line}\n")
    with open(f"./cache_settings.txt", "w+") as cache_settings_file:
        default_cache_config = ["# FiEncrypt", "[cache_settings.txt]",
                                "auto-sync = False", "max_size = 2GB"]
        for line in default_cache_config:
            cache_settings_file.write(f"{line}\n")
    with open(f"./code.txt", "w+") as code_file:
        pass
    with open(f"./logs.txt", "w+") as logs_file:
        pass
    with open(f"./messagein.txt", "w+") as message_in_file:
        pass
    with open(f"./messageout.txt", "w+") as message_out_file:
        pass
    with open(f"./CREDENTIALS.txt", "w+") as credientials:
        pass
    urllib.request.urlretrieve(
        "https://www.gnu.org/licenses/agpl-3.0.txt", f"./LICENSE")
    os.mkdir(f"./cache")
    log("FiEncrypt directory structure established! ['./config.txt', './cache_settings.txt', './code.txt', './logs.txt', './messagein.txt', './messageout.txt', './CREDENTIALS.txt', './LICENSE', './cache']", "fileManager", get_current_user(), None)
    if sys.platform == "win32":
        hide_tree()


def clear_cache():
    """Deletes all files saved to the cache during the user's session"""
    enter_home_directory()
    try:
        shutil.rmtree(f"./cache")
        os.mkdir(f"./cache")
        log("FiEncrypt public cache reset!", "fileManager", get_current_user(), None)
    except:
        pass


def add_new_user():
    """Creates user login using SHA256, saved under CREDENTIALS.txt"""
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
        os.mkdir(f"./{hash_current_user(username.lower())}")
    except FileExistsError:
        pass
    os.chdir(f"./{hash_current_user(username.lower())}")
    os.mkdir(f"./inbox")
    os.mkdir(f"./files")
    os.mkdir(f"./contacts")
    with open(f"./inbox/messages.txt", "w+") as indox_file:
        pass
    animated_print(f"New user {username} successfully added to FiEncrypt!")
    log(f"New user {username} added to FiEncrypt and personal file tree created!",
        "fileManager", get_current_user, None)


def validate_login(username, password):
    """Checks both the username and password entered by encrypting them and running a comparison"""
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
                    log(f"Successful login to FiEncrypt", "loginManager", username, None)
                    return True
            else:
                valid_username = False
    log(f"Inavlid login to FiEncrypt",
        "loginManager", username, None)
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
    log(f"Host IP requested! IP: {your_ip}", "networkManager", get_current_user(), None)
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
        log("ARP Scan aborted!", "networkManager", get_current_user(), None)
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
                    log(f"ARP Scan run for MAC {mac} on {IP_str[0]}.{IP_str[1]}.{i}.0/24 Result: {str(format(mapping['IP']))}",
                        "networkManager", get_current_user(), None)
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
                log(f"ARP Scan run for MAC {mac} on {scan_ip} Result: {str(format(mapping['IP']))}", "networkManager", get_current_user(
                ), None)
                return str(format(mapping['IP']))
    return None


@contextlib.contextmanager
def ignore_stderr():
    """Overrides behaviour of Python's standard error (stderr) to supress errors raised during creation of voice message"""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


def is_private():
    """Returns 1 or 0 based on whether private mode is enabled, effectively hiding any input under privacy_input() module"""
    enter_home_directory()
    private_mode = retrieve_config_settings(exclusive="private_mode")
    if private_mode:
        return 1
    else:
        return 0


def get_current_user(**kwargs):
    """Collects the name of the FiEncrypt user account that is currently logged in and saves it to a global variable"""
    global current_user
    try:
        old_user = current_user
    except:
        pass
    current_user = kwargs.get('new_user', None)
    if current_user == None:
        try:
            current_user = old_user
        except UnboundLocalError:
            current_user = None
    #log(f"Current user requested!", "loginManager", current_user, None)
    return current_user


def get_foreign_user(**kwargs):
    """Collects the name of the FiEncrypt user account you are currently communicating with over the network and saves it to a global variable"""
    global foreign_user
    try:
        old_foreign_user = foreign_user
    except:
        pass
    foreign_user = kwargs.get('new_user', None)
    if foreign_user == None:
        try:
            foreign_user = old_foreign_user.replace("\n", "")
        except UnboundLocalError:
            foreign_user = None
        except AttributeError:
            foreign_user = None
        return foreign_user
    elif foreign_user == "\\reset":
        foreign_user = None
        return foreign_user
    else:
        foreign_user = foreign_user.replace("\n", "")
        log(f"Foreign user requested! Foreign user: {foreign_user}",
            "networkManager", get_current_user(), None)
        return foreign_user


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
    contact_manager = Contacts(user, get_current_user().lower().strip(),
                               print_logs, default_colour, error_colour, private_mode)
    if "." not in name:
        return contact_manager.check_for(name)
    else:
        return name


def retrieve_config_settings(**kwargs):
    """Saves all relevant settings from the config file to a series of variables that are all returned"""
    exclusive_mode = kwargs.get("exclusive", None)
    enter_home_directory()
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
        voice_record_time = config_lines[11].split(" = ")
        voice_record_time = voice_record_time[1]
        if exclusive_mode == None:
            return print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code, voice_record_time
        elif exclusive_mode == "print_logs":
            return print_logs
        elif exclusive_mode == "display_initiate":
            return display_initiate
        elif exclusive_mode == "graphic_mode":
            return graphic_mode
        elif exclusive_mode == "private_mode":
            return private_mode
        elif exclusive_mode == "colour_enabled":
            return colour_enabled
        elif exclusive_mode == "default_colour":
            return default_colour
        elif exclusive_mode == "auto_code":
            return auto_code
        elif exclusive_mode == "voice_record_time":
            return voice_record_time


def log(string, log_type, user, display):
    """Records events in the log file based on paramters passed, also printing them to screen when display paramter is True"""
    enter_home_directory()
    if user == None:
        try:
            username = get_current_user()
            if username == None:
                raise NameError
        except NameError:
            username = "Undefined"
    else:
        username = user
    if display == None:
        if "FiEncrypt" in os.getcwd():
            with open(f"./config.txt", "r") as config_file:
                config_lines = config_file.read().split("\n")
                if "debug_mode" in config_lines[2]:
                    display = config_lines[2].split(" = ")
                    display = to_boolean(display[0])
        else:
            display = False

    log_entry = f"{datetime.datetime.now()}: {log_type} - {string}, Username: {username}, OS: {sys.platform}"
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
    """Takes a username and capitalizes each word"""
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
        src = f". /anarchy.png"
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


def get_recipient_ip(user, display_initiate, print_logs, default_colour, private_mode, error_colour, temp_sc, **kwargs):
    """Obtains the desired IP, MAC, or contact name that a message is to be sent to. Calls arp_scan() and mac_resolve() modules as appropiate"""
    target_mac, target_name, is_invite, confirm_ip, message = None, None, kwargs.get(
        "is_invite", False), kwargs.get("confirm_ip", None), kwargs.get("message", None)
    if confirm_ip == None:
        ip = privacy_input(
            "Enter the IP, MAC address or contact name of the recipient", private_mode)
    else:
        ip = confirm_ip
    if ip == None:
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif is_invite:
        if "@" in ip:
            ip = ip.split("@")
            target_name = ip[0].strip()
            ip = ip[1].strip()
            if "." not in ip:
                contact_search = Contacts(user, get_current_user().lower().strip(
                ), print_logs, default_colour, error_colour, private_mode)
                target_name, target_mac, target_ip, details = contact_search.check_for(
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
                    contact_search.add_ip(target_name, ip)
            else:
                target_mac = None
    elif "@" in ip:
        ip = ip.split("@")
        expected_user = ip[0].strip()
        ip = ip[1].strip()
        if "." not in ip:
            contact_search = Contacts(user, get_current_user().lower().strip(
            ), print_logs, default_colour, error_colour, private_mode)
            target_name, target_mac, target_ip, details = contact_search.check_for(
                ip)
            target_name = target_name.replace("\n", "")
            if target_ip != None:
                ip = target_ip.strip()
            else:
                ip = mac_resolve(target_mac.strip(), print_logs)
            if ip == None:
                animated_print(
                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                Colours(default_colour)
                connected = False
            else:
                contact_search.add_ip(target_name, ip)
        validated, temp_sc = validate_foreign_user(
            ip, expected_user, print_logs, temp_sc, message=message)
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
                                 default_colour, private_mode, error_colour, temp_sc)
        time.sleep(8)
    if "." not in ip:
        if ":" in ip:
            temp = ip
            contact_search = Contacts(user, get_current_user().lower().strip(
            ), print_logs, default_colour, error_colour, private_mode)
            target_name, target_mac, target_ip, details = contact_search.check_for(
                temp)
            target_name = target_name.replace("\n", "")
            if target_ip.strip() != None:
                ip = target_ip.strip()
            else:
                ip = mac_resolve(target_mac.strip(), print_logs)
            if ip == None:
                animated_print(
                    f"{error_colour}WARNING: Unable to resolve IP address through ARP!")
                Colours(default_colour)
                connected = False
            else:
                contact_search.add_ip(target_name, ip)
        else:
            try:
                contact_search = Contacts(user, get_current_user().lower().strip(
                ), print_logs, default_colour, error_colour, private_mode)
                target_name, mac, target_ip, details = contact_search.check_for(
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
                        contact_search.add_ip(target_name, ip)
            except ValueError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact name entered!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour, temp_sc)
            except TypeError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact details!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour, temp_sc)
            except AttributeError:
                animated_print(
                    f"{error_colour}WARNING: Invalid contact details!")
                Colours(default_colour)
                connected = False
                get_recipient_ip(user, display_initiate, print_logs,
                                 default_colour, private_mode, error_colour, temp_sc)
    valid_vars = check_vars(ip, target_mac, target_name)
    return valid_vars[0], valid_vars[1], valid_vars[2], temp_sc


def gnu_ip_resolve(print_logs, private_mode):
    """Employs the modules to handle obtaining an IP address from a GNU/Linux system with multiple interfaces"""
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
    log(f"IP of GNU/Linux system requested! IP: {ip}", "networkManager", get_current_user(), None)
    return ip


def secretcode(user, current_user, default_colour, print_logs, private_mode, error_colour):
    """Accepts secret codes to execute special behaviours, like an easter egg! NO PEAKING!"""
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
                "encryptionManager", current_user, print_logs)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                       print_logs, private_mode, error_colour)
        else:
            pass
    except ValueError:
        animated_print(
            f"{error_colour}WARNING: Code format not valid!")
        Colours(default_colour)
        log("Secret Code Entered! Valid? False",
            "encryptionManager", current_user, print_logs)
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
            "encryptionManager", current_user, print_logs)
        secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_colour,
                   print_logs, private_mode, error_colour)
    else:
        log("Secret Code Entered! Valid? True",
            "encryptionManager", current_user, print_logs)
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
                "https://archive.org/download/ramranch/Ram%20Ranch.mp3", f"./Music/ramranch.mp3")
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
    """Outputs the current encryption code in various forms, based on input parameters"""
    enter_home_directory()
    with open(f"./code.txt", "r+") as temp_file:
        code = temp_file.read()
    if current_user != 1 and current_user != 2:
        animated_print(
            f"This is the current code saved in the code.txt file:")
        if code == "":
            animated_print(
                f"{error_colour}WARNING: No code present in the code.txt file! Either it has not been generated or manually overwritten!")
            Colours(default_colour)
        else:
            animated_print(code)
        log(f"Existing encryption requested!", "encryptionManager", current_user, print_logs)
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    elif current_user == 2:
        pass
    else:
        try:
            code = code.split("_")
            timestamp, prefix, code = code[0], code[2], code[1]
            return code, prefix, timestamp
        # TODO: Find a way to bypass the associated errors with not having a code saved in the file
        except:
            randomcode(user, get_current_user().lower().strip(), True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
            showcode(
                user, 1, private_mode, print_logs, error_colour, default_colour)


def even_num():
    """Produces a random even number between 2 and (number between 4 and 100)"""
    num2 = 1
    while (num2 % 2) / 2 != 0:
        num1 = random.randint(4, 100)
        num2 = random.randint(2, int(num1))
    return num2


def parse_size(size, filename):
    try:
        size = int(size)
    except:
        return None
    mb_extract = size / 1048576
    if mb_extract > 1024:
        gb_extract = size / 1073741824
        return f"{float(gb_extract)}GB"
    else:
        if int(mb_extract) == 0 and "." not in filename.strip():
            return "Directory"
        else:
            return f"{int(mb_extract)}MB"


def stringify_filepath(filepath):
    return filepath.strip().replace(" ", "\ ").replace(
        "'", "\\'").replace("(", "\\(").replace(")", "\\)")


def random_filler(length, string):
    """Produces filler to accompany a message before it is send over the network"""
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
    """Reconstructs message with filler removed"""
    new_string = ""
    for k, char in enumerate(string):
        if k in range(0, int(int(length)/2)):
            pass
        else:
            new_string += char
    new_string = new_string[:int(f"-{int(int(length)/2)}")]
    return new_string


def randomcode(user, current_user, auto_request, private_mode, print_logs, default_colour, error_colour, **auto_code):
    """Generates fresh encryption code"""
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
        log("Invalid Encryption code generated! Retrying...",
            "encryptionManager", get_current_user(), None)
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
            log("Code override ordered... leaving blank!",
                "encryptionManager", get_current_user(), None)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    try:
        new_string = f"${str(a)}_{str(rand_code)}_${str(b)}#"
        if lazy == None:
            randomcode(user, current_user, auto_request, private_mode,
                       print_logs, default_colour, error_colour, auto_code=auto_code)
        if "y" in lazy.lower():
            pass
        else:
            animated_print(str(
                f"Current code as of {str(datetime.datetime.now())} is ${str(a)}_{str(rand_code)}_${b}#"))
        enter_home_directory()
        with open("./code.txt", "w+") as code_file:
            code_file.seek(0)
            code_file.truncate()
            code_file.write(new_string)
        log(f"New encryption code requested!",
            "encryptionManager", current_user, print_logs)
        enter_home_directory()
        hide_tree()
        if not auto_code:
            animated_print(f"New code successfully written to code.txt file")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        else:
            pass
    except UnboundLocalError:
        log("Invalid Encryption code generated! Retrying...",
            "encryptionManager", get_current_user(), None)
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_colour, error_colour, auto_code=auto_code)


def newmessage(code, user, recipient_ip, temp_sc, prefix, date, talking_to_self, error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, auto_code, **kwargs):
    """Allows user to create and send an encrypted message"""
    previous_message, poked, voice_message, outbound_file, manual, faulty_override, stored_message, sc = kwargs.get(
        "message", ""), kwargs.get("poked", False), False, False, False, kwargs.get("faulty", False), kwargs.get("stored_message", ""), temp_sc
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
    if (recipient_ip == "" or code2 == "") and not faulty_override:
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
    elif faulty_override:
        code2 = code
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
            if faulty_override and stored_message.strip() != "":
                message_text = stored_message
            else:
                message_text = privacy_input(
                    f"How do you feel", private_mode, line_break=True)
            if message_text == None:
                Colours(default_colour)
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            while message_text.strip() == "":
                animated_print(
                    f"{error_colour}WARNING: No message was entered!")
                Colours(default_colour)
                message_text = privacy_input(
                    f"How do you feel", private_mode)
            if message_text == None:
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                newmessage(code, user, "", temp_sc, prefix, date, talking_to_self,
                           error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, message=previous_message)
        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    elif conversation_mode and recipient_ip != "":
        try:
            if faulty_override and stored_message.strip() != "":
                message_text = stored_message
            else:
                message_text = privacy_input(
                    f"Enter a reply here", private_mode, line_break=True)
            if message_text == None:
                Colours(default_colour)
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            while message_text.strip() == "":
                animated_print(
                    f"{error_colour}WARNING: No message was entered!")
                Colours(default_colour)
                message_text = privacy_input(
                    f"Enter a reply here", private_mode)
            if message_text == None:
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
                newmessage(code, user, "", temp_sc, prefix, date, talking_to_self,
                           error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, message=previous_message)
        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    else:
        if faulty_override and stored_message.strip() != "":
            message_text = stored_message
        else:
            message_text = privacy_input(
                f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colours(default_colour)
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            menu(user, display_initiate, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        while message_text.strip() == "":
            animated_print(
                f"{error_colour}WARNING: No message was entered!")
            Colours(default_colour)
            message_text = privacy_input(
                f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colours(default_colour)
            animated_print(f"Returning to menu...")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            menu(user, display_initiate, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    if message_text.strip() == "\\exit" and recipient_ip != "":
        skip = True
        mailbox = False
    else:
        skip = False
    if "\\v" in message_text.strip().lower():
        enter_home_directory()
        voice_file = f"./cache/voice_message.wav"
        with ignore_stderr():
            try:
                voice_record_time = retrieve_config_settings(exclusive="voice_record_time")
                if str(voice_record_time).strip().lower().endswith("s"):
                    voice_record_time = int(str(voice_record_time).replace("s", "").strip())
                    if voice_record_time > 120:
                        voice_record_time = 120
                    indicator = f"{voice_record_time} Seconds"
                elif str(voice_record_time).strip().lower().endswith("m"):
                    indicator = f"{float(str(voice_record_time).replace('m', '').strip())} Minutes"
                    voice_record_time = int(str(voice_record_time).replace("m", "").strip()) * 60
                else:
                    try:
                        voice_record_time = int(voice_record_time)
                        indicator = f"{voice_record_time} Seconds"
                    except:
                        voice_record_time = 15
                        indicator = "15 Seconds"
                if voice_record_time > 120:
                    voice_record_time = 120
                    indicator = "2 Minutes"
                voice_module = pyaudio.PyAudio()
                chunk, FORMAT, channels, sample_rate, record_seconds = 1024, pyaudio.paInt16, 1, 44100, voice_record_time
                stream = voice_module.open(format=FORMAT, channels=channels,
                                           rate=sample_rate, input=True, output=True, frames_per_buffer=chunk)
            except OSError:
                animated_print(f"{error_colour}WARNING: Unable to detect microphone!")
                Colours(default_colour)
                log("Unable to detect microphone!", "voiceManager", get_current_user(), print_logs)
            else:
                frames = []
                animated_print(f"Recording for {indicator}")
                for i in range(int((44100 / chunk) * record_seconds)):
                    data = stream.read(chunk, exception_on_overflow=False)
                    frames.append(data)
                stream.stop_stream()
                stream.close()
                voice_module.terminate()
                audio_out = wave.open(voice_file, "wb")
                audio_out.setnchannels(channels)
                audio_out.setsampwidth(voice_module.get_sample_size(FORMAT))
                audio_out.setframerate(sample_rate)
                audio_out.writeframes(b"".join(frames))
                audio_out.close()
    if message_text.count("\"\"") >= 2:
        temp_message_text = message_text.split("\"\"")
        if message_text.count("\"\"") == 2:
            if temp_message_text[1].replace("\"\"", "") in previous_message:
                message_text = f"YOU ({get_foreign_user().capitalize()}): {temp_message_text[1].strip()} -> {temp_message_text[0].strip()} {temp_message_text[2].strip()}"
        else:
            message_text = f"{temp_message_text[0].strip()}"
            for i in range(2, len(temp_message_text), 2):
                message_text += f"YOU ({get_foreign_user().capitalize()}): {temp_message_text[i-1].strip()} -> {temp_message_text[i].strip()}"
    if "\\file" in message_text.strip() or "\\v" in message_text.strip():
        outbound_file = True
        if "\\v" in message_text.strip():
            voice_message = True
            if message_text.lower().strip() == "\\v":
                append_to_message = privacy_input(f"Enter additional text", private_mode)
                if append_to_message.strip() != "":
                    message_text = f"{message_text.strip()} {append_to_message}".strip()
        else:
            voice_message = False
    else:
        outbound_file = False
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
                # time.sleep(0.2)
                # for k in range(1, int(line_breaks) + 2):
                #    sys.stdout.write("\033[F")
                # time.sleep(0.2)
                animated_print(f"{temp_output_phrase}")
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
        for i in range(len(message_text)):
            if message_text[i] == output_phrase[i]:
                if message_text[i].strip() != "" and output_phrase[i].strip() != "":
                    # ?It is really difficult to nail down what causes either @code_seg1 or 2 to equal zero, so I added this catcher instead
                    for _ in range(2):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                    output_file.close()
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_colour, error_colour, auto_code=True)
                    code, prefix, timestamp = showcode(
                        user, 1, private_mode, print_logs, error_colour, default_colour)
                    newmessage(code, user, recipient_ip, temp_sc, prefix, date, talking_to_self, error_colour,
                               default_colour, private_mode, print_logs, mailing, display_initiate, True, faulty=True, stored_message=message_text)
            else:
                pass
        else:
            output_file.write(scrambled_output_phrase)
            output_file.close()
            log(f"New encrypted message successfully generated!",
                "encryptionManager", current_user, print_logs)
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
        if sc == None:
            link = socket.socket()
        connected = False
        talking_to_self = False
        while not connected:
            try:
                if conversation_mode and recipient_ip != "":
                    ip = recipient_ip
                elif recipient_ip == "":
                    ip, target_mac, target_name, sc = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour, sc, message=scrambled_output_phrase)
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
                    log(f"Message sent to self... wtf?",
                        "networkManager", current_user, print_logs)
                    if len(str(code2)) != 2 and not manual:
                        retrievemessage(
                            code, user, 2, backup_prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                    elif manual != None and manual:
                        retrievemessage(
                            code2, user, 2, None, recipient_ip, temp_sc, None, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                    else:
                        retrievemessage(
                            code, user, 2, backup_prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, None, display_initiate)
                else:
                    if sc == None:
                        link.connect((recipient_ip, 15753))
                        sc = link
                    connected = True
                    mailbox = False
            except ConnectionRefusedError:
                log(f"Message delivery refused! Redirecting to {ip}'s mailbox!", "networkManager", get_current_user(
                ), print_logs)
                connected = False
                try:
                    error_link = socket.socket()
                    error_link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_colour, error_colour, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except UnboundLocalError:
                        animated_print(
                            f"{error_colour}WARNING: Unable to reach the host! Try a different address!")
                        Colours(default_colour)
                        ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour, None, message=scrambled_output_phrase)
                        if ip == None or ip.strip() == "":
                            menu(user, None, print_logs, default_colour,
                                 private_mode, error_colour, print_speed=0)
                        elif "." not in ip:
                            if ":" in ip:
                                if ip == None:
                                    menu(user, None, print_logs, default_colour,
                                         private_mode, error_colour, print_speed=0)
                                temp = ip
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_colour, error_colour, private_mode)
                                target_name, target_mac, target_ip, details = contact_search.check_for(
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
                                    contact_search.add_ip(target_name, ip)
                            else:
                                try:
                                    contact_search = Contacts(user, get_current_user().lower().strip(
                                    ), print_logs, default_colour, error_colour, private_mode)
                                    target_name, mac, target_ip, details = contact_search.check_for(
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
                                            contact_search.add_ip(target_name, ip)
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
                log(f"Message delivery override! Redirecting to {ip}'s mailbox!", "networkManager", get_current_user(
                ), print_logs)
                try:
                    error_link = socket.socket()
                    error_link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_colour, error_colour, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                    except:
                        animated_print(f"Aborting...")
                        menu(user, None, print_logs, default_colour,
                             private_mode, error_colour, print_speed=0)
            except TimeoutError:
                connected = False
                log(f"Message delivery timeout! Redirecting to {ip}'s mailbox!", "networkManager", get_current_user(
                ), print_logs)
                try:
                    error_link = socket.socket()
                    error_link.connect((ip, 19507))
                    connected = True
                    mailbox = True
                    skip = True
                except KeyboardInterrupt:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_colour, error_colour, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                    except:
                        pass
                    animated_print(f"Aborting...")
                    menu(user, None, print_logs, default_colour,
                         private_mode, error_colour, print_speed=0)
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_colour, error_colour, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
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
                                                                       default_colour, private_mode, error_colour, None, message=scrambled_output_phrase)
                    else:
                        contact_ip = Contacts(user, get_current_user().lower().strip(
                        ), print_logs, default_colour, error_colour, private_mode)
                        contact_ip.add_ip(target_name, ip)
                    if "." not in ip:
                        if ":" in ip:
                            if ip == None:
                                menu(user, None, print_logs, default_colour,
                                     private_mode, error_colour, print_speed=0)
                            temp = ip
                            contact_search = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_colour, error_colour, private_mode)
                            target_name, target_mac, target_ip, details = contact_search.check_for(
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
                                contact_search.add_ip(target_name, ip)
                        else:
                            try:
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_colour, error_colour, private_mode)
                                target_name, mac, target_ip, details = contact_search.check_for(
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
                                        contact_search.add_ip(target_name, ip)
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
                log(f"Message delivery OSError! Redirecting to {ip}'s mailbox!", "networkManager", get_current_user(
                ), print_logs)
                connected = False
                if ip == None:
                    pass
                else:
                    ip = ip.replace("\n", "")
                try:
                    error_link = socket.socket()
                    error_link.connect((ip, 19507))
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
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_colour, error_colour, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except:
                        animated_print(
                            f"{error_colour}WARNING: Unable to reach the host! Try a different address!")
                    Colours(default_colour)
                    if ip == None or ip.strip() == "":
                        ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_colour, private_mode, error_colour, None, message=scrambled_output_phrase)
                    else:
                        try:
                            contact_ip = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_colour, error_colour, private_mode)
                            contact_ip.add_ip(target_name, ip)
                        except UnboundLocalError:
                            pass
                    if "." not in ip:
                        if ":" in ip:
                            temp = ip
                            contact_search = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_colour, error_colour, private_mode)
                            target_name, target_mac, target_ip, details = contact_search.check_for(
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
                                contact_search.add_ip(target_name, ip)
                        else:
                            try:
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_colour, error_colour, private_mode)
                                target_name, mac, target_ip, details = contact_search.check_for(
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
                                        contact_search.add_ip(target_name, ip)
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
        if sc == None:
            try:
                link.send(packet.encode())
            except:
                error_link(packet.encode())
        else:
            sc.send(packet.encode())
        try:
            error_link.shutdown(socket.SHUT_RDWR)
            error_link.close()
        except:
            pass
        if outbound_file:
            sftp_send(ip, default_colour, error_colour, voice_message, code, prefix, sc)
        if not skip and print_logs:
            animated_print(
                f"Message {message.decode()} with decryption code {decrypt_code} successfully sent to {ip}!")
        elif mailbox and print_logs:
            animated_print(
                f"Message {message.decode()} with decryption code {decrypt_code} sent to {ip}'s mailbox!")
        elif conversation_mode and recipient_ip.strip() != "" and message_text.strip().endswith("\\exit"):
            animated_print(
                f"Message sent! Exiting conversation with {get_foreign_user().capitalize()}")
            sc.close()
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        elif not skip:
            animated_print(f"Message sent!")
        elif mailbox and conversation_mode:
            if get_foreign_user() != None:
                animated_print(
                    f"{get_foreign_user().capitalize()} is not available! Message left in their mailbox!")
                get_foreign_user(new_user="\\reset")
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
        server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate, silent=True)
    elif poke and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_colour, default_colour)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate, silent=True)
    elif love_sent and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_colour, default_colour)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                       date, default_colour, print_logs, private_mode, error_colour, display_initiate, silent=True)
    else:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_colour, error_colour, auto_code=True)
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)


def hash_current_user(user):
    """Applies SHA256 encryption on string passed"""
    hash_user = user.encode("utf-8")
    hash_user = hashlib.sha256(hash_user).hexdigest()
    return hash_user


def decode_foreign_user(code, prefix, user, default_colour):
    """Decrypts the username of person who sent a message, using the main encryption code"""
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


def validate_foreign_user(ip, expected_user, print_logs, temp_sc, **kwargs):
    """When someone declares the name of a desired recipient, that string is compared to the user curretly logged in, returning True/False"""
    message = kwargs.get("message", None)
    if temp_sc == None:
        reply_link = socket.socket()
        try:
            reply_link.connect((ip.strip(), 15753))
        except ConnectionRefusedError:
            try:
                reply_link.connect((ip.strip(), 19507))
            except ConnectionRefusedError:
                return False, None
        sc = reply_link
    else:
        sc = temp_sc
    try:
        sc.send(
            f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
    except:
        try:
            if temp_sc == None:
                reply_link.connect((ip.strip(), 19507))
                reply_link.send(
                    f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
            else:
                reply_link = socket.socket()
                reply_link.connect((ip.strip(), 19507))
                reply_link.send(
                    f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
        except ConnectionRefusedError:
            return False, sc
        sc = reply_link
    info = sc.recv(1024)
    info = info.decode()
    if "true" in info.lower():
        return True, sc
    else:
        reply_link = socket.socket()
        try:
            reply_link.connect((ip.strip(), 19507))
        except ConnectionRefusedError:
            return False, sc
        reply_link.send(
            f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
        info = reply_link.recv(1024)
        info = info.decode()
        if "true" in info.lower():
            log("Foreign user succesfully validated!", "networkManager", get_current_user(), None)
            if message != None:
                reply_link.send(message.encode())
            else:
                reply_link.send("\\exit".encode())
            reply_link.close()
            get_foreign_user(new_user=expected_user)
            return True, sc
        else:
            log("Foreign user failed validation!", "networkManager", get_current_user(), None)
            reply_link.send("\\exit".encode())
            return False, sc


def get_auto_code():
    """Specifically retrieves the state of the auto_code parameter in the config file"""
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code, voice_record_time = retrieve_config_settings()
    return auto_code


def private_file_integrity(filename):
    private_cache_queried = False
    enter_home_directory()
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        for i, line in enumerate(credential_lines):
            if line.strip().lower() in filename.strip().lower() or "$mycache" in filename.strip().lower():
                private_cache_queried = True
    if ("FiEncrypt" in filename or "FiEncrypt" in os.getcwd()) and not private_cache_queried:
        temp_path = filename.split("/")
        try:
            if "cache" in temp_path[-2] or "cache" in temp_path[-1]:
                return True, 1
            else:
                return False, 1
        except IndexError:
            return False, 1
    elif private_cache_queried:
        hash_user = hash_current_user(get_current_user().lower().strip())
        if hash_user not in filename:
            enter_home_directory()
            for file in os.listdir("."):
                if file.strip() == hash_user.strip() and "$mycache" in filename.strip() and parse_size(os.path.getsize(f"./{file}"), file) == "Directory":
                    return True, 2
            return False, 2
        else:
            return True, 2
    else:
        return True, 0


def to_boolean(state):
    if "true" in state.lower().strip():
        return True
    else:
        return False


def get_ip_from_socket(sc):
    try:
        temp = str(sc).split("raddr=('")
        target_ip = substring(temp[1], "'", 0)
    except:
        target_ip = ""
    return target_ip


def sftp_send(recipient_ip, default_colour, error_colour, voice_message, code, prefix, temp_sc, **kwargs):
    """Sends file using unique socket"""
    try:
        file_link = socket.socket()
        file_link.bind((get_own_ip(False, False).strip(), 41731))
        file_link.listen(10)
        sc, address = file_link.accept()
    except:
        animated_print(f"{error_colour}WARNING: Connection failed! Aborting file transfer!")
        Colours(default_colour)
        temp_sc.send("\\exit".encode())
        temp_sc.close()
        assisted_menu()
    alphabet, valid_file, old_file_path, is_directory = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                                                         'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'], False, kwargs.get("file_path", None), False
    ready = to_boolean(sc.recv(1024).decode())
    if ready:
        try:
            if len(prefix[0]) == 2:
                code_seg1 = code[int(prefix[0][0]):int(prefix[0][1])]
            elif len(prefix[0]) == 3:
                code_seg1 = code[int(prefix[0][0]):int(prefix[0][1:3])]
            elif len(prefix[0]) == 4:
                code_seg1 = code[int(prefix[0][0:2]):int(prefix[0][1:3])]
            code_seg1 = list(code_seg1)
            code_seg1 = sum(map(int, code_seg1))
            if len(prefix[1][0]) == 2:
                code_seg2 = code[int(prefix[1][0][0]):int(prefix[1][0][1])]
            elif len(prefix[1][0]) == 3:
                code_seg2 = code[int(prefix[1][0][0]):int(prefix[1][0][1:3])]
            elif len(prefix[1][0]) == 4:
                code_seg2 = code[int(prefix[1][0][0:2]):int(prefix[1][0][1:3])]
            code_seg2 = list(code_seg2)
            code_seg2 = sum(map(int, code_seg2))
            code3 = code
            Colours(default_colour, force=True)
        except:
            code_seg1 = str(code_seg1)[::-1]
            temp = code_seg2
            code_seg2 = int(code_seg1)
            code_seg1 = temp
            Colours(default_colour)
        if get_foreign_user() == None or get_foreign_user().strip() == "":
            temp_foreign_user = recipient_ip
        else:
            temp_foreign_user = get_foreign_user()
        while not valid_file:
            if voice_message:
                filename = "cache/voice_message.wav"
            else:
                try:
                    if old_file_path == None:
                        filename = privacy_input(
                            f"Enter path of file to send to {temp_foreign_user}", 0)
                    else:
                        filename = old_file_path
                except KeyboardInterrupt:
                    log(f"File transfer interrupted!", "networkManager", get_current_user(
                    ), None)
                    animated_print(f"{error_colour}WARNING: File transfer aborted!")
                    Colours(default_colour)
            integrity, return_value = private_file_integrity(filename)
            if not integrity:
                final_file, valid_file = True, False
                if return_value == 1:
                    animated_print(
                        f"{error_colour}WARNING: You cannot access core FiEncrypt files outside of the public or private cache!")
                    Colours(default_colour)
                    log("Sftp access to core FiEncrypt files rejected!",
                        "encryptionManager", get_current_user(), None)
                elif return_value == 2:
                    animated_print(
                        f"{error_colour}WARNING: You cannot access the private cache of any other user!")
                    Colours(default_colour)
                    log("Sftp access to private cache rejected!",
                        "encryptionManager", get_current_user(), None)
            else:
                if return_value == 2 and not filename.strip().endswith("/"):
                    filename = f"{filename.strip()}/"
                try:
                    if not filename.startswith(".") and not filename.startswith("/") and filename[0].lower() not in alphabet:
                        filename = f"./{filename}"
                    if "$mycache/" in filename.strip().lower():
                        filename = filename.split("$mycache/", 1)
                        enter_home_directory()
                        animated_print(f"Please confirm your login: ")
                        username = privacy_input("Username", 0)
                        password = privacy_input("Password", 1)
                        valid = validate_login(username, password)
                        current_valid = username.lower().strip() == get_current_user().lower().strip()
                        if valid and current_valid:
                            filename = f"./{hash_current_user(username.lower().strip())}/files/{filename[1]}"
                    if filename.strip().endswith("/"):
                        final_file = False
                        while not final_file:
                            options, option_type = [], []
                            for files in os.listdir(f"{filename.strip()}"):
                                options.append(files)
                            for i, option in enumerate(options):
                                if not option.strip().startswith("."):
                                    animated_print(
                                        f"{i+1}. {option} ({parse_size(os.path.getsize(filename+option), option)})", speed=0)
                                    option_type.append(parse_size(os.path.getsize(
                                        filename+option), option))
                                else:
                                    del options[i]
                                    animated_print(
                                        f"{i+1}. {options[i]} ({parse_size(os.path.getsize(filename+options[i]), options[i])})", speed=0)
                                    option_type.append(parse_size(os.path.getsize(
                                        filename+options[i]), options[i]))
                            file_choice = privacy_input(f"Select one of these", 0)
                            if "directory" in option_type[int(file_choice)-1].lower().strip():
                                filename = f"{filename}{options[int(file_choice)-1]}/"
                                #filename = stringify_filepath(filename)
                                final_file = False
                            else:
                                filename = f"{filename}{options[int(file_choice)-1]}"
                                final_file = True
                    filesize = os.path.getsize(filename)
                    try:
                        with open(filename, "rb") as test_file:
                            valid_file = True
                    except IsADirectoryError:
                        is_directory = True
                        raise FileNotFoundError
                except FileNotFoundError:
                    try:
                        if filename.strip().endswith("/"):
                            base_directory = filename[::-1].split("/", 2)
                            del base_directory[-1]
                        elif is_directory:
                            base_directory = filename
                        else:
                            base_directory = filename[::-1].split("/", 1)
                        desired_file = base_directory[0][::-1]
                        base_directory = base_directory[-1][::-1]
                        os.chdir(base_directory)
                        options = []
                        for files in os.listdir(f"./"):
                            if desired_file.lower().strip() in files.lower().strip():
                                options.append(files)
                        if len(options) > 1:
                            for i, option in enumerate(options):
                                animated_print(f"{i+1}. {option}", speed=0)
                            file_choice = privacy_input(f"Select one of these files", 0)
                            filename = f"{base_directory}/{options[int(file_choice)-1]}"
                        else:
                            filename = f"{base_directory}/{options[0]}"
                        filesize = os.path.getsize(filename)
                        try:
                            with open(filename, "rb") as test_file:
                                valid_file = True
                        except:
                            valid_file = False
                    except:
                        animated_print(f"{error_colour}WARNING: File not found!")
                        Colours(default_colour)
                        valid_file = False
                if valid_file:
                    decrypted_header, passs, encrypted_header, header = [
                    ], 0, '', f"{filename}<SEPERATOR>{filesize}"
                    for i, k in enumerate(header):
                        if i < len(header) / 2 and len(str(code)) >= 4:
                            if len(str(code)) > 4:
                                code2 = code_seg1
                            else:
                                code3 = str(code)[0:2]
                                code2 = int(code3)
                        elif len(str(code3)) >= 4:
                            if len(str(code3)) > 4:
                                code2 = code_seg2
                            else:
                                code3 = str(code)[2:4]
                                code2 = int(code3)
                        decrypted_header.append(k)
                        decrypted_header[passs] = ord(k)
                        decrypted_header[passs] = int(
                            decrypted_header[passs]) + int(code2)
                        if decrypted_header[passs] < 32:
                            decrypted_header[passs] = int(
                                decrypted_header[passs]) + 95
                        elif decrypted_header[passs] > 126:
                            decrypted_header[passs] = int(
                                decrypted_header[passs]) - 95
                        passs += 1
                    for char in decrypted_header:
                        encrypted_header += chr(char)
                    try:
                        sc.send(encrypted_header.encode())
                        accepted = to_boolean(sc.recv(1024).decode())
                        time.sleep(2)
                        if accepted:
                            progress = tqdm.tqdm(
                                range(filesize), f"Sending {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)
                            with open(filename, "rb") as f:
                                for _ in progress:
                                    bytes_read = f.read(4096)
                                    if not bytes_read:
                                        break
                                    sc.sendall(bytes_read)
                                    progress.update(len(bytes_read))
                            sys.stdout.write("\033[F")
                            sys.stdout.write("\033[K")
                            log(f"File of size {filesize}B sent successfully!",
                                "networkManager", get_current_user(), None)
                        else:
                            print("not accepted!")
                    except KeyboardInterrupt:
                        animated_print(f"{error_colour}WARNING: File transfer interrupted!")
                        Colours(default_colour)
                    except OverflowError:
                        animated_print(f"{error_colour}WARNING: File too large! Aborting...")
                        Colours(default_colour)
                    except ConnectionResetError:
                        if foreign_user != None:
                            animated_print(
                                f"{error_colour}WARNING: {foreign_user.capitalize()} has reset the conenction!")
                        else:
                            animated_print(f"{error_colour}WARNING: Peer has reset the conenction!")
                        Colours(default_colour)
                        sc.close()


def sftp_recieve(recipient_ip, user, default_colour, error_colour, code, prefix, temp_sc, **kwargs):
    """Recieves file over socket"""
    autosync, max_size, voice_message, encrypted_header, decrypted_header, passs = kwargs.get(
        "autosync", False), kwargs.get("max_size", "2GB"), kwargs.get("voice", False), [], "", 0
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
        code3 = code
        Colours(default_colour, force=True)
    except:
        temp = code_seg2
        code_seg2 = int(str(code_seg1)[::-1])
        code_seg1 = temp
        code3 = code
        Colours(default_colour)
    file_recipient = socket.socket()
    file_recipient.connect((recipient_ip, 41731))
    file_recipient.send(str(True).encode())
    Colours(default_colour)
    if voice_message:
        animated_print(f"New Voice Messge!")
    else:
        animated_print(f"Awaiting file...")
    try:
        inbound = file_recipient.recv(1024).decode()
        for i, k in enumerate(inbound):
            if i < len(inbound) / 2 and len(str(code3)) >= 4:
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
            encrypted_header.append(k)
            encrypted_header[passs] = ord(k)
            encrypted_header[passs] = int(
                encrypted_header[passs] - code)
            if encrypted_header[passs] < 32:
                encrypted_header[passs] = int(
                    encrypted_header[passs]) + 95
            elif encrypted_header[passs] > 126:
                encrypted_header[passs] = int(
                    encrypted_header[passs]) - 95
            passs += 1
        for char in encrypted_header:
            decrypted_header += chr(char)
        try:
            filename, filesize = decrypted_header.split("<SEPERATOR>")
        except ValueError:
            file_recipient.send(str(False).encode())
        else:
            file_recipient.send(str(True).encode())
            filename = os.path.basename(filename)
            progress = tqdm.tqdm(range(int(filesize)),
                                 f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            enter_home_directory()
            if filename == "voice_message.wav":
                filename = "foreign_voice_message.wav"
            with open(f"./cache/{filename}", "wb") as f:
                for _ in progress:
                    bytes_read = file_recipient.recv(4096)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
            file_extension = filename.split(".")
            file_extension = file_extension[1]
            if file_extension.lower() in ["png", "jpg", "jpeg", "bmp", "ico"]:
                cached_image = Image.open(f"./cache/{filename}")
                cached_image.show()
            for _ in range(2):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
            print("Sucessfully retrieved!")
            if str(filesize).strip() == str(os.path.getsize(f"./cache/{filename}")).strip():
                if not voice_message:
                    animated_print(f"File {filename} saved to {os.getcwd()}/cache/{filename}")
                if autosync and filename.lower().strip() != "foreign_voice_message.wav" and filename.lower().strip() != "voice_message.wav":
                    animated_print("*** Autosync ***")
                    enter_home_directory()
                    if "gb" in max_size.lower():
                        max_size = max_size.lower().split("gb")
                        if "." in max_size[0]:
                            max_size = float(max_size[0]) * 1073741824
                        else:
                            max_size = int(max_size[0]) * 1073741824
                        max_size = int(max_size)
                    else:
                        max_size = max_size.lower().split("mb")
                        max_size = int(max_size[0]) * 1048576
                    cache_transfer_size = os.path.getsize(f"./cache/{filename}")
                    personal_cache_total_size = 0
                    for path, dirs, temp_files in os.walk(f"./{hash_current_user(get_current_user().lower().strip())}/files"):
                        for temp_file in temp_files:
                            personal_cache_total_size += os.path.getsize(
                                f"./{hash_current_user(get_current_user().lower().strip())}/files/{temp_file}")
                    os.chdir(f"./{hash_current_user(get_current_user().lower().strip())}/files")
                    if pass_os() == "win32":
                        copy = "copy"
                    else:
                        copy = "cp"
                        filename = filename.strip().replace(" ", "\ ").replace(
                            "'", "\\'").replace("(", "\\(").replace(")", "\\)")
                    if (int(cache_transfer_size) + int(personal_cache_total_size)) > max_size:
                        animated_print(
                            f"{error_colour}WARNING: Size of {filename} would exceed max allocated size of your private cache!")
                        Colours(default_colour)
                    else:
                        os.system(f"{copy} ../../cache/{filename} {filename}")
                        time.sleep(1)
                        for _ in range(3):
                            sys.stdout.write("\033[F")
                            sys.stdout.write("\033[K")
                elif autosync:
                    animated_print(
                        f"{error_colour}WARNING: Storing voice messages in your Private Cache is discouraged!")
                    Colours(default_colour)
                    override = privacy_input("Do you wish to proceed anyway? [Y|N]", 0)
                    if "y" in override.lower().strip():
                        valid_name = False
                        while not valid_name:
                            new_name = privacy_input(
                                "Enter a new name for the voice message file", 0)
                            if substring(new_name, ".", 0).lower().strip() != substring(filename, ".", 0).lower().strip():
                                valid_name = True
                                if pass_os() == "win32":
                                    copy = "copy"
                                else:
                                    copy = "cp"
                                    filename = filename.strip().replace(" ", "\ ").replace(
                                        "'", "\\'").replace("(", "\\(").replace(")", "\\)")
                                    new_name = new_name.strip().replace(" ", "\ ").replace(
                                        "'", "\\'").replace("(", "\\(").replace(")", "\\)")
                                enter_home_directory()
                                os.chdir(
                                    f"./{hash_current_user(get_current_user().lower().strip())}/files")
                                os.system(
                                    f"{copy} ../../cache/{filename} {stringify_filepath(new_name.replace('.wav','').strip())}.wav")
                                for _ in range(6):
                                    sys.stdout.write("\033[F")
                                    sys.stdout.write("\033[K")
                            else:
                                animated_print(f"{error_colour}WARNING: Names still match!")
                                Colours(default_colour)
                                time.sleep(2)
                                for _ in range(5):
                                    sys.stdout.write("\033[F")
                                    sys.stdout.write("\033[K")
            else:
                animated_print(
                    f"{error_colour}WARNING: File corrupt or incomplete! Check {os.getcwd()}/cache/{filename}")
                Colours(default_colour)

    except OverflowError:
        log(f"File transfer overflow! File too large!", "networkManager", get_current_user(
        ), None)
        animated_print(f"{error_colour}WARNING: File too large! Aborting...")
        Colours(default_colour)
    except KeyboardInterrupt:
        log(f"File transfer interrupted!", "networkManager", get_current_user(
        ), None)
        animated_print(f"\n{error_colour}WARNING: Aborting file transfer...")
        Colours(default_colour)
    try:
        file_recipient.close()
    except:
        pass
    return temp_sc


def retrievemessage(old_code, user, current_user, prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_colour, print_logs, private_mode, error_colour, index, display_initiate):
    """Recieves message from other FiEncrypt user, or yourself (loopback), decrypts and displays it"""
    # ?Names such as @old_code are used to seperate the various states the string is put into during decryption
    try:
        prefix = prefix
    except:
        prefix = ""
    background_colour = "\033[41m"
    if temp_sc != None and recipient_ip.strip() == "":
        recipient_ip = get_ip_from_socket(temp_sc)
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
        months, rd_dates, st_dates, nd_dates, th_dates = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], [
            "3", "23"], ["1", "21", "31"], ["2", "22"], ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "24", "25", "26", "27", "28", "29", "30"]
        if len(date) == 3:
            if date[0] == "0":
                date = f"{date[-1]}/{date[0:len(date)-1]}"
            elif date[-2] == "0":
                date = f"{date[-1]}/0{date[0]}"
            else:
                date = f"{date[0]}/{date[0:len(date)-1]}"
        elif len(date) == 4:
            if date[0] == "0" and date[2] == "0":
                date = f"{date[3]}/0{date[1]}"
            elif date[0] == "0":
                date = f"{date[2:len(date)]}/0{date[1]}"
            elif date[2] == "0":
                date = f"{date[len(date)]}/{date[0:2]}"
            else:
                date = f"{date[-2:len(date)]}/{date[0:2]}"
        elif len(date) == 2:
            date = f"{date[0]}/{date[-1]}"
        else:
            date = "Date: Unknown"
        if date != "Date: Unknown":
            day, month = date.split("/")
            pure_day, pure_month = day, month
            try:
                month = months[int(month)-1]
            except IndexError:
                month = months[0]
            if day in rd_dates:
                day = f"{day}rd"
            elif day in st_dates:
                day = f"{day}st"
            elif day in nd_dates:
                day = f"{day}nd"
            elif day in th_dates:
                day = f"{day}th"
            if int(pure_day) <= 31 and int(pure_day) > 0 and int(pure_month) <= 12 and int(pure_month) > 0:
                date = f"{day} of {month}, {substring(str(datetime.datetime.now()), '-', 0)}"
            else:
                date = "Date: Unknown"
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
                hrs = int(timestamp[0][::-1]) - int(time_decode)
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
    if "\\file" in temp_output_phrase.strip() or "\\v" in temp_output_phrase.strip():
        temp_output_phrase = temp_output_phrase.replace("\\file", "").strip()
        expecting_file = True
        if "\\v" in temp_output_phrase.strip():
            temp_output_phrase = temp_output_phrase.replace("\\v", "").strip()
            voice_message = True
        else:
            voice_message = False
    else:
        expecting_file = False
        voice_message = False
    if temp_output_phrase.strip().count("$") >= 2:
        try:
            cached_output_phrase = temp_output_phrase
            temp_output_phrase_list = temp_output_phrase.split("$")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[9m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_colour}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                del temp_output_phrase_list[0]
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
    if expecting_file:
        autosync, max_size = cache_settings(
            user, current_user, default_colour, print_logs, private_mode, error_colour, mode="read")
        temp_sc = sftp_recieve(recipient_ip, user, default_colour, error_colour, old_code, prefix, temp_sc, autosync=autosync,
                               max_size=max_size, voice=voice_message)
        if voice_message:
            enter_home_directory()
            try:
                pass
                # playsound(f"./cache/foreign_voice_message.wav")
            except ValueError:
                log("Voice message playback error!", "voiceManager", get_current_user(), print_logs)
                animated_print(
                    f"{error_colour}WARNING: Unable to play voice message! Maybe {sys.platform} doesn't support PyAudio?")
            except KeyboardInterrupt:
                pass
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
        newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
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
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
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
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)
        elif talking_to_self:
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
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
                lines = code_file.readlines()
                if not manual:
                    text = code_file.read()
                    # TODO: Check all files that are used get properly closed as such
                    code_file.close()
                    code_file = open("./code.txt", "r+")
                    code_file.seek(0)
                    for line in text.split('\n'):
                        if line != old_code.strip():
                            code_file.write(line + '\n')
                    code_file.truncate()
                    files += 1
                    code_file.close()
                    log(
                        f"Message successfully decrypted!", "encryptionManager", current_user, print_logs)
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
                    f"Message not successfully decrypted!", "encryptionManager", current_user, print_logs)
                animated_print(
                    f"That is unfortunate :( We will launch the encryption assistant momentarily")
                #!Current unreliable
                helper("decrypt", user, current_user)
    # *Called if in conversation mode
    else:
        if poked:
            get_poked(get_foreign_user(), poke_num=pokes)
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), poked=True, message=temp_output_phrase)
        else:
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_colour, default_colour, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase)


def server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix, date, default_colour, print_logs, private_mode, error_colour, display_initiate, **kwargs):
    """Opens server to recieve and interpret message"""
    silent = kwargs.get("silent", False)
    if not silent:
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
    if not silent:
        print("Done!")
    try:
        if temp_sc == None:
            link = socket.socket()
            if not silent:
                animated_print("Socket opened... ")
            link.bind((ip, 15753))
            time.sleep(1)
            if not silent:
                sys.stdout.write("\033[K")
                sys.stdout.write("\033[F")
                animated_print("Socket bound... ")
            link.listen(10)
            time.sleep(2)
            sys.stdout.write("\033[F")
        if not silent:
            animated_print(f"Socket bound... {ip}:15753")
            animated_print("Listening on socket... ")
        log(f"Server started on {ip}:15753", "networkManager",
            current_user, print_logs)
        if temp_sc == None:
            sc, address = link.accept()
        else:
            sc = temp_sc
    except KeyboardInterrupt:
        log("Server channel terminated!", "networkManager", get_current_user(), print_logs)
        animated_print("\nServer Terminated!")
        try:
            sc.close()
        except:
            pass
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            link.close()
        except:
            pass
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    if not silent:
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[F")
        animated_print("Connection established!")
    try:
        info = sc.recv(1024)
    except KeyboardInterrupt:
        log("Server channel terminated!", "networkManager", get_current_user(), print_logs)
        animated_print("\nServer Terminated!")
        try:
            sc.close()
        except:
            pass
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            link.close()
        except:
            pass
        menu(user, None, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    except ConnectionResetError:
        log("Server channel reset!", "networkManager", get_current_user(), print_logs)
        animated_print(
            f"{error_colour}Connection reset by peer!")
        Colours(default_colour)
        try:
            sc.close()
        except:
            pass
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            link.close()
        except:
            pass
        menu(user, display_initiate, print_logs,
             default_colour, private_mode, error_colour, print_speed=0)
    if not silent:
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
            sc.send(str(True).encode())
            animated_print(f"Foreign user validated!")
            for _ in range(7):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
            try:
                link.close()
            except:
                pass
            server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                           date, default_colour, print_logs, private_mode, error_colour, display_initiate)
        else:
            sc.send(str(False).encode())
            animated_print(
                f"{error_colour}WARNING: Foreign user validation failed!")
            Colours(default_colour)
            for _ in range(7):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
            try:
                link.close()
            except:
                pass
            server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                           date, default_colour, print_logs, private_mode, error_colour, display_initiate)
    else:
        try:
            if "\\exit" in message or "\\poke" in message:
                pass
            else:
                info = message[1]
            message = message[0]
        except IndexError:
            if message[0].strip() == "":
                animated_print(f"{error_colour}WARNING: Pipe broken! Returning to menu!")
                Colours(default_colour)
                try:
                    sc.close()
                except:
                    pass
                try:
                    link.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    link.close()
                except:
                    pass
                menu(user, None, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
            else:
                log("Invalid message recieved! Server channel restarting",
                    "networkManager", get_current_user(), print_logs)
                animated_print(
                    f"{error_colour}WARNING: {message} recieved but not valid! Restarting Server!")
                Colours(default_colour)
                try:
                    link.close()
                except:
                    pass
                server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix,
                               date, default_colour, print_logs, private_mode, error_colour, display_initiate)
        if not silent:
            animated_print("Done!")
    try:
        link.shutdown(socket.SHUT_RDWR)
    except:
        pass
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
            try:
                sc.close()
            except:
                pass
            try:
                link.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                link.close()
            except:
                pass
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
        if recipient_ip.strip() == "" and temp_sc == None:
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
                temp_foreign_user = temp_foreign_user.replace("\033[F", "").replace(
                    "\033[K", "").replace("\n", "")
                if not silent:
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
        log("Encrypted message recieved!",
            "networkManager", current_user, print_logs)
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
            if not silent:
                animated_print(
                    f"Message from {foreign_user.capitalize()} recieved!")
            foreign_user = get_foreign_user(new_user=foreign_user)

            retrievemessage(code, user, 2, prefix, recipient_ip, sc, timestamp, False, False,
                            default_colour, print_logs, private_mode, error_colour, None, display_initiate)
        except KeyboardInterrupt:
            try:
                sc.close()
            except:
                pass
            try:
                link.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                link.close()
            except:
                pass
            menu(user, display_initiate, print_logs,
                 default_colour, private_mode, error_colour, print_speed=0)
    else:
        try:
            sc.close()
        except:
            pass
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            link.close()
        except:
            pass
        menu(user, display_initiate, print_logs,
             default_colour, private_mode, error_colour, print_speed=0)


def send_conversation_invite(user, current_user, default_colour, private_mode, error_colour, print_logs, display_initiate):
    """Sends a simple alert to recipient, prompting them with an IP address to send a message to, through listener.py"""
    if sys.platform.startswith("linux"):
        ip = gnu_ip_resolve(print_logs, private_mode)
        if ip == "":
            ip = privacy_input(
                "Enter your IP in dotted decimal format", private_mode)
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    try:
        dest_ip, target_mac, target_name = get_recipient_ip(user, display_initiate, print_logs,
                                                            default_colour, private_mode, error_colour, None, is_invite=True)
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
            log(f"Invite delivery refused!", "networkManager", get_current_user(
            ), print_logs)
            connected = False
            animated_print(
                f"{error_colour}WARNING: Connection to recipient unexpectedly terminated! Try again!")
            Colours(default_colour)
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
        except TimeoutError:
            log(f"Invite delivery timeout!", "networkManager", get_current_user(
            ), print_logs)
            connected = False
            animated_print(
                f"{error_colour}WARNING: Unable to obtain a response from recipient address! Try again!")
            Colours(default_colour)
            send_conversation_invite(user, current_user, default_colour,
                                     private_mode, error_colour, print_logs, display_initiate)
        except OSError:
            log(f"Invite delivery OSError!", "networkManager", get_current_user(
            ), print_logs)
            connected = False
            animated_print(
                f"{error_colour}WARNING: Unable to obtain a response from recipient address! Try again!")
            Colours(default_colour)
            send_conversation_invite(user, current_user, default_colour,
                                     private_mode, error_colour, print_logs, display_initiate)
        except KeyboardInterrupt:
            log(f"Invite delivery interrupted!", "networkManager", get_current_user(
            ), print_logs)
            animated_print(f"\nAborting!")
            menu(user, None, print_logs, default_colour,
                 private_mode, error_colour, print_speed=0)
    log(f"Conversation invite sent to {dest_ip}",
        "networkManager", current_user, print_logs)
    if target_name != None or target_name.strip() != "":
        content = f"Request:True Source_IP:{ip} Name:{current_user} Target:{target_name}"
    else:
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
    """Checks your mailbox for any unread messages"""
    enter_home_directory()
    if current_user != 2:
        os.chdir(f"./{hash_current_user(get_current_user().strip().lower())}/inbox")
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
            "fileManager", current_user, print_logs)
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
                log("Corrupted message in mailbox!", "mailManager", get_current_user(), print_logs)
                animated_print(
                    f"{error_colour}WARNING: Message {i} contains corrupted format! This message will be removed!")
                Colours(default_colour)
            del(index[i])
            enter_home_directory()
            os.chdir(f"./{hash_current_user(get_current_user().strip().lower())}/inbox")
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
                    ip, target_mac, target_name = get_recipient_ip(
                        user, display_initiate, print_logs, default_colour, private_mode, error_colour, None, confirm_ip=f"{message[1][1][0]}@{message[1][1][1]}")
                    newmessage(code, user, message[1][1][1], None, prefix, None,
                               False, error_colour, default_colour, private_mode, print_logs, False, display_initiate, False)
                else:
                    check_mailbox(user, 2, index, mailing, timestamp, error_colour,
                                  default_colour, display_initiate, print_logs, private_mode)
            except UnboundLocalError:
                Colours(default_colour)
    hide_tree()
    mailing = False
    menu(user, display_initiate, print_logs,
         default_colour, private_mode, error_colour, print_speed=0)


def config_settings(user, current_user, default_colour, print_logs, private_mode, error_colour):
    """Provides an interface to modify the config file through"""
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
            if "false" in display_initiate.lower():
                display_initiate = False
            else:
                display_initiate = True
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
        if "voice_message" in config_lines[11].lower():
            voice_record_time = config_lines[11].split(" = ")
            voice_record_time = int(voice_record_time[1].strip().replace("s", "").replace("m", ""))
            if voice_record_time >= 60:
                voice_record_time = f"{float(voice_record_time / 60)} Minutes"
            else:
                voice_record_time = f"{voice_record_time} Seconds"
        else:
            voice_record_time = "15 Seconds"
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
            animated_print(
                f"10. Voice Message Duration: {voice_record_time}", speed=master_printing_speed)
            animated_print(f"11. Create new user...", speed=master_printing_speed)
            animated_print(f"12. Return to main menu", speed=master_printing_speed)
        else:
            animated_print(
                f"5. Conversation mode: {conversation_mode}", speed=master_printing_speed)
            animated_print(
                f"6. Graphic mode: {graphic_mode}", speed=master_printing_speed)
            animated_print(
                f"7. Privacy mode: {private_mode}", speed=master_printing_speed)
            animated_print(
                f"8. Auto code: {auto_code}", speed=master_printing_speed)
            animated_print(
                f"9. Voice Message Duration: {voice_record_time}", speed=master_printing_speed)
            animated_print(f"10. Create new user...", speed=master_printing_speed)
            animated_print(f"11. Return to main menu", speed=master_printing_speed)
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
                valid_value = False
                while not valid_value:
                    try:
                        voice_record_time = privacy_input(f"Voice message duration", private_mode)
                        if voice_record_time.lower().endswith("s"):
                            voice_record_time = f"{int(voice_record_time.replace('s', '').strip())}s"
                        elif voice_record_time.lower().endswith("m"):
                            voice_record_time = f"{int(voice_record_time.replace('m', '').strip()) * 60}s"
                        else:
                            voice_record_time = f"{int(voice_record_time)}s"
                        valid_value = True
                    except:
                        valid_value = False
                config_lines[11] = f"voice_message = {voice_record_time}"
        elif choice == "10":
            if custom_scheme:
                valid_value = False
                while not valid_value:
                    try:
                        voice_record_time = privacy_input(f"Voice message duration", private_mode)
                        if voice_record_time.lower().endswith("s"):
                            voice_record_time = f"{int(voice_record_time.replace('s', '').strip())}s"
                        elif voice_record_time.lower().endswith("m"):
                            voice_record_time = f"{int(voice_record_time.replace('m', '').strip()) * 60}s"
                        else:
                            voice_record_time = f"{int(voice_record_time)}s"
                        valid_value = True
                    except:
                        valid_value = False
                config_lines[11] = f"voice_message = {voice_record_time}"
            else:
                add_new_user()
        elif choice == "11":
            if custom_scheme:
                add_new_user()
            else:
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
        elif choice == "12":
            if custom_scheme:
                menu(user, display_initiate, print_logs, default_colour,
                     private_mode, error_colour, print_speed=0)
        config_file.close()
        os.remove(f"./config.txt")
        with open("./config.txt", "w+") as config_file:
            for line in config_lines:
                if line.strip() != "" and line != "-":
                    line = f"{line}\n"
                config_file.write(line)
        master_printing_speed = 0


def cache_settings(user, current_user, default_colour, print_logs, private_mode, error_colour, **kwargs):
    mode = kwargs.get("mode", "read")
    escape = False
    if mode.lower() == "read":
        with open(f"./cache_settings.txt", "r") as cache_settings_file:
            old_cache_settings = cache_settings_file.read()
            old_cache_settings = old_cache_settings.split("\n")
        if "auto-sync" in old_cache_settings[2].lower():
            autosync = old_cache_settings[2].split(" = ")
            autosync = to_boolean(autosync[1])
        else:
            autosync = False
        if "max_size" in old_cache_settings[3].lower():
            max_size = old_cache_settings[3].split(" = ")
            max_size = max_size[1]
        else:
            max_size = "2GB"
        return autosync, max_size

    elif mode.lower() == "edit":
        with open(f"./cache_settings.txt", "r+") as cache_settings_file:
            old_cache_settings = cache_settings_file.read()
            old_cache_settings = old_cache_settings.split("\n")
    while not escape:
        if "auto-sync" in old_cache_settings[2].lower():
            autosync = old_cache_settings[2].split(" = ")
            autosync = to_boolean(autosync[1])
        else:
            autosync = False
        if "max_size" in old_cache_settings[3].lower():
            max_size = old_cache_settings[3].split(" = ")
            max_size = max_size[1]
        else:
            max_size = "2GB"
        # more settings go here

        # output
        animated_print(f"1. Auto Sync: {autosync}")
        animated_print(f"2. Max Personal Cache Size: {max_size}")
        animated_print(f"6. Return to Cache Menu")
        choice = privacy_input(f"What setting would you like to modify", private_mode)
        if choice == None:
            escape = True
        elif choice == "1":
            autosync = privacy_input(f"True/False", private_mode)
            old_cache_settings[2] = f"auto-sync = {to_boolean(autosync)}"
        elif choice == "2":
            valid_size = False
            while not valid_size:
                max_size = privacy_input(f"Enter size in MB or GB", private_mode)
                if not max_size.strip().lower().endswith("mb") and not max_size.strip().lower().endswith("gb"):
                    if len(max_size.strip()) <= 2 or "." in max_size.strip():
                        assumed_type = "GB"
                    else:
                        assumed_type = "MB"
                    animated_print(
                        f"{error_colour}WARNING: Data unit not declared... assuming {assumed_type}")
                    Colours(default_colour)
                    try:
                        if "." in max_size or assumed_type == "gb":
                            max_size = float(max_size.strip())
                        else:
                            max_size = int(max_size.strip())
                        valid_size = True
                        old_cache_settings[3] = f"max_size = {max_size}{assumed_type.upper()}"
                    except:
                        animated_print(f"{error_colour}WARNING: Invalid personal cache size!")
                        Colours(default_colour)
                else:
                    if max_size.strip().lower().endswith("gb"):
                        requested_size = substring(max_size.lower(), "gb", 0)
                        unit = substring(max_size.lower(), "gb", 1)
                    elif max_size.strip().lower().endswith("mb"):
                        requested_size = substring(max_size.lower(), "mb", 0)
                        unit = substring(max_size.lower(), "mb", 1)
                    else:
                        animated_print(f"{error_colour}WARNING: Invalid data unit... assuming MB")
                        Colours(default_colour)
                        unit = "mb"
                    try:
                        if "." in requested_size or unit == "gb":
                            requested_size = float(requested_size.strip())
                        else:
                            requested_size = int(requested_size.strip())
                        valid_size = True
                        old_cache_settings[3] = f"max_size = {requested_size}{unit.upper()}"
                    except:
                        animated_print(f"{error_colour}WARNING: Invalid personal cache size!")
                        Colours(default_colour)
        elif choice == "6":
            escape = True
        else:
            animated_print(f"{error_colour}WARNING: Invalid option!")
            Colours(default_colour)
        with open(f"./cache_settings.txt", "w+") as new_cache_file:
            for line in old_cache_settings:
                line = line.replace("\n", "").strip()
                new_cache_file.write(f"{line}\n")
        log("Cache settings updated!", "fileManager", get_current_user(), None)


def manage_cache(user, current_user, default_colour, print_logs, private_mode, error_colour, **kwargs):
    enter_home_directory()
    straight_to_menu, old_files = kwargs.get("menu", False), kwargs.get("files", None)
    os.chdir(f"./cache")
    if len([filenum for filenum in os.listdir(".")]) > 0:
        if not straight_to_menu:
            animated_print("Dumping cache...")
        for root, dirs, files in os.walk("./cache", topdown=False):
            if not straight_to_menu:
                animated_print(files)
        enter_home_directory()
        if len([filenum for filenum in os.listdir(f"./{hash_current_user(get_current_user().lower().strip())}/files")]) > 0:
            menu_state = ["", "", "", "", "", ""]
        else:
            if not straight_to_menu:
                animated_print(f"{error_colour}WARNING: Private cache is empty!")
                Colours(default_colour)
            menu_state = ["", "", "", "\033[9m", "\033[9m", ""]
    else:
        files = None
        enter_home_directory()
        if len([filenum for filenum in os.listdir(f"./{hash_current_user(get_current_user().lower().strip())}/files")]) > 0:
            if not straight_to_menu:
                animated_print(f"{error_colour}WARNING: Public cache is empty!")
                Colours(default_colour)
            menu_state = ["\033[9m", "\033[9m", "\033[9m", "", "", ""]
        else:
            if not straight_to_menu:
                animated_print(f"{error_colour}WARNING: Public and Private caches are empty!")
                Colours(default_colour)
            menu_state = ["\033[9m", "\033[9m", "\033[9m", "\033[9m", "\033[9m", ""]
    animated_print(f"{menu_state[0]}1. Archive public cache\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"{menu_state[1]}2. Delete from public cache\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"{menu_state[2]}3. Empty public cache\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"{menu_state[3]}4. View private cache\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"{menu_state[4]}5. Empty private cache\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"{menu_state[5]}6. Cache settings\033[0m", speed=0.01)
    Colours(default_colour)
    animated_print(f"7. Return to main menu", speed=0.01)
    valid_choice = False
    while not valid_choice:
        cache_option = privacy_input("Select an option", private_mode)
        try:
            cache_option = int(cache_option)
            valid_choice = True
        except:
            animated_print(f"{error_colour}WARNING: Invalid selection!")
            Colours(default_colour)
    if cache_option == 1:
        if menu_state[0].strip() == "":
            enter_home_directory()
            autosync, max_size = cache_settings(
                user, current_user, default_colour, print_logs, private_mode, error_colour, mode="read")
            if "gb" in max_size.lower():
                max_size = max_size.lower().split("gb")
                if "." in max_size[0]:
                    max_size = float(max_size[0]) * 1073741824
                else:
                    max_size = int(max_size[0]) * 1073741824
                max_size = int(max_size)
            else:
                max_size = max_size.lower().split("mb")
                max_size = int(max_size[0]) * 1048576
            cache_total_size = 0
            for path, dirs, temp_files in os.walk(f"./cache"):
                for temp_file in temp_files:
                    cache_total_size += os.path.getsize(f"./cache/{temp_file}")
            personal_cache_total_size = 0
            for path, dirs, temp_files in os.walk(f"./{hash_current_user(get_current_user().lower().strip())}/files"):
                for temp_file in temp_files:
                    personal_cache_total_size += os.path.getsize(
                        f"./{hash_current_user(get_current_user().lower().strip())}/files/{temp_file}")
            os.chdir(f"./{hash_current_user(get_current_user().lower().strip())}/files")
            if pass_os == "win32":
                copy = "copy"
            else:
                copy = "cp"
                file = file.strip().replace(" ", "\ ").replace(
                    "'", "\\'").replace("(", "\\(").replace(")", "\\)")
            if (int(cache_total_size) + int(personal_cache_total_size)) > max_size:
                animated_print(
                    f"{error_colour}WARNING: Size of files in public cache exceeds max allocated size of your private cache!")
                Colours(default_colour)
            else:
                try:
                    for file in files:
                        if "voice_message.wav" not in file:
                            os.system(f"{copy} ../../cache/{file} {file}")
                except UnboundLocalError:
                    if old_files != None:
                        for file in old_files:
                            if "voice_message.wav" not in file:
                                os.system(f"{copy} ../../cache/{file} {file}")
                        files = old_files
                    else:
                        animated_print(
                            f"{error_colour}WARNING: Files in public cache no longer accessible!")
                        Colours(default_colour)
                        files = None
        else:
            animated_print(f"{error_colour}WARNING: Option not available!")
            Colours(default_colour)
    elif cache_option == 2:
        if menu_state[1].strip() == "":
            file_string = ""
            for i, file in enumerate(files):
                if i > 0 and i < len(files):
                    file_string += " OR "
                file_string += f"{i+1}[{file}]"
            enter_home_directory()
            file_to_delete = privacy_input(f"Delete {file_string}", private_mode)
        else:
            animated_print(f"{error_colour}WARNING: Option not available!")
            Colours(default_colour)
    elif cache_option == 3:
        if menu_state[2].strip() == "":
            confirm = privacy_input(f"Are you sure? [Y|N]", private_mode)
            if "y" in confirm.lower():
                clear_cache()
            else:
                pass
        else:
            animated_print(f"{error_colour}WARNING: Option not available!")
            Colours(default_colour)
    elif cache_option == 4:
        if menu_state[3].strip() == "":
            enter_home_directory()
            animated_print(f"Please confirm your login: ")
            username = privacy_input("Username", private_mode)
            password = privacy_input("Password", 1)
            valid = validate_login(username, password)
            current_valid = username.lower().strip() == get_current_user().lower().strip()
            if valid and current_valid:
                os.chdir(f"./{hash_current_user(username.lower().strip())}/files")
                for root, dirs, files in os.walk("./", topdown=False):
                    for file in files:
                        animated_print(file)
                animated_print(f"Private cache cleared!")
            else:
                animated_print(f"{error_colour}WARNING: Access Denied!")
                Colours(default_colour)
        else:
            animated_print(f"{error_colour}WARNING: Option not available!")
            Colours(default_colour)
    elif cache_option == 5:
        if menu_state[4].strip() == "":
            enter_home_directory()
            animated_print(f"Please confirm your login: ")
            username = privacy_input("Username", private_mode)
            password = privacy_input("Password", 1)
            valid = validate_login(username, password)
            current_valid = username.lower().strip() == get_current_user().lower().strip()
            if valid and current_valid:
                os.chdir(f"./{hash_current_user(username.lower().strip())}")
                shutil.rmtree("./files")
                os.mkdir("./files")
            else:
                animated_print(f"{error_colour}WARNING: Access Denied!")
                Colours(default_colour)
        else:
            animated_print(f"{error_colour}WARNING: Option not available!")
            Colours(default_colour)
    elif cache_option == 6:
        if menu_state[5].strip() == "":
            enter_home_directory()
            cache_settings(user, current_user, default_colour, print_logs,
                           private_mode, error_colour, mode="edit")
    elif cache_option == 7:
        print("")
        menu(user, False, print_logs, default_colour,
             private_mode, error_colour, print_speed=0)
    else:
        pass
    print("")
    enter_home_directory()
    os.chdir(f"./cache")
    if len([filenum for filenum in os.listdir(f"../{hash_current_user(get_current_user().lower().strip())}/files")]) == 0 or len([filenum for filenum in os.listdir(".")]) == 0:
        manage_cache(user, current_user, default_colour, print_logs,
                     private_mode, error_colour, files=files)
    else:
        manage_cache(user, current_user, default_colour, print_logs,
                     private_mode, error_colour, menu=True, files=files)


def assisted_menu():
    home_directory, operating_system, user = enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code, voice_record_time = retrieve_config_settings()
    error_colour = "\033[91m"
    menu(user, display_initiate, print_logs, default_colour, private_mode, error_colour)


def menu(user, display_initiate, print_logs, default_colour, private_mode, error_colour, **print_speed):
    """Main menu for FiEncrypt"""
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
        animated_print(f"13. Manage Cache", speed=print_speed)
        animated_print(f"14. Reload", speed=print_speed)
        animated_print(f"15. Quit", speed=print_speed)
    else:
        animated_print(f"5. Encryption Helper", speed=print_speed)
        animated_print(f"6. Secret Code", speed=print_speed)
        animated_print(f"7. Open Inbound Server", speed=print_speed)
        animated_print(f"8. Invite to Conversation", speed=print_speed)
        animated_print(f"9. Check Mailbox", speed=print_speed)
        animated_print(f"10. Manage Contacts", speed=print_speed)
        animated_print(f"11. Config Settings", speed=print_speed)
        animated_print(f"12. Manage Cache", speed=print_speed)
        animated_print(f"13. Reload", speed=print_speed)
        animated_print(f"14. Quit", speed=print_speed)
    # *While loop to force the user to enter correct function num
    while func not in range(1, 16):
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
            try:
                func = int(new_func)
            except ValueError:
                func = 0
        log(f"Function run: {func} Valid? {func in range(1,16)}",
            "moduleManager", current_user, print_logs)
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
                    contact_manager = Contacts(user, get_current_user().lower(
                    ).strip(), print_logs, default_colour, error_colour, private_mode)
                    if contact_func == 1:
                        new_name = privacy_input(
                            f"Enter contact name here", private_mode)
                        new_ip = privacy_input(
                            f"Enter MAC address here (or leave blank)", private_mode)
                        new_details = privacy_input(
                            f"Enter any additional details here", private_mode)
                        contact_manager.add(new_name, new_ip, new_details)
                        contact_func = 0
                    elif contact_func == 2:
                        target_name = privacy_input(
                            f"Enter name of contact to be removed", private_mode)
                        contact_manager.remove(target_name)
                        contact_func = 0
                    elif contact_func == 3:
                        search = privacy_input(
                            f"Enter the contact name here", private_mode)
                        result = contact_manager.check_for(search)
                        if result != None:
                            animated_print(result)
                        else:
                            animated_print(
                                f"No contact matching {search} found!")
                        contact_func = 0
                    elif contact_func == 4:
                        contact_manager.list_all()
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
                    contact_manager = Contacts(user, get_current_user().lower(
                    ).strip(), print_logs, default_colour, error_colour, private_mode)
                    if contact_func == 1:
                        new_name = privacy_input(
                            f"Enter contact name here", private_mode)
                        new_ip = privacy_input(
                            f"Enter MAC address here (or leave blank)", private_mode)
                        new_details = privacy_input(
                            f"Enter any additional details here", private_mode)
                        contact_manager.add(new_name, new_ip, new_details)
                        contact_func = 0
                    elif contact_func == 2:
                        target_name = privacy_input(
                            f"Enter name of contact to be removed", private_mode)
                        contact_manager.remove(target_name)
                        contact_func = 0
                    elif contact_func == 3:
                        search = privacy_input(
                            f"Enter the contact name here", private_mode)
                        result = contact_manager.check_for(search)
                        if result != None:
                            animated_print(result)
                        else:
                            animated_print(
                                f"No contact matching {search} found!")
                        contact_func = 0
                    elif contact_func == 4:
                        contact_manager.list_all()
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
                manage_cache(user, capitalize_user(get_current_user()), default_colour,
                             print_logs, private_mode, error_colour)
        elif func == 13:
            if display_initiate:
                manage_cache(user, capitalize_user(get_current_user()), default_colour,
                             print_logs, private_mode, error_colour)
            else:
                clear_cache()
                initiate()
        elif func == 14:
            if display_initiate:
                clear_cache()
                initiate()
            else:
                clear_cache()
                log("FiEncrypt shutting down!", "moduleManager", get_current_user(), None)
                exit()
        elif func == 15:
            if display_initiate:
                clear_cache()
                log("FiEncrypt shutting down!", "moduleManager", get_current_user(), None)
                exit()
        else:
            animated_print(f"Invalid Fuction!")


def login(display_initiate, user_account_name, error_colour, default_colour, print_logs, private_mode, auto_code):
    """Login portal, referring to CREDENTIALS.txt for validation"""
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
            if int(attempts) < 3:
                for _ in range(3):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
            else:
                for _ in range(2):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
            animated_print(
                f"Incorrect Login! {attempts} attempts left! Try again!")
            log(f"Login attempt Success? False Attempts left: {str(attempts)}",
                "loginManager", current_user, print_logs)
            attempts -= 1


def initiate():
    """Startup script for FiEncrypt"""
    ImportStructure("logic")
    ImportStructure("system")
    log("--== FiEncrypt Warming Up! ==--", "", get_current_user(), False)
    log("Logic modules imported!", "moduleManager", get_current_user(), False)
    log("System modules imported!", "moduleManager", get_current_user(), False)
    ImportStructure("string")
    log("String modules imported!", "moduleManager", get_current_user(), False)
    ImportStructure("network")
    log("Network modules imported!", "moduleManager", get_current_user(), False)
    home_directory, operating_system, user = enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, colour_enabled, default_colour, auto_code, voice_record_time = retrieve_config_settings()
    error_colour = "\033[91m"
    if colour_enabled:
        Colours(default_colour)
    else:
        Colours(None)
    clear_cache()
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        if len(credential_lines) < 2:
            animated_print(
                f"Welcome to FiEncrypt! Please create a user account by entering a username and password below!")
            add_new_user()
    login(display_initiate, user, error_colour,
          default_colour, print_logs, private_mode, auto_code)


initiate()
