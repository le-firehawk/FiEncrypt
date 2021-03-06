from scapy.all import *
try:
    from bluetooth import *
except:
    pass
import contextlib
# FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.
# Copyright (C) 2021 le_firehawk

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
            global os, sys, shutil, subprocess, zipfile, ctypes, hashlib, Image, pyaudio, wave, playsound, tk, filedialog
            import os
            import sys
            import shutil
            import subprocess
            import zipfile
            import ctypes
            import hashlib
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
            except:
                pass
            try:
                from PIL import Image
            except:
                pass
            try:
                import pyaudio
            except:
                pass
            import wave
            from playsound import playsound
        elif import_set == "string":
            global getpass, textwrap, tl
            import getpass
            import textwrap
            from textblob import TextBlob as tl
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


class Colors:
    """Manages application of color codes for the standard out"""

    def __init__(self, color, **kwargs):
        self.error, self.reset, force_apply = "\033[91m", "\033[0m", kwargs.get("force", False)
        if color == None:
            self.default_color = parse_colors("\033[0m")
        else:
            self.default_color = parse_colors(color)
            if force_apply and "40" in self.default_color:
                self.error = True
        apply_color(self.default_color, self.error, self.reset)

    def return_default(self):
        """Returns the color code parsed by parse_colors() to be saved as a variable or be directly applied"""
        return self.default_color


class Contacts:
    """Allows MAC addresses to be saved locally and referred to when sending messages"""

    def __init__(self, user, current_user, print_logs, default_color, error_color, private_mode):
        """Gathers a list of all names of contacts present in the Contacts directory"""
        self.user, self.current_user, self.print_logs, self.default_color, self.error_color, self.private_mode, self.contact_names = user, current_user, print_logs, default_color, error_color, private_mode, []
        enter_home_directory()
        os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
        for root, dirs, files in os.walk(f"."):
            for name in files:
                self.contact_names.append(name.replace(".txt", ""))

    def check_for(self, contact_name):
        """Checks for the name passed as a parameter against all identified names in Contacts directory"""
        for contact in self.contact_names:
            enter_home_directory()
            os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
            if contact_name.lower() in contact.lower():
                enter_home_directory()
                os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
                with open(f"./{contact}.txt", "r+") as contact_file:
                    contact_lines = contact_file.readlines()
                if "-" in contact_lines[2]:
                    contact_lines[2] = None
                if "agreed" in contact_lines[3].lower():
                    contact_lines[3] = substring(contact_lines[3], " = ", -1).strip()
                    if contact_lines[3].strip() == "None":
                        contact_lines[3] = None
                else:
                    contact_lines[3] = None
                try:
                    contact_lines[4] = substring(contact_lines[4], ": ", -1).strip()
                    contact_lines[4] = int(contact_lines[4])
                except:
                    raise
                    contact_lines[4] = None
                try:
                    contact_lines[5] = contact_lines[5]
                except IndexError:
                    contact_lines.append("No details provided!")
                return contact_lines[0], contact_lines[1], contact_lines[2], contact_lines[3], contact_lines[5], contact_lines[4]
            elif ":" in contact_name:
                with open(f"./{contact}.txt", "r+") as contact_file:
                    contact_lines = contact_file.readlines()
                if contact_name in contact_lines[1]:
                    log(f"Contact Search: {contact_name} - {contact_lines}",
                        "contactManager", self.current_user, self.print_logs)
                    return contact_lines[0], contact_lines[1], contact_lines[2], contact_lines[3], contact_lines[5], contact_lines[4]
        log(f"Contact Search: {contact_name} - {[None, None, None, None, None, None]}",
            "contactManager", self.current_user, self.print_logs)
        return None, None, None, None, None, None

    def add_ip(self, contact_name, ip):
        """Locates a contact's file and appends the ip parameter into the relevant line of said file"""
        enter_home_directory()
        os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
        with open(f"./{contact_name}.txt", "r+") as update_contact:
            contact_lines = update_contact.read().split("\n")
            update_contact.seek(0)
            update_contact.truncate()
            update_contact.write(
                f"{contact_lines[0]}\n{contact_lines[1]}\n{ip}\n")
            for i in range(3, len(contact_lines)):
                update_contact.write(f"{contact_lines[i]}\n")
        log(f"Contact Updated: {contact_name}({contact_lines[1]}) New IP: {ip}",
            "contactManager", self.current_user, self.print_logs)

    def add(self, contact_name, mac, agreed_code, details, override_port):
        """Adds a new contact file into the Contacts directory, with all details being written"""
        enter_home_directory()
        os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
        with open(f"./{contact_name}.txt", "w+") as new_contact:
            new_contact.write(f"{contact_name}\n{mac}\n-\nAgreed Code = {agreed_code}\nOverride Port: {override_port}\n{details}")
        log(f"New Contact: {contact_name}({mac})",
            "contactManager", self.current_user, self.print_logs)

    def remove(self, contact_name):
        """Deletes a contact's file, if the search returns a result"""
        enter_home_directory()
        os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
        name, mac, ip, agreed_code, details, override_port = self.check_for(contact_name)
        if None in [name, mac, ip, details]:
            if not graphic_mode:
                animated_print(f"WARNING: Unable to locate contact to delete!",
                               error=True, reset=True)
        else:
            os.remove(f"./{name.strip()}.txt")
            log(f"Contact Removed: {name}({mac})", "contactManager",
                self.current_user, self.print_logs)

    def list_all(self, **kwargs):
        """Lists every contact name found within the Contacts directory"""
        mac_check, target_mac, ip_wipe = kwargs.get("mac_check", False), kwargs.get("target_mac", None), kwargs.get("ip_wipe", False)
        if len(self.contact_names) == 0:
            if graphic_mode:
                gui.Popup(gui_translate("No contacts found in your address book!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: No contacts found in your address book!",
                               error=True, reset=True)
        else:
            for i, name in enumerate(self.contact_names):
                if not mac_check and ip_wipe and not graphic_mode:
                    animated_print(f"Contact {i+1}: ")
                enter_home_directory()
                os.chdir(f"./{hash_value(current_user.lower().strip())}/contacts")
                with open(f"./{name}.txt", "r+") as contact:
                    contact_lines = contact.readlines()
                    if not mac_check and ip_wipe:
                        if not graphic_mode:
                            animated_print(
                                f"Name: {contact_lines[0]}\nMAC Address: {contact_lines[1]}\nLast IP: {contact_lines[2]}\nAgreed Code: {contact_lines[3]}\nOverride Port: {contact_lines[4]}\nDetails:")
                            for i, line in enumerate(contact_lines):
                                if i > 4 and line != "\n":
                                    spec_print = contact_lines[i].replace("\n", "")
                                    animated_print(f"{spec_print}\n")
                        else:
                            temp_details = ""
                            for i, line in enumerate(contact_lines):
                                if i > 4 and line != "\n":
                                    temp_details += f"{line}\n"
                            layout = [[gui.Text(gui_translate("Name:")), gui.Text(contact_lines[0])], [gui.Text(gui_translate("MAC Address:")), gui.Text(contact_lines[1])], [gui.Text(gui_translate("Last IP:")), gui.Text(contact_lines[2])], [gui.Text(gui_translate("Agreed Code: ")), gui.Text(contact_lines[3])], [gui.Text(gui_translate("Override Port:")), gui.Text(contact_lines[4])], [gui.Text(gui_translate("Details:")), gui.Text(temp_details)]]
                            gui.Window(title=f"FiEncrypt - Contact Search (Currently logged in as: {get_current_user()}", layout=layout, finalize=True, auto_close=True, auto_close_duration=20)
                            time.sleep(5)
                    elif ip_wipe:
                        self.add_ip(contact_lines[0], "-")
                    else:
                        if target_mac != None:
                            if hash_value(contact_lines[1].strip()) == target_mac.strip():
                                return True, [contact_line for contact_line in contact_lines]
            if mac_check:
                return False, None
        log(f"Contact Dump: {self.contact_names}",
            "contactManager", self.current_user, self.print_logs)


class Translate:
    """Translates strings passed through to the language defined in the config file"""

    def __init__(self, lang):
        self.lang = lang

    def translate(self, string, **kwargs):
        self.temp_lang = kwargs.get("lang", self.lang)
        self.translate_object = tl(string)
        try:
            if self.temp_lang.strip().lower() != "en" and self.temp_lang.strip().lower() != "english":
                return self.translate_object.translate(to=self.temp_lang)
            else:
                return string
        except:
            return string


def display_license():
    """Prints out short form message, outlining the basics of the AGPLv3 license, which is applied to FiEncrypt"""
    try:
        if graphic_mode:
            layout = [[gui.Text("FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2021 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>")], [gui.Text("Do you accept?")], [gui.Button("Accept"), gui.Button("Decline")]]
            window = gui.Window(title="FiEncrypt - License Notice", layout=layout,
                                margins=(100, 50), font="Courier 20")
            while True:
                event, values = window.read()
                if event == "Decline" or gui.WIN_CLOSED:
                    exit()
                elif event == "Accept":
                    break
            window.close()
        else:
            print("FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2021 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>\n")
    except:
        print("FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2021 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>\n")


def parse_colors(color):
    """Takes plain text color reference from the config file and returns the applicable color code for Python's standard out"""
    if "bold" in color.lower():
        return "\033[1m"
    elif "faded" in color.lower():
        return "\033[2m"
    elif "faded_italic" in color.lower():
        return "\033[3m"
    elif "faded_italic_underline" in color.lower():
        return "\033[4m"
    elif "faded_italic_underline_highlighted" in color.lower():
        return "\033[7m"
    elif "highlight_out" in color.lower():
        return "\033[8m"
    elif "invisible" in color.lower():
        return "\033[27m"
    elif "dark_grey" in color.lower():
        return "\033[28m"
    elif "grey" in color.lower():
        return "\033[29m"
    elif "black" in color.lower():
        return "\033[30m"
    elif "red" in color.lower():
        return "\033[31m"
    elif "green" in color.lower():
        return "\033[32m"
    elif "yellow" in color.lower():
        return "\033[33m"
    elif "blue" in color.lower():
        return "\033[34m"
    elif "purple" in color.lower():
        return "\033[35m"
    elif "teal" in color.lower():
        return "\033[36m"
    elif "black_background" in color.lower():
        return "\033[40m"
    elif "red_background" in color.lower():
        return "\033[41m"
    elif "green_background" in color.lower():
        return "\033[42m"
    elif "yellow_background" in color.lower():
        return "\033[43m"
    elif "blue_background" in color.lower():
        return "\033[44m"
    elif "purple_background" in color.lower():
        return "\033[45m"
    elif "ocean_background" in color.lower():
        return "\033[40m"
    elif "teal_background" in color.lower():
        return "\033[46m"
    elif "white_background" in color.lower():
        return "\033[47m"
    else:
        return "\033[0m"


def parse_region(lang, **kwargs):
    """Turns the region code for a language into the language name, and vice versa"""
    order = kwargs.get("order", 0)
    languages = {"en": "English", "de": "German", "zh": "Chinese", "cs": "Czech", "es": "Spanish", "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic", "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "my": "Burmese", "ca": "Catalan", "ny": "Chichewa", "co": "Corsican", "hr": "Croatian", "da": "Danish", "nl": "Dutch", "eo": "Esperanto", "et": "Estonian", "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian", "el": "Greek", "gu": "Gujarati", "ht": "Haitian", "ha": "Hausa", "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian", "id": "Indonesian", "ga": "Irish", "ig": "Igbo", "is": "Icelandic", "it": "Italian", "ja": "Japanese", "jv": "Javanese", "kn": "Kannada", "kk": "Kazakh", "km": "Central Khmer", "rw": "Kinyarwanda", "ky": "Kirghiz", "kg": "Kongo", "ko": "Korean", "ku": "Kurdish", "la": "Latin", "lb": "Luxembourgish", "lo": "Lao",
                 "lt": "Lithuanian", "lv": "Latvian", "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese", "mi": "Maori", "mr": "Marathi", "mn": "Monogolian", "ne": "Nepali", "nb": "Norwegian Bokmal", "nn": "Norwegian Nynorsk", "no": "Norsk", "or": "Oriya", "pa": "Punjabi", "fa": "Persian", "pl": "Polish", "ps": "Pashto", "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sd": "Sindhi", "sm": "Samoan", "sr": "Serbian", "gd": "Gaelic", "sn": "Shona", "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "st": "Southern Sotho", "su": "Sundanese", "sw": "Swahili", "sv": "Swedish", "ta": "Tamil", "te": "Telugu", "tg": "Tajik", "th": "Thai", "tk": "Turkmen", "tl": "Tagalog", "tr": "Turkish", "tt": "Tatar", "ug": "Uighur", "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh", "fy": "Western Frisian", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu"}
    if order == 0:
        return languages.get(lang, lang)
    else:
        for item in languages.items():
            if lang.strip().lower() in item[1].strip().lower():
                return item[0]
        return lang


def apply_theme(theme):
    """Applies the theme in config file to PySimpleGUI"""
    try:
        gui.theme(theme)
    except:
        gui.theme("default")
        if graphic_mode:
            gui.Popup(gui_translate("Invalid Theme! Launching Theme Previewer!"),
                      title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            gui.theme_previewer()


def gui_translate(string, **kwargs):
    """Translates the string passed through in simplified form, for PySimpleGUI Text elements"""
    enable, private_message = kwargs.get("status", True), kwargs.get("pm", False)
    try:
        if not retrieve_config_settings(exclusive="pm_translate") and string.count(" - ") == string.count("\n") and translation and not enable:
            pass
        elif not enable and translation:
            pass
        elif private_message:
            pass
        elif translation:
            string = TranslationManager.translate(string)
        return string
    except:
        try:
            if TranslationManager == None:
                gui.Popup("Translation manager not initiated, restarting FiEncrypt to resolve", title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                clear_cache()
                initiate()
            else:
                return string
        except NameError:
            return string
        except UnboundLocalError:
            return string


def apply_color(default, error, reset):
    """Prints out the default color defined within the config file and saves it as a global variable applied_default_color"""
    global applied_default_color
    applied_default_color, error_color, reset_color = default, error, reset
    if int(default.replace("\033[", "").replace("m", "")) / 10 != 4:
        print(f"{default}", end="")
    elif error == True:
        log("Invalid Color passed from config file!", "fileManager", get_current_user(), None)
        raise Exception("Invalid Color!")
    else:
        pass


def animated_print(string, **kwargs):
    """Accepts a string to be printed, along with the optional parameter for how long Python should wait before printing the next character"""
    try:
        speed, newline, error, reset_at_end, private_message = kwargs.get("speed", None), kwargs.get(
            "newline", False), kwargs.get("error", False), kwargs.get("reset", False), kwargs.get("pm", False)
        if translation and not private_message:
            temp_string = string
            try:
                format_count, target_list = string.count("\033["), []
                for _ in range(format_count):
                    if string.find("\033[") != -1:
                        target_string = string[string.find("\033["):string.find("\033[")+5]
                        target_string = f"{substring(target_string, 'm', 0)}m"
                        target_list.append([target_string, int(
                            string.find("\033[")), int(string.find("\033["))+5])
                        string = string.replace(target_string, "")
                string = TranslationManager.translate(string)
                if len(target_list) != 0:
                    temp_list = list(string)
                    string = ""
                    for entry in target_list:
                        if "0m" not in entry[0]:
                            temp_list.insert(entry[1], entry[0])
                        else:
                            reset_at_end = True
                    for char in temp_list:
                        string += char
            except:
                log("Connection error with translation server!",
                    "languageManager", get_current_user(), None)
                string = temp_string
        if error and reset_at_end:
            string = f"\033[91m{string}\033[0m{applied_default_color}"
        elif error:
            string = f"\033[91m{string}"
        elif reset_at_end:
            string = f"{string}\033[0m{applied_default_color}"
        enter_home_directory()
        if speed == None:
            try:
                with open(f"./config.txt", "r+") as config_file:
                    config_lines = config_file.readlines()
                    if "print" in config_lines[4] and speed == None and not check_debug_mode():
                        printing_speed = config_lines[4].split(" = ")
                        printing_speed = printing_speed[1]
                    elif check_debug_mode():
                        printing_speed = 0
                    else:
                        printing_speed = 0.05
            except:
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
        print(applied_default_color)
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
    if graphic_mode:
        layout = [[gui.Text(gui_translate("Would you like to quit?"))], [gui.Button(gui_translate("Yes"), key="Yes", bind_return_key=True), gui.Button(gui_translate("No"), key="No")], [
            gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        window = gui.Window(title=gui_translate("FiEncrypt"), layout=layout, margins=(100, 50), font="Courier 20")
        while True:
            event, values = window.read()
            if event == "Yes" or gui.WIN_CLOSED:
                quit = "y"
            else:
                quit = "n"
            break
        window.close()
    else:
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


def protect_tree():
    """Applies hidden attribute or permission protection to FiEncrypt directory"""
    enter_home_directory()
    succes_count = 0
    if sys.platform == "win32":
        for path, dirs, files in os.walk("."):
            for dir in dirs:
                subprocess.check_call(["attrib", "+H", dir])
            for file in files:
                subprocess.check_call(["attrib", "+H", file])
        subprocess.check_call(["attrib", "+H", f"../FiEncrypt"])
        log("FiEncrypt files hidden!", "fileManager", get_current_user(), None)
    elif sys.platform == "linux":
        with ignore_stderr():
            for path, dirs, files in os.walk("."):
                for dir in dirs:
                    os.system(f"chmod 000 {dir}")
                for file in files:
                    if ".py" not in file and ".md" not in file and "LICENSE" not in file and "git" not in file and "cache" not in file:
                        os.system(f"chmod 000 {file}")
        log("FiEncrypt files permission protected", "fileManager", get_current_user(), None)


def set_home_directory(operating_system):
    """Performs a variety of checks, including the drive letter being used, to determine the ideal location for FiEncrypt directory to be created"""
    if operating_system == "win32":
        file_path = str(os.getcwd()).split(":")
        drive_letter = file_path[0]
        if drive_letter.lower() == "c":
            user = substring(file_path[1], "Users\\", 2)
            user = substring(user, "\\", 0)
            path = f"c:/Users/{user}/FiEncrypt"
        else:
            path = f"{drive_letter}:/FiEncrypt"
            user = None
        if os.path.exists(path):
            # log(f"Existing FiEncrypt directory found!", "fileManager", None, None)
            return path, user
        else:
            os.mkdir(path)
            # log(f"New FiEncrypt directory created!", "fileManager", None, None)
            return path, user
    elif operating_system == "linux":
        file_path = os.getcwd()
        user = substring(file_path, f"home/", 2)
        user = substring(user, f"/", 0)
        path = f"/home/{user}/FiEncrypt"
        if os.path.exists(path):
            # log(f"Existing FiEncrypt directory found!", "fileManager", None, None)
            return path, user
        else:
            os.mkdir(path)
            # log(f"New FiEncrypt directory created!", "fileManager", None, None)
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
        # log(f"Home directory entered", "fileManager", None, None)
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
                          "display_initiate = False", "printing_speed = 0.02", "default_color = None", "custom_scheme = False", "conversation_mode = True", "graphic_mode = False", "private_mode = False", "auto_code = True", "voice_message = 15s", "gui_theme = default", "translation = False", "lang = en", "override_port = 15753"]
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
    urllib.request.urlretrieve(
        "https://cdn1.iconfinder.com/data/icons/hawcons/32/699001-icon-152-paperclip-512.png", f"./attach.png")
    os.mkdir(f"./cache")
    log("FiEncrypt directory structure established! ['./config.txt', './cache_settings.txt', './code.txt', './logs.txt', './messagein.txt', './messageout.txt', './CREDENTIALS.txt', './LICENSE', './cache']", "fileManager", get_current_user(), None)
    if sys.platform == "win32":
        protect_tree()


def disable_translation():
    """When needed, forcefully disables translations in both the current instance of FiEncrypt and the config file"""
    global translation
    enter_home_directory()
    with open("./config.txt", "r+") as config_file:
        config_lines = config_file.read().split("\n")
        config_lines[13] = "translation = False"
        config_file.seek(0)
        config_file.truncate()
        for line in config_lines:
            config_file.write(f"{line}\n")
    translation = False


def generate_filetypes(filename):
    """Returns the tuples needed for tkinter's file open/save dialog"""
    filetype = filename.split(".")
    if filetype[-1] == "txt":
        return ("text files", "*.txt")
    elif filetype[-1] in ["jpg", "bmp", "png", "ico"]:
        return ("images", f"*.{filetype[-1].strip()}")
    elif filetype[-1] in ["deb", "rpn", "exe"]:
        return ("program files", f"*.{filetype[-1].strip()}")
    elif filetype[-1] in ["odf", "odp", "py", "html", "cshtml", "js"]:
        return ("document files", f"*.{filetype[-1].strip()}")
    elif filetype[-1] in ["zip", "xz", "rar"]:
        return ("archives", f"*.{filetype[-1].strip()}")
    else:
        return ("other files", f"*.{filetype[-1].strip()}")


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
    if graphic_mode:
        while not valid_username or not valid_password:
            layout = [[gui.Text("Enter a username here"), gui.InputText(key="username")], [gui.Text("Enter a password here"), gui.InputText(
                key="password", password_char="*")], [gui.Text("Confirm Password"), gui.InputText(key="confirm_password", password_char="*")], [gui.Button("Confirm", bind_return_key=True), gui.Button("Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title="FiEncrypt - Add User", layout=layout,
                                margins=(100, 50), font="Courier 20")
            event, values = window.read()
            window.close()
            if event == "Confirm":
                username = values.get("username", "")
                hash_user = username.encode("utf-8")
                hash_user = hashlib.sha256(hash_user).hexdigest()
                with open(f"./CREDENTIALS.txt", "r+") as credentials:
                    credential_lines = credentials.readlines()
                    if len(credential_lines) == 0:
                        valid_username = True
                    else:
                        for line in credential_lines:
                            if hash_user in line:
                                gui.Popup("Username aleady taken!", title=gui_translate("Warning"),
                                          font="Courier 15", text_color="red", auto_close=True, auto_close_duration=5)
                                valid_username = False
                                break
                            else:
                                valid_username = True
                    credentials.seek(0)
                    credentials.truncate()
                if valid_username:
                    password = values.get("password", "")
                    hash_pass = password.encode("utf-8")
                    hash_pass = hashlib.sha256(hash_pass).hexdigest()
                    confirm_password = values.get("confirm_password", "").encode("utf-8")
                    if password.strip().startswith("\\unlim_"):
                        unlimited_password = True
                        password = password.replace("\\unlim_", "").strip()
                        hash_pass = password.encode("utf-8")
                        hash_pass = hashlib.sha256(hash_pass).hexdigest()
                    else:
                        unlimited_password = False
                    if hash_pass != hashlib.sha256(confirm_password).hexdigest():
                        valid_password = False
                        gui.Popup("Passwords do not match!", title=gui_translate("Warning"),
                                  font="Courier 15", text_color="red", auto_close=True, auto_close_duration=5)
                    elif len(password) <= 8 and not unlimited_password:
                        valid_password = False
                        gui.Popup("Password is too short!", title=gui_translate("Warning"),
                                  font="Courier 15", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        valid_password = True
            elif event == "Cancel":
                valid_username = False
                break
    else:
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
        password, unlimited_password = "", False
        while (len(password) <= 8 and not unlimited_password) or password == None:
            password = privacy_input("Enter a password here", 1)
            if password.strip().startswith("\\unlim_") or password.strip().startswith("\\\\unlim_"):
                unlimited_password = True
                password = password.replace("\\\\unlim_", "").replace("\\unlim_", "").strip()
            else:
                unlimited_password = False
            if password == None:
                pass
            elif len(password) <= 8 and not unlimited_password:
                animated_print("WARNING: Password is too short!", error=True, reset=True)
        hash_pass = password.encode("utf-8")
        hash_pass = hashlib.sha256(hash_pass).hexdigest()
        confirm_password = "".encode("utf-8")
        while hash_pass != hashlib.sha256(confirm_password).hexdigest():
            confirm_password = privacy_input("Enter password again", 1).encode("utf-8")
            if hash_pass != hashlib.sha256(confirm_password).hexdigest():
                animated_print(f"WARNING: Passwords do not match!", error=True, reset=True)
    if valid_username:
        hash = username + password
        hash = hash.encode("utf-8")
        hash = hashlib.sha256(hash).hexdigest()
        with open(f"./CREDENTIALS.txt", "r+") as credentials:
            existing_credentials = credentials.readlines()
            credentials.seek(0)
            credentials.truncate()
            existing_credentials.append(hash_user)
            existing_credentials.append(hash)
            for credential in existing_credentials:
                credential = credential.replace("\n", "")
                credentials.write(f"{credential}\n")
        try:
            os.mkdir(f"./{hash_value(username.lower())}")
            if pass_os() == "linux":
                os.system(f"chmod 000 ./{hash_value(username.lower())}")
        except FileExistsError:
            pass
        os.chdir(f"./{hash_value(username.lower())}")
        try:
            os.mkdir(f"./inbox")
            os.mkdir(f"./files")
            os.mkdir(f"./contacts")
        except FileExistsError:
            pass
        with open(f"./inbox/messages.txt", "w+") as indox_file:
            pass
        if graphic_mode:
            gui.Popup(f"New user {username} successfully added to FiEncrypt!",
                      title="FiEncrypt - Success", font="Courier 15", auto_close=True, auto_close_duration=5)
        else:
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
            if graphic_mode:
                layout = [[gui.Text("Enter your IP in dottec decimal format"),
                           gui.InputText(key="ip")], [gui.Button("Submit", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=f"FiEncrypt - IP Resolution (Logged in as: {get_current_user()})", layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Submit":
                    your_ip = values.get("ip", None)
                window.close()
            else:
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
        ans, unans = srp(request, timeout=.5, retry=0, verbose=0)
        result = []
        for sent, received in ans:
            # ?Using dictionaries allows the check in @mac_resolve() function to search by 'IP' or 'MAC'
            result.append({'IP': received.psrc, 'MAC': received.hwsrc})
        return result
    except KeyboardInterrupt:
        log("ARP Scan aborted!", "networkManager", get_current_user(), None)
        return None
    except:
        log("ARP Scan failed!", "networkManager", get_current_user(), None)
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
        if graphic_mode and print_logs:
            temp_popup = gui.Window(title=f"FiEncrypt ARP Scan Protocol (Logged in as: {get_current_user()})", layout=[[gui.Text(gui_translate("Do you wish to only scan a /24 range to save time?")), gui.Button(gui_translate("Yes"), key="yes"), gui.Button(gui_translate("No"), key="no")]], font="Courier 20", margins=(100, 50))
            event, values = temp_popup.read()
            if event == "yes":
                scan_24 = True
            else:
                scan_24 = False
            temp_popup.close()
        elif print_logs:
            scan_24 = to_boolean(privacy_input("Do you wish to only scan a /24 range to save time? (True/False)", 0))
        else:
            scan_24 = False
        if not scan_24:
            # ?Due to memory restrictions with running arp_scan on /16 or larger network, this loop checks each band and only continues if no results are found
            for i in range(254):
                result = arp_scan(
                    f"{IP_str[0]}.{IP_str[1]}.{i}.0/24")
                if result == None:
                    if graphic_mode:
                        gui.Popup(
                            f"ARP Resolution unavailable on {pass_os()}!", title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    return None
                for mapping in result:
                    # ?Strips both results to avoid rampant fucking spaces from affecting the comparison query lol
                    if mac == None:
                        return None
                    elif mac.strip() in str(mapping['MAC']).strip():
                        log(f"ARP Scan run for MAC {mac} on {IP_str[0]}.{IP_str[1]}.{i}.0/24 Result: {str(format(mapping['IP']))}",
                            "networkManager", get_current_user(), None)
                        return str(format(mapping['IP']))
        else:
            result = arp_scan(
                f"{IP_str[0]}.{IP_str[1]}.{IP_str[2]}.0/24")
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


@contextlib.contextmanager
def ignore_stdout():
    """Overrides behaviour of Python's standard output (stdout) to prevent any output from being flushed in the stdout"""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stdout = os.dup(2)
    sys.stdout.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stdout, 2)
        os.close(old_stdout)


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
    # log(f"Current user requested!", "loginManager", current_user, None)
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
    line_break, reset_at_end = line_break.get("line_break", None), False
    if translation:
        try:
            format_count, target_list = string.count("\033["), []
            for _ in range(format_count):
                if string.find("\033[") != -1:
                    target_string = string[string.find("\033["):string.find("\033[")+5]
                    target_string = f"{substring(target_string, 'm', 0)}m"
                    target_list.append([target_string, int(
                        string.find("\033[")), int(string.find("\033["))+5])
                    string = string.replace(target_string, "")
            string = TranslationManager.translate(string)
            if len(target_list) != 0:
                temp_list = list(string)
                string = ""
                for entry in target_list:
                    if "0m" not in entry[0]:
                        temp_list.insert(entry[1], entry[0])
                    else:
                        reset_at_end = True
                for char in temp_list:
                    string += char
            if reset_at_end:
                string = f"{string}\033[0m{applied_default_color}"
        except:
            log("Connection error with translation server!",
                "languageManager", get_current_user(), None)
            exit()
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
        if temp == "EXIT":
            return None
        else:
            return temp.strip()
    except KeyboardInterrupt:
        print("")
        maybe_quit()
        temp = None
        while temp == None:
            if state == 1 or "true" in str(state).lower():
                try:
                    if line_break:
                        temp = getpass.getpass(f"{string}: \n")
                    else:
                        temp = getpass.getpass(f"{string}: ")
                except KeyboardInterrupt:
                    print("")
                    maybe_quit()
                    temp = None
            else:
                if line_break:
                    temp = input(f"{string}: \n")
                else:
                    temp = input(f"{string}: ")
            if temp == "EXIT":
                return None
            elif temp != None:
                return temp.strip()
            else:
                temp = None
    except UnboundLocalError:
        privacy_input(string, state, line_break)


def contact_input(string):
    """Automatic check from the Contacts class for the name passed as input"""
    if graphic_mode:
        layout = [[gui.Text("Enter contact name"), gui.InputText(key="name")],
                  [gui.Button("Submit", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        window = gui.Window(
            title=f"FiEncrypt - Contact Input (Logged in as: {get_current_user()})", layout=layout, margins=(100, 50))
        event, values = window.read()
        if event == "Submit":
            name = values.get("name", None)
        window.close()
    else:
        name = privacy_input(f"{string}", 0)
    contact_manager = Contacts(user, get_current_user().lower().strip(),
                               print_logs, default_color, error_color, private_mode)
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
        color_enabled = config_lines[6].split(" = ")
        try:
            color_enabled = color_enabled[1]
            if "true" in color_enabled.lower():
                color_enabled = True
                default_color = config_lines[5].split(" = ")
                default_color = default_color[1]
            else:
                color_enabled = False
        except IndexError:
            color_enabled = False
            default_color = None
        auto_code = config_lines[10].split(" = ")
        auto_code = auto_code[1]
        if "true" in auto_code.lower():
            auto_code = True
        else:
            auto_code = False
        voice_record_time = config_lines[11].split(" = ")
        voice_record_time = voice_record_time[1]
        gui_theme = config_lines[12].split(" = ")
        gui_theme = gui_theme[1].strip()
        translation_enabled = config_lines[13].split(" = ")
        translation_enabled = to_boolean(translation_enabled[1].strip())
        override_port = config_lines[15].split(" = ")
        override_port = override_port[1].strip()
        if "troll_with_filler" in config_lines[-2] or "troll_with_filler" in config_lines[-1]:
            troll_with_filler = True
        else:
            troll_with_filler = False
        if "no_translate_pm" in config_lines:
            translate_private_messages = False
        else:
            translate_private_messages = True
        try:
            override_port = int(str(override_port).strip())
        except TypeError:
            override_port = 15753
        if translation_enabled:
            if "supress_translate_warning" not in config_lines[-1] and "supress_translate_warning" not in config_lines[-2]:
                if graphic_mode:
                    layout = [[gui.Text("*** WARNING ***", text_color="red", font="Courier 30")], [gui.Text(gui_translate("Enabling translate will expose sensitive data, including private messages,\nto data harvesting on the part of the relevant services. Please disable translation if you take issue with this."))], [gui.Button(gui_translate("Accept")), gui.Button(gui_translate("Decline"))], [gui.Checkbox(gui_translate("Supress future warnings (Ignored if declined)"), key="supress_translate_warning")], [gui.Checkbox(gui_translate("Do not translate private messages"), key="no_translate_pm")]]
                    temp_popup = gui.Window(title=f"FiEncrypt - Enable Translation (Logged in as: {get_current_user()})", layout=layout, font="Courier 20")
                    while True:
                        event, values = temp_popup.read()
                        if event == "Accept":
                            supress_translate_warning, no_translate_pm = values.get("supress_translate_warning", False), values.get("no_translate_pm", False)
                            bypass_warning = True
                            break
                        elif event == "Decline":
                            bypass_warning, supress_translate_warning, no_translate_pm = False, False, False
                            break
                    temp_popup.close()
                    if to_boolean(supress_translate_warning) and translation_enabled:
                        if "supress_translate_warning" not in config_lines:
                            config_lines.append("supress_translate_warning")
                        if not bypass_warning:
                            config_lines[13] = "translation = False"
                    if to_boolean(no_translate_pm) and translation_enabled:
                        if "no_translate_pm" not in config_lines:
                            config_lines.append("no_translate_pm")
                        if not bypass_warning:
                            config_lines[13] = "translation = False"
                    config_file.seek(0)
                    config_file.truncate()
                    for line in config_lines:
                        line = line.replace("\n", "")
                        config_file.write(f"{line}\n")
                else:
                    animated_print("WARNING: Enabling translate will expose sensitive data, including private messages, to data harvesting on the part of the relevant services. Please disable translation if you take issue with this.", error=True, reset=True)
                    bypass_warning, supress_translate_warning, no_translate_pm = True, True, False
            else:
                bypass_warning = True
            if bypass_warning:
                lang = config_lines[14].split(" = ")
                lang = lang[1].strip()
                if len(lang) > 3:
                    parse_region(lang, order=1)
            else:
                lang = None
        else:
            lang = None
        if exclusive_mode == None:
            return print_logs, display_initiate, graphic_mode, private_mode, color_enabled, default_color, auto_code, voice_record_time, gui_theme, translation_enabled, lang, override_port
        elif exclusive_mode == "print_logs":
            return print_logs
        elif exclusive_mode == "display_initiate":
            return display_initiate
        elif exclusive_mode == "graphic_mode":
            return graphic_mode
        elif exclusive_mode == "private_mode":
            return private_mode
        elif exclusive_mode == "color_enabled":
            return color_enabled
        elif exclusive_mode == "default_color":
            return default_color
        elif exclusive_mode == "auto_code":
            return auto_code
        elif exclusive_mode == "voice_record_time":
            return voice_record_time
        elif exclusive_mode == "gui_theme":
            return gui_theme
        elif exclusive_mode == "override_port":
            return override_port
        elif exclusive_mode == "filler_troll":
            return troll_with_filler
        elif exclusive_mode == "pm_translate":
            return translate_private_messages


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


def get_poked(foreign_user, **kwargs):
    """Pokes the user with majestic ASCII art"""
    pokes = kwargs.get('poke_num', 1)
    line1, line2, line3, line4, line5, line6, line7, line8, line9, line10, line11, line12, line13, line14, line15, line16 = "                                     _______________________", "                                    /                       \\", "                                    \__________              \\", " ______________________________________________|              \\", "/                                                              \\", "\________________________                                       \\", "           ______________/                                       \\", "          /                                                      |", "          \______________                                        |", "           ______________/                                       |", "          /                                                      |", "          \______________                                        |", "           _____________/                             ___________|", "          /                                         /", "          \_____________                           /", "                        \_________________________/"
    if pokes > 10:
        pokes = 10
    if graphic_mode:
        for poke in range(pokes):
            gui.Popup(f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}\n{line6}\n{line7}\n{line8}\n{line9}\n{line10}\n{line11}\n{line12}\n{line13}\n{line14}\n{line15}\n{line15}\n{line16}",
                      title=f"FiEncrypt - Poke (Logged in as: {get_current_user()})", font="Courier 20", auto_close=True, auto_close_duration=5)
    else:
        for poke in range(pokes):
            if pass_os() != "win32":
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
            else:
                print(f"{line1}")
                print(f"{line2}")
                print(f"{line3}")
                print(f"{line4}")
                print(f"{line5}")
                print(f"{line6}")
                print(f"{line7}")
                print(f"{line8}")
                print(f"{line9}")
                print(f"{line10}")
                print(f"{line11}")
                print(f"{line12}")
                print(f"{line13}")
                print(f"{line14}")
                print(f"{line15}")
                print(f"{line16}")
    if capitalize_user(get_current_user()).strip().lower() == foreign_user.strip().lower():
        if graphic_mode:
            gui.Popup(gui_translate("You have poked yourself... Don't you think that is a little weird?"),
                      title=gui_translate(f"FiEncrypt - Poke (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
            animated_print(
                f"You have poked yourself... Don't you think that is a little weird?")
    else:
        if graphic_mode:
            if pokes > 1:
                gui.Popup(gui_translate(
                    f"Hey {capitalize_user(get_current_user())}...\n{foreign_user.capitalize()} has poked you {pokes} times!"), title=gui_translate(f"FiEncrypt - Poke (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                gui.Popup(gui_translate(
                    f"Hey {capitalize_user(get_current_user())}...\n{foreign_user.capitalize()} has poked you!"), title=gui_translate(f"FiEncrypt - Poke (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"Hey {capitalize_user(get_current_user())}...")
            if pokes > 1:
                animated_print(
                    f"{foreign_user.capitalize()} has poked you {pokes} times!")
            else:
                animated_print(f"{foreign_user.capitalize()} has poked you!")


def you_are_loved(foreign_user, **kwargs):
    """Prints out hearts for the user, when someone is willing to share them around..."""
    hearts = kwargs.get("hearts", 1)
    if foreign_user == None:
        foreign_user = "Anonymous"
    line1, line2, line3, line4, line5, line6, line7, line8 = "  ____      ____       ", " /    \____/    \\      ", "|                |     ", "|                |     ", " \              /      ", "   \          /        ", "     \      /          ", "       \__/            "
    if hearts >= 5:
        heart_range = 5
    else:
        heart_range = hearts + 1
    if graphic_mode:
        for heart in range(heart_range-1):
            gui.Window(layout=[[gui.Text(f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}\n{line6}\n{line7}\n{line8}", text_color="purple")], [gui.Button(gui_translate("OK"), key="OK", bind_return_key=True)]],
                       title=gui_translate(f"FiEncrypt - You Are Loved (Logged in as: {get_current_user()})"), font="Courier 20", finalize=True)
    else:
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
        if not graphic_mode:
            animated_print(
                f"Congratulations! You have fallen in love with yourself!")
    else:
        if graphic_mode:
            if hearts > 1:
                if hearts == 2:
                    gui.Popup(gui_translate(
                        f"No... those are not boobs! I swear...\n{foreign_user.capitalize()} loves you {hearts} times over!"), title=gui_translate(f"FiEncrypt - You Are Loved (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
                else:
                    gui.Popup(gui_translate(f"{foreign_user.capitalize()} loves you {hearts} times over!"),
                              title=gui_translate(f"FiEncrypt - You Are Loved (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                gui.Popup(gui_translate(f"{foreign_user.capitalize()} loves you {capitalize_user(get_current_user())}!"),
                          title=gui_translate(f"FiEncrypt - You Are Loved (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
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


def handle_bluetooth_error(error, **kwargs):
    """Takes a variety of errors handed down by btcommon.BluetoothError and gives a more specific output"""
    resolution = kwargs.get("resolution", "exit")
    if resolution == "revert":
        resolution = "Returning to previous function"
    elif resolution == "exit":
        resolution = "Aborting communications"
    if "connection refused" in str(error).lower():
        if graphic_mode:
            gui.Popup(gui_translate(f"Bluetooth: Connection refused by peer! {resolution}"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"WARNING: Bluetooth - Connection refused by peer! {resolution}", error=True, reset=True)
    elif "connection reset" in str(error).lower():
        if graphic_mode:
            gui.Popup(gui_translate(f"Bluetooth: Connection reset by peer! {resolution}"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"WARNING: Bluetooth - Connection reset by peer! {resolution}", error=True, reset=True)
    elif "connection aborted" in str(error).lower():
        if graphic_mode:
            gui.Popup(gui_translate(f"Bluetooth: Connection aborted! {resolution}"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"WARNING: Bluetooth - Connection aborted! {resolution}", error=True, reset=True)


def check_secret_code(code):
    """Checks secret code entered by the user against a number of preset codes, dictating which secret function should be executed"""
    accepted_codes = ["6663bf546c17ad9e331a98e07921762af2fd74b72d8dd00667f69df52bc315d5", "49312f6e7d6661b89d2dbc4956d5995158b5a5078615c598b25195f3ff4f62b0", "de00c642838326eb5eacfdf308258a4f70f17008e449197d4dd411dbffa43374", "d7c2cc41c984c6bdd7e4eddfa5d335e71472661eae72080aa12df15329264657", "1b313b51407e4ed21b9241ce7073704e"]
    for length, accepted_code in enumerate(accepted_codes):
        if code == accepted_code:
            if length == 0:
                code_func = 1
            elif length == 1:
                code_func = 2
            elif length == 2:
                code_func = 3
            elif length == 3:
                code_func = 4
            elif length == 4:
                code_func = 5
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


def get_recipient_ip(user, display_initiate, print_logs, default_color, private_mode, error_color, temp_sc, **kwargs):
    """Obtains the desired IP, MAC, or contact name that a message is to be sent to. Calls arp_scan() and mac_resolve() modules as appropiate"""
    target_mac, target_name, is_invite, confirm_ip, message, ip, agreed_code, use_bluetooth, manual_port, return_immediately = None, None, kwargs.get(
        "is_invite", False), kwargs.get("confirm_ip", None), kwargs.get("message", None), None, None, kwargs.get("use_bluetooth", False), False, kwargs.get("return_immediately", False)
    try:
        override_port = int(override_port)
    except:
        override_port = 15753
    if confirm_ip == None and not use_bluetooth:
        if graphic_mode:
            layout = [[gui.Text(gui_translate("Enter IP, MAC address or contact name of the recipient")), gui.InputText(
                key="ip_in")], [gui.Button(gui_translate("Send"), key="Send", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Recipient IP (Logged in as: {get_current_user()})"), layout=layout,
                                margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Send":
                ip = values.get("ip_in", None)
            window.close()
        else:
            ip = privacy_input(
                "Enter the IP, MAC address or contact name of the recipient", private_mode)
    elif use_bluetooth:
        nearby_devices = discover_devices()
        override_port = 23
        if graphic_mode:
            while True:
                layout = [[gui.Text(gui_translate("Select one of these bluetooth addresses"))], [gui.Text(f"{i+1}. {address.strip()}\n") for i, address in enumerate(nearby_devices)], [gui.InputText(key="selected_bt_address")], [gui.Button(gui_translate("Rescan"), key="Rescan"), gui.Button(gui_translate("Submit"), key="Submit", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")]]
                temp_window = gui.Window(title=gui_translate(f"FiEncrypt - Bluetooth Selector (Logged in as: {get_current_user()})"), layout=layout, font="Courier 20", margins=(100, 50))
                event, values = temp_window.read()
                if event == "Submit":
                    try:
                        if ":" in values.get("selected_bt_address", ""):
                            ip = values.get("selected_bt_address", None).strip()
                        else:
                            ip = nearby_devices[int(values.get("selected_bt_address", "0").strip())-1]
                            if ip == 0:
                                ip = None
                    except:
                        ip = None
                    break
                elif event == "Rescan":
                    iteration, old_length = 0, len(nearby_devices)
                    gui.popup_no_wait(gui_translate("Rescanning..."), title=gui_translate(f"FiEncrypt - Bluetooth Scan (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    while len(nearby_devices) == old_length:
                        nearby_devices = discover_devices()
                        if len(nearby_devices) != old_length or iteration >= 25:
                            old_length = len(nearby_devices)
                            temp_window.close()
                            break
                        else:
                            time.sleep(2)
                            iteration += 1
                    if len(nearby_devices) == 0:
                        gui.Popup(gui_translate("No nearby Bluetooth devices found!"), font="Courier 20", text_color="red", title="Warning", auto_close=True, auto_close_duration=5)
                        temp_window.close()
                        ip, target_mac, target_name, temp_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                                default_color, private_mode, error_color, temp_sc, confirm_ip=confirm_ip, message=message, is_invite=is_invite, use_bluetooth=False)
                        break
                    else:
                        temp_window.close()
                elif event == "Cancel":
                    ip = None
                    temp_window.close()
                    break
                else:
                    ip = None
            temp_window.close()
        else:
            if len(nearby_devices) == 0:
                animated_print("WARNING: Scan did not return any nearby devices!", error=True, reset=True)
                ip = privacy_input("Enter known Bluetooth address", private_mode).strip()
            else:
                for i, address in enumerate(nearby_devices):
                    animated_print(f"{i+1}. {address}")
                try:
                    chosen_address = privacy_input("Select one of these bluetooth addresses", private_mode).strip()
                    try:
                        chosen_address = int(chosen_address)
                        ip = nearby_devices[chosen_address-1]
                        if ip == 0:
                            ip = None
                    except:
                        ip = chosen_address.strip()
                except:
                    ip = None
    else:
        ip = confirm_ip
    if ip == None or ip.strip() == "":
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif "," in ip:
        ip = ip.split(",")
    if type(ip) == str:
        if is_invite:
            if "@" in ip:
                ip = ip.split("@")
                target_name = ip[0].strip()
                ip = ip[1].strip()
                if ip.count(":") == 1:
                    ip = ip.split(":", 1)
                    override_port, contact_override_port = ip[1].strip(), ip[1].strip()
                    ip = ip[0].strip()
                    manual_port = True
                if "." not in ip:
                    if use_bluetooth:
                        target_mac = None
                    else:
                        contact_search = Contacts(user, get_current_user().lower().strip(
                        ), print_logs, default_color, error_color, private_mode)
                        target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                            ip)
                        if not manual_port:
                            override_port = int(override_port)
                        else:
                            override_port = int(contact_override_port)
                        target_name = target_name.replace("\n", "")
                        if "." in ip and ip.count(":") == 1:
                            ip = ip.split(":")
                            override_port = int(ip[1].strip())
                            ip = ip[0].strip()
                        target_name = target_name.replace("\n", "")
                        if target_ip != None:
                            ip = target_ip
                        else:
                            ip = mac_resolve(target_mac, print_logs)
                        if return_immediately:
                            try:
                                return ip, None, None, temp_sc, None, override_port
                            except:
                                menu(user, display_initiate, print_logs,
                                     default_color, private_mode, error_color, print_speed=0)
                        if ip == None:
                            animated_print(
                                f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                            Colors(default_color)
                            connected = False
                        else:
                            contact_override_port = override_port
                            contact_search.add_ip(target_name, ip)
                else:
                    target_mac = None
        elif "@" in ip:
            ip = ip.split("@")
            expected_user = ip[0].strip()
            ip = ip[1].strip()
            if ip.count(":") == 1:
                ip = ip.split(":", 1)
                override_port, contact_override_port = ip[1].strip(), ip[1].strip()
                ip = ip[0].strip()
                manual_port = True
            if "." not in ip:
                if use_bluetooth:
                    pass
                else:
                    contact_search = Contacts(user, get_current_user().lower().strip(
                    ), print_logs, default_color, error_color, private_mode)
                    target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                        ip)
                    if not manual_port:
                        override_port = int(override_port)
                    else:
                        override_port = int(contact_override_port)
                    if target_mac == None:
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid contact details!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(
                                f"WARNING: Invalid contact details!", error=True, reset=True)
                            Colors(default_color)
                        connected = False
                    if target_name != None:
                        target_name = target_name.replace("\n", "")
                    if target_ip != None:
                        ip = target_ip.strip()
                    elif target_mac != None:
                        ip = mac_resolve(target_mac.strip(), print_logs)
                    else:
                        ip, target_mac, target_name, temp_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                         default_color, private_mode, error_color, temp_sc, return_immediately=True)
                if return_immediately:
                    try:
                        return ip, None, None, temp_sc, None, override_port
                    except:
                        menu(user, display_initiate, print_logs,
                             default_color, private_mode, error_color, print_speed=0)
                if ip == None:
                    animated_print(
                        f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                    Colors(default_color)
                    connected = False
                else:
                    contact_override_port = override_port
                    contact_search.add_ip(target_name, ip)
            validated, temp_sc = validate_foreign_user(
                ip, expected_user, print_logs, temp_sc, message=message, port=override_port)
            if not validated:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate(f"Unable to verify if recipient is {expected_user}!"), text_color="red")], [
                        gui.Text(gui_translate("Do you wish to proceed anyway?"))], [gui.Button(gui_translate("Yes"), key="Yes", bind_return_key=True), gui.Button(gui_translate("No"), key="No")]]
                    window = gui.Window(title=gui_translate("Warning"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Yes":
                        proceed = "y"
                    else:
                        proceed = "n"
                    window.close()
                else:
                    animated_print(
                        f"WARNING: Unable to verify if recipient is {expected_user}!", error=True, reset=True)
                    Colors(default_color)
                    proceed = privacy_input(
                        f"Do you wish to proceed anyway? [Y|N]", private_mode)
                if "y" in proceed.lower():
                    pass
                else:
                    ip, target_mac, target_name, temp_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                            default_color, private_mode, error_color, temp_sc)
            time.sleep(2)
        elif "." not in ip:
            if ip.count(":") == 1:
                ip = ip.split(":", 1)
                override_port, contact_override_port = ip[1].strip(), ip[1].strip()
                ip = ip[0].strip()
                manual_port = True
            if ip.count(":") > 1:
                if use_bluetooth:
                    passtarget_mac = None
                else:
                    temp = ip
                    contact_search = Contacts(user, get_current_user().lower().strip(
                    ), print_logs, default_color, error_color, private_mode)
                    target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                        ip)
                    override_port = int(override_port)
                    target_name = target_name.replace("\n", "")
                    if target_ip.strip() != None:
                        ip = target_ip.strip()
                    else:
                        ip = mac_resolve(target_mac.strip(), print_logs)
                    if return_immediately:
                        try:
                            return ip, None, None, temp_sc, None, override_port
                        except:
                            menu(user, display_initiate, print_logs,
                                 default_color, private_mode, error_color, print_speed=0)
                    if ip == None:
                        animated_print(
                            f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                    else:
                        contact_override_port = override_port
                        contact_search.add_ip(target_name, ip)
            else:
                try:
                    contact_search = Contacts(user, get_current_user().lower().strip(
                    ), print_logs, default_color, error_color, private_mode)
                    target_name, mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                        ip)
                    if not manual_port:
                        override_port = int(override_port)
                    else:
                        override_port = int(contact_override_port)
                    target_name = target_name.replace("\n", "")
                    if mac.strip() == "":
                        animated_print(
                            f"WARNING: MAC address for contact is blank!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                    else:
                        target_mac = mac
                        if target_ip != None:
                            ip = target_ip
                        else:
                            ip = mac_resolve(target_mac, print_logs)
                        if return_immediately:
                            try:
                                return ip, None, None, temp_sc, None, override_port
                            except:
                                menu(user, display_initiate, print_logs,
                                     default_color, private_mode, error_color, print_speed=0)
                        if ip == None:
                            animated_print(
                                f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                            Colors(default_color)
                            connected = False
                        else:
                            contact_override_port = override_port
                            contact_search.add_ip(target_name, ip)
                except ValueError:
                    animated_print(
                        f"WARNING: Invalid contact name entered!", error=True, reset=True)
                    Colors(default_color)
                    connected = False
                    get_recipient_ip(user, display_initiate, print_logs,
                                     default_color, private_mode, error_color, temp_sc)
                except TypeError:
                    animated_print(
                        f"WARNING: Invalid contact details!", error=True, reset=True)
                    Colors(default_color)
                    connected = False
                    get_recipient_ip(user, display_initiate, print_logs,
                                     default_color, private_mode, error_color, temp_sc)
                except AttributeError:
                    animated_print(
                        f"WARNING: Invalid contact details!", error=True, reset=True)
                    Colors(default_color)
                    connected = False
                    get_recipient_ip(user, display_initiate, print_logs,
                                     default_color, private_mode, error_color, temp_sc)
        else:
            if ip.count(":") == 1:
                ip = ip.split(":", 1)
                override_port, contact_override_port = ip[1].strip(), ip[1].strip()
                ip = ip[0].strip()
                manual_port = True
            target_mac, target_name, agreed_code = None, None, None
    elif type(ip) == list:
        temp_sc = []
        for address in ip:
            if is_invite:
                if "@" in address:
                    address = address.split("@")
                    target_name = address[0].strip()
                    address = address[1].strip()
                    if "." not in address:
                        contact_search = Contacts(user, get_current_user().lower().strip(
                        ), print_logs, default_color, error_color, private_mode)
                        target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                            ip)
                        override_port = int(override_port)
                        target_name = target_name.replace("\n", "")
                        if target_ip != None:
                            address = target_ip
                        else:
                            address = mac_resolve(target_mac, print_logs)
                        if address == None:
                            animated_print(
                                f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                            Colors(default_color)
                            connected = False
                        else:
                            contact_override_port = override_port
                            contact_search.add_ip(target_name, address)
                    else:
                        target_mac = None
            elif "@" in address:
                address = address.split("@")
                expected_user = address[0].strip()
                address = address[1].strip()
                if "." not in address:
                    contact_search = Contacts(user, get_current_user().lower().strip(
                    ), print_logs, default_color, error_color, private_mode)
                    target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                        ip)
                    override_port = int(override_port)
                    target_name = target_name.replace("\n", "")
                    if target_ip != None:
                        address = target_ip.strip()
                    else:
                        address = mac_resolve(target_mac.strip(), print_logs)
                    if address == None:
                        animated_print(
                            f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                    else:
                        contact_override_port = override_port
                        contact_search.add_ip(target_name, address)
                validated, validiate_sc = validate_foreign_user(
                    address, expected_user, print_logs, temp_sc, message=message, port=override_port)
                temp_sc.append(validate_sc)
                if not validated:
                    if graphic_mode:
                        layout = [[gui.Text(gui_translate(f"Unable to verify if recipient is {expected_user}!"), text_color="red")], [
                            gui.Text(gui_translate("Do you wish to proceed anyway?"))], [gui.Button(gui_translate("Yes"), key="Yes", bind_return_key=True), gui.Button(gui_translate("No"), key="No")]]
                        window = gui.Window(title=gui_translate("Warning"), layout=layout,
                                            margins=(100, 50), font="Courier 20")
                        event, values = window.read()
                        if event == "Yes":
                            proceed = "y"
                        else:
                            proceed = "n"
                        window.close()
                    else:
                        animated_print(
                            f"WARNING: Unable to verify if recipient is {expected_user}!", error=True, reset=True)
                        Colors(default_color)
                        proceed = privacy_input(
                            f"Do you wish to proceed anyway? [Y|N]", private_mode)
                    if "y" in proceed.lower():
                        pass
                    else:
                        address, target_mac, target_name, temp_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs, default_color, private_mode, error_color, temp_sc)
                time.sleep(8)
            elif "." not in address:
                if ":" in address:
                    temp = address
                    contact_search = Contacts(user, get_current_user().lower().strip(
                    ), print_logs, default_color, error_color, private_mode)
                    target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                        ip)
                    override_port = int(override_port)
                    target_name = target_name.replace("\n", "")
                    if target_ip.strip() != None:
                        address = target_ip.strip()
                    else:
                        address = mac_resolve(target_mac.strip(), print_logs)
                    if address == None:
                        animated_print(
                            f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                    else:
                        contact_override_port = override_port
                        contact_search.add_ip(target_name, address)
                else:
                    try:
                        contact_search = Contacts(user, get_current_user().lower().strip(
                        ), print_logs, default_color, error_color, private_mode)
                        target_name, mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                            ip)
                        override_port = int(override_port)
                        target_name = target_name.replace("\n", "")
                        if mac.strip() == "":
                            animated_print(
                                f"WARNING: MAC address for contact is blank!", error=True, reset=True)
                            Colors(default_color)
                            connected = False
                        else:
                            target_mac = mac
                            if target_ip != None:
                                address = target_ip
                            else:
                                address = mac_resolve(target_mac, print_logs)
                            if address == None:
                                animated_print(
                                    f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            else:
                                contact_override_port = override_port
                                contact_search.add_ip(target_name, address)
                    except ValueError:
                        animated_print(
                            f"WARNING: Invalid contact name entered!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                        get_recipient_ip(user, display_initiate, print_logs,
                                         default_color, private_mode, error_color, temp_sc)
                    except TypeError:
                        animated_print(
                            f"WARNING: Invalid contact details!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                        get_recipient_ip(user, display_initiate, print_logs,
                                         default_color, private_mode, error_color, temp_sc)
                    except AttributeError:
                        animated_print(
                            f"WARNING: Invalid contact details!", error=True, reset=True)
                        Colors(default_color)
                        connected = False
                        get_recipient_ip(user, display_initiate, print_logs,
                                         default_color, private_mode, error_color, temp_sc)
    valid_vars = check_vars(ip, target_mac, target_name)
    return valid_vars[0], valid_vars[1], valid_vars[2], temp_sc, agreed_code, override_port


def gnu_ip_resolve(print_logs, private_mode):
    """Employs the modules to handle obtaining an IP address from a GNU/Linux system with multiple interfaces"""
    print("")
    interfaces, graphic_interfaces = netifaces.interfaces(), ""
    if print_logs:
        for i, interface in enumerate(interfaces):
            if graphic_mode:
                graphic_interfaces += f"{i}. {interface}\n"
            else:
                animated_print(f"{i}. {interface}")
        if graphic_mode:
            layout = [[gui.Text(gui_translate(graphic_interfaces))], [gui.Text(gui_translate("Select one of these")), gui.InputText(key="chosen_interface"), gui.Button(
                gui_translate("Select"), bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Interface Selector (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Select":
                chosen_interface = values.get("chosen_interface", None)
            window.close()
        else:
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


def id_packet(sc, **kwargs):
    """Provides, or requests the peer with relevant information about your profile (upon your approval), allowing contacts to be automatically generated, assisting the process of locating individuals to talk with"""
    mode, ip, code_details, accepted = kwargs.get("mode", None), kwargs.get("ip", None), kwargs.get("code", None), False
    if mode == "send":
        try:
            sc.send(f"\\request_user".encode())
            info = sc.recv(1024).decode()
        except:
            info = None
        if info == None or "None" in info:
            return sc, None, None, None
        else:
            #info = decode_foreign_user(code_details[0], code_details[1], info.strip(), applied_default_color)
            info = info[::-1].strip().split(" || ")
            decrypted_username, decrypted_mac, decrypted_override_port, encrypted_username, encrypted_mac, encrypted_override_port, new_user, temp_new_mac, new_mac, override_port = [], [], [], [], [], [], "", "", "", ""
            if len(info) < 3:
                return sc, None, None, None
            for i, char in enumerate(info[1]):
                encrypted_username.append(ord(char))
                decrypted_username.append(chr(int(encrypted_username[i])-22))
            for char in decrypted_username:
                new_user += char
            mac_offset = f"{new_user[0]}{new_user[-1]}"
            new_user = new_user[1:-1]
            for i, char in enumerate(info[0]):
                encrypted_mac.append(ord(char))
                try:
                    temp_char = int(encrypted_mac[i])-int(mac_offset)
                    if temp_char < 32:
                        temp_char = temp_char + 95
                    elif temp_char > 126:
                        temp_char = temp_char - 95
                    decrypted_mac.append(chr(temp_char))
                except:
                    pass
            for char in decrypted_mac:
                temp_new_mac += char
            verify_mac = temp_new_mac.split("=", 1)
            try:
                if verify_mac[1].count(":") == 5:
                    temp_new_mac = verify_mac[1].strip()
            except:
                pass
            if len(temp_new_mac.split(":")[0]) == 4:
                override_port_offset = f"{temp_new_mac[3]}{temp_new_mac[2]}"
                ununual_mac, compounded_mac = True, True
            elif len(temp_new_mac) != 19:
                override_port_offset = f"{temp_new_mac[2]}{temp_new_mac[-4]}"
                ununual_mac, compounded_mac = True, False
            else:
                override_port_offset = f"{temp_new_mac[2]}{temp_new_mac[-5]}"
                ununual_mac, compounded_mac = False, False
            for i in range(len(temp_new_mac)):
                if i == 2 or (i == len(temp_new_mac) - 5 and not ununual_mac):
                    pass
                elif i == 3 and compounded_mac:
                    pass
                else:
                    new_mac += temp_new_mac[i]
            verify_mac = new_mac.split("=", 1)
            try:
                if verify_mac[1].count(":") == 5:
                    new_mac = verify_mac[1].strip()
            except:
                pass
            for i, char in enumerate(info[2]):
                encrypted_override_port.append(ord(char))
                try:
                    temp_char = int(encrypted_override_port[i])-int(override_port_offset)
                    if temp_char < 32:
                        temp_char = temp_char + 95
                    elif temp_char > 126:
                        temp_char = temp_char - 95
                    decrypted_override_port.append(chr(temp_char))
                except:
                    pass
            for char in decrypted_override_port:
                override_port += char
            get_foreign_user(new_user=new_user.strip().capitalize())
            return sc, new_user, new_mac, override_port
    elif mode == "recieve":
        if ip.strip() == "":
            ip = "Unknown"
        if graphic_mode:
            layout = [[gui.Text(gui_translate(f"Do you wish to share your profile to {ip}?")), gui.Button(gui_translate("Yes"), key="yes"), gui.Button(gui_translate("No"), key="no")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            confirm_window = gui.Window(title=f"FiEncrypt - Username Request (Logged in as: {get_current_user()})", layout=layout, font="Courier 20")
            event, values = confirm_window.read()
            if event == "yes":
                accepted = True
            else:
                accepted = False
            confirm_window.close()
        else:
            accepted = privacy_input(f"Do you wish to reveal your username to {ip}? [Y|N]", 0)
            if "y" in accepted.lower():
                accepted = True
            else:
                accepted = False
        if accepted:
            decrypted_username, decrypted_mac, decrypted_override_port, encrypted_username, encrypted_mac, encrypted_override_port, temp_user, temp_mac, temp_override_port, packet = [], [], [], [], [], [], "", "", "", ""
            offset1, offset2, random_port = [random.randint(1, 5), random.randint(0, 9)], [random.randint(1, 5), random.randint(0, 9)], random.randint(2000,20000)
            decrypted_username.append(ord(str(offset1[0])))
            for i, char in enumerate(get_current_user().lower()):
                decrypted_username.append(ord(char))
            decrypted_username.append(ord(str(offset1[1])))
            for i, char in enumerate(decrypted_username):
                encrypted_username.append(chr(int(decrypted_username[i])+22))
            for char in encrypted_username:
                temp_user += char
            for i, char in enumerate(get_mac()):
                try:
                    if i == 2:
                        decrypted_mac.append(ord(str(offset2[0])))
                except IndexError:
                    pass
                decrypted_mac.append(ord(char))
            decrypted_mac.insert(int(decrypted_mac.index(decrypted_mac[len(get_mac())-3])), ord(str(offset2[1])))
            for i, char in enumerate(decrypted_mac):
                temp_char = int(decrypted_mac[i])+int(f"{offset1[0]}{offset1[1]}")
                if temp_char < 32:
                    temp_char = temp_char + 95
                elif temp_char > 126:
                    temp_char = temp_char - 95
                encrypted_mac.append(chr(temp_char))
            for char in encrypted_mac:
                temp_mac += char
            for i, char in enumerate(str(random_port)):
                decrypted_override_port.append(ord(char))
                temp_char = int(decrypted_override_port[i])+int(f"{offset2[0]}{offset2[1]}")
                if temp_char < 32:
                    temp_char = temp_char + 95
                elif temp_char > 126:
                    temp_char = temp_char - 95
                encrypted_override_port.append(chr(temp_char))
            for char in encrypted_override_port:
                temp_override_port += char
            packet = f"{temp_mac} || {temp_user} || {temp_override_port}"[::-1]
            sc.send(packet.encode())
        else:
            sc.send(str(None).encode())
        return accepted


def secretcode(user, current_user, default_color, print_logs, private_mode, error_color):
    """Accepts secret codes to execute special behaviours, like an easter egg! NO PEAKING!"""
    enter_home_directory()
    if graphic_mode:
        layout = [[gui.Text(gui_translate("Enter the secret code here")), gui.InputText(key="secret_code")], [gui.Button(
            gui_translate("Submit"), bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        window = gui.Window(title=gui_translate(f"FiEncrypt - Secret Code (Logged in as: {get_current_user()})"), layout=layout,
                            margins=(100, 50), font="Courier 20")
        event, values = window.read()
        window.close()
        if event == "Submit":
            secret_code = values.get("secret_code", None)
        elif event == "Cancel":
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
    else:
        secret_code = privacy_input(f"Enter the secret code here", private_mode)
    if secret_code == None:
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    try:
        if secret_code.strip() == "":
            if graphic_mode:
                gui.Popup(gui_translate("Code format not valid!"),
                          title=gui_translate("Warning"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                animated_print(
                    f"WARNING: Code format not valid!", error=True, reset=True)
                Colors(default_color)
            log("Secret Code Entered! Valid? False",
                "encryptionManager", current_user, print_logs)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                       print_logs, private_mode, error_color)
        else:
            secret_code = int(secret_code)
    except:
        if graphic_mode:
            gui.Popup(gui_translate("Code format not valid!"),
                      title=gui_translate("Warning"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
            animated_print(
                f"WARNING: Code format not valid!", error=True, reset=True)
            Colors(default_color)
        log("Secret Code Entered! Valid? False",
            "encryptionManager", current_user, print_logs)
        secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                   print_logs, private_mode, error_color)
    completed_code = hash_value(str(secret_code))
    valid, func = check_secret_code(completed_code)
    if not valid:
        completed_code = hash_value(str(secret_code), hash="md5")
        valid, func = check_secret_code(completed_code)
        if valid:
            log("Secret Code Entered! Valid? True",
                "encryptionManager", current_user, print_logs)
        else:
            if graphic_mode:
                gui.Popup(gui_translate(f"Secret code {secret_code} does not exist!"),
                          title=gui_translate("Warning"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                animated_print(
                    f"WARNING: Code not valid!", error=True, reset=True)
                Colors(default_color)
            log("Secret Code Entered! Valid? False",
                "encryptionManager", current_user, print_logs)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                       print_logs, private_mode, error_color)
    else:
        log("Secret Code Entered! Valid? True",
            "encryptionManager", current_user, print_logs)
    if func == 1:
        if graphic_mode:
            temp_popup = gui.Window(title=gui_translate("Alert"), layout=[
                                    [gui.Text(gui_translate("Config editor mode entered! Standby..."))]], font="Courier 20", finalize=True)
        else:
            animated_print("Config editor mode entered! Standby...")
        config_file = open(f"./config.txt", "r+")
        config_data = config_file.read()
        config_lines = config_data.split("\n")
        if not graphic_mode:
            animated_print("Dumping current config file...")
        else:
            temp_popup.close()
        lines = []
        for line, content in enumerate(config_lines):
            animated_print(f"{line}. {content}")
            lines.append(content)
        config_file.close()
        os.remove(f"./config.txt")
        if graphic_mode:
            gui.Popup(gui_translate("Writing a custom config file can cause the program to break. Delete the FiEncrypt folder if you have any issues! Good luck"),
                      title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(
                f"WARNING: Writing a custom config file can cause the program to break. Delete the FiEncrypt folder if you have any issues! Good Luck!", error=True, reset=True)
            Colors(default_color)
        config_file = open("./config.txt", "w+")
        if graphic_mode:
            window = gui.Window(title=gui_translate(f"FiEncrypt - Config Editor (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate("Enter a semi-colon (;) in order for a line break"))], [gui.InputText(
                key="new_code"), gui.Button("Write")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Write":
                new_code = values.get("new_code", None)
            window.close()
        else:
            new_code = privacy_input(
                "Enter a semi-colon (;) in order for a line break", 0)
        new_code = new_code.split(";")
        if len(new_code) != len(config_lines):
            if graphic_mode:
                layout = [[gui.Text(gui_translate("Number of lines differs from the expected value!"), text_color="red")], [gui.Text(gui_translate("Do you wish to proceed?")), gui.Button(
                    gui_translate("Yes"), bind_return_key=True), gui.Button(gui_translate("No"), key="No")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Config Editor (Logged in as: {get_current_user()})"),
                                    layout=layout, margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Yes":
                    proceed = "y"
                else:
                    proceed = "n"
                window.close()
            else:
                animated_print(
                    f"WARNING: Number of lines differs from the expected value!", error=True, reset=True)
                Colors(default_color)
                proceed = input("Do you wish to proceed? (Y/N): ")
            if "y" in proceed.lower():
                for line in new_code:
                    line = f"{line}\n"
                    config_file.write(line)
                config_file.close()
                time.sleep(1)
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
            else:
                secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                           print_logs, private_mode, error_color)
    elif func == 2:
        if not graphic_mode:
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
                if graphic_mode:
                    window = gui.Window(title=gui_translate(f"FiEncrypt - BREADFISH!!! (Logged in as: {get_current_user()})"), layout=[[gui.Text(line1, text_color="blue")], [gui.Text(line2, text_color="blue")], [gui.Text(line3, text_color="blue")], [gui.Text(line4, text_color="blue")], [gui.Text(line5, text_color="blue")], [gui.Text(line6, text_color="blue")], [gui.Text(line7, text_color="blue")], [gui.Text(line8, text_color="blue")], [gui.Text(line9, text_color="blue")], [gui.Text(line10, text_color="blue")], [
                                        gui.Text(line11, text_color="blue")], [gui.Text(line12, text_color="blue")], [gui.Text(line13, text_color="blue")], [gui.Text(line14, text_color="blue")], [gui.Text(line15, text_color="blue")], [gui.Text(line16, text_color="blue")], [gui.Text(line17, text_color="blue")]], margins=(100, 50), size=(random.randint(600, 1000), random.randint(400, 800)), font=f"Courier {random.randint(10, 20)}", finalize=True)
                    time.sleep(0.5)
                    window.close()
                else:
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
            if graphic_mode:
                break
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
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
        enter_home_directory()
        with open(f"./config.txt", "r+") as config_file:
            config_lines, refresh_config = config_file.read().split("\n"), False
            for i, line in enumerate(config_lines):
                if "troll_with_filler" in line:
                    refresh_config = True
                    config_file.seek(0)
                    config_file.truncate()
                    del(config_lines[i])
            if not refresh_config:
                config_file.write("troll_with_filler")
                status = "enabled... ;) Enjoy"
            else:
                config_file.seek(0)
                for line in config_lines:
                    config_file.write(f"{line}\n")
                status = "disabled"
        if graphic_mode:
            gui.Popup(gui_translate(f"Word filler troll {status}"), title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"Word filler troll {status}")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif func == 5:
        enter_home_directory()
        if graphic_mode:
            username, password = "", ""
            while username == None or username.strip() == "" or password == None or password.strip() == "":
                layout = [[gui.Text(gui_translate("Please confirm your login"))], [gui.Text(gui_translate("Username")), gui.InputText(
                    key="username")], [gui.Text(gui_translate("Password")), gui.InputText(key="password", password_char="*")], [gui.Button(gui_translate("Login"), key="Login", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate("FiEncrypt - Login Confirmation"),
                                    layout=layout, margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Login":
                    username = values.get("username", None)
                    password = values.get("password", None)
                    if username == None or username.strip() == "":
                        gui.Popup(gui_translate("Username cannot be blank!"), title=gui_translate("Warning"),
                                  text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    elif password == None or password.strip() == "":
                        gui.Popup(gui_translate("Password cannot be blank!"), title=gui_translate("Warning"),
                                  text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                window.close()
        else:
            animated_print(f"Please confirm your login: ")
            username = privacy_input("Username", private_mode)
            password = privacy_input("Password", 1)
        valid = validate_login(username, password)
        current_valid = username.lower().strip() == get_current_user().lower().strip()
        if valid and current_valid:
            user_target = privacy_input("Enter name of user you wish to delete (Case sensitive)", private_mode)
            if user_target != None and user_target.strip() != "":
                if user_target.strip().lower() == get_current_user().strip().lower():
                    if graphic_mode:
                        confirm_self_delete = gui.popup_yes_no(gui_translate(f"This action could affect the currently logged in account {get_current_user()}!\nDo you wish to proceed?"), title=gui_translate("Warning"), font="Courier 20", text_color="red")
                        if confirm_self_delete == "Yes":
                            confirm_self_delete = True
                        else:
                            gui.Popup(gui_translate("Aborting"), title=gui_translate("Warning"), font="Courier 20", auto_close=True, auto_close_duration=5)
                            confirm_self_delete = False
                    else:
                        confirm_self_delete = to_boolean(privacy_input("Delete currently logged in account? [True|False]", private_mode))
                    if confirm_self_delete:
                        pass
                    else:
                        menu(user, None, print_logs, default_color,
                            private_mode, error_color, print_speed=0)
                enter_home_directory()
                with open("CREDENTIALS.txt", "r+") as credentials_file:
                    credentials = credentials_file.read().split("\n")
                    for i, credential in enumerate(credentials):
                        if hash_value(user_target.strip()) == credential and (i % 2) / 2 == 0:
                            target_user_hash, target_user_index = credential, i
                            print(credentials[i], credentials[i+1])
                            del(credentials[i], credentials[i+1])
                    credentials_file.seek(0)
                    credentials_file.truncate()
                    for new_credential in credentials:
                        new_credential = new_credential.replace("\n", "")
                        credentials_file.write(f"{new_credential}\n")
                enter_home_directory()
                try:
                    shutil.rmtree(target_user_hash)
                    if graphic_mode:
                        gui.Popup(gui_translate(f"User account {user_target} successfully deleted! Restarting FiEncrypt"), title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"User account {user_target} successfully deleted! Restarting FiEncrypt")
                    initiate()
                except:
                    if graphic_mode:
                        gui.Popup(gui_translate(f"User {user_target} does not exist!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"WARNING: User {user_target} does not exist!", error=True, reset=True)
                    secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                               print_logs, private_mode, error_color)
            else:
                if graphic_mode:
                    gui.Popup(gui_translate("Target cannot be blank!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print("WARNING: Target cannot be blank!", error=True, reset=True)
                secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                           print_logs, private_mode, error_color)
        else:
            if valid:
                if graphic_mode:
                    gui.Popup(gui_translate(f"Cannot log in as any user except {get_current_user()}!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(f"WARNING: Cannot log in as any user except {get_current_user()}!", error=True, reset=True)
            else:
                if graphic_mode:
                    gui.Popup(gui_translate("Invalid login!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print("WARNING: Invalid login!", error=True, reset=True)
            secretcode(user, capitalize_user(capitalize_user(get_current_user())), default_color,
                       print_logs, private_mode, error_color)


def showcode(user, current_user, private_mode, print_logs, error_color, default_color):
    """Outputs the current encryption code in various forms, based on input parameters"""
    #enter_home_directory()
    with open(f"./code.txt", "r+") as temp_file:
        code = temp_file.read()
    if current_user != 1 and current_user != 2:
        if graphic_mode:
            if code == "":
                layout = [[gui.Text(gui_translate("This is the current code saved in the code.txt file"))], [gui.Text(gui_translate("No code present in the code.txt file! Either it has not been generated or manually overwritten!"), text_color="red")], [
                    gui.Text(gui_translate("FiEncrypt (C) le_firehawk 2021"), font="Courier 10", text_color="grey")]]
            else:
                layout = [[gui.Text(gui_translate("This is the current code saved in the code.txt file"))], [gui.Text(code)], [
                    gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Current Code (Logged in as: {get_current_user()})"), layout=layout,
                                margins=(100, 50), font="Courier 20", finalize=True)
        else:
            animated_print(
                f"This is the current code saved in the code.txt file:")
            if code == "":
                animated_print(
                    f"WARNING: No code present in the code.txt file! Either it has not been generated or manually overwritten!", error=True, reset=True)
                Colors(default_color)
            else:
                animated_print(code)
        log(f"Existing encryption requested!", "encryptionManager", current_user, print_logs)
        if graphic_mode:
            time.sleep(4)
            window.close()
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
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
                       print_logs, default_color, error_color, auto_code=True)
            showcode(
                user, 1, private_mode, print_logs, error_color, default_color)


def even_num():
    """Produces a random even number between 2 and (number between 4 and 100)"""
    num2 = 1
    while (num2 % 2) / 2 != 0:
        num1 = random.randint(4, 100)
        num2 = random.randint(2, int(num1))
    return num2


def parse_size(size, filename):
    """Transforms the raw byte-size of a file into human readable format"""
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
    """Adds/replaces the characters of a string to make it compatible for reference in bash/related terminal interfaces that do not take kindly to spaces"""
    return filepath.strip().replace(" ", "\ ").replace(
        "'", "\\'").replace("(", "\\(").replace(")", "\\)")


def random_filler(length, string):
    """Produces filler to accompany a message before it is send over the network"""
    output, alphabet, number, symbols, new_string, troll_with_filler = "", ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                                                         "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"], [1, 2, 3, 4, 5, 6, 7, 8, 9], ["!", "@", "#", "$", "%", "^", "&", "*",
                                                                                                                                                              "(", ")", "-", "=", "+", "{", "}", "[", "]", ";", ":", "'", "\"", ",", ".", "<", ">", "/", "?"], "", retrieve_config_settings(exclusive="filler_troll")
    if troll_with_filler:
        words, output = ["a", "the", "johnny"], ["", ""]
        chosen_word, length_left = None, int(length)
        while chosen_word == None or len(chosen_word) > length_left or length_left > 0:
            chosen_word = random.choice(words)
            if len(chosen_word) <= length_left / 2:
                if len(output[0]) <= length_left / 2:
                    output[0] += chosen_word
                else:
                    output[1] += chosen_word
                length_left -= len(chosen_word)
            elif len(chosen_word) <= length_left:
                output[1] += chosen_word
                length_left -= len(chosen_word)
            print(length_left, chosen_word)
            if length_left <= 0:
                break
    else:
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
    elif not troll_with_filler:
        for i in range(0, int(len(output)/2)):
            new_string += output[i]
        new_string += string
        for j in range(int(len(output)/2), int(len(output))):
            new_string += output[j]
        return new_string
    else:
        for word in output[0]:
            new_string += word
        new_string += string
        if len(output[1]) > len(output[0]):
            output[1] = output[1][:len(output[0])]
        elif len(output[1]) < len(output[0]):
            output[1] = f"{output[1]}{output[0][:len(output[0])-len(output[1])]}"
        for word in output[1]:
            new_string += word
        print(output[0], output[1], string)
        print(new_string)
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


def randomcode(user, current_user, auto_request, private_mode, print_logs, default_color, error_color, **auto_code):
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
                   print_logs, default_color, error_color, auto_code=auto_code)
    if not auto_request:
        if graphic_mode:
            custom_code = "y"
        else:
            custom_code = privacy_input(
                f"Would you like to have a UUID code generated for you? (Y/N)", 0)
    else:
        custom_code = "y"
    if custom_code == None:
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_color, error_color, auto_code=auto_code)
    elif "y" in custom_code.lower() and not auto_code:
        temp_string = str(
            f"{gui_translate('New code generated as of')} {str(datetime.datetime.now())} {gui_translate('is')} ${str(a)}_{str(rand_code)}_${b}#")
        if graphic_mode:
            window = gui.Window(title=gui_translate(f"FiEncrypt - New Code (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate(temp_string))], [gui.Text(
                "FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20", finalize=True)
        else:
            animated_print(temp_string)
    elif "y" in custom_code.lower():
        pass
    else:
        try:
            # ?The user can input a code of their own, which will be combined with the prefix and timestamp that were automatically generated
            if graphic_mode:
                window = gui.Window(title=gui_translate(f"FiEncrypt - New Code (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate("Enter the code you wish to set (or leave this blank to leave code empty)"))], [gui.InputText(
                    key="manual_code"), gui.Button(gui_translate("Save"), key="Save", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Save":
                    rand_code = values.get("manual_code", None)
                window.close()
            else:
                rand_code = privacy_input(
                    f"Enter the code you wish to set (or leave this blank to leave code empty)", private_mode)
            if rand_code == None or rand_code.strip() == "":
                if graphic_mode:
                    gui.Popup(gui_translate("No code entered!"), title=gui_translate("Warning"),
                              font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print("No code entered!")
                randomcode(user, current_user, auto_request, private_mode,
                           print_logs, default_color, error_color, auto_code=auto_code)
        except ValueError:
            animated_print(
                f"WARNING: With no code saved locally, auto-generated key functions will not work!", error=True, reset=True)
            log("Code override ordered... leaving blank!",
                "encryptionManager", get_current_user(), None)
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
    try:
        new_string = f"${str(a)}_{str(rand_code)}_${str(b)}#"
        if custom_code == None:
            randomcode(user, current_user, auto_request, private_mode,
                       print_logs, default_color, error_color, auto_code=auto_code)
        if "y" in custom_code.lower():
            pass
        else:
            if graphic_mode:
                window = gui.Window(title=gui_translate(f"FiEncrypt - New Code (Logged in as: {get_current_user()})"), layout=[[gui.Text(f"{gui_translate('New code generated as of')} {str(datetime.datetime.now())} {gui_translate('is')} ${str(a)}_{str(rand_code)}_${b}#")], [
                                    gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20", finalize=True)
            else:
                animated_print(str(
                    f"Current code as of {str(datetime.datetime.now())} is ${str(a)}_{str(rand_code)}_${b}#"))
        enter_home_directory()
        if pass_os() == "win32":
            with open("./code.txt", "r+") as code_file:
                code_file.seek(0)
                code_file.truncate()
                code_file.write(new_string)
        else:
            with open("./code.txt", "w+") as code_file:
                code_file.seek(0)
                code_file.truncate()
                code_file.write(new_string)
        log(f"New encryption code requested!",
            "encryptionManager", current_user, print_logs)
        enter_home_directory()
        protect_tree()
        if not auto_code:
            if not graphic_mode:
                animated_print(f"New code successfully written to code.txt file")
            else:
                try:
                    time.sleep(4)
                    window.close()
                except:
                    pass
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        else:
            pass
    except UnboundLocalError:
        log("Invalid Encryption code generated! Retrying...",
            "encryptionManager", get_current_user(), None)
        randomcode(user, current_user, auto_request, private_mode,
                   print_logs, default_color, error_color, auto_code=auto_code)


def newmessage(code, user, recipient_ip, temp_sc, prefix, date, talking_to_self, error_color, default_color, private_mode, print_logs, mailing, display_initiate, auto_code, **kwargs):
    """Allows user to create and send an encrypted message"""
    global override_port, contact_override_port
    previous_message, poked, voice_message, outbound_file, manual, faulty_override, stored_message, sc, prev_messages, window, early_file, in_contacts, priority_code, use_bluetooth, checking_mailbox = kwargs.get(
        "message", ""), kwargs.get("poked", False), False, False, False, kwargs.get("faulty", False), kwargs.get("stored_message", ""), temp_sc, kwargs.get("prev", []), kwargs.get("window", None), None, kwargs.get("in_contacts", None), kwargs.get("priority_code", None), kwargs.get("use_bluetooth", False), kwargs.get("checking_mailbox", False)
    temp_display_name, prev_message_temp, images, agreed_code, get_username = get_foreign_user(), "", [], None, False
    if temp_display_name == None:
        temp_display_name = recipient_ip
    try:
        if contact_override_port != None and contact_override_port.strip() != "":
            override_port = contact_override_port
    except:
        pass
    for i, messages in enumerate(prev_messages):
        if len(messages) == 4 or len(messages) == 5:
            message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_user", "").replace("\\request_username", "").strip()
            if messages[2].strip().lower() == get_current_user().strip().lower():
                gap = 30
            else:
                gap = 40
            if len(message_to_show) > gap:
                temp_list = list(message_to_show)
                for i in range(gap, len(temp_list), gap):
                    j = i
                    try:
                        while temp_list[j] != " ":
                            j += 1
                            if j >= i + 5:
                                break
                        if messages[2].strip().lower() == get_current_user().strip().lower():
                            temp_list.insert(j, "\n\t\t\t\t")
                        else:
                            temp_list.insert(j, "\n")
                    except IndexError:
                        if messages[2].strip().lower() == get_current_user().strip().lower():
                            temp_list.insert(j-i, "\n\t\t\t\t")
                        else:
                            temp_list.insert(j-i, "\n")
                message_to_show = ""
                for char in temp_list:
                    message_to_show += char
            if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
            elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
            elif message_to_show.strip() != "" and has_emoji(messages[0]):
                prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
            elif message_to_show.strip() != "" and has_file(messages[0]):
                prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
            elif message_to_show.strip() != "":
                prev_message_temp += f"{message_to_show} - {messages[1]}\n"
            elif has_emoji(messages[0]):
                prev_message_temp += f"(emoji) - {messages[1]}\n"
            elif has_file(messages[0]):
                prev_message_temp += f"(file) - {messages[1]}\n"
            temp_day = str(datetime.datetime.now()).split("-", 2)
            temp_day = temp_day[2].split()
            if temp_day[0].strip().startswith("0"):
                temp_day[0] = temp_day[0].replace("0", "").strip()
            # if temp_day[0].strip() not in messages[3][0:2]:
            #     prev_message_temp += f"{messages[3]}\n"
            try:
                if messages[4] != None:
                    temp_name = messages[4].split(".")[0]
                    images.append(f"{temp_name}.png")
            except:
                pass
        else:
            pass
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
    if graphic_mode:
        try:
            window.close()
        except:
            pass
    if (recipient_ip == "" or code2 == "") and not faulty_override:
        if graphic_mode:
            temp_layout = [[gui.Text(gui_translate("Enter the encryption code for the message here! Or, leave it blank for the auto-generated key"))], [
                gui.InputText(key="code")], [gui.Button(gui_translate("Set Code"), key="Set Code", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            temp_window = gui.Window(title=gui_translate(f"FiEncrypt - Code Input (Logged in as: {get_current_user()})"), layout=temp_layout,
                                     margins=(100, 50), font="Courier 20")
            event, values = temp_window.read()
            temp_window.close()
            if event == "Set Code":
                code2 = values.get("code", "")
            elif event == "Cancel":
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        else:
            code2 = privacy_input(
                f"Enter the encryption code for the message here! Or, leave it blank for the auto-generated key", private_mode)
        if code2 == "EXIT" or code2 == None:
            Colors(default_color)
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        if code2 == "":
            if code != "":
                code2 = code
            else:
                animated_print(
                    f"WARNING: Unable to retrieve auto-generated key! Make sure the key is in the code.txt file", error=True, reset=True)
                Colors(default_color)
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
        # ?You may notice some scripts are better run than others, that's because this program really grew with my knowledge, and I'm too custom_code to refine everything
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
            Colors(default_color, force=True)
        except:
            code_seg1 = str(code_seg1)[::-1]
            temp = code_seg2
            code_seg2 = int(code_seg1)
            code_seg1 = temp
            Colors(default_color)
    try:
        temp_date = timestamp.split("|")
        temp_date = temp_date[1]
        time_decode = int(prefix[1][1].replace("#", ""))
        months, rd_dates, st_dates, nd_dates, th_dates = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], [
            "3", "23"], ["1", "21", "31"], ["2", "22"], ["4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "24", "25", "26", "27", "28", "29", "30"]
        if len(temp_date) == 3:
            if temp_date[0] == "0":
                temp_date = f"{temp_date[-1]}/{temp_date[0:len(temp_date)-1]}"
            elif temp_date[-2] == "0":
                temp_date = f"{temp_date[-1]}/0{temp_date[0]}"
            else:
                temp_date = f"{temp_date[0]}/{temp_date[0:len(temp_date)-1]}"
        elif len(temp_date) == 4:
            if temp_date[0] == "0" and temp_date[2] == "0":
                temp_date = f"{temp_date[3]}/0{temp_date[1]}"
            elif temp_date[0] == "0":
                temp_date = f"{temp_date[2:len(temp_date)]}/0{temp_date[1]}"
            elif temp_date[2] == "0":
                temp_date = f"{temp_date[len(temp_date)]}/{temp_date[0:2]}"
            else:
                temp_date = f"{temp_date[-2:len(temp_date)]}/{temp_date[0:2]}"
        elif len(temp_date) == 2:
            temp_date = f"{temp_date[0]}/{temp_date[-1]}"
        else:
            temp_date = "Date: Unknown"
        if temp_date != "Date: Unknown":
            day, month = temp_date.split("/")
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
                temp_date = f"{day} of {month}, {substring(str(datetime.datetime.now()), '-', 0)}"
            else:
                temp_date = "Date: Unknown"
        temp_timestamp = timestamp.split("A")
        temp_timestamp[0] = temp_timestamp[0].replace("$", "")
        temp_timestamp[1] = temp_timestamp[1].split("|")
        temp_timestamp[1] = temp_timestamp[1][0]
        try:
            hrs = int(temp_timestamp[0]) - int(time_decode)
            mins = int(temp_timestamp[1]) - int(time_decode)
        except ValueError:
            hrs = int(temp_timestamp[0][:: -1]) - int(time_decode)
            mins = int(temp_timestamp[1][:: -1]) - int(time_decode)
        if int(hrs) <= 9:
            try:
                hrs = str(hrs).replace("-", "")
                hrs = int(f"0{hrs}")
            except ValueError:
                # ? Sometimes the @time_decode value is poorly generated and exceeds the value of the encrypted temp_timestamp, so this warning is displayed before the program attempts to decrypt the time after reversing the string
                animated_print(
                    f"WARNING: Irregularity detected in the decrypted temp_timestamp! It may be wrong!", error=True, reset=True)
                Colors(default_color)
                hrs = int(temp_timestamp[0][::-1]) - int(time_decode)
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
                mins = int(temp_timestamp[1][:: -1]) - int(time_decode)
                mins = f"0{mins}"
        else:
            try:
                if mins < 0:
                    mins = int(temp_timestamp[1][:: -1]) - int(time_decode)
                else:
                    mins = int(mins)
            except ValueError:
                mins = int(temp_timestamp[1][:: -1]) - int(time_decode)
        temp_timestamp = f"{hrs}:{mins}{suffix}"
    except:
        pass
    if prev_messages == None:
        prev_messages = []
    if conversation_mode and recipient_ip != "" and poked and not checking_mailbox:
        try:
            if faulty_override and stored_message.strip() != "":
                message_text = stored_message
            else:
                if graphic_mode:
                    temp_display_name, early_file = get_foreign_user(), None
                    if temp_display_name == None:
                        temp_display_name = recipient_ip
                    enter_home_directory()
                    os.chdir("./cache")
                    for i, image_name in enumerate(images):
                        if not os.path.exists(image_name):
                            del(images[i])
                    enter_home_directory()
                    os.chdir("./cache")
                    layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                        gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window, overwrite_file = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20"), False
                    while True:
                        try:
                            event, values = window.read()
                        except:
                            message_text = "\\exit"
                            break
                        if event == ">>":
                            message_text = values.get("message_input", "")
                            break
                        elif event == "file":
                            if early_file == None:
                                early_file = filedialog.askopenfilename(
                                    title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                                if len(early_file) == 0:
                                    early_file = None
                            else:
                                if not overwrite_file:
                                    gui.Popup(gui_translate("Only one file can be sent at a time"),
                                              title="Warning", font="Courier 20", text_color="red", grab_anywhere=True, auto_close=True, auto_close_duration=5)
                                    overwrite_file = True
                                else:
                                    early_file = None
                        elif event == "exit":
                            message_text = values.get("message_input", "")
                            message_text += "\\exit"
                            break
                    window.close()
                else:
                    message_text = privacy_input(
                        f"How do you feel", private_mode, line_break=True)
            if message_text == None:
                Colors(default_color)
                menu(user, display_initiate, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
            while message_text.strip() == "":
                if graphic_mode:
                    early_file = None
                    gui.Popup(gui_translate("No message was entered!"), title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    enter_home_directory()
                    os.chdir("./cache")
                    for i, image_name in enumerate(images):
                        if not os.path.exists(image_name):
                            del(images[i])
                    enter_home_directory()
                    os.chdir("./cache")
                    layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                        gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    while True:
                        try:
                            event, values = window.read()
                        except:
                            message_text = "\\exit"
                            break
                        if event == ">>":
                            message_text = values.get("message_input", "")
                            break
                        elif event == "file":
                            if early_file == None:
                                early_file = filedialog.askopenfilename(
                                    title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                                if len(early_file) == 0:
                                    early_file = None
                            else:
                                gui.Popup(gui_translate("Only one file can be sent at a time"),
                                          title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        elif event == "exit":
                            message_text = values.get("message_input", "")
                            message_text += "\\exit"
                            break
                    window.close()
                else:
                    animated_print(
                        f"WARNING: No message was entered!", error=True, reset=True)
                    Colors(default_color)
                    message_text = privacy_input(
                        f"How do you feel", private_mode)
            prev_messages.append([message_text, temp_timestamp,
                                  get_current_user().strip().lower(), temp_date])
            if message_text == None:
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
                newmessage(code, user, "", temp_sc, prefix, date, talking_to_self,
                           error_color, default_color, private_mode, print_logs, mailing, display_initiate, message=previous_message, prev=prev_messages, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
            elif graphic_mode:
                prev_message_temp, images = "", []
                try:
                    window.close()
                except:
                    pass
                for i, messages in enumerate(prev_messages):
                    if len(messages) == 4 or len(messages) == 5:
                        if messages[0] == prev_messages[i-1][0] and messages[1] == prev_messages[i-1][1] and messages[2] == prev_messages[i-1][2]:
                            pass
                        else:
                            message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                                "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_user", "").replace("\\request_username", "").strip()
                            if messages[2].strip().lower() == get_current_user().strip().lower():
                                gap = 30
                            else:
                                gap = 40
                            if len(message_to_show) > gap:
                                temp_list = list(message_to_show)
                                for i in range(gap, len(temp_list), gap):
                                    j = i
                                    try:
                                        while temp_list[j] != " ":
                                            j += 1
                                            if j >= i + 5:
                                                break
                                        if messages[2].strip().lower() == get_current_user().strip().lower():
                                            temp_list.insert(j, "\n\t\t\t\t")
                                        else:
                                            temp_list.insert(j, "\n")
                                    except IndexError:
                                        if messages[2].strip().lower() == get_current_user().strip().lower():
                                            temp_list.insert(j-i, "\n\t\t\t\t")
                                        else:
                                            temp_list.insert(j-i, "\n")
                                message_to_show = ""
                                for char in temp_list:
                                    message_to_show += char
                            if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                                prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                            elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                                prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                            elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                                prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                            elif message_to_show.strip() != "" and has_emoji(messages[0]):
                                prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                            elif message_to_show.strip() != "" and has_file(messages[0]):
                                prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                            elif message_to_show.strip() != "":
                                prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                            elif has_emoji(messages[0]):
                                prev_message_temp += f"(emoji) - {messages[1]}\n"
                            elif has_file(messages[0]):
                                prev_message_temp += f"(file) - {messages[1]}\n"
                            temp_day = str(datetime.datetime.now()).split("-", 2)
                            temp_day = temp_day[2].split()
                            if temp_day[0].strip().startswith("0"):
                                temp_day[0] = temp_day[0].replace("0", "").strip()
                            # if temp_day[0].strip() not in messages[3][0:2]:
                            #     prev_message_temp += f"{messages[3]}\n"
                            try:
                                if messages[4] != None:
                                    temp_name = messages[4].split(".")[0]
                                    images.append(f"{temp_name}.png")
                            except:
                                pass
                    else:
                        pass
                enter_home_directory()
                os.chdir("./cache")
                for i, image_name in enumerate(images):
                    if not os.path.exists(image_name):
                        del(images[i])
                enter_home_directory()
                os.chdir("./cache")
                layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                    gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                    layout=layout, margins=(100, 50), font="Courier 20")

        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
    elif conversation_mode and recipient_ip != "" and not checking_mailbox:
        try:
            if faulty_override and stored_message.strip() != "":
                message_text = stored_message
            else:
                if graphic_mode:
                    temp_display_name, early_file = get_foreign_user(), None
                    if temp_display_name == None:
                        temp_display_name = recipient_ip
                    enter_home_directory()
                    os.chdir("./cache")
                    for i, image_name in enumerate(images):
                        if not os.path.exists(image_name):
                            del(images[i])
                    enter_home_directory()
                    os.chdir("./cache")
                    layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                        gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    while True:
                        try:
                            event, values = window.read()
                        except:
                            message_text = "\\exit"
                            break
                        if event == ">>":
                            message_text = values.get("message_input", "")
                            break
                        elif event == "file":
                            if early_file == None:
                                early_file = filedialog.askopenfilename(
                                    title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                                if len(early_file) == 0:
                                    early_file = None
                            else:
                                gui.Popup(gui_translate("Only one file can be sent at a time"),
                                          title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        elif event == "exit":
                            message_text = values.get("message_input", "")
                            message_text += "\\exit"
                            break
                    window.close()
                else:
                    message_text = privacy_input(
                        f"Enter a reply here", private_mode, line_break=True)
            if message_text == None:
                Colors(default_color)
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                menu(user, display_initiate, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
            while message_text.strip() == "":
                if graphic_mode:
                    early_file = None
                    gui.Popup("No message was entered!", title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    enter_home_directory()
                    os.chdir("./cache")
                    for i, image_name in enumerate(images):
                        if not os.path.exists(image_name):
                            del(images[i])
                    enter_home_directory()
                    os.chdir("./cache")
                    layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                        gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    while True:
                        try:
                            event, values = window.read()
                        except:
                            message_text = "\\exit"
                            break
                        if event == ">>":
                            message_text = values.get("message_input", "")
                            break
                        elif event == "file":
                            if early_file == None:
                                early_file = filedialog.askopenfilename(
                                    title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                                if len(early_file) == 0:
                                    early_file = None
                            else:
                                gui.Popup(gui_translate("Only one file can be sent at a time"),
                                          title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        elif event == "exit":
                            message_text = values.get("message_input", "")
                            message_text += "\\exit"
                            break
                    window.close()
                else:
                    animated_print(
                        f"WARNING: No message was entered!", error=True, reset=True)
                    Colors(default_color)
                    message_text = privacy_input(
                        f"Enter a reply here", private_mode)
            prev_messages.append([message_text, temp_timestamp,
                                  get_current_user().strip().lower(), temp_date])
            if message_text == None:
                try:
                    sc.send(str("\\exit").encode())
                except:
                    pass
                sc.close()
                log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
                newmessage(code, user, "", temp_sc, prefix, date, talking_to_self,
                           error_color, default_color, private_mode, print_logs, mailing, display_initiate, message=previous_message, prev=prev_messages, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        # *When the exit exits, the other client they have a TCP connection to automatically recieves the exit code, triggering their connection to close as well
        except KeyboardInterrupt:
            animated_print(f"\nKilling server channel!")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            log("Server channel shutting down!", "networkManager", get_current_user(), print_logs)
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
    else:
        if faulty_override and stored_message.strip() != "":
            message_text = stored_message
        else:
            if graphic_mode:
                temp_display_name, early_file = get_foreign_user(), None
                if temp_display_name == None:
                    temp_display_name = recipient_ip
                enter_home_directory()
                os.chdir("./cache")
                for i, image_name in enumerate(images):
                    if not os.path.exists(image_name):
                        del(images[i])
                enter_home_directory()
                os.chdir("./cache")
                layout = [[gui.Text(gui_translate(f"New Conversation"), font="Courier 30", text_color="red")], [gui.Text(
                    gui_translate(prev_message_temp, pm=True), font="Courier 20")], [gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file", font="Courier 20"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - New Conversation (Logged in as: {get_current_user()})"),
                                    layout=layout, margins=(100, 50))
                while True:
                    try:
                        event, values = window.read()
                    except:
                        message_text = "\\exit"
                        break
                    if event == ">>":
                        message_text = values.get("message_input", "")
                        break
                    elif event == "file":
                        if early_file == None:
                            early_file = filedialog.askopenfilename(
                                title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                            if len(early_file) == 0:
                                early_file = None
                        else:
                            gui.Popup(gui_translate("Only one file can be sent at a time"),
                                      title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                window.close()
            else:
                message_text = privacy_input(
                    f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colors(default_color)
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            finally:
                try:
                    sc.close()
                except:
                    pass
            menu(user, display_initiate, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        while message_text.strip() == "":
            if graphic_mode:
                early_file = None
                gui.Popup("No message was entered!", title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                enter_home_directory()
                os.chdir("./cache")
                for i, image_name in enumerate(images):
                    if not os.path.exists(image_name):
                        del(images[i])
                enter_home_directory()
                os.chdir("./cache")
                layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                    gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.InputText(key="message_input", font="Courier 20"), gui.Button(gui_translate("File"), key="file"), gui.Button(gui_translate("Exit"), key="exit"), gui.Button(">>", bind_return_key=True, font="Courier 20")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                    layout=layout, margins=(100, 50), font="Courier 20")
                while True:
                    try:
                        event, values = window.read()
                    except:
                        message_text = "\\exit"
                        break
                    if event == ">>":
                        message_text = values.get("message_input", "")
                        break
                    elif event == "file":
                        if early_file == None:
                            early_file = filedialog.askopenfilename(
                                title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../../")

                            if len(early_file) == 0:
                                early_file = None
                        else:
                            gui.Popup(gui_translate("Only one file can be sent at a time"),
                                      title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    elif event == "exit":
                        message_text = values.get("message_input", "")
                        message_text += "\\exit"
                        break
                window.close()
            else:
                animated_print(
                    f"WARNING: No message was entered!", error=True, reset=True)
                Colors(default_color)
                message_text = privacy_input(
                    f"Enter your text here", private_mode, line_break=True)
        if message_text == None:
            Colors(default_color)
            animated_print(f"Returning to menu...")
            try:
                sc.send(str("\\exit").encode())
            except:
                pass
            sc.close()
            menu(user, display_initiate, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        elif graphic_mode and recipient_ip != "":
            prev_messages.append([message_text, temp_timestamp,
                                  get_current_user().strip().lower(), temp_date])
            for i, messages in enumerate(prev_messages):
                if len(messages) == 4 or len(messages) == 5:
                    if messages[0] == prev_messages[i-1][0] and messages[1] == prev_messages[i-1][1] and messages[2] == prev_messages[i-1][2]:
                        pass
                    else:
                        message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                            "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_user", "").replace("\\request_username", "").strip()
                        if messages[2].strip().lower() == get_current_user().strip().lower():
                            gap = 30
                        else:
                            gap = 40
                        if len(message_to_show) > gap:
                            temp_list = list(message_to_show)
                            for i in range(gap, len(temp_list), gap):
                                j = i
                                try:
                                    while temp_list[j] != " ":
                                        j += 1
                                        if j >= i + 5:
                                            break
                                    if messages[2].strip().lower() == get_current_user().strip().lower():
                                        temp_list.insert(j, "\n\t\t\t\t")
                                    else:
                                        temp_list.insert(j, "\n")
                                except IndexError:
                                    if messages[2].strip().lower() == get_current_user().strip().lower():
                                        temp_list.insert(j-i, "\n\t\t\t\t")
                                    else:
                                        temp_list.insert(j-i, "\n")
                            message_to_show = ""
                            for char in temp_list:
                                message_to_show += char
                        if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                            prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_emoji(messages[0]):
                            prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_file(messages[0]):
                            prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                        elif message_to_show.strip() != "":
                            prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                        elif has_emoji(messages[0]):
                            prev_message_temp += f"(emoji) - {messages[1]}\n"
                        elif has_file(messages[0]):
                            prev_message_temp += f"(file) - {messages[1]}\n"
                        temp_day = str(datetime.datetime.now()).split("-", 2)
                        temp_day = temp_day[2].split()
                        if temp_day[0].strip().startswith("0"):
                            temp_day[0] = temp_day[0].replace("0", "").strip()
                        # if temp_day[0].strip() not in messages[3][0:2]:
                        #     prev_message_temp += f"{messages[3]}\n"
                        try:
                            if messages[4] != None:
                                temp_name = messages[4].split(".")[0]
                                images.append(f"{temp_name}.png")
                        except:
                            pass
                else:
                    pass
            enter_home_directory()
            os.chdir("./cache")
            for i, image_name in enumerate(images):
                if not os.path.exists(image_name):
                    del(images[i])
            enter_home_directory()
            os.chdir("./cache")
            layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20")
        elif graphic_mode:
            try:
                prev_messages.append([message_text, temp_timestamp,
                                      get_current_user().strip().lower(), temp_date])
            except:
                pass
            for i, messages in enumerate(prev_messages):
                if len(messages) == 4 or len(messages) == 5:
                    message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                        "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_user", "").replace("\\request_username", "").strip()
                    if messages[2].strip().lower() == get_current_user().strip().lower():
                        gap = 30
                    else:
                        gap = 40
                    if len(message_to_show) > gap:
                        temp_list = list(message_to_show)
                        for i in range(gap, len(temp_list), gap):
                            j = i
                            try:
                                while temp_list[j] != " ":
                                    j += 1
                                    if j >= i + 5:
                                        break
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j, "\n")
                            except IndexError:
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j-i, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j-i, "\n")
                        message_to_show = ""
                        for char in temp_list:
                            message_to_show += char
                    if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                        prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "":
                        prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                    elif has_emoji(messages[0]):
                        prev_message_temp += f"(emoji) - {messages[1]}\n"
                    elif has_file(messages[0]):
                        prev_message_temp += f"(file) - {messages[1]}\n"
                    temp_day = str(datetime.datetime.now()).split("-", 2)
                    temp_day = temp_day[2].split()
                    if temp_day[0].strip().startswith("0"):
                        temp_day[0] = temp_day[0].replace("0", "").strip()
                    # if temp_day[0].strip() not in messages[3][0:2]:
                    #     prev_message_temp += f"{messages[3]}\n"
                    try:
                        if messages[4] != None:
                            temp_name = messages[4].split(".")[0]
                            images.append(f"{temp_name}.png")
                    except:
                        pass
                else:
                    pass
            enter_home_directory()
            os.chdir("./cache")
            for i, image_name in enumerate(images):
                if not os.path.exists(image_name):
                    del(images[i])
            enter_home_directory()
            os.chdir("./cache")
            layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20")
    try:
        window.close()
    except:
        pass
    enter_home_directory()
    if message_text.strip() == "\\exit" and recipient_ip != "":
        skip = True
        mailbox = False
    else:
        skip = False
    if "\\ip" in message_text.strip().lower():
        if graphic_mode and get_foreign_user() != None:
            gui.Popup(gui_translate(f"{get_foreign_user().strip().capitalize()}'s IP address is {recipient_ip}"),
                      title=gui_translate("IP Address"), font="Courier 20", auto_close=True, auto_close_duration=5)
        elif graphic_mode:
            gui.Popup(gui_translate(f"Peer's IP address is {recipient_ip}"), title=gui_translate(
                "IP Address"), font="Courier 20", auto_close=True, auto_close_duration=5)
        elif get_foreign_user() != None:
            animated_print(
                f"{get_foreign_user().strip().capitalize()}'s IP address is {recipient_ip}")
        else:
            animated_print(f"Peer's IP address is {recipient_ip}")
    if "\\request_user" in message_text.strip().lower() and recipient_ip != "" and (get_foreign_user() == None or get_foreign_user().strip() == ""):
        message_text = message_text.replace("\\request_user", "").replace("\\request_username", "")
        get_username = True
        sc, username, temp_mac, temp_save_override_port = id_packet(sc, code=[code2, prefix], mode="send")
        auto_generate_contact = Contacts(user, get_current_user(), print_logs, default_color, error_color, private_mode)
        auto_generate_contact.add(username, temp_mac, None, "Auto-generated contact on username request", temp_save_override_port)
        accepted = id_packet(sc, mode="recieve", ip=get_ip_from_socket(sc))
        if username == None:
            get_foreign_user(new_user="\\reset")
            temp_display_name = None
        else:
            pass
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
                if pass_os() != "win32":
                    voice_module = pyaudio.PyAudio()
                    chunk, FORMAT, channels, sample_rate, record_seconds = 1024, pyaudio.paInt16, 1, 44100, voice_record_time
                    stream = voice_module.open(format=FORMAT, channels=channels,
                                               rate=sample_rate, input=True, output=True, frames_per_buffer=chunk)
                else:
                    if graphic_mode:
                        gui.Popup(gui_translate("Microphone functionality currently unavailable on Windows!"),
                                  title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"WARNING: Microphone functionality currently unavailable on Windows!", error=True, reset=True)
                        colors(default_color)
            except OSError:
                animated_print(f"WARNING: Unable to detect microphone!", error=True, reset=True)
                Colors(default_color)
                log("Unable to detect microphone!", "voiceManager", get_current_user(), print_logs)
            else:
                if pass_os != "win32":
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
        if early_file != None:
            message_text += "\\file"
        decrypted_message = []
        decrypted_current_user = []
        passs2 = 0
        passs = 0
        output_phrase = ''
        if private_mode:
            current_user = "Anonymous"
        else:
            current_user = get_current_user()
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
            current_user = get_current_user()
        if not graphic_mode:
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
                animated_print(f"{temp_output_phrase}", pm=True)
            if print_logs and not graphic_mode:
                animated_print(
                    f"{temp_output_phrase}{' ' * int(len(temp_output_phrase) / 60)}", pm=True)
                animated_print(f"Scrambling...")
                animated_print(f"{scrambled_output_phrase}", pm=True)
            elif not graphic_mode:
                animated_print(f"{temp_scrambled_output_phrase}", pm=True)
        elif not graphic_mode:
            animated_print(f"{scrambled_output_phrase}", pm=True)
            sys.stdout.write("\033[K")
        output_file = open("./messageout.txt", "r+")
        for i in range(len(message_text)):
            if message_text[i].lower() == output_phrase[i].lower():
                if message_text[i].strip() != "" and output_phrase[i].strip() != "":
                    # ?It is really difficult to nail down what causes either @code_seg1 or 2 to equal zero, so I added this catcher instead
                    for _ in range(2):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                    output_file.close()
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_color, error_color, auto_code=True)
                    code, prefix, timestamp = showcode(
                        user, 1, private_mode, print_logs, error_color, default_color)
                    newmessage(code, user, recipient_ip, temp_sc, prefix, date, talking_to_self, error_color,
                               default_color, private_mode, print_logs, mailing, display_initiate, True, faulty=True, stored_message=message_text, prev=prev_messages, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
            else:
                pass
        else:
            output_file.write(scrambled_output_phrase)
            output_file.close()
            log(f"New encrypted message successfully generated!",
                "encryptionManager", current_user, print_logs)
            decrypt_code = showcode(
                user, 2, private_mode, print_logs, error_color, default_color)
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
                    if graphic_mode:
                        host = "y"
                    else:
                        host = privacy_input(
                            "Send message? (Y/N)", 0)
                except KeyboardInterrupt:
                    maybe_quit()
                    Colors(default_color)
                if host == None:
                    host = ""
        else:
            host = "y"
    except NameError:
        host = privacy_input(
            "Send message? (Y/N)", 0)
        recipient_ip = ""
    if host == None:
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif "y" in host:
        if sc == None:
            try:
                temp = RFCOMM
                bluetooth_available = True
                if graphic_mode:
                    use_bluetooth = gui.popup_yes_no(gui_translate("Use Bluetooth for communication?"), title=gui_translate(f"FiEncrypt - Activate Bluetooth (Logged in as {get_current_user()}"), font="Courier 20")
                    if use_bluetooth == "Yes":
                        use_bluetooth = True
                    else:
                        use_bluetooth = False
                else:
                    use_bluetooth = to_boolean(privacy_input("Use Bluetooth for communication? [True|False]", private_mode))
                if use_bluetooth:
                    link = BluetoothSocket(RFCOMM)
                    ip = ""
                    override_port = 23
                else:
                    raise TypeError
            except:
                bluetooth_available, use_bluetooth = False, False
                link = socket.socket()
        connected, talking_to_self, ip = False, False, None
        while not connected:
            try:
                if conversation_mode and recipient_ip != "":
                    ip = recipient_ip
                elif recipient_ip == "":
                    ip, target_mac, target_name, sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                       default_color, private_mode, error_color, sc, message=scrambled_output_phrase, use_bluetooth=use_bluetooth)
                    reset_ip = Contacts(user, get_current_user(), print_logs, default_color, error_color, private_mode)
                    try:
                        reset_ip.add_ip(target_name, "-")
                    except:
                        pass
                    if type(ip) != list:
                        try:
                            recipient_ip = ip.strip().replace("\n", "")
                        except:
                            recipient_ip = None
                if ip == None:
                    ip = recipient_ip
                else:
                    ip = ip.replace("\n", "").strip()
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
                            code, user, 2, backup_prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_color, print_logs, private_mode, error_color, None, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
                    elif manual != None and manual:
                        retrievemessage(
                            code2, user, 2, None, recipient_ip, temp_sc, None, mailing, talking_to_self, default_color, print_logs, private_mode, error_color, None, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
                    else:
                        retrievemessage(
                            code, user, 2, backup_prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_color, print_logs, private_mode, error_color, None, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
                else:
                    if sc == None:
                        if type(ip) == list:
                            for connection_num in range(len(ip)):
                                locals()[f"link{connection_num}"] = socket.socket()
                                locals()[f"link{connection_num}"].connect(
                                    (ip[connection_num].strip(), int(override_port)))
                                locals()[f"sc{connection_num}"] = locals()[f"link{connection_num}"]
                        else:
                            link.connect((recipient_ip, int(override_port)))
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
                            ).strip(), print_logs, default_color, error_color, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except UnboundLocalError:
                        animated_print(
                            f"WARNING: Unable to reach the host! Try a different address!", error=True, reset=True)
                        Colors(default_color)
                        ip, target_mac, target_name, empty_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                                 default_color, private_mode, error_color, None, message=scrambled_output_phrase)
                        if ip == None or ip.strip() == "":
                            menu(user, None, print_logs, default_color,
                                 private_mode, error_color, print_speed=0)
                        elif "." not in ip:
                            if ":" in ip:
                                if ip == None:
                                    menu(user, None, print_logs, default_color,
                                         private_mode, error_color, print_speed=0)
                                temp = ip
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_color, error_color, private_mode)
                                target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                    temp)
                                target_name = target_name.replace("\n", "")
                                if target_ip != None:
                                    ip = target_ip
                                else:
                                    ip = mac_resolve(target_mac, print_logs)
                                if ip == None:
                                    animated_print(
                                        f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                    Colors(default_color)
                                    connected = False
                                else:
                                    contact_search.add_ip(target_name, ip)
                            else:
                                try:
                                    contact_search = Contacts(user, get_current_user().lower().strip(
                                    ), print_logs, default_color, error_color, private_mode)
                                    target_name, mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                        ip)
                                    target_name = target_name.replace("\n", "")
                                    if mac.strip() == "":
                                        animated_print(
                                            f"WARNING: MAC address for contact is blank!", error=True, reset=True)
                                        Colors(default_color)
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
                                                f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                            Colors(default_color)
                                            connected = False
                                        else:
                                            contact_search.add_ip(target_name, ip)
                                except ValueError:
                                    animated_print(
                                        f"WARNING: Invalid contact name entered!", error=True, reset=True)
                                    Colors(default_color)
                                    connected = False
                                except TypeError:
                                    animated_print(
                                        f"WARNING: Invalid contact details!", error=True, reset=True)
                                    Colors(default_color)
                                    connected = False
                                except AttributeError:
                                    animated_print(
                                        f"WARNING: Invalid contact details!", error=True, reset=True)
                                    Colors(default_color)
                                    connected = False
                        recipient_ip = ip.strip().replace("\n", "")
            # ?Linux had some issues with their timeout being some huge value, so @KeyboardInterrupt also does the same
            except KeyboardInterrupt:
                connected = False
                animated_print(
                    f"WARNING: Keyboard Interrupt! Attempting to deliver message!", error=True, reset=True)
                Colors(default_color)
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
                            ).strip(), print_logs, default_color, error_color, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                    except:
                        animated_print(f"Aborting...")
                        menu(user, None, print_logs, default_color,
                             private_mode, error_color, print_speed=0)
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
                            ).strip(), print_logs, default_color, error_color, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                    except:
                        pass
                    animated_print(f"Aborting...")
                    menu(user, None, print_logs, default_color,
                         private_mode, error_color, print_speed=0)
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_color, error_color, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except:
                        animated_print(
                            f"WARNING: Unable to reach the host! Try a different address!", error=True, reset=True)
                    Colors(default_color)
                    try:
                        if ip:
                            pass
                    except UnboundLocalError:
                        ip = None
                    if ip == None or ip.strip() == "":
                        ip, target_mac, target_name, empty_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                                 default_color, private_mode, error_color, None, message=scrambled_output_phrase)
                    else:
                        contact_ip = Contacts(user, get_current_user().lower().strip(
                        ), print_logs, default_color, error_color, private_mode)
                        contact_ip.add_ip(target_name, ip)
                    if "." not in ip:
                        if ":" in ip:
                            if ip == None:
                                menu(user, None, print_logs, default_color,
                                     private_mode, error_color, print_speed=0)
                            temp = ip
                            contact_search = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_color, error_color, private_mode)
                            target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                temp)
                            target_name = target_name.replace("\n", "")
                            if target_ip != None:
                                ip = target_ip
                            else:
                                ip = mac_resolve(target_mac, print_logs)
                            if ip == None:
                                animated_print(
                                    f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            else:
                                contact_search.add_ip(target_name, ip)
                        else:
                            try:
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_color, error_color, private_mode)
                                target_name, mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                    ip)
                                target_name = target_name.replace("\n", "")
                                if mac.strip() == "":
                                    animated_print(
                                        f"WARNING: MAC address for contact is blank!", error=True, reset=True)
                                    Colors(default_color)
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
                                            f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                        Colors(default_color)
                                        connected = False
                                    else:
                                        contact_search.add_ip(target_name, ip)
                            except ValueError:
                                animated_print(
                                    f"WARNING: Invalid contact name entered!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            except TypeError:
                                animated_print(
                                    f"WARNING: Invalid contact details!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            except AttributeError:
                                animated_print(
                                    f"WARNING: Invalid contact details!", error=True, reset=True)
                                Colors(default_color)
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
                    menu(user, None, print_logs, default_color,
                         private_mode, error_color, print_speed=0)
                except:
                    try:
                        if target_name != None and target_name.strip() != "":
                            contact_remove_ip = Contacts(user, get_current_user().lower(
                            ).strip(), print_logs, default_color, error_color, private_mode)
                            contact_remove_ip.add_ip(target_name, "-")
                        ip = mac_resolve(target_mac, print_logs)
                    except:
                        animated_print(
                            f"WARNING: Unable to reach the host! Try a different address!", error=True, reset=True)
                    Colors(default_color)
                    if ip == None or ip.strip() == "":
                        ip, target_mac, target_name, empty_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                                 default_color, private_mode, error_color, None, message=scrambled_output_phrase)
                    else:
                        try:
                            contact_ip = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_color, error_color, private_mode)
                            contact_ip.add_ip(target_name, ip)
                        except UnboundLocalError:
                            pass
                    if "." not in ip:
                        if ":" in ip:
                            temp = ip
                            contact_search = Contacts(user, get_current_user().lower().strip(
                            ), print_logs, default_color, error_color, private_mode)
                            target_name, target_mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                temp)
                            target_name = target_name.replace("\n", "")
                            if target_ip != None:
                                ip = target_ip
                            else:
                                ip = mac_resolve(target_mac, print_logs)
                            if ip == None:
                                animated_print(
                                    f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            else:
                                contact_search.add_ip(target_name, ip)
                        else:
                            try:
                                contact_search = Contacts(user, get_current_user().lower().strip(
                                ), print_logs, default_color, error_color, private_mode)
                                target_name, mac, target_ip, agreed_code, details, override_port = contact_search.check_for(
                                    ip)
                                target_name = target_name.replace("\n", "")
                                if mac.strip() == "":
                                    animated_print(
                                        f"WARNING: MAC address for contact is blank!", error=True, reset=True)
                                    Colors(default_color)
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
                                            f"WARNING: Unable to resolve IP address through ARP!", error=True, reset=True)
                                        Colors(default_color)
                                        connected = False
                                    else:
                                        contact_search.add_ip(target_name, ip)
                            except ValueError:
                                animated_print(
                                    f"WARNING: Invalid contact name entered!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            except TypeError:
                                animated_print(
                                    f"WARNING: Invalid contact details!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                            except AttributeError:
                                animated_print(
                                    f"WARNING: Invalid contact details!", error=True, reset=True)
                                Colors(default_color)
                                connected = False
                    recipient_ip = ip.strip().replace("\n", "")
        if not skip:
            enter_home_directory()
            content = open(f"./messageout.txt", "rb")
            decrypt_code = user, 2
            if code3 == "" and decrypt_code == "":
                decrypt_code, out_file = randomcode(
                    user, user, True, private_mode, print_logs, default_color, error_color)
            elif code3 != "":
                try:
                    decrypt_code = f"{timestamp}_{backup_code}_{backup_prefix}"
                except UnboundLocalError:
                    decrypt_code = int(code2)
            message = content.read()
            if (agreed_code == None or agreed_code.strip().lower() == "none") and priority_code != None:
                agreed_code = priority_code
            if agreed_code != None and agreed_code.strip().lower() != "none":
                agreed_code = agreed_code.split("|")
                agreed_code[1] = agreed_code[1].split("_")
                timestamp, code2, prefix = agreed_code[0][0], agreed_code[1][1], agreed_code[1][2]
                prefix = prefix.split("fE")
                filler_length = agreed_code[-1]
                filler_length = filler_length.replace("#", "")
                prefix[1] = prefix[1].split("||")
                prefix[0] = prefix[0].replace("$", "")
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
                    Colors(default_color, force=True)
                except:
                    code_seg1 = str(code_seg1)[::-1]
                    temp = code_seg2
                    code_seg2 = int(code_seg1)
                    code_seg1 = temp
                    Colors(default_color)
                decrypted_message = []
                decrypted_current_user = []
                passs2 = 0
                passs = 0
                output_phrase = ''
                if private_mode:
                    current_user = "Anonymous"
                else:
                    current_user = get_current_user()
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
                if len(str(code3)) != 2:
                    message = random_filler(filler_length, output_phrase)
                else:
                    message = output_phrase
                packet = f"{message} |||| agreed, {hash_value(get_mac().strip())} | {encrypted_current_user}"
            else:
                packet = f"{message} |||| {str(decrypt_code)} | {encrypted_current_user}"
            content.close()
        elif mailbox:
            if sys.platform.startswith("linux"):
                your_ip = gnu_ip_resolve(print_logs, private_mode)
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
                    user, user, True, private_mode, print_logs, default_color, error_color)
            elif code3 != "":
                try:
                    decrypt_code = f"{timestamp}_{backup_code}_{backup_prefix}"
                except UnboundLocalError:
                    decrypt_code = int(code2)
            message = content.read()
            if agreed_code != None and agreed_code.strip().lower() != "none":
                packet = f"Request:False | Source_IP:{your_ip} | Name:{encrypted_current_user} |||| {message} |||| agreed, {hash_value(get_mac().strip())}"
            else:
                packet = f"Request:False | Source_IP:{your_ip} | Name:{encrypted_current_user} |||| {message} |||| {str(decrypt_code)}"
            content.close()
        if sc == None:
            try:
                if type(ip) == list:
                    for connection_num in range(len(ip)):
                        locals()[f"link{connection_num}"].send(packet.encode())
                else:
                    link.send(packet.encode())
            except:
                error_link.send(packet.encode())
        else:
            try:
                if type(sc) == list:
                    for connection_num in range(len(sc)):
                        locals()[f"sc{connection_num}"].send(packet.encode())
                else:
                    try:
                        sc.send(packet.encode())
                    except UnboundLocalError:
                        try:
                            sc.send("\\exit".encode())
                        except:
                            pass
                    except BrokenPipeError:
                        try:
                            sc.send("\\exit".encode())
                        except:
                            pass
                        raise
            except:
                if graphic_mode:
                    gui.Popup(gui_translate("Connection lost! Returning to menu..."),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(f"WARNING: Connection lost! Returning to menu",
                                   error=True, reset=True)
                    Colors(default_color)
                sc.close()
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        try:
            error_link.shutdown(socket.SHUT_RDWR)
            error_link.close()
        except:
            pass
        if outbound_file:
            attach_image, filename = sftp_send(
                ip, default_color, error_color, voice_message, code, prefix, sc, file_path=early_file, use_bluetooth=use_bluetooth)
            try:
                if attach_image:
                    prev_messages[-1].append(filename)
                else:
                    prev_messages[-1].append(None)
            except:
                pass
        recipient_ip = recipient_ip.replace("\n", "")
        if not skip and print_logs:
            if not graphic_mode:
                animated_print(
                    f"Message {message.decode()} with decryption code {decrypt_code} successfully sent to {ip}!")
        elif mailbox and print_logs:
            if not graphic_mode:
                animated_print(
                    f"Message {message.decode()} with decryption code {decrypt_code} sent to {ip}'s mailbox!")
        elif conversation_mode and recipient_ip.strip() != "" and message_text.strip().endswith("\\exit"):
            if not graphic_mode:
                animated_print(
                    f"Message sent! Exiting conversation with {get_foreign_user().capitalize()}")
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        elif not skip:
            if not graphic_mode:
                animated_print(f"Message sent!")
        elif mailbox and conversation_mode:
            if not graphic_mode:
                if get_foreign_user() != None:
                    animated_print(
                        f"{get_foreign_user().capitalize()} is not available! Message left in their mailbox!")
                    get_foreign_user(new_user="\\reset")
                else:
                    animated_print(f"Message left in {recipient_ip.strip()}'s mailbox")
            else:
                if get_foreign_user() != None:
                    gui.Popup(gui_translate(f"{get_foreign_user().capitalize()} is not available! Message left in their mailbox!"),
                              title=gui_translate(f"FiEncrypt - Sent To Mailbox (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    get_foreign_user(new_user="\\reset")
                else:
                    gui.Popup(gui_translate(f"{recipient_ip.strip()} unavailable! Message left in their mailbox!"),
                              title=gui_translate(f"FiEncrypt - Sent To Mailbox (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        elif mailbox:
            if not graphic_mode:
                animated_print(f"Message left!")
            else:
                gui.Popup(gui_translate(f"{recipient_ip} unavailable! Message left in their mailbox!"),
                          title=gui_translate(f"FiEncrypt - Sent To Mailbox (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        elif poke:
            if not graphic_mode:
                animated_print(f"Poke sent!")
        else:
            if graphic_mode:
                gui.Popup(gui_translate(f"Leaving conversation with {foreign_user.capitalize()}!"),
                          title=gui_translate(f"FiEncrypt - Leaving Conversation (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                animated_print(
                    f"Leaving conversation with {foreign_user.capitalize()}!")
    elif host != "":
        # *Informs the user of the decryption code, as it is EXTREMELY rare for the same code to be generated by two different computers
        animated_print(
            f"Send this code to the recipient of the message! {backup_code}")
    if graphic_mode:
        try:
            window.close()
        except:
            pass
    if conversation_mode and "y" in host and not skip:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_color, error_color, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_color, default_color)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        if graphic_mode:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, silent=True, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
    elif poke and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_color, error_color, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_color, default_color)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        if graphic_mode:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, silent=True, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
    elif love_sent and conversation_mode and "y" in host:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_color, error_color, auto_code=True)
        code, prefix, timestamp = showcode(
            user, 1, private_mode, print_logs, error_color, default_color)
        # ?In conversation mode, an inbound server will automatically be started, so the user can recieve the message promptly
        if graphic_mode:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            server_recieve(user, code, user, sc, recipient_ip, timestamp, backup_prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, silent=True, prev=prev_messages, window=window, temp_user=temp_display_name, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
    else:
        if auto_code:
            randomcode(user, current_user, True, private_mode,
                       print_logs, default_color, error_color, auto_code=True)
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)


def hash_value(value, **kwargs):
    """Applies various encryption methods on string passed"""
    hash_type = kwargs.get("hash", "sha256")
    hash_value = value.encode("utf-8")
    if hash_type == "sha256":
        hash_value = hashlib.sha256(hash_value).hexdigest()
    elif hash_type == "md5":
        hash_value = hashlib.md5(hash_value).hexdigest()
    return hash_value


def decode_foreign_user(code, prefix, user, default_color):
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
        Colors(default_color, force=True)
    except:
        temp = code_seg2
        code_seg2 = int(str(code_seg1)[::-1])
        code_seg1 = temp
        Colors(default_color)
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
    message, port = kwargs.get("message", None), kwargs.get("port", override_port)
    if temp_sc == None:
        reply_link = socket.socket()
        try:
            reply_link.connect((ip.strip(), int(port)))
        except:
            try:
                reply_link.connect((ip.strip(), 19507))
            except:
                return False, None
        sc = reply_link
    else:
        sc = temp_sc
    encrypted_expected_user = hash_value(expected_user)[::-1]
    if graphic_mode:
        temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - User Validation (Logged in as: {get_current_user()})"), layout=[
                                [gui.Text(gui_translate("Validating User..."))]], margins=(100, 50), font="Courier 20", finalize=True)
    else:
        animated_print("Validating User...")
    try:
        sc.send(
            f"\\user_confirm={encrypted_expected_user} |||| {get_own_ip(False, False)}".encode())
    except:
        try:
            if temp_sc == None:
                reply_link.connect((ip.strip(), 19507))
                reply_link.send(
                    f"\\user_confirm={encrypted_expected_user} |||| {get_own_ip(False, False)}".encode())
            else:
                reply_link = socket.socket()
                reply_link.connect((ip.strip(), 19507))
                reply_link.send(
                    f"\\user_confirm={encrypted_expected_user} |||| {get_own_ip(False, False)}".encode())
        except ConnectionRefusedError:
            return False, sc
        sc = reply_link
    info = sc.recv(1024)
    info = info.decode()
    if "true" in info.lower():
        get_foreign_user(new_user=expected_user)
        if graphic_mode:
            temp_popup.close()
            temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - User Validation (Logged in as: {get_current_user()})"), layout=[
                                    [gui.Text(gui_translate("Validating User... Success!"))]], margins=(100, 50), font="Courier 20", finalize=True)
            time.sleep(2)
            temp_popup.close()
        else:
            for _ in range(2):
                sys.stdout.write("\033[F")
                #sys.stdout.write("\033[K")
            animated_print("Validating User... Success!")
        return True, sc
    else:
        reply_link = socket.socket()
        try:
            reply_link.connect((ip.strip(), 19507))
        except ConnectionRefusedError:
            if graphic_mode:
                temp_popup.close()
                temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - User Validation (Logged in as: {get_current_user()})"), layout=[
                                        [gui.Text(gui_translate("Validating User... Failed!"))]], margins=(100, 50), font="Courier 20", finalize=True)
                time.sleep(2)
                temp_popup.close()
            else:
                for _ in range(2):
                    sys.stdout.write("\033[F")
                    #sys.stdout.write("\033[K")
                animated_print("Validating User... Failed!")
            return None, sc
        try:
            reply_link.send(
                f"\\user_confirm={expected_user} |||| {get_own_ip(False, False)}".encode())
            info = reply_link.recv(1024)
            info = info.decode()
        except ConnectionResetError:
            if graphic_mode:
                if foreign_user != None:
                    gui.Popup(gui_translate(f"{foreign_user.capitalize()} has reset the conenction!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    gui.Popup(gui_translate("Peer has reset the connection!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                if foreign_user != None:
                    animated_print(
                        f"WARNING: {foreign_user.capitalize()} has reset the conenction!", error=True, reset=True)
                else:
                    animated_print(
                        f"WARNING: Peer has reset the conenction!", error=True, reset=True)
                Colors(default_color)
        except ConnectionRefusedError:
            if graphic_mode:
                if foreign_user != None:
                    gui.Popup(gui_translate(f"{foreign_user.capitalize()} has refused the conenction!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    gui.Popup(gui_translate("Peer has refused the connection!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                if foreign_user != None:
                    animated_print(
                        f"WARNING: {foreign_user.capitalize()} has refused the conenction!", error=True, reset=True)
                else:
                    animated_print(
                        f"WARNING: Peer has refused the conenction!", error=True, reset=True)
                Colors(default_color)
        except ConnectionAbortedError:
            if graphic_mode:
                if foreign_user != None:
                    gui.Popup(gui_translate(f"{foreign_user.capitalize()} has aborted the conenction!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    gui.Popup(gui_translate("Peer has aborted the connection!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                if foreign_user != None:
                    animated_print(
                        f"WARNING: {foreign_user.capitalize()} has aborted the conenction!", error=True, reset=True)
                else:
                    animated_print(
                        f"WARNING: Peer has aborted the conenction!", error=True, reset=True)
                Colors(default_color)
        except exception as e:
            handle_bluetooth_error(e, resolution="revert")
        if "true" in info.lower():
            log("Foreign user succesfully validated!", "networkManager", get_current_user(), None)
            if message != None:
                reply_link.send(message.encode())
            else:
                reply_link.send("\\exit".encode())
            reply_link.close()
            get_foreign_user(new_user=expected_user)
            if graphic_mode:
                temp_popup.close()
                temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - User Validation (Logged in as: {get_current_user()})"), layout=[
                                        [gui.Text(gui_translate("Validating User... Success!"))]], margins=(100, 50), font="Courier 20", finalize=True)
                time.sleep(2)
                temp_popup.close()
            return True, sc
        else:
            log("Foreign user failed validation!", "networkManager", get_current_user(), None)
            reply_link.send("\\exit".encode())
            if graphic_mode:
                temp_popup.close()
                temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - User Validation (Logged in as: {get_current_user()})"), layout=[
                                        [gui.Text(gui_translate("Validating User... Failed!"))]], margins=(100, 50), font="Courier 20", finalize=True)
                time.sleep(2)
                temp_popup.close()
            return False, sc


def get_auto_code():
    """Specifically retrieves the state of the auto_code parameter in the config file"""
    print_logs, display_initiate, graphic_mode, private_mode, color_enabled, default_color, auto_code, voice_record_time, gui_theme, translation, lang, override_port = retrieve_config_settings()
    return auto_code


def get_mac():
    """Returns your MAC address"""
    try:
        import re, uuid
        return ":".join(re.findall("..", "%012x" % uuid.getnode()))
    except:
        return None


def private_file_integrity(filename):
    """Checks file to be sent, and prevents it should it violate the integrity of the FiEncrypt filestructure"""
    private_cache_queried = False
    enter_home_directory()
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        for i, line in enumerate(credential_lines):
            if line == None:
                return False, 0
            elif (line.strip().lower() in filename.strip().lower() and line.strip() != "") or "$mycache" in filename.strip().lower():
                private_cache_queried = True
    if ("FiEncrypt/" in filename or "FiEncrypt.py" in filename) and not private_cache_queried:
        temp_path = filename.split("/")
        try:
            if "cache" in temp_path[-2] or "cache" in temp_path[-1]:
                return True, 1
            else:
                return False, 1
        except IndexError:
            return False, 1
    elif private_cache_queried:
        hash_user = hash_value(get_current_user().lower().strip())
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
    """Transforms passed string into the appropiate boolean"""
    if "true" in str(state).lower().strip():
        return True
    else:
        return False


def has_emoji(message):
    """Returns True if a message contains an emoji"""
    emojis = ["\\heart", "\\<3", "\\poke", "\\thumbs_up", "\\thumbs_down"]
    for emoji in emojis:
        if emoji in message.lower().strip():
            return True
    return False


def has_file(message):
    """Returns True if message has file attached"""
    if "\\file" in message.strip().lower():
        return True
    else:
        return False


def get_ip_from_socket(sc):
    """Takes the socket object and extracts peer's IP address from it"""
    try:
        temp = str(sc).split("raddr=('")
        target_ip = substring(temp[1], "'", 0)
    except:
        target_ip = ""
    return target_ip


def socket_type(sc):
    if "bluetooth" in str(sc).lower():
        return "Bluetooth"
    else:
        return "IP"


def sftp_send(recipient_ip, default_color, error_color, voice_message, code, prefix, temp_sc, **kwargs):
    """Sends file using unique socket"""
    use_bluetooth, file_path = kwargs.get("use_bluetooth", False), kwargs.get("file_path", None)
    try:
        if use_bluetooth:
            file_link = BluetoothSocket(RFCOMM)
            file_link.bind(("", 24))
        else:
            file_link = socket.socket()
            file_link.bind((get_own_ip(False, False).strip(), 41731))
        #file_link.settimeout(20)
        file_link.listen(10)
        sc, address = file_link.accept()
        #sc.settimeout(20)
    except TimeoutError:
        ready = False
    except BluetoothError:
        ready = False
    except:
        if graphic_mode:
            gui.popup_no_wait(gui_translate("Connection failed! Aborting file transfer"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"WARNING: Connection failed! Aborting file transfer!",
                           error=True, reset=True)
        Colors(default_color)
        temp_sc.send("\\exit".encode())
        temp_sc.close()
        assisted_menu()
    alphabet, valid_file, is_directory, attach_image = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                                                                       'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'], False, False, False
    try:
        ready = to_boolean(sc.recv(1024).decode().strip())
    except TimeoutError:
        ready = False
    except btcommon.BluetoothError:
        ready = False
    except UnboundLocalError:
        ready = False
    if ready:
        #sc.settimeout(1000)
        #file_link.settimeout(1000)
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
            Colors(default_color, force=True)
        except:
            code_seg1 = str(code_seg1)[::-1]
            temp = code_seg2
            code_seg2 = int(code_seg1)
            code_seg1 = temp
            Colors(default_color)
        if get_foreign_user() == None or get_foreign_user().strip() == "":
            temp_foreign_user = recipient_ip
        else:
            temp_foreign_user = get_foreign_user()
        while not valid_file:
            if voice_message:
                filename = "cache/voice_message.wav"
            else:
                try:
                    if file_path == None:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate(f"Select file to send to {temp_foreign_user}"))], [
                                gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - File Transfer (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20", finalize=True)
                            filename = filedialog.askopenfilename(
                                title="FiEncrypt - Open File", filetypes=[("all files", "*")], initialdir="../")
                            window.close()
                        else:
                            filename = privacy_input(
                                f"Enter path of file to send to {temp_foreign_user}", 0)
                    else:
                        filename = file_path.strip()
                    if pass_os() == "win32":
                        filename = filename.replace("\\", "/")
                except KeyboardInterrupt:
                    log(f"File transfer interrupted!", "networkManager", get_current_user(
                    ), None)
                    if graphic_mode:
                        gui.Popup(gui_translate("File transfer aborted!"), title=gui_translate("Warning"),
                                  font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"WARNING: File transfer aborted!", error=True, reset=True)
                        Colors(default_color)
                    file_link.close()
                    sc.close()
            integrity, return_value = private_file_integrity(filename)
            if not integrity:
                final_file, valid_file = True, False
                if return_value == 1:
                    if graphic_mode:
                        gui.Popup(gui_translate("You cannot access core FiEncrypt files outside of the public or private cache!"),
                                  title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"WARNING: You cannot access core FiEncrypt files outside of the public or private cache!", error=True, reset=True)
                        Colors(default_color)
                    log("Sftp access to core FiEncrypt files rejected!",
                        "encryptionManager", get_current_user(), None)
                elif return_value == 2:
                    if graphic_mode:
                        gui.Popup(gui_translate("You cannot access the private cache of any other user!"),
                                  title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"WARNING: You cannot access the private cache of any other user!", error=True, reset=True)
                        Colors(default_color)
                    log("Sftp access to private cache rejected!",
                        "encryptionManager", get_current_user(), None)
            else:
                if return_value == 2 and not filename.strip().endswith("/"):
                    filename = f"{filename.strip()}/"
                try:
                    if not filename.startswith(".") and not filename.startswith("/") and filename[0].lower() not in alphabet:
                        filename = f"./{filename}"
                    if "$mycache/" in filename.strip().lower():
                        filename, valid, current_valid = filename.split(
                            "$mycache/", 1), False, False
                        enter_home_directory()
                        while not valid or not current_valid:
                            if graphic_mode:
                                layout = [[gui.Text(gui_translate("Please confirm your login"))], [gui.Text(gui_translate("Username")), gui.InputText(
                                    key="username")], [gui.Text(gui_translate("Password")), gui.InputText(key="password", password_char="*")], [gui.Button(gui_translate("Login"), key="Login", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                                window = gui.Window(title=gui_translate(f"FiEncrypt - Login"), layout=layout,
                                                    margins=(100, 50), font="Courier 20")
                                event, values = window.read()
                                if event == "Login":
                                    username = values.get("username", None)
                                    password = values.get("password", None)
                                elif event == "Cancel":
                                    window.close()
                                    maybe_quit()
                                window.close()
                            else:
                                animated_print(f"Please confirm your login: ")
                                username = privacy_input("Username", 0)
                                password = privacy_input("Password", 1)
                            valid = validate_login(username, password)
                            current_valid = username.lower().strip() == get_current_user().lower().strip()
                            if valid and current_valid:
                                filename = f"./{hash_value(username.lower().strip())}/files/{filename[1]}"
                            else:
                                if graphic_mode:
                                    gui.Popup(gui_translate("Invalid login!"), title=gui_translate("Warning"),
                                              font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                                else:
                                    animated_print(f"WARNING: Inavlid login!",
                                                   error=True, reset=True)
                                    colors(default_color)
                    if filename.strip().endswith("/") or filename.strip().endswith("\\"):
                        final_file = False
                        while not final_file:
                            options, option_type, graphic_options = [], [], ""
                            for files in os.listdir(f"{filename.strip()}"):
                                options.append(files)
                            if len(options) == 0:
                                final_file, valid_file = True, False
                                break
                            for i, option in enumerate(options):
                                if not option.strip().startswith("."):
                                    if graphic_mode:
                                        graphic_options += f"{i+1}. {option} ({parse_size(os.path.getsize(filename+option), option)})\n"
                                    else:
                                        animated_print(
                                            f"{i+1}. {option} ({parse_size(os.path.getsize(filename+option), option)})", speed=0)
                                    option_type.append(parse_size(os.path.getsize(
                                        filename+option), option))
                                else:
                                    del options[i]
                                    if graphic_mode:
                                        graphic_options += f"{i+1}. {options[i]} ({parse_size(os.path.getsize(filename+options[i]), options[i])})\n"
                                    else:
                                        animated_print(
                                            f"{i+1}. {options[i]} ({parse_size(os.path.getsize(filename+options[i]), options[i])})", speed=0)
                                    option_type.append(parse_size(os.path.getsize(
                                        filename+options[i]), options[i]))
                            if graphic_mode:
                                layout = [[gui.Column([[gui.Text(gui_translate(graphic_options))]], scrollable=True, size=(800, 600))], [gui.Text(gui_translate("Select one of these")), gui.InputText(key="file_choice"), gui.Button(
                                    gui_translate("Send"), bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                                window = gui.Window(title=gui_translate(f"FiEncrypt - File Transfer (Logged in as: {get_current_user()})"),
                                                    layout=layout, margins=(100, 50), font="Courier 20")
                                event, values = window.read()
                                if event == "Send":
                                    file_choice = values.get("file_choice", None)
                                window.close()
                            else:
                                file_choice = privacy_input(f"Select one of these", 0)
                            if "directory" in option_type[int(file_choice)-1].lower().strip():
                                filename = f"{filename}{options[int(file_choice)-1]}/"
                                # filename = stringify_filepath(filename)
                                final_file = False
                            else:
                                filename = f"{filename}{options[int(file_choice)-1]}"
                                final_file = True
                    try:
                        file_extension = filename.split(".")
                        temp_name = file_extension[0]
                        file_extension = file_extension[1]
                        if file_extension.lower() in ["png", "jpg", "jpeg", "bmp", "ico"]:
                            if "png" not in file_extension.lower():
                                cached_image = Image.open(filename)
                                enter_home_directory()
                                cached_image.save(f"./cache/{os.path.basename(temp_name)}.png")
                                filename = f"{os.getcwd()}/cache/{os.path.basename(temp_name)}.png"
                    except IndexError:
                        if graphic_mode:
                            gui.Popup(gui_translate("Sending of typeless files is not supported"), font="Courier 20", text_color="red", title="Warning", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print("WARNING: Sending of typeless files is not supported", error=True, reset=True)
                        valid_file, old_file_path = False, None
                    else:
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
                        options, graphic_options = [], ""
                        for i, files in enumerate(os.listdir(f"./")):
                            if desired_file.lower().strip() in files.lower().strip():
                                options.append(files)
                                if graphic_mode:
                                    graphic_options += f"{i+1}. {files}\n"
                        if len(options) > 1:
                            if not graphic_mode:
                                for i, option in enumerate(options):
                                    animated_print(f"{i+1}. {option}", speed=0)
                                file_choice = privacy_input(f"Select one of these files", 0)
                            else:
                                layout = [[gui.Column([[gui.Text(gui_translate(graphic_options))]], scrollable=True, size=(800, 600))], [gui.Text(gui_translate("Select one of these files")), gui.InputText(key="filename"), gui.Button(
                                    gui_translate("Send"), bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                                window = gui.Window(title=gui_translate(f"FiEncrypt - File Transfer (Logged in as: {get_current_user()})"),
                                                    layout=layout, margins=(100, 50), font="Courier 20")
                                event, values = window.read()
                                if event == "Send":
                                    file_choice = values.get("filename", None)
                                window.close()
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
                        if graphic_mode:
                            gui.Popup(gui_translate("File not found!"), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: File not found!", error=True, reset=True)
                            Colors(default_color)
                        valid_file = False
                if valid_file:
                    if pass_os() == "win32":
                        copy = "copy"
                    else:
                        copy = "cp"
                    temp_path = os.getcwd()
                    enter_home_directory()
                    if pass_os() == "win32":
                        filename = filename.replace("/", "\\")
                        with ignore_stderr():
                            os.system(f"{copy} {filename} .\\cache\\{os.path.basename(filename)}")
                        filename = filename.replace("\\", "/")
                    else:
                        with ignore_stderr():
                            os.system(f"{copy} {filename} ./cache/{os.path.basename(filename)}")
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
                            if graphic_mode:
                                temp_window = gui.Window(
                                    title=gui_translate(f"FiEncrypt - File Transfer (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate("Sending file..."))]], font="Courier 20", finalize=True)
                                progress = tqdm.tqdm(range(
                                    int(filesize)), f"Sending {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)
                                sys.stdout.write("\033[F")
                                sys.stdout.write("\033[K")
                                sys.stdout.flush()
                            else:
                                progress = tqdm.tqdm(
                                    range(int(filesize)), f"Sending {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)
                            connection_type = socket_type(sc)
                            if connection_type == "Bluetooth":
                                buffer_size = 4096
                            else:
                                buffer_size = 8192
                            with open(filename, "rb") as f:
                                try:
                                    for _ in progress:
                                        bytes_read = f.read(buffer_size)
                                        if not bytes_read:
                                            break
                                        sc.sendall(bytes_read)
                                        progress.update(len(bytes_read))
                                except BrokenPipeError:
                                    if graphic_mode:
                                        gui.Popup(gui_translate("Pipe Broken!"), title=gui_translate("Warning"),
                                                  font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                                    else:
                                        animated_print(f"WARNING: Pipe Broken!",
                                                       error=True, reset=True)
                                        Colors(default_color)
                                    file_link.close()
                                    sc.close()
                                else:
                                    time.sleep(2)
                                    sc.send("\\exit".encode())
                            if graphic_mode:
                                temp_window.close()
                            else:
                                sys.stdout.write("\033[F")
                                sys.stdout.write("\033[K")
                            log(f"File of size {filesize}B sent successfully!",
                                "networkManager", get_current_user(), None)
                        else:
                            filename = None
                            file_link.close()
                    except KeyboardInterrupt:
                        if graphic_mode:
                            gui.Popup(gui_translate("File transfer interrrupted"), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red")
                        else:
                            animated_print(f"WARNING: File transfer interrupted!",
                                           error=True, reset=True)
                            Colors(default_color)
                        file_link.close()
                        sc.close()
                    except OverflowError:
                        if graphic_mode:
                            gui.Popup(gui_translate("File too large! Aborting..."), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: File too large! Aborting...",
                                           error=True, reset=True)
                            Colors(default_color)
                        file_link.close()
                        sc.close()
                    except ConnectionResetError:
                        if graphic_mode:
                            if foreign_user != None:
                                gui.Popup(gui_translate(f"{foreign_user.capitalize()} has reset the conenction!"),
                                          title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                            else:
                                gui.Popup(gui_translate("Peer has reset the connection!"),
                                          title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            if foreign_user != None:
                                animated_print(
                                    f"WARNING: {foreign_user.capitalize()} has reset the conenction!", error=True, reset=True)
                            else:
                                animated_print(
                                    f"WARNING: Peer has reset the conenction!", error=True, reset=True)
                            Colors(default_color)
                        file_link.close()
                        sc.close()
                    file_extension = os.path.basename(filename).split(".")
                    file_extension = file_extension[1]
                    if file_extension.lower() in ["png", "jpg", "jpeg", "bmp", "ico"]:
                        if graphic_mode:
                            attach_image = True
                        else:
                            attach_image = False
                    file_link.close()
                    sc.close()
                    return attach_image, os.path.basename(filename)
    else:
        return None, None


def sftp_recieve(recipient_ip, user, default_color, error_color, code, prefix, temp_sc, **kwargs):
    """Recieves file over socket"""
    autosync, max_size, voice_message, encrypted_header, decrypted_header, passs, attach_image, use_bluetooth = kwargs.get(
        "autosync", False), kwargs.get("max_size", "2GB"), kwargs.get("voice", False), [], "", 0, False, kwargs.get("use_bluetooth", False)
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
        Colors(default_color, force=True)
    except:
        temp = code_seg2
        code_seg2 = int(str(code_seg1)[::-1])
        code_seg1 = temp
        code3 = code
        Colors(default_color)
    try:
        if use_bluetooth:
            file_recipient = BluetoothSocket(RFCOMM)
            time.sleep(1)
            file_recipient.connect((recipient_ip, 24))
        else:
            file_recipient = socket.socket()
            time.sleep(1)
            file_recipient.connect((recipient_ip, 41731))
        file_recipient.send(str(True).encode())
        connection_type = socket_type(file_recipient)
    except ConnectionResetError:
        if graphic_mode:
            gui.Popup(gui_translate("Connection reset by peer!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print("WARNING: Connection reset by peer!", error=True, reset=True)
    except ConnectionRefusedError:
        if graphic_mode:
            gui.Popup(gui_translate("Connection refused by peer!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print("WARNING: Connection refused by peer!", error=True, reset=True)
    except ConnectionAbortedError:
        if graphic_mode:
            gui.Popup(gui_translate("Connection aborted!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print("WARNING: Connection aborted!", error=True, reset=True)
    except btcommon.BluetoothError as e:
        handle_bluetooth_error(e, resolution="revert")
        try:
            return temp_sc, attach_image, None
        except UnboundLocalError:
            return temp_sc, None, None
    Colors(default_color)
    if voice_message:
        if graphic_mode:
            temp_popup = gui.Window(layout=[[gui.Text("New Voice Message!")]],
                                    title=gui_translate("Alert"), font="Courier 20", finalize=True)
        else:
            animated_print(f"New Voice Message!")
    else:
        if graphic_mode:
            temp_popup = gui.Window(layout=[[gui.Text("Awaiting file...")]],
                                    title=gui_translate("Alert"), font="Courier 20", finalize=True)
        else:
            animated_print(f"Awaiting File...")
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
            filename = os.path.basename(filename.replace("\\", "/"))
            if not graphic_mode:
                progress = tqdm.tqdm(range(int(filesize)),
                                     f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                fallback = False
            else:
                temp_popup.close()
                try:
                    progress = tqdm.tqdm(range(int(filesize)),
                                         f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
                    fallback = False
                except OSError:
                    fallback = True
                else:
                    fallback = False
            enter_home_directory()
            if filename == "voice_message.wav":
                filename = "foreign_voice_message.wav"
            if connection_type == "Bluetooth":
                buffer_size = 4096
            else:
                buffer_size = 8192
            file_recipient.settimeout(10)
            with open(f"./cache/{filename}", "wb") as inbound_file:
                if not fallback:
                    exception_counter = 0
                    for _ in progress:
                        try:
                            bytes_read = file_recipient.recv(buffer_size)
                            try:
                                if bytes_read.decode().strip() != "\\exit":
                                    inbound_file.write(bytes_read)
                                else:
                                    break
                            except:
                                inbound_file.write(bytes_read)
                        except TimeoutError:
                            break
                        except:
                            if exception_counter <= 5:
                                exception_counter += 1
                            else:
                                break
                        if not bytes_read:
                            break
                        if graphic_mode:
                            gui_recieve = gui.one_line_progress_meter(title=gui_translate(
                                f"FiEncrypt - Recieving File (Logged in as: {get_current_user()})"), current_value=os.path.getsize(f"./cache/{filename}"), max_value=int(filesize), orientation="h")
                        else:
                            progress.update(len(bytes_read))
                else:
                    if graphic_mode:
                        gui.Popup("File transfer failed", title=gui_translate("Warning"),
                                  font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"WARNING: File transfer failed!", error=True, reset=True)
                        Colors(default_color)
                    file_recipient.close()
            if graphic_mode:
                path_to_save = filedialog.asksaveasfilename(defaultextension="."+substring(os.path.basename(filename), ".", -1).strip(), filetypes=[generate_filetypes(os.path.basename(filename))],
                                                            title=f"FiEncrypt - Save {os.path.basename(filename)}")
                if len(path_to_save) != 0:
                    with open(f"./cache/{filename}", "rb") as cached_file:
                        with open(path_to_save, "wb") as save_file:
                            save_file.write(cached_file.read())
            file_extension = filename.split(".")
            temp_name = file_extension[0]
            file_extension = file_extension[1]
            if file_extension.lower() in ["png", "jpg", "jpeg", "bmp", "ico"]:
                if "png" not in file_extension.lower():
                    cached_image = Image.open(filename)
                    enter_home_directory()
                    cached_image.save(f"./cache/{os.path.basename(temp_name)}.png")
                    filename = f"{os.getcwd()}/cache/{os.path.basename(temp_name)}.png"
                if graphic_mode:
                    attach_image = True
                else:
                    attach_image = False
                    try:
                        if pass_os() != "win32":
                            with ignore_stdout():
                                cached_image.show()
                        else:
                            cached_image.show()
                    except:
                        if graphic_mode:
                            gui.Popup("Unable to open image!", title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: Unable to open image!",
                                           error=True, reset=True)
                            Colors(default_color)
            if not graphic_mode:
                for _ in range(2):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
                print("Sucessfully retrieved!")
            if str(filesize).strip() == str(os.path.getsize(f"./cache/{filename}")).strip():
                if not voice_message:
                    if graphic_mode:
                        gui.Popup(gui_translate(
                            f"File {filename} saved to {os.getcwd()}/cache/{filename}"), title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"File {filename} saved to {os.getcwd()}/cache/{filename}")
                if autosync and filename.lower().strip() != "foreign_voice_message.wav" and filename.lower().strip() != "voice_message.wav":
                    enter_home_directory()
                    cache_transfer_size = os.path.getsize(f"./cache/{filename}")
                    if not graphic_mode:
                        animated_print("*** Autosync ***")
                    else:
                        layout = [[gui.Text(gui_translate(f"Copying {filename} to your private cache"))], [gui.Text(gui_translate(f"Size of {filename}: {parse_size(cache_transfer_size, filename)}"))], [
                            gui.Text(gui_translate(f"Max Size of Personal Cache: {max_size}"))], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                        window = gui.Window(title=gui_translate(f"FiEncrypt - Autosync (Logged in as: {get_current_user()})"), layout=layout,
                                            margins=(100, 50), font="Courier 20", finalize=True)
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
                    personal_cache_total_size = 0
                    for path, dirs, temp_files in os.walk(f"./{hash_value(get_current_user().lower().strip())}/files"):
                        for temp_file in temp_files:
                            personal_cache_total_size += os.path.getsize(
                                f"./{hash_value(get_current_user().lower().strip())}/files/{temp_file}")
                    os.chdir(f"./{hash_value(get_current_user().lower().strip())}/files")
                    if pass_os() == "win32":
                        copy = "copy"
                    else:
                        copy = "cp"
                        filename = filename.strip().replace(" ", "\ ").replace(
                            "'", "\\'").replace("(", "\\(").replace(")", "\\)")
                    if (int(cache_transfer_size) + int(personal_cache_total_size)) > max_size:
                        if graphic_mode:
                            gui.Popup(gui_translate(f"Size of {filename} would exceed max allocated size of your private cache!"),
                                      title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                            window.close()
                        else:
                            animated_print(
                                f"WARNING: Size of {filename} would exceed max allocated size of your private cache!", error=True, reset=True)
                            Colors(default_color)
                    else:
                        if pass_os() == "win32":
                            filename = filename.replace("/", "\\")
                            os.system(f"{copy} ..\\..\\cache\\{filename} {filename}")
                            filename = filename.replace("\\", "/")
                        else:
                            os.system(f"{copy} ../../cache/{filename} {filename}")
                        time.sleep(1)
                        if not graphic_mode:
                            for _ in range(3):
                                sys.stdout.write("\033[F")
                                sys.stdout.write("\033[K")
                elif autosync:
                    if graphic_mode:
                        vm_layout = [[gui.Text(gui_translate("Storing voice messages in your Private Cache is discouraged!"), text_color="red")], [gui.Text(
                            gui_translate("Do you wish to proceed anyway?")), gui.Button(gui_translate("Yes"), key="Yes", bind_return_key=True), gui.Button(gui_translate("No"), key="No")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                        vm_window = gui.Window(title=gui_translate(f"FiEncrypt - Voice Message (Logged in as: {get_current_user()})"),
                                               layout=vm_layout, margins=(100, 50), font="Courier 20")
                        event, values = vm_window.read()
                        if event == "Yes":
                            override = "y"
                        else:
                            override = "n"
                        vm_window.close()
                    else:
                        animated_print(
                            f"WARNING: Storing voice messages in your Private Cache is discouraged!", error=True, reset=True)
                        Colors(default_color)
                        override = privacy_input("Do you wish to proceed anyway? [Y|N]", 0)
                    if "y" in override.lower().strip():
                        valid_name = False
                        while not valid_name:
                            if graphic_mode:
                                name_layout = [[gui.Text(gui_translate("Enter a new name for the voice message file")), gui.InputText(
                                    key="new_name"), gui.Button(gui_translate("Save"), key="Save", bind_return_key=True)]]
                                name_window = gui.Window(
                                    title=gui_translate("Alert"), layout=name_layout, margins=(100, 50), font="Courier 20")
                                event, values = name_window.read()
                                if event == "Save":
                                    new_name = values.get("new_name", None)
                                name_window.close()
                            else:
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
                                    f"./{hash_value(get_current_user().lower().strip())}/files")
                                if pass_os() == "win32":
                                    filename = filename.replace("/", "\\")
                                    os.system(
                                        f"{copy} ..\\..\\cache\\{filename} {stringify_filepath(new_name.replace('.wav','').strip())}.wav")
                                    filename = filename.replace("\\", "/")
                                else:
                                    os.system(
                                        f"{copy} ../../cache/{filename} {stringify_filepath(new_name.replace('.wav','').strip())}.wav")
                                if not graphic_mode:
                                    for _ in range(6):
                                        sys.stdout.write("\033[F")
                                        sys.stdout.write("\033[K")
                            else:
                                if graphic_mode:
                                    gui.Popup(gui_translate("Names still match!"), title=gui_translate("Warning"),
                                              font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                                else:
                                    animated_print(f"WARNING: Names still match!",
                                                   error=True, reset=True)
                                    Colors(default_color)
                                    time.sleep(2)
                                    for _ in range(5):
                                        sys.stdout.write("\033[F")
                                        sys.stdout.write("\033[K")
            else:
                if graphic_mode:
                    gui.Popup(
                        gui_translate(f"File corrupt or incomplete! Check {os.getcwd()}/cache/{filename}"), title=gui_translate("Warning"), font="Courier 20", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(
                        f"WARNING: File corrupt or incomplete! Check {os.getcwd()}/cache/{filename}", error=True, reset=True)
                    Colors(default_color)
    except OSError:
        if graphic_mode:
            gui.Popup(gui_translate("Connection error! Aborting file transfer..."), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print("WARNING: Connection error! Aborting file transfer...", error=True, reset=True)
        file_recipient.close()
        try:
            temp_popup.close()
        except:
            pass
        filename = None
    except OverflowError:
        log(f"File transfer overflow! File too large!", "networkManager", get_current_user(
        ), None)
        if graphic_mode:
            gui.Popup(gui_translate("File too large! Aborting..."), title=gui_translate("Warning"),
                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        else:
            animated_print(f"WARNING: File too large! Aborting...", error=True, reset=True)
            Colors(default_color)
        file_recipient.close()
        try:
            temp_popup.close()
        except:
            pass
    except KeyboardInterrupt:
        log(f"File transfer interrupted!", "networkManager", get_current_user(
        ), None)
        animated_print(f"\nWARNING: Aborting file transfer...", error=True, reset=True)
        Colors(default_color)
        filename = None
        file_recipient.close()
    try:
        file_recipient.close()
    except:
        pass
    if graphic_mode:
        try:
            temp_popup.close()
            time.sleep(2)
            window.close()
        except:
            pass
    elif not autosync:
        enter_home_directory()
        os.chdir("./cache")
    try:
        return temp_sc, attach_image, filename
    except UnboundLocalError:
        return temp_sc, attach_image, None


def retrievemessage(old_code, user, current_user, prefix, recipient_ip, temp_sc, timestamp, mailing, talking_to_self, default_color, print_logs, private_mode, error_color, index, display_initiate, **kwargs):
    """Recieves message from other FiEncrypt user, or yourself (loopback), decrypts and displays it"""
    prev_messages, sender, temp_display_name, window, in_mailbox, in_contacts, priority_code, just_recieved, use_bluetooth = kwargs.get(
        "prev", []), kwargs.get("temp_user", None), get_foreign_user(), kwargs.get("window", None), kwargs.get("in_mailbox", False), kwargs.get("in_contacts", None), kwargs.get("priority_code", None), kwargs.get("just_recieved", False), kwargs.get("use_bluetooth", False)
    if sender == None:
        sender = "Anonymous"
    if temp_display_name == None and sender != "Anonymous":
        temp_display_name = sender
    elif temp_display_name == None:
        temp_display_name = recipient_ip
    prev_message_temp, images = "", []
    try:
        prefix = prefix
    except:
        prefix = ""
    background_color = "\033[41m"
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
        if graphic_mode:
            window = gui.Window(title=gui_translate(f"FiEncrypt - Message Decryption (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate("Enter the encryption code for the message here! Or, leave it blank for the auto-generated key"))], [gui.InputText(key="manual_code")], [
                                gui.Button(gui_translate("Decrypt"), key="Decrypt", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20")
            event, values = window.read()
            window.close()
            if event == "Decrypt":
                code2 = values.get("manual_code", None)
            elif event == "Cancel":
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        else:
            code2 = privacy_input(
                f"Enter the encryption code for the message here! Or, leave it blank for the auto-generated key", private_mode)
        # ?All caps EXIT is the standard escape phrase for inputs in this program
        if code2 == None:
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        # *Checks multiple variable before concluding there is no encryption code present
        if code2 == "":
            if old_code != "":
                code2 = old_code
                #!Manual is set to False by default
                break
            else:
                if old_code == "":
                    animated_print(
                        f"WARNING: Unable to retrieve auto-generated key! Make sure the key is in the code.txt file", error=True, reset=True)
                    Colors(default_color)
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
            Colors(default_color, force=True)
        except:
            temp = code_seg2
            code_seg2 = int(str(code_seg1)[::-1])
            code_seg1 = temp
            Colors(default_color)
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
            date = f"{date[-1]}/{date[0]}"
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
                    f"WARNING: Irregularity detected in the decrypted timestamp! It may be wrong!", error=True, reset=True)
                Colors(default_color)
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
        temp_timestamp = f"{hrs}:{mins}{suffix}"
        temp_date = date
        code3 = code2
    passs = 0
    output_phrase = ''
    files = 0
    if allow_message_input:
        message_text = privacy_input(f"Enter message to be decrypted", private_mode)
    if len(message_text) == 0:
        if not allow_message_input:
            animated_print(
                f"WARNING: Message cannot be blank!", error=True, reset=True)
            Colors(default_color)
            menu(user, current_user, None, default_color,
                 private_mode, error_color, print_speed=0)
        else:
            while len(message_text) == 0:
                animated_print(
                    f"WARNING: Message cannot be blank!", error=True, reset=True)
                Colors(default_color)
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
    if not graphic_mode:
        animated_print(f"Decrypting...")
    if not manual and timestamp != None and not graphic_mode:
        print(timestamp)
    elif not manual and not graphic_mode:
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
    if temp_output_phrase.strip().count("$") >= 2 and not graphic_mode:
        try:
            cached_output_phrase = temp_output_phrase
            temp_output_phrase_list = temp_output_phrase.split("$")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[9m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_color}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                del temp_output_phrase_list[0]
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[9m"
                else:
                    temp_output_phrase = f"\033[9m"
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[9m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                temp_output_phrase = f"\033[9m"
                next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[9m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "$", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("_") >= 2 and not graphic_mode:
        try:
            temp_output_phrase_list = temp_output_phrase.split("_")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[4m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_color}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[4m"
                else:
                    temp_output_phrase = f"\033[4m"
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[4m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[4m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[4m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[4m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "_", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("~") >= 2 and not graphic_mode:
        try:
            temp_output_phrase_list = temp_output_phrase.split("~")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[3m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_color}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[3m"
                else:
                    temp_output_phrase = f"\033[3m"
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[3m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[3m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[3m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[3m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "~", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("*") >= 2 and not graphic_mode:
        try:
            temp_output_phrase_list = temp_output_phrase.split("*")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[1m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_color}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[1m"
                else:
                    temp_output_phrase = f"\033[1m"
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[1m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[1m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[1m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[1m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "*", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            else:
                temp_output_phrase = cached_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    if temp_output_phrase.strip().count("^") >= 2 and not graphic_mode:
        try:
            temp_output_phrase_list = temp_output_phrase.split("^")
            if len(temp_output_phrase_list) == 3:
                temp_output_phrase = f"{temp_output_phrase_list[0]}\033[5m{temp_output_phrase_list[1]}\033[0m\033[41m{applied_default_color}{temp_output_phrase_list[2]}"
                temp_output_phrase = temp_output_phrase.replace(
                    "^", "", len(temp_output_phrase_list))
            elif (len(temp_output_phrase_list) % 2) / 2 != 0:
                if temp_output_phrase_list[0].strip() != "":
                    temp_output_phrase = ""
                    next_format = f"\033[5m"
                else:
                    temp_output_phrase = f"\033[5m"
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                    del temp_output_phrase_list[0]
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[5m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
                temp_output_phrase = temp_output_phrase.replace(
                    "^", "", len(temp_output_phrase_list))
                cached_output_phrase = temp_output_phrase
            elif (len(temp_output_phrase_list) % 2) / 2 == 0:
                del(temp_output_phrase_list[0])
                temp_output_phrase = f"\033[5m"
                if temp_output_phrase_list[0].strip() != "":
                    next_format = "\033[5m"
                else:
                    next_format = f"\033[0m\033[41m{applied_default_color}"
                for i in range(len(temp_output_phrase_list)):
                    temp_output_phrase += f"{temp_output_phrase_list[0]}{next_format}"
                    del temp_output_phrase_list[0]
                    if next_format == f"\033[0m\033[41m{applied_default_color}":
                        next_format = "\033[5m"
                    else:
                        next_format = f"\033[0m\033[41m{applied_default_color}"
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
                    if not graphic_mode:
                        animated_print(
                            f"\033[3m\033[43m{temp_reply_output_phrase.strip()}\"\033[0m{applied_default_color} -> \033[41m{reply_output_phrase[i+1].strip()}\033[0m", pm=True)
                        Colors(default_color)
            else:
                temp_output_phrase = reply_output_phrase[1].strip()
                reply_output_phrase = reply_output_phrase[0].strip()
                reply_output_phrase = reply_output_phrase.split(": ", 1)
                reply_output_phrase[1] = f" \"{reply_output_phrase[1]}"
                reply_output_phrase = f"{reply_output_phrase[0]}:{reply_output_phrase[1]}"
                if not graphic_mode:
                    animated_print(
                        f"\033[3m\033[43m{reply_output_phrase}\"\033[0m{applied_default_color} -> \033[41m{temp_output_phrase}\033[0m", pm=True)
            cached_output_phrase = temp_output_phrase
        except:
            temp_output_phrase = cached_output_phrase
    else:
        if not graphic_mode:
            animated_print(f"\033[41m{temp_output_phrase}\033[0m", pm=True)
    if graphic_mode:
        prev_messages.append([temp_output_phrase, temp_timestamp, temp_display_name, temp_date])
        if just_recieved:
            for i, messages in enumerate(prev_messages):
                if len(messages) == 4 or len(messages) == 5:
                    message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                        "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_username", "").strip()
                    if messages[2].strip().lower() == get_current_user().strip().lower():
                        gap = 30
                    else:
                        gap = 40
                    if len(message_to_show) > gap:
                        temp_list = list(message_to_show)
                        for i in range(gap, len(temp_list), gap):
                            j = i
                            try:
                                while temp_list[j] != " ":
                                    j += 1
                                    if j >= i + 5:
                                        break
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j, "\n")
                            except IndexError:
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j-i, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j-i, "\n")
                        message_to_show = ""
                        for char in temp_list:
                            message_to_show += char
                    if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                        prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "":
                        prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                    elif has_emoji(messages[0]):
                        prev_message_temp += f"(emoji) - {messages[1]}\n"
                    elif has_file(messages[0]):
                        prev_message_temp += f"(file) - {messages[1]}\n"
                    temp_day = str(datetime.datetime.now()).split("-", 2)
                    temp_day = temp_day[2].split()
                    if temp_day[0].strip().startswith("0"):
                        temp_day[0] = temp_day[0].replace("0", "").strip()
                    # if temp_day[0].strip() not in messages[3][0:2]:
                    #     prev_message_temp += f"{messages[3]}\n"
                    try:
                        if messages[4] != None:
                            temp_name = messages[4].split(".")[0]
                            images.append(f"{temp_name}.png")
                    except:
                        pass
                else:
                    pass
        if (current_user != 2 or not in_mailbox) and recipient_ip.strip() != "":
            for i, messages in enumerate(prev_messages):
                if len(messages) == 4 or len(messages) == 5:
                    message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                        "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_username", "").strip()
                    if messages[2].strip().lower() == get_current_user().strip().lower():
                        gap = 30
                    else:
                        gap = 40
                    if len(message_to_show) > gap:
                        temp_list = list(message_to_show)
                        for i in range(gap, len(temp_list), gap):
                            j = i
                            try:
                                while temp_list[j] != " ":
                                    j += 1
                                    if j >= i + 5:
                                        break
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j, "\n")
                            except IndexError:
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j-i, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j-i, "\n")
                        message_to_show = ""
                        for char in temp_list:
                            message_to_showmessage_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                        "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_username", "").strip()
                    if messages[2].strip().lower() == get_current_user().strip().lower():
                        gap = 30
                    else:
                        gap = 40
                    if len(message_to_show) > gap:
                        temp_list = list(message_to_show)
                        for i in range(gap, len(temp_list), gap):
                            j = i
                            try:
                                while temp_list[j] != " ":
                                    j += 1
                                    if j >= i + 5:
                                        break
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j, "\n")
                            except IndexError:
                                if messages[2].strip().lower() == get_current_user().strip().lower():
                                    temp_list.insert(j-i, "\n\t\t\t\t")
                                else:
                                    temp_list.insert(j-i, "\n")
                        message_to_show = ""
                        for char in temp_list:
                            message_to_show += char
                    if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                        prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "":
                        prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                    elif has_emoji(messages[0]):
                        prev_message_temp += f"(emoji) - {messages[1]}\n"
                    elif has_file(messages[0]):
                        prev_message_temp += f"(file) - {messages[1]}\n"
                    temp_day = str(datetime.datetime.now()).split("-", 2)
                    temp_day = temp_day[2].split()
                    if temp_day[0].strip().startswith("0"):
                        temp_day[0] = temp_day[0].replace("0", "").strip()
                    # if temp_day[0].strip() not in messages[3][0:2]:
                    #     prev_message_temp += f"{messages[3]}\n"
                    try:
                        if messages[4] != None:
                            temp_name = messages[4].split(".")[0]
                            images.append(f"{temp_name}.png")
                    except:
                        pass
                    if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                        prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                    elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                        prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_emoji(messages[0]):
                        prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                    elif message_to_show.strip() != "" and has_file(messages[0]):
                        prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                    elif message_to_show.strip() != "":
                        prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                    elif has_emoji(messages[0]):
                        prev_message_temp += f"(emoji) - {messages[1]}\n"
                    elif has_file(messages[0]):
                        prev_message_temp += f"(file) - {messages[1]}\n"
                    temp_day = str(datetime.datetime.now()).split("-", 2)
                    temp_day = temp_day[2].split()
                    if temp_day[0].strip().startswith("0"):
                        temp_day[0] = temp_day[0].replace("0", "").strip()
                    # if temp_day[0].strip() not in messages[3][0:2]:
                    #     prev_message_temp += f"{messages[3]}\n"
                    try:
                        if messages[4] != None:
                            temp_name = messages[4].split(".")[0]
                            images.append(f"{temp_name}.png")
                    except:
                        pass
                else:
                    pass
            enter_home_directory()
            os.chdir("./cache")
            for i, image_name in enumerate(images):
                if not os.path.exists(image_name):
                    del(images[i])
            enter_home_directory()
            os.chdir("./cache")
            if temp_display_name.strip() != "":
                layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                    gui_translate(prev_message_temp, pm=True))]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            else:
                layout = [[gui.Text(gui_translate(f"Decrypted Message!"), font="Courier 30", text_color="red")], [gui.Text(gui_translate(f"From: UNKNOWN"))], [
                    gui.Text(temp_timestamp)], [gui.Text(gui_translate(temp_output_phrase))], [gui.Button(gui_translate("Delete"), key="Delete", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20")
        else:
            current_user = get_current_user().strip().lower()
            enter_home_directory()
            os.chdir("./cache")
            if temp_display_name.strip() != "":
                layout = [[gui.Text(gui_translate(f"New message!"), font="Courier 30", text_color="red")], [gui.Text(gui_translate(f"From: {temp_display_name}"))], [
                    gui.Text(temp_timestamp)], [gui.Text(gui_translate(temp_output_phrase))], [gui.Button(gui_translate("Reply"), key="Reply", bind_return_key=True), gui.Button(gui_translate("Delete"), key="Delete")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            else:
                layout = [[gui.Text(gui_translate(f"Decrypted Message!"), font="Courier 30", text_color="red")], [gui.Text(gui_translate(f"From: UNKNOWN"))], [
                    gui.Text(temp_timestamp)], [gui.Text(gui_translate(temp_output_phrase))], [gui.Button(gui_translate("Delete"), key="Delete", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Mailbox (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Reply":
                window.close()
                return True
            elif event == "Delete" and temp_display_name.strip() != "":
                try:
                    sc.send("\\exit".encode())
                except:
                    pass
                try:
                    sc.close()
                except:
                    pass
                window.close()
                return False
            elif event == "Delete":
                window.close()
    enter_home_directory()
    if expecting_file:
        autosync, max_size = cache_settings(
            user, current_user, default_color, print_logs, private_mode, error_color, mode="read")
        temp_sc, attach_image, filename = sftp_recieve(recipient_ip, user, default_color, error_color, old_code, prefix, temp_sc, autosync=autosync,
                                                       max_size=max_size, voice=voice_message, use_bluetooth=use_bluetooth)
        try:
            if attach_image:
                prev_messages[-1].append(filename)
            else:
                prev_messages[-1].append(None)
        except:
            pass
        if voice_message:
            enter_home_directory()
            try:
                pass
                # playsound(f"./cache/foreign_voice_message.wav")
            except ValueError:
                log("Voice message playback error!", "voiceManager", get_current_user(), print_logs)
                animated_print(
                    f"WARNING: Unable to play voice message! Maybe {sys.platform} doesn't support PyAudio?", error=True, reset=True)
            except KeyboardInterrupt:
                pass
    else:
        try:
            prev_messages[-1].append(None)
        except:
            pass
    Colors(default_color)
    # *@recipient_ip needs to be defined for the below if statement, if it is not, it gets set to blank
    try:
        recipient_ip = recipient_ip
    except NameError:
        recipient_ip = ""
    # ?The @mailing variable is set in the @check_mailbox() module, and remains true if there are unread messages present
    # *Calls the @check_mailbox() module if there are unread messages, which will send the next message back by calling this module again
    if thumb != None:
        thumbs(get_foreign_user(), thumb)
    if graphic_mode:
        try:
            window.close()
        except:
            pass
    if mailing:
        # check_mailbox(user, 2, index, mailing, timestamp, error_color,
        #              default_color, display_initiate, print_logs, private_mode)
        if love_sent and poked:
            you_are_loved(get_foreign_user(), hearts=hearts)
            Colors(default_color)
            get_poked(get_foreign_user(), poke_num=pokes)
        elif love_sent:
            you_are_loved(get_foreign_user(), hearts=hearts)
            Colors(default_color)
        elif poked:
            get_poked(get_foreign_user(), poke_num=pokes)
        else:
            pass
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip() and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colors(default_color)
        get_poked(get_foreign_user(), poke_num=pokes)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and "\\poke" in output_phrase.strip():
        get_poked(get_foreign_user(), poke_num=pokes)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit") and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colors(default_color)
        animated_print(
            f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and "\\poke" in output_phrase.strip() and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colors(default_color)
        get_poked(get_foreign_user(), poke_num=pokes)
        newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                   error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), poked=True, message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
    elif conversation_mode and recipient_ip.strip() != "" and output_phrase.strip().endswith("\\exit"):
        if get_foreign_user() != None:
            animated_print(
                f"{get_foreign_user().capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
        else:
            animated_print(
                f"Peer has left chat! Goodbye {capitalize_user(get_current_user())}!")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif conversation_mode and recipient_ip.strip() != "" and love_sent:
        you_are_loved(get_foreign_user(), hearts=hearts)
        Colors(default_color)
        if not talking_to_self:
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
    elif "\\poke" in output_phrase.strip() and not conversation_mode:
        pass
    elif love_sent and not conversation_mode:
        pass
    elif not conversation_mode or recipient_ip == "" or talking_to_self:
        if poked and talking_to_self:
            get_poked(capitalize_user(get_current_user()), poke_num=pokes)
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        elif talking_to_self:
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            if graphic_mode:
                window = gui.Window(title=gui_translate(f"FiEncrypt - Message Decryption (Logged in as: {get_current_user()})"), layout=[[gui.Text(gui_translate("Was the decryption successful?"))], [gui.Button(gui_translate("Yes"), key="Yes", bind_return_key=True), gui.Button(
                    gui_translate("No"))], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]], margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Yes":
                    success = "y"
                else:
                    success = "n"
                window.close()
            else:
                success = privacy_input(f"Was the decryption successful? (Y/N)", 0)
            if success == None:
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
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
                    if graphic_mode:
                        gui.Popup(gui_translate("The code used to decrypt this message will be deleted from local storage, for your security"),
                                  title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"The code used to decrypt this message will be deleted from local storage, for your security")
                else:
                    if graphic_mode:
                        gui.Popup(gui_translate("Manual code decryption concluded. It is not recommended that you use this code again!"),
                                  title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"Manual code decryption concluded. It is not recommended that you use this code again!")
                    time.sleep(2)
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
            else:
                log(
                    f"Message not successfully decrypted!", "encryptionManager", current_user, print_logs)
                if graphic_mode:
                    gui.Popup(
                        gui_translate("That is unfortunate :( We will launch the encryption assistant momentarily"), title=gui_translate("Alert"), font="Courier 20", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(
                        f"That is unfortunate :( We will launch the encryption assistant momentarily")
                #!Current unreliable
                helper("decrypt", user, current_user)
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
    # *Called if in conversation mode
    else:
        if poked:
            get_poked(get_foreign_user(), poke_num=pokes)
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), poked=True, message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            newmessage(old_code, user, recipient_ip, temp_sc, backup_prefix, date, talking_to_self,
                       error_color, default_color, private_mode, print_logs, mailing, display_initiate, get_auto_code(), message=temp_output_phrase, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)


def server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix, date, default_color, print_logs, private_mode, error_color, display_initiate, **kwargs):
    """Opens server to recieve and interpret message"""
    global override_port
    silent, prev_messages, window, temp_display_name, sender, in_contacts, priority_code, display_port, use_bluetooth = kwargs.get(
        "silent", False), kwargs.get("prev", []), kwargs.get("window", None), get_foreign_user(), kwargs.get("temp_user", None), kwargs.get("in_contacts", None), kwargs.get("priority_code", None), override_port, kwargs.get("use_bluetooth", False)
    try:
        if contact_override_port != None:
            override_port = contact_override_port
    except:
        pass
    if not silent and not graphic_mode:
        print("Server warming up... ", end="")
    elif graphic_mode:
        if temp_display_name == None and sender != None:
            temp_display_name = sender
        elif temp_display_name == None:
            temp_display_name = recipient_ip
        prev_message_temp, images = "", []
        try:
            window.close()
        except:
            pass
        if len(prev_messages) > 1:
            for i, messages in enumerate(prev_messages):
                if len(messages) == 4 or len(messages) == 5:
                    if messages[0] == prev_messages[i-1][0] and messages[1] == prev_messages[i-1][1] and messages[2] == prev_messages[i-1][2]:
                        pass
                    else:
                        message_to_show = messages[0].replace("\\ip", "").replace("\\v", "").replace("\\heart", "").replace("\\poke", "").replace(
                            "\\exit", "").replace("\\thumbs_up", "").replace("\\thumbs_down", "").replace("\\file", "").replace("\\request_username", "").strip()
                        if messages[2].strip().lower() == get_current_user().strip().lower():
                            gap = 30
                        else:
                            gap = 40
                        if len(message_to_show) > gap:
                            temp_list = list(message_to_show)
                            for i in range(gap, len(temp_list), gap):
                                j = i
                                try:
                                    while temp_list[j] != " ":
                                        j += 1
                                        if j >= i + 5:
                                            break
                                    if messages[2].strip().lower() == get_current_user().strip().lower():
                                        temp_list.insert(j, "\n\t\t\t\t")
                                    else:
                                        temp_list.insert(j, "\n")
                                except IndexError:
                                    if messages[2].strip().lower() == get_current_user().strip().lower():
                                        temp_list.insert(j-i, "\n\t\t\t\t")
                                    else:
                                        temp_list.insert(j-i, "\n")
                            message_to_show = ""
                            for char in temp_list:
                                message_to_show += char
                        if messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_emoji(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "" and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and message_to_show.strip() != "":
                            prev_message_temp += f"\t\t\t\t{message_to_show} - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_emoji(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (emoji) - {messages[1]}\n"
                        elif messages[2].strip().lower() == get_current_user().strip().lower() and has_file(messages[0]):
                            prev_message_temp += f"\t\t\t\t{message_to_show} (file) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_emoji(messages[0]) and has_file(messages[0]):
                            prev_message_temp += f"{message_to_show} (file, emoji) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_emoji(messages[0]):
                            prev_message_temp += f"{message_to_show} (emoji) - {messages[1]}\n"
                        elif message_to_show.strip() != "" and has_file(messages[0]):
                            prev_message_temp += f"{message_to_show} (file) - {messages[1]}\n"
                        elif message_to_show.strip() != "":
                            prev_message_temp += f"{message_to_show} - {messages[1]}\n"
                        elif has_emoji(messages[0]):
                            prev_message_temp += f"(emoji) - {messages[1]}\n"
                        elif has_file(messages[0]):
                            prev_message_temp += f"(file) - {messages[1]}\n"
                        temp_day = str(datetime.datetime.now()).split("-", 2)
                        temp_day = temp_day[2].split()
                        if temp_day[0].strip().startswith("0"):
                            temp_day[0] = temp_day[0].replace("0", "").strip()
                        # if temp_day[0].strip() not in messages[3][0:2]:
                        #     prev_message_temp += f"{messages[3]}\n"
                        try:
                            if messages[4] != None:
                                temp_name = messages[4].split(".")[0]
                                images.append(f"{temp_name}.png")
                        except:
                            pass
                else:
                    pass
            enter_home_directory()
            os.chdir("./cache")
            for i, image_name in enumerate(images):
                if not os.path.exists(image_name):
                    del(images[i])
            enter_home_directory()
            os.chdir("./cache")
            layout = [[gui.Text(gui_translate(f"Conversation with {temp_display_name}"), font="Courier 30", text_color="red")], [gui.Column([[gui.Text(
                gui_translate(prev_message_temp, pm=True))], [gui.Text("...")]], scrollable=True, size=(1000, 400))], [gui.Text(gui_translate("Media"), font="Courier 10")], [gui.Column([[gui.Image(filename=f"./{image_name}", size=(250, 200)) for image_name in images]], scrollable=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation (Logged in as: {get_current_user()})"),
                                layout=layout, margins=(100, 50), font="Courier 20", finalize=True)
    enter_home_directory()
    if sys.platform.startswith("linux"):
        ip = gnu_ip_resolve(print_logs, private_mode)
        if ip == "":
            animated_print(
                f"WARNING: Unable to determine IP address!", error=True, reset=True)
            Colors(default_color)
            ip = privacy_input(
                "Enter your IP in dotted decimal format", private_mode)
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    if not silent and not graphic_mode:
        print("Done!")
    try:
        if "bluetooth" in str(temp_sc).lower():
            ip = "<Bluetooth>"
        if temp_sc == None:
            try:
                temp = RFCOMM
                bluetooth_available = True
                if graphic_mode and not use_bluetooth:
                    use_bluetooth = gui.popup_yes_no(gui_translate("Use Bluetooth for communication?"), title=gui_translate(f"FiEncrypt - Activate Bluetooth (Logged in as {get_current_user()})"), font="Courier 20")
                    if use_bluetooth == "Yes":
                        use_bluetooth = True
                    else:
                        use_bluetooth = False
                elif not use_bluetooth:
                    use_bluetooth = to_boolean(privacy_input("Use Bluetooth for communication? [True|False]", private_mode))
                if use_bluetooth:
                    server_port_override = False
                    link = BluetoothSocket(RFCOMM)
                    ip = ""
                    override_port = 23
                else:
                    raise TypeError
            except:
                bluetooth_available = False
                link = socket.socket()
                if not silent:
                    if graphic_mode:
                        layout = [[gui.Text(gui_translate("Set port for contact?")), gui.Button(gui_translate("Yes"), key="yes"), gui.Button(gui_translate("No"), key="no")], [gui.Text(gui_translate("If yes, enter contact's name here")), gui.InputText(key="target_contact")], [gui.Button(gui_translate("Submit"), key="submit", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="cancel")],[gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                        window = gui.Window(title=f"FiEncrypt - Port Adjustment (Logged in as {get_current_user()})", layout=layout, font="Courier 20")
                        while True:
                            event, values = window.read()
                            if event == "yes":
                                server_port_override = True
                            elif event == "no":
                                server_port_override = False
                            elif event == "cancel":
                                window.close()
                                menu(user, None, print_logs, default_color,
                                     private_mode, error_color, print_speed=0)
                            elif event == "submit":
                                try:
                                    if not server_port_override:
                                        server_port_override = False
                                except UnboundLocalError:
                                    server_port_override = False
                                target_contact = values.get("target_contact", None)
                                break
                        window.close()
                    else:
                        contact_socket = privacy_input("Do you wish to set the port according to a contact file? [Y|N]", private_mode)
                        if "y" in contact_socket.lower():
                            target_contact = privacy_input("Enter contact name here", private_mode)
                            contact_port_search = Contacts(user, get_current_user(), print_logs, default_color, error_color, private_mode)
                            contact_name, contact_mac, contact_ip, details, agreed_code, temp_override_port = contact_port_search.check_for(target_contact.strip())
                            server_port_override = True
                        else:
                            temp_override_port = override_port
                            server_port_override = False
                else:
                    server_port_override = False
            if not silent and not graphic_mode:
                animated_print("Socket opened... ")
            if use_bluetooth or "bluetooth" in str(temp_sc).lower():
                ip = "<Bluetooth>"
            try:
                if server_port_override:
                    link.bind((ip, int(temp_override_port)))
                    display_port = temp_override_port
                else:
                    link.bind((ip, int(override_port)))
                    display_port = override_port
            except:
                if pass_os() == "linux":
                    try:
                        temp_sc.close()
                        link.close()
                        os.system("sudo systemctl restart bluetooth")
                    except:
                        pass
                server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix,
                               date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, use_bluetooth=use_bluetooth)
            override_port = display_port
            time.sleep(1)
            if not silent and not graphic_mode:
                sys.stdout.write("\033[K")
                sys.stdout.write("\033[F")
                animated_print("Socket bound... ")
            link.listen(10)
            time.sleep(2)
            if not silent and not graphic_mode:
                sys.stdout.write("\033[F")
        if not silent and not graphic_mode:
            animated_print(f"Socket bound... {ip}:{display_port}")
            animated_print("Listening on socket... ")
        elif graphic_mode:
            time.sleep(1)
            if silent:
                layout = [[gui.Text(gui_translate("Awaiting Message"))]]
            else:
                layout = [[gui.Text(gui_translate("Awaiting Message"))], [gui.Text(gui_translate("Bound to:")), gui.Text(f"{ip}:{display_port}")]]
            temp_popup = gui.Window(title=gui_translate(f"FiEncrypt - Inbound Server (Logged in as: {get_current_user()})"),
                                    layout=layout, margins=(100, 50), font="Courier 20", finalize=True)
        log(f"Server started on {ip}:{display_port}", "networkManager",
            current_user, print_logs)
        if temp_sc == None:
            sc, address = link.accept()
        else:
            sc = temp_sc
    except KeyboardInterrupt:
        log("Server channel terminated!", "networkManager", get_current_user(), print_logs)
        if graphic_mode:
            temp_popup.close()
        else:
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
        try:
            window.close()
            connection_window.close()
        except:
            pass
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    if not silent and not graphic_mode:
        sys.stdout.write("\033[K")
        sys.stdout.write("\033[F")
        animated_print("Connection established!")
    try:
        if type(sc) == list:
            for pipe in range(len(sc)):
                locals()[f"info{pipe}"] = sc[pipe].recv(1024)
        else:
            info = sc.recv(1024)
        if graphic_mode:
            temp_popup.close()
    except btcommon.BluetoothError as e:
        handle_bluetooth_error(e)
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
        try:
            window.close()
            connection_window.close()
        except:
            pass
        menu(user, display_initiate, print_logs,
             default_color, private_mode, error_color, print_speed=0)
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
        try:
            window.close()
            connection_window.close()
        except:
            pass
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    except ConnectionAbortedError:
        log("Server channel terminated!", "networkManager", get_current_user(), print_logs)
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
        if graphic_mode:
            gui.Popup(gui_translate("Server Connection Aborted!"), title=gui_translate("Warning"),
                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            try:
                window.close()
                connection_window.close()
            except:
                pass
        else:
            animated_print("Server Connection Aborted!")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    except ConnectionResetError:
        log("Server channel reset!", "networkManager", get_current_user(), print_logs)
        animated_print(
            f"Connection reset by peer!", error=True, reset=True)
        Colors(default_color)
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
        try:
            window.close()
            connection_window.close()
        except:
            pass
        menu(user, display_initiate, print_logs,
             default_color, private_mode, error_color, print_speed=0)
    except:
        raise
        log("Server channel terminated!", "networkManager", get_current_user(), print_logs)
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
        if graphic_mode:
            gui.Popup(gui_translate("Unhandled error occured! Shutting down server"), title=gui_translate("Warning"),
                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            try:
                window.close()
                connection_window.close()
            except:
                pass
        else:
            animated_print("Unknown error! Server shutting down")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    if not silent and not graphic_mode:
        print("Recieving information... ", end="\n\n")
    elif graphic_mode:
        try:
            temp_popup.close()
        except:
            pass
        connection_layout = [[gui.Text(gui_translate("Incoming Message"))], [
            gui.Text(key="progress")], [gui.Button(gui_translate("Dismiss"), key="Dismiss")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        connection_window = gui.Window(title=gui_translate(f"FiEncrypt - Server (Logged in as: {get_current_user()})"),
                                       layout=connection_layout, margins=(100, 50), font="Courier 20", finalize=True)
    for i in range(1, 6):
        if not silent and not graphic_mode:
            sys.stdout.write("\033[F")
            print(f"{'-'*(i*2)}> {i*20}%")
            time.sleep(0.5)
        elif graphic_mode:
            gui.one_line_progress_meter(title=gui_translate(
                f"FiEncrypt - Server (Logged in as: {get_current_user()})"), current_value=i*20, max_value=100, orientation="h")
            time.sleep(0.5)
    try:
        connection_window.close()
    except:
        pass
    if type(sc) == list:
        info = []
        for pipe in range(len(sc)):
            info.append(locals()[f"info{pipe}"].decode())
    else:
        info = info.decode()
    if to_boolean(info):
        recipient_ip = recipient_ip.replace("\n", "")
        if graphic_mode:
            gui.Popup(gui_translate(f"{recipient_ip} unavailable! Message left in their mailbox!"),
                      title=gui_translate(f"FiEncrypt - Sent To Mailbox (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
            for _ in range(2):
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
            animated_print("Message left!")
        try:
            sc.close()
        finally:
            try:
                link.close()
            except:
                pass
        try:
            window.close()
            connection_window.close()
        except:
            pass
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    if type(info) == list:
        for info_set, temp_info in enumerate(info):
            message = temp_info.split(" |||| ")
            if "\\user_confirm" in message[0]:
                message[0] = message[0].split("=")
                expected_user = message[0][1]
                message[0] = message[0][0]
                reply_ip = message[1]
                decrypted_target_user, encrypted_target_user = [], []
                for i, char in enumerate(expected_user[::-1]):
                    encrypted_target_user.append(ord(char))
                    decrypted_target_user.append(chr(int(encrypted_target_user[i])-31))
                expected_user = ""
                for char in decrypted_target_user:
                    expected_user += char
                if expected_user.strip().lower() == get_current_user().strip().lower():
                    sc[info_set].send(str(True).encode())
                    if not graphic_mode and not silent:
                        animated_print(f"Foreign user validated!")
                        for _ in range(9):
                            sys.stdout.write("\033[F")
                            sys.stdout.write("\033[K")
                    try:
                        link.close()
                    except:
                        pass
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                                   date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, use_bluetooth=use_bluetooth)
                else:
                    sc[info_set].send(str(False).encode())
                    if graphic_mode:
                        gui.Popup(gui_translate("Foreign user validation failed!"), title=gui_translate("Warning"),
                                  font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    elif not silent:
                        animated_print(
                            f"WARNING: Foreign user validation failed!", error=True, reset=True)
                        Colors(default_color)
                        for _ in range(7):
                            sys.stdout.write("\033[F")
                            sys.stdout.write("\033[K")
                    try:
                        link.close()
                    except:
                        pass
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                                   date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, use_bluetooth=use_bluetooth)
            else:
                try:
                    if "\\exit" in message or "\\poke" in message:
                        pass
                    else:
                        temp_info = message[1]
                    message = message[0]
                except IndexError:
                    if message[0].strip() == "":
                        if graphic_mode:
                            gui.Popup(gui_translate("Pipe Broken! Returning to menu!"), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: Pipe broken! Returning to menu!",
                                           error=True, reset=True)
                            Colors(default_color)
                        try:
                            sc[info_set].close()
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
                        try:
                            window.close()
                            connection_window.close()
                        except:
                            pass
                        menu(user, None, print_logs, default_color,
                             private_mode, error_color, print_speed=0)
                    else:
                        log("Invalid message recieved! Server channel restarting",
                            "networkManager", get_current_user(), print_logs)
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid message recieved!"), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            if message == "None\\request_user":
                                try:
                                    newmessage(code, user, recipient_ip, temp_sc, prefix, date, False, error_color, default_color, private_mode, mailing, display_initiate, auto_code)
                                except:
                                    if graphic_mode:
                                        gui.Popup(f"Pipe out of sync! Try to message {recipient_ip} again", title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                                    else:
                                        animated_print(f"WARNING: Pipe out of sync! Try to message {recipient_ip} again", error=True, reset=True)
                                    try:
                                        temp_sc.send("\\exit".encode())
                                    except:
                                        pass
                                    finally:
                                        temp_sc.close()
                                    try:
                                        link.close()
                                    except:
                                        pass
                                    menu(user, None, print_logs, default_color,
                                         private_mode, error_color, print_speed=0)
                            else:
                                if graphic_mode:
                                    gui.Popup(gui_translate("Invalid message recieved!"), title=gui_translate("Warning"),
                                              font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                                else:
                                    animated_print(
                                        f"WARNING: {message} recieved but not valid! Restarting Server!", error=True, reset=True)
                        Colors(default_color)
                        try:
                            link.close()
                        except:
                            pass
                        try:
                            window.close()
                            connection_window.close()
                        except:
                            pass
                        server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix,
                                       date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, use_bluetooth=use_bluetooth)
                if not silent and not graphic_mode:
                    animated_print("Done!")
            try:
                link.shutdown(socket.SHUT_RDWR)
            except:
                pass
            temp_info = temp_info.split(" | ")
            try:
                message = message.decode()
            except AttributeError:
                pass
            try:
                foreign_user = temp_info[1]
                temp_info[0] = temp_info[0].split("|")
                temp_info[0][1] = temp_info[0][1].split("_")
                date = temp_info[0][1][0]
            except IndexError:
                if "\\exit" in message or "\\poke" in message:
                    pass
                else:
                    if print_logs:
                        animated_print(temp_info)
                    animated_print(
                        f"WARNING: Error with date formatting! Returning to menu!", error=True, reset=True)
                    Colors(default_color)
                    try:
                        sc[info_set].close()
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
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    menu(user, None, print_logs, default_color,
                         private_mode, error_color, print_speed=0)
            if "\\exit" in message:
                skip = True
                if get_foreign_user() == None:
                    foreign_user = "Anonymous"
                else:
                    foreign_user = get_foreign_user()
                if graphic_mode:
                    gui.Popup(gui_translate(f"{foreign_user.capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!"),
                              title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
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
                code = temp_info[0][1][1].replace("'", "")
                if recipient_ip.strip() == "" and temp_sc[info_set] == None:
                    recipient_ip = address[0]
                if print_logs and not graphic_mode:
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
                        if not silent and not graphic_mode:
                            animated_print(f"Message from {temp_foreign_user} received!")
                    else:
                        foreign_user = "Anonymous"
                prefix = temp_info[0][1][2]
                if temp_info[0][2].strip() != "":
                    prefix = f"{prefix}||{temp_info[0][2]}"
                    hrs = int(str(timer[2][3: 5])) + int(info[0][2].replace("#", ""))
                    mns = int(str(timer[2][6: 8])) + int(info[0][2].replace("#", ""))
                else:
                    prefix = f"{prefix}||{temp_info[0][3]}"
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
                        foreign_user = decode_foreign_user(
                            code, prefix, foreign_user, default_color)
                    if not graphic_mode:
                        sys.stdout.write("\033[F")
                    if get_foreign_user() != None and foreign_user.strip().lower() != get_foreign_user().strip().lower():
                        if get_foreign_user() != None and foreign_user.strip().lower() == "Anonymous":
                            pass
                        else:
                            if graphic_mode:
                                gui.Popup(gui_translate("The user sending the message has changed!"),
                                          title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(
                                    f"WARNING: The user sending the message has changed!", error=True, reset=True)
                                Colors(default_color)
                            foreign_user = get_foreign_user(new_user=foreign_user)
                    if not silent and not graphic_mode:
                        animated_print(
                            f"Message from {foreign_user.capitalize()} recieved!")
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    retrievemessage(code, user, 2, prefix, recipient_ip, sc, timestamp, False, False,
                                    default_color, print_logs, private_mode, error_color, None, display_initiate, prev=prev_messages, temp_user=foreign_user, window=window, just_recieved=True, use_bluetooth=use_bluetooth)
                except KeyboardInterrupt:
                    try:
                        sc[info_set].close()
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
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    menu(user, display_initiate, print_logs,
                         default_color, private_mode, error_color, print_speed=0)
            else:
                try:
                    sc[info_set].close()
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
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                menu(user, display_initiate, print_logs,
                     default_color, private_mode, error_color, print_speed=0)
    else:
        message = info.split(" |||| ")
        if len(message) == 1:
            pass
        elif "agreed" in message[1]:
            contact_key_extract = Contacts(user, get_current_user().lower().strip(
            ), print_logs, default_color, error_color, private_mode)
            contact_mac = substring(message[1], ",", -1).strip()
            contact_mac = substring(contact_mac, " | ", 0).strip()
            in_contacts, contact_details = contact_key_extract.list_all(mac_check=True, target_mac=contact_mac)
            if in_contacts:
                priority_code = contact_details[3].strip().replace("\n", "")
        if "\\user_confirm" in message[0]:
            message[0] = message[0].split("=")
            expected_user = message[0][1].strip()
            message[0] = message[0][0]
            reply_ip = message[1]
            if expected_user[::-1] == hash_value(get_current_user().strip().lower()):
                sc.send(str(True).encode())
                if not graphic_mode and not silent:
                    animated_print(f"Foreign user validated!")
                    for _ in range(7):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                try:
                    link.close()
                except:
                    pass
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                               date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
            else:
                sc.send(str(False).encode())
                if graphic_mode:
                    gui.Popup(gui_translate("Foreign user validation failed!"), title=gui_translate("Warning"),
                              font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                elif not silent:
                    animated_print(
                        f"WARNING: Foreign user validation failed!", error=True, reset=True)
                    Colors(default_color)
                    for _ in range(7):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                try:
                    link.close()
                except:
                    pass
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                               date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        else:
            try:
                if "\\exit" in message or "\\poke" in message or "\\request_user" in message:
                    pass
                else:
                    info = message[1]
                    message = message[0]
            except IndexError:
                if message[0].strip() == "":
                    if graphic_mode:
                        gui.Popup(gui_translate("Pipe Broken! Returning to menu!"), title=gui_translate("Warning"),
                                  font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"WARNING: Pipe broken! Returning to menu!",
                                       error=True, reset=True)
                        Colors(default_color)
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
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    menu(user, None, print_logs, default_color,
                         private_mode, error_color, print_speed=0)
                else:
                    log("Invalid message recieved! Server channel restarting",
                        "networkManager", get_current_user(), print_logs)
                    if message == "None\\request_user":
                        try:
                            newmessage(code, user, recipient_ip, temp_sc, prefix, date, False, error_color, default_color, private_mode, mailing, display_initiate, auto_code)
                        except:
                            if graphic_mode:
                                gui.Popup(f"Pipe out of sync! Try to message {recipient_ip} again", title="Warning", font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(f"WARNING: Pipe out of sync! Try to message {recipient_ip} again", error=True, reset=True)
                            try:
                                temp_sc.send("\\exit".encode())
                            except:
                                pass
                            finally:
                                temp_sc.close()
                            try:
                                link.close()
                            except:
                                pass
                            menu(user, None, print_logs, default_color,
                                 private_mode, error_color, print_speed=0)
                    else:
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid message recieved!"), title=gui_translate("Warning"),
                                      font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(
                                f"WARNING: {message} recieved but not valid! Restarting Server!", error=True, reset=True)
                    Colors(default_color)
                    try:
                        link.close()
                    except:
                        pass
                    try:
                        window.close()
                        connection_window.close()
                    except:
                        pass
                    server_recieve(user, code, current_user, temp_sc, recipient_ip, timestamp, prefix,
                                   date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
            if not silent and not graphic_mode:
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
            foreign_user = info[-1]
            if priority_code != None:
                info[0] = substring(priority_code, " = ", -1).strip()
            info[0] = info[0].split("|")
            info[0][1] = info[0][1].split("_")
            date = info[0][1][0]
        except IndexError:
            if "\\exit" in message or "\\poke" in message or "\\request_user" in message:
                pass
            else:
                if "agreed" in info[0][0]:
                    if graphic_mode:
                        gui.Popup(gui_translate("No/Invalid agreed code found!"), title=gui_translate("Warning"),
                                  text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(f"WARNING: No/Invalid agreed code found!", error=True, reset=True)
                        Colors(default_color)
                else:
                    if print_logs:
                        animated_print(info)
                    animated_print(
                        f"WARNING: Error with date formatting! Returning to menu!", error=True, reset=True)
                    Colors(default_color)
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
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                menu(user, None, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        if "\\exit" in message:
            skip = True
            if get_foreign_user() == None:
                foreign_user = "Anonymous"
            else:
                foreign_user = get_foreign_user()
            if graphic_mode:
                gui.Popup(gui_translate(f"{foreign_user.capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!"),
                          title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                animated_print(
                    f"{foreign_user.capitalize()} has left chat! Goodbye {capitalize_user(get_current_user())}!")
            backup_current_user = user
        elif "\\request_user" in message and get_foreign_user() == None:
            skip = True
            accepted = id_packet(sc, mode="recieve", ip=get_ip_from_socket(sc))
            sc, username, temp_mac, temp_save_override_port = id_packet(sc, code=[code, prefix], mode="send")
            auto_generate_contact = Contacts(user, get_current_user(), print_logs, default_color, error_color, private_mode)
            try:
                if temp_save_override_port.strip() == "":
                    temp_save_override_port = None
            except:
                pass
            if username != None and username != "None" and len(temp_mac) == 19:
                auto_generate_contact.add(username, temp_mac, None, "Auto-generated contact on username request", temp_save_override_port)
            server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
        elif "\\request_user" in message:
            skip = True
            server_recieve(user, code, current_user, sc, recipient_ip, timestamp, prefix,
                           date, default_color, print_logs, private_mode, error_color, display_initiate, prev=prev_messages, window=window, in_contacts=in_contacts, priority_code=priority_code, use_bluetooth=use_bluetooth)
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
            if print_logs and not graphic_mode:
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
                    if not silent and not graphic_mode:
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
                    foreign_user = decode_foreign_user(code, prefix, foreign_user, default_color)
                if not graphic_mode:
                    sys.stdout.write("\033[F")
                if get_foreign_user() != None and foreign_user.strip().lower() != get_foreign_user().strip().lower():
                    if get_foreign_user() != None and foreign_user.strip().lower() == "Anonymous":
                        pass
                    else:
                        if graphic_mode:
                            gui.Popup(gui_translate("The user sending the message has changed!"),
                                      title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(
                                f"WARNING: The user sending the message has changed!", error=True, reset=True)
                            Colors(default_color)
                        foreign_user = get_foreign_user(new_user=foreign_user)
                if not silent and not graphic_mode:
                    animated_print(
                        f"Message from {foreign_user.capitalize()} recieved!")
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                retrievemessage(code, user, 2, prefix, recipient_ip, sc, timestamp, False, False,
                                default_color, print_logs, private_mode, error_color, None, display_initiate, prev=prev_messages, temp_user=foreign_user, window=window, in_contacts=in_contacts, priority_code=priority_code, just_recieved=True, use_bluetooth=use_bluetooth)
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
                try:
                    window.close()
                    connection_window.close()
                except:
                    pass
                menu(user, display_initiate, print_logs,
                     default_color, private_mode, error_color, print_speed=0)
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
            try:
                window.close()
                connection_window.close()
            except:
                pass
            menu(user, display_initiate, print_logs,
                 default_color, private_mode, error_color, print_speed=0)


def helper(issue, user, current_user):
    """Module meant to automatically address known persistent issues in FiEncrypt"""
    try:
        animated_print("WARNING: Helper not currently available! Please check back to https://www.github.com/le-firehawk/FiEncrypt for updates!", error=True, reset=True)
    except:
        print("Helper not currently available! Please check back to https://www.github.com/le-firehawk/FiEncrypt for updates!")


def send_conversation_invite(user, current_user, default_color, private_mode, error_color, print_logs, display_initiate):
    """Sends a simple alert to recipient, prompting them with an IP address to send a message to, through listener.py"""
    if sys.platform.startswith("linux"):
        ip = gnu_ip_resolve(print_logs, private_mode)
        if ip == "":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("Enter your IP in dotted decimal format")), gui.InputText(key="ip"), gui.Button(
                    gui_translate("Set"), bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate("FiEncrypt - IP"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Set":
                    ip = values.get("ip", None)
            else:
                ip = privacy_input(
                    "Enter your IP in dotted decimal format", private_mode)
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    try:
        dest_ip, target_mac, target_name, empty_sc, agreed_code, override_port = get_recipient_ip(user, display_initiate, print_logs,
                                                                      default_color, private_mode, error_color, None, is_invite=True)
        if type(dest_ip) != list:
            dest_ip = dest_ip.strip()
    except KeyboardInterrupt:
        print("")
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    connected = False
    while not connected:
        try:
            if type(dest_ip) == list:
                for connection_num in range(len(dest_ip)):
                    try:
                        locals()[f"link{connection_num}"] = socket.socket()
                        locals()[f"link{connection_num}"].connect(
                            (dest_ip[connection_num].strip(), 19507))
                    except Exception as e:
                        raise
                        print(e)
            else:
                link = socket.socket()
                link.connect((dest_ip, 19507))
            connected = True
        except:
            raise
        # except ConnectionRefusedError:
        #     log(f"Invite delivery refused!", "networkManager", get_current_user(
        #     ), print_logs)
        #     connected = False
        #     if graphic_mode:
        #         gui.Popup(gui_translate("Connection to recipient unexpectedly terminated! Try again!"),
        #                   title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        #     else:
        #         animated_print(
        #             f"WARNING: Connection to recipient unexpectedly terminated! Try again!", error=True, reset=True)
        #         Colors(default_color)
        #     menu(user, None, print_logs, default_color,
        #          private_mode, error_color, print_speed=0)
        # except TimeoutError:
        #     log(f"Invite delivery timeout!", "networkManager", get_current_user(
        #     ), print_logs)
        #     connected = False
        #     if graphic_mode:
        #         gui.Popup(gui_translate("Unable to obtain a response from recipient address! Try again!"),
        #                   title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        #     else:
        #         animated_print(
        #             f"WARNING: Unable to obtain a response from recipient address! Try again!", error=True, reset=True)
        #         Colors(default_color)
        #     send_conversation_invite(user, current_user, default_color,
        #                              private_mode, error_color, print_logs, display_initiate)
        # except OSError:
        #     log(f"Invite delivery OSError!", "networkManager", get_current_user(
        #     ), print_logs)
        #     connected = False
        #     if graphic_mode:
        #         gui.Popup(gui_translate("Unable to obtain a response from recipient address! Try again!"),
        #                   title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        #     else:
        #         animated_print(
        #             f"WARNING: Unable to obtain a response from recipient address! Try again!", error=True, reset=True)
        #         Colors(default_color)
        #     send_conversation_invite(user, current_user, default_color,
        #                              private_mode, error_color, print_logs, display_initiate)
        # except KeyboardInterrupt:
        #     log(f"Invite delivery interrupted!", "networkManager", get_current_user(
        #     ), print_logs)
        #     if graphic_mode:
        #         gui.Popup(gui_translate("Aborting!"), title=gui_translate("Warning"),
        #                   font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
        #     else:
        #         animated_print(f"\nAborting!")
        #     try:
        #         sc.close()
        #     except:
        #         pass
        #     try:
        #         link.close()
        #     except:
        #         pass
        #     menu(user, None, print_logs, default_color,
        #          private_mode, error_color, print_speed=0)
    if target_name != None:
        content = f"Request:True | Source_IP:{ip} | Name:{current_user} |||| Target:{target_name}"
    else:
        content = f"Request:True | Source_IP:{ip} | Name:{current_user}"
    packet = content.encode()
    if type(dest_ip) == list:
        for connection_num in range(len(dest_ip)):
            locals()[f"link{connection_num}"].send(packet)
            try:
                locals()[f"link{connection_num}"].shutdown(socket.SHUT_RDWR)
            except:
                pass
            locals()[f"link{connection_num}"].close()
    else:
        link.send(packet)
        log(f"Conversation invite sent to {dest_ip}",
            "networkManager", current_user, print_logs)
        try:
            link.shutdown(socket.SHUT_RDWR)
        except:
            pass
        link.close()
    # *The code 1 will tell listener.py that it is recieving a conversation request, not a message
    code, prefix, timestamp = showcode(user, 1, private_mode,
                                       print_logs, error_color, default_color)
    date = timestamp.split("|")
    date = date[1]
    if graphic_mode:
        if type(dest_ip) == list:
            layout = [[gui.Text(gui_translate(f"Contact(s) have been invited!"))], [gui.Text(gui_translate("Start server?")), gui.Button(
                gui_translate("Yes"), bind_return_key=True), gui.Button(gui_translate("No"), key="No")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        else:
            layout = [[gui.Text(gui_translate(f"{dest_ip} has been invited!"))], [gui.Text(gui_translate("Start server?")), gui.Button(
                gui_translate("Yes"), bind_return_key=True), gui.Button(gui_translate("No"), key="No")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation Invite (Logged in as: {get_current_user()})"),
                            layout=layout, margins=(100, 50), font="Courier 20")
        event, values = window.read()
        if event == "Yes":
            start_server = "y"
        else:
            start_server = "n"
        window.close()
    else:
        if type(dest_ip) == list:
            animated_print(f"Contacts have been invited!")
        else:
            animated_print(f"{dest_ip} has been invited!")
        start_server = privacy_input(f"Start server? [Y|N]", private_mode)
    if start_server == None:
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    elif "y" in start_server.lower():
        server_recieve(user, code, user, current_user, dest_ip, timestamp,
                       prefix, date, default_color, print_logs, private_mode, error_color, display_initiate)
    else:
        menu(user, None, print_logs, default_color,
             private_mode, error_color, print_speed=0)


def check_mailbox(user, current_user, index, mailing, timestamp, error_color, default_color, display_initiate, print_logs, private_mode):
    """Checks your mailbox for any unread messages"""
    enter_home_directory()
    if current_user != 2:
        os.chdir(f"./{hash_value(get_current_user().strip().lower())}/inbox")
        with open(f"./messages.txt", "r+") as mailbox:
            letters = mailbox.readlines()
        for i, letter in enumerate(letters):
            try:
                letter = int(letter)
            except ValueError:
                pass
        # ?Due to the formatting of the mailbox entries made by listener.py, each message uses two lines, so the printed value is half the length
        if graphic_mode:
            gui.Popup(gui_translate(f"You have {int(len(letters)/2)} unread messages!"),
                      title=gui_translate(f"{int(len(letters)/2)} Unread Messages! (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
        else:
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
            enter_home_directory()
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
                        old_code, prefix, message[1][1][0].strip(), default_color)
                else:
                    message[1][1][0] = "Anonymous"
                message[1][1][0] = get_foreign_user(new_user=message[1][1][0])
                if not graphic_mode:
                    animated_print(f"Message from {message[1][1][0].capitalize()}")
                bad_message = False
            except IndexError:
                log("Corrupted message in mailbox!", "mailManager", get_current_user(), print_logs)
                if graphic_mode:
                    gui.Popup(gui_translate(f"Message {i} contains corrupted format! This message will be removed!"), title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(
                        f"WARNING: Message {i} contains corrupted format! This message will be removed!", error=True, reset=True)
                    Colors(default_color)
                bad_message = True
            del(index[i])
            enter_home_directory()
            os.chdir(f"./{hash_value(get_current_user().strip().lower())}/inbox")
            with open(f"./messages.txt", "w+") as inbox:
                inbox.seek(0)
                inbox.truncate()
                try:
                    inbox.write(f"{i}\n{index[i]}")
                except IndexError:
                    pass
            try:
                if graphic_mode and not bad_message:
                    send_reply = retrievemessage(old_code, user, 2, prefix, message[1][1], None, timestamp,
                                                 True, False, default_color, print_logs, private_mode, error_color, index, display_initiate, temp_user=message[1][1][0], in_mailbox=True)
                elif not bad_message:
                    send_reply = None
                    retrievemessage(old_code, user, 2, prefix, message[1][1], None, timestamp,
                                    True, False, default_color, print_logs, private_mode, error_color, index, display_initiate, temp_user=message[1][1][0])
                Colors(default_color)
                if not bad_message:
                    if send_reply != None and graphic_mode:
                        if send_reply:
                            reply = "y"
                        else:
                            reply = "n"
                    else:
                        reply = privacy_input(
                            f"Would you like to send a reply? [Y|N]", private_mode)
                    if "y" in reply.lower():
                        code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                           print_logs, error_color, default_color)
                        ip, target_mac, target_name, temp_sc, agreed_code, override_port = get_recipient_ip(
                            user, display_initiate, print_logs, default_color, private_mode, error_color, None, confirm_ip=f"{message[1][1][0]}@{message[1][1][1]}")
                        newmessage(code, user, message[1][1][1], temp_sc, prefix, None,
                                   False, error_color, default_color, private_mode, print_logs, False, display_initiate, False, checking_mailbox=True)
                    else:
                        check_mailbox(user, 2, index, mailing, timestamp, error_color,
                                      default_color, display_initiate, print_logs, private_mode)
                else:
                    check_mailbox(user, 2, index, mailing, timestamp, error_color,
                                  default_color, display_initiate, print_logs, private_mode)
            except UnboundLocalError:
                Colors(default_color)
    protect_tree()
    mailing = False
    menu(user, display_initiate, print_logs,
         default_color, private_mode, error_color, print_speed=0)


def config_settings(user, current_user, default_color, print_logs, private_mode, error_color):
    """Provides an interface to modify the config file through"""
    global graphic_mode, gui_theme, translation, TranslationManager, override_port
    master_printing_speed = None
    if not graphic_mode:
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
        master_print_speed = printing_speed
        if "default" in config_lines[5].lower():
            display_color = config_lines[5].split(" = ")
            display_color = display_color[1]
        else:
            display_color = "White (default)"
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
            graphic_mode = to_boolean(graphic_mode[1].strip())
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
        if "gui_theme" in config_lines[12].lower():
            gui_theme = config_lines[12].split(" = ")
            gui_theme = gui_theme[1].strip().capitalize()
        else:
            gui_theme = "Default"
        if "translation" in config_lines[13].lower():
            translation = config_lines[13].split(" = ")
            translation = to_boolean(translation[1].strip())
        else:
            translation = False
        if "override_port" in config_lines[15].lower():
            override_port = config_lines[15].split(" = ")
            override_port = override_port[1].strip()
        else:
            override_port = 15753
        if translation:
            if "lang" in config_lines[14].lower():
                lang = config_lines[14].split(" = ")[1].strip()
                if len(lang) > 3:
                    region_code = parse_region(lang, order=1)
                else:
                    region_code = lang
                    lang = parse_region(lang, order=0).capitalize()
            else:
                lang, region_code = "English", "en"
        else:
            lang, region_code = "English", "en"
        if graphic_mode:
            if custom_scheme:
                layout = [[gui.Text(f"{gui_translate('1. Debug mode:')} {debug_mode}")], [gui.Text(f"{gui_translate('2. Display initiate:')} {display_initiate}")], [gui.Text(f"{gui_translate('3. Print Speed:')} {printing_speed}")], [gui.Text(f"{gui_translate('4. Enable custom color scheme:')} {custom_scheme}")], [gui.Text(f"{gui_translate('5. Custom color:')} {display_color}")], [gui.Text(f"{gui_translate('6. Conversation mode:')} {conversation_mode}")], [gui.Text(f"{gui_translate('7. Graphic mode:')} {graphic_mode}")], [gui.Text(f"{gui_translate('8. Privacy mode:')} {private_mode}")], [gui.Text(f"{gui_translate('9. Auto code:')} {auto_code}")], [
                    gui.Text(f"{gui_translate('10. Voice Message Duration:')} {voice_record_time}")], [gui.Text(f"{gui_translate('11. GUI Theme:')} {gui_theme}")], [gui.Text(f"{gui_translate('12. Translation:')} {translation}")], [gui.Text(f"{gui_translate('13. Region:')} {lang}")], [gui.Text(f"{gui_translate('14. Override Port:')} {override_port}")], [gui.Text(gui_translate("15. Create new user..."))], [gui.Text(gui_translate("Which setting would you like to modify")), gui.InputText(key="choice"), gui.Button(gui_translate("Select"), key="Select", bind_return_key=True)], [gui.Button(gui_translate("Return to Main Menu"), key="Return")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            else:
                layout = [[gui.Text(f"{gui_translate('1. Debug mode:')} {debug_mode}")], [gui.Text(f"{gui_translate('2. Display initiate:')} {display_initiate}")], [gui.Text(f"{gui_translate('3. Print Speed:')} {printing_speed}")], [gui.Text(f"{gui_translate('4. Enable custom color scheme:')} {custom_scheme}")], [gui.Text(f"{gui_translate('5. Conversation mode:')} {conversation_mode}")], [gui.Text(f"{gui_translate('6. Graphic mode:')} {graphic_mode}")], [
                    gui.Text(f"{gui_translate('7. Privacy mode:')} {private_mode}")], [gui.Text(f"{gui_translate('8. Auto code:')} {auto_code}")], [gui.Text(f"{gui_translate('9. Voice Message Duration:')} {voice_record_time}")], [gui.Text(f"{gui_translate('10. GUI Theme:')} {gui_theme}")], [gui.Text(f"{gui_translate('11. Translation:')} {translation}")], [gui.Text(f"{gui_translate('12. Region:')} {lang}")], [gui.Text(f"{gui_translate('13. Override Port:')} {override_port}")], [gui.Text(gui_translate("14. Create new user..."))], [gui.Text(gui_translate("Which setting would you like to modify")), gui.InputText(key="choice"), gui.Button(gui_translate("Select"), key="Select", bind_return_key=True)], [gui.Button(gui_translate("Return to Main Menu"), key="Return")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Config Settings (Logged in as: {get_current_user()})"), layout=layout,
                                margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Select":
                choice = values.get("choice", "").strip()
                if choice == "":
                    choice = None
            elif event == "Return":
                if custom_scheme:
                    choice = "16"
                else:
                    choice = "15"
            window.close()
        else:
            animated_print(
                f"1. Debug mode: {debug_mode}", speed=master_printing_speed)
            animated_print(
                f"2. Display initiate: {display_initiate}", speed=master_printing_speed)
            animated_print(
                f"3. Print speed: {printing_speed}", speed=master_printing_speed)
            animated_print(
                f"4. Enable custom color scheme: {custom_scheme}", speed=master_printing_speed)
            if custom_scheme:
                animated_print(
                    f"5. Custom color: {display_color}", speed=master_printing_speed)
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
                animated_print(f"11. GUI Theme: {gui_theme}", speed=master_printing_speed)
                animated_print(f"12. Translation: {translation}", speed=master_printing_speed)
                animated_print(f"13. Region: {lang}", speed=master_printing_speed)
                animated_print(f"14. Override Port: {override_port}", speed=master_printing_speed)
                animated_print(f"15. Create new user...", speed=master_printing_speed)
                animated_print(f"16. Return to main menu", speed=master_printing_speed)
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
                animated_print(f"10. GUI Theme: {gui_theme}", speed=master_printing_speed)
                animated_print(f"11. Translation: {translation}", speed=master_printing_speed)
                animated_print(f"12. Region: {lang}", speed=master_printing_speed)
                animated_print(f"13. Override Port: {override_port}", speed=master_printing_speed)
                animated_print(f"14. Create new user...", speed=master_printing_speed)
                animated_print(f"15. Return to main menu", speed=master_printing_speed)
            choice = privacy_input(
                f"What setting would you like to modify", private_mode)
        if choice == None:
            menu(user, None, print_logs, default_color,
                 private_mode, error_color, print_speed=0)
        elif choice == "1":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="debug_mode")],
                          [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Debug Mode (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Update":
                    debug_mode = values.get("debug_mode", False)
                window.close()
            else:
                debug_mode = privacy_input(f"True/False", private_mode)
            config_lines[2] = f"debug_mode = {to_boolean(debug_mode)}"
        elif choice == "2":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="display_initiate")],
                          [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Display Initiate (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Update":
                    display_initiate = values.get("display_initiate", False)
                window.close()
            else:
                display_initiate = privacy_input(f"True/False", private_mode)
            config_lines[3] = f"display_initiate = {to_boolean(display_initiate)}"
        elif choice == "3":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("Enter Print Speed")), gui.InputText(key="print_speed")],
                          [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Print Speed (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Update":
                    new_print_speed = values.get("print_speed", 0.3)
                window.close()
            else:
                new_print_speed = privacy_input(
                    f"Enter print speed", private_mode)
            config_lines[4] = f"printing_speed = {float(str(new_print_speed).strip())}"
        elif choice == "4":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="custom_scheme")],
                          [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Custom Color Scheme (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Update":
                    true_false = values.get("custom_scheme", False)
                window.close()
            else:
                true_false = privacy_input(f"True/False", private_mode)
            config_lines[6] = f"custom_scheme = {to_boolean(true_false)}"
        elif choice == "5":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter Color")), gui.InputText(key="new_color")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Update Color (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        new_color = values.get("new_color", False)
                    window.close()
                    gui.Popup(gui_translate("Program restart will be required for color change!"),
                              title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                else:
                    new_color = privacy_input(
                        f"Enter color (in plain text)", private_mode)
                    animated_print(
                        f"WARNING: Program restart will be required for color change!", error=True, reset=True)
                    Colors(default_color)
                config_lines[5] = f"default_color = {new_color}"
            elif conversation_mode or not conversation_mode:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="conversation_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        conversation_mode = values.get("conversation_mode", False)
                    window.close()
                else:
                    conversation_mode = privacy_input(
                        f"True/False", private_mode)
                config_lines[7] = f"conversation_mode = {to_boolean(conversation_mode)}"
        elif choice == "6":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="conversation_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Conversation Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        conversation_mode = values.get("conversation_mode", False)
                    window.close()
                else:
                    conversation_mode = privacy_input(
                        f"True/False", private_mode)
                config_lines[7] = f"conversation_mode = {to_boolean(conversation_mode)}"
            else:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="graphic_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Graphic Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        graphic_mode = values.get("graphic_mode", False)
                    window.close()
                else:
                    graphic_mode = privacy_input(f"True/False", private_mode)
                config_lines[8] = f"graphic_mode = {to_boolean(graphic_mode)}"
        elif choice == "7":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="graphic_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Graphic Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        graphic_mode = values.get("graphic_mode", False)
                    window.close()
                else:
                    graphic_mode = privacy_input(f"True/False", private_mode)
                config_lines[8] = f"graphic_mode = {to_boolean(graphic_mode)}"
            else:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="private_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Private Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        private_mode = values.get("private_mode", False)
                    window.close()
                    gui.Popup(gui_translate("Program restart will be required for privacy mode change!"),
                              title=gui_translate("Warning"), text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    private_mode = privacy_input(f"True/False", private_mode)
                    animated_print(
                        f"WARNING: Program restart will be required for privacy mode change!", error=True, reset=True)
                    Colors(default_color)
                config_lines[9] = f"private_mode = {to_boolean(private_mode)}"
        elif choice == "8":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="private_mode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Private Mode (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        private_mode = values.get("private_mode", False)
                    window.close()
                    gui.Popup(gui_translate("Program restart will be required for privacy mode change!"),
                              title=gui_translate("Warning"), text_color="red", auto_close=True, auto_close_duration=5)
                else:
                    private_mode = privacy_input(f"True/False", private_mode)
                    animated_print(
                        f"WARNING: Program restart will be required for privacy mode change!", error=True, reset=True)
                    Colors(default_color)
                config_lines[9] = f"private_mode = {to_boolean(private_mode)}"
            else:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="autocode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Auto Code (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        autocode = values.get("autocode", False)
                    window.close()
                else:
                    auto_code = privacy_input(f"True/False", private_mode)
                config_lines[10] = f"auto_code = {to_boolean(auto_code)}"
        elif choice == "9":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="autocode")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Auto Code (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        autocode = values.get("autocode", False)
                    window.close()
                else:
                    auto_code = privacy_input(f"True/False", private_mode)
                config_lines[10] = f"auto_code = {to_boolean(auto_code)}"
            else:
                valid_value = False
                while not valid_value:
                    try:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Voice message duration")), gui.InputText(key="voice_time")],
                                      [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Voice Message Duration (Logged in as: {get_current_user()})"), layout=layout,
                                                margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Update":
                                voice_record_time = values.get("voice_time", "15s").strip()
                            window.close()
                        else:
                            voice_record_time = privacy_input(
                                f"Voice message duration", private_mode).strip()
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
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Voice message duration")), gui.InputText(key="voice_time")],
                                      [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Voice Message Duration (Logged in as: {get_current_user()})"), layout=layout,
                                                margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Update":
                                voice_record_time = values.get("voice_time", "15s").strip()
                            window.close()
                        else:
                            voice_record_time = privacy_input(
                                f"Voice message duration", private_mode).strip()
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
                gui.theme_previewer()
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter GUI Theme")), gui.InputText(key="new_theme")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Update GUI Theme (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        gui_theme = values.get("new_theme", False)
                    window.close()
                    apply_theme(gui_theme)
                else:
                    gui_theme = privacy_input(
                        f"Enter new theme name", private_mode)
                config_lines[12] = f"gui_theme = {gui_theme}"
        elif choice == "11":
            gui.theme_previewer()
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter GUI Theme")), gui.InputText(key="new_theme")],
                              [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Update GUI Theme (Logged in as: {get_current_user()})"), layout=layout,
                                        margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        gui_theme = values.get("new_theme", "default")
                    window.close()
                    apply_theme(gui_theme)
                else:
                    gui_theme = privacy_input(
                        f"Enter new theme name", private_mode)
                config_lines[12] = f"gui_theme = {gui_theme}"
            else:
                old_translate = translation
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False", status=old_translate)), gui.InputText(key="translate")], [gui.Button(gui_translate("Update", status=old_translate), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Enable Translation (Logged in as: {get_current_user()})", status=old_translate), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        translation = values.get("translate", False)
                    window.close()
                else:
                    translation = to_boolean(privacy_input(f"True/False", private_mode))
                if translation and "supress_translate_warning" not in config_lines:
                    if graphic_mode:
                        layout = [[gui.Text("*** WARNING ***", text_color="red", font="Courier 30")], [gui.Text(gui_translate("Enabling translate will expose sensitive data, including private messages,\nto data harvesting on the part of the relevant services. Please disable translation if you take issue with this.", status=old_translate))], [gui.Button(gui_translate("Accept", status=old_translate)), gui.Button(gui_translate("Decline", status=old_translate))], [gui.Checkbox(gui_translate("Supress future warnings (Ignored if declined)", status=old_translate), key="supress_translate_warning")], [gui.Checkbox(gui_translate("Do not translate private messages", status=old_translate), key="no_translate_pm")]]
                        temp_popup = gui.Window(title=f"FiEncrypt - Enable Translation (Logged in as: {get_current_user()})", layout=layout, font="Courier 20")
                        while True:
                            event, values = temp_popup.read()
                            if event == "Accept":
                                supress_translate_warning, no_translate_pm = values.get("supress_translate_warning", False), values.get("no_translate_pm", False)
                                break
                            elif event == "Decline":
                                supress_translate_warning, no_translate_pm = False, False
                                break
                        temp_popup.close()
                        if to_boolean(supress_translate_warning) and translation:
                            if "supress_translate_warning" not in config_lines:
                                config_lines.append("supress_translate_warning")
                            if not supress_translate_warning:
                                translation = False
                        if to_boolean(no_translate_pm) and translation:
                            if "no_translate_pm" not in config_lines:
                                config_lines.append("no_translate_pm")
                            if not supress_translate_warning:
                                translation = False
                    else:
                        animated_print("WARNING: Enabling translate will expose sensitive data, including private messages,\nto data harvesting on the part of the relevant services.\nPlease disable translation if you take issue with this.", error=True, reset=True, speed=printing_speed)
                        config_lines.append("supress_translate_warning")
                        message_translate_override = privacy_input("Disable translation of private messages? [Y|N]", private_mode)
                        if "y" in message_translate_override.lower() and "no_translate_pm" not in config_lines:
                            config_lines.append("no_translate_pm")
                        elif "y" in message_translate_override.lower():
                            animated_print("Private message translation already disabled!")
                config_lines[13] = f"translation = {to_boolean(translation)}"
                if to_boolean(translation):
                    TranslationManager = Translate(region_code)
                    if not graphic_mode:
                        animated_print("WARNING: Restarting FiEncrypt to apply language change!", error=True, reset=True)
                        initiate()
        elif choice == "12":
            if custom_scheme:
                old_translate = translation
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("True/False", status=old_translate)), gui.InputText(key="translate")], [gui.Button(gui_translate("Update", status=old_translate), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Enable Translation (Logged in as: {get_current_user()})", status=old_translate), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        translation = values.get("translate", False)
                    window.close()
                else:
                    translation = to_boolean(privacy_input(f"True/False", private_mode))
                if translation and "supress_translate_warning" not in config_lines:
                    if graphic_mode:
                        layout = [[gui.Text("*** WARNING ***", text_color="red", font="Courier 30")], [gui.Text(gui_translate("Enabling translate will expose sensitive data, including private messages,\nto data harvesting on the part of the relevant services. Please disable translation if you take issue with this.", status=old_translate))], [gui.Button(gui_translate("Accept", status=old_translate)), gui.Button(gui_translate("Decline", status=old_translate))], [gui.Checkbox(gui_translate("Supress future warnings (Ignored if declined)", status=old_translate), key="supress_translate_warning")], [gui.Checkbox(gui_translate("Do not translate private messages", status=old_translate), key="no_translate_pm")]]
                        temp_popup = gui.Window(title=f"FiEncrypt - Enable Translation (Logged in as: {get_current_user()})", layout=layout, font="Courier 20")
                        while True:
                            event, values = temp_popup.read()
                            if event == "Accept":
                                supress_translate_warning, no_translate_pm = values.get("supress_translate_warning", False), values.get("no_translate_pm", False)
                                break
                            elif event == "Decline":
                                supress_translate_warning, no_translate_pm = False, False
                                break
                        temp_popup.close()
                        if to_boolean(supress_translate_warning) and translation:
                            if "supress_translate_warning" not in config_lines:
                                config_lines.append("supress_translate_warning")
                            if not supress_translate_warning:
                                translation = False
                        if to_boolean(no_translate_pm) and translation:
                            if "no_translate_pm" not in config_lines:
                                config_lines.append("no_translate_pm")
                            if not supress_translate_warning:
                                translation = False
                    else:
                        animated_print("WARNING: Enabling translate will expose sensitive data, including private messages,\nto data harvesting on the part of the relevant services.\nPlease disable translation if you take issue with this.", error=True, reset=True, speed=printing_speed)
                        config_lines.append("supress_translate_warning")
                        message_translate_override = privacy_input("Disable translation of private messages? [Y|N]", private_mode)
                        if "y" in message_translate_override.lower() and "no_translate_pm" not in config_lines:
                            config_lines.append("no_translate_pm")
                        elif "y" in message_translate_override.lower():
                            animated_print("Private message translation already disabled!")
                config_lines[13] = f"translation = {to_boolean(translation)}"
                if to_boolean(translation):
                    TranslationManager = Translate(region_code)
                    if not graphic_mode:
                        animated_print("WARNING: Restarting FiEncrypt to apply language change!", error=True, reset=True)
                        initiate()
            else:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter Region Code or Language")), gui.InputText(key="region_code")], [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Set Language (Logged in as: {get_current_user()})"), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        lang = values.get("region_code", "en")
                        if len(lang.strip()) > 3:
                            cfg_lang = parse_region(lang, order=1)
                        else:
                            cfg_lang = lang
                    window.close()
                else:
                    lang = privacy_input("Enter Region Code or Language", private_mode)
                    if len(lang.strip()) > 3:
                        cfg_lang = parse_region(lang, order=1)
                    else:
                        cfg_lang = lang
                config_lines[14] = f"lang = {cfg_lang}"
                TranslationManager = Translate(lang)
                lang = parse_region(lang, order=0)
        elif choice == "13":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter Region Code or Language")), gui.InputText(key="region_code")], [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Set Language (Logged in as: {get_current_user()})"), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        lang = values.get("region_code", "en")
                        if len(lang.strip()) > 3:
                            cfg_lang = parse_region(lang, order=1)
                        else:
                            cfg_lang = lang
                    window.close()
                else:
                    lang = privacy_input("Enter Region Code or Language", private_mode)
                    if len(lang.strip()) > 3:
                        cfg_lang = parse_region(lang, order=1)
                    else:
                        cfg_lang = lang
                config_lines[14] = f"lang = {cfg_lang}"
                TranslationManager = Translate(lang)
                lang = parse_region(lang, order=0)
            else:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter Override Port")), gui.InputText(key="override_port")], [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Set Override Port (Logged in as: {get_current_user()})"), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        override_port = values.get("override_port", 15753)
                    window.close()
                else:
                    override_port = privacy_input("Enter Override Port", private_mode)
                config_lines[15] = f"override_port = {int(str(override_port).strip())}"
        elif choice == "14":
            if custom_scheme:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter Override Port")), gui.InputText(key="override_port")], [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [
                        gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(
                        title=gui_translate(f"FiEncrypt - Set Override Port (Logged in as: {get_current_user()})"), layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        override_port = values.get("override_port", 15753)
                    window.close()
                else:
                    override_port = privacy_input("Enter Override Port", private_mode).strip()
                config_lines[15] = f"override_port = {int(str(override_port).strip())}"
            else:
                add_new_user()
        elif choice == "15":
            if custom_scheme:
                add_new_user()
            else:
                menu(user, display_initiate, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        elif choice == "16":
            if custom_scheme:
                menu(user, display_initiate, print_logs, default_color,
                     private_mode, error_color, print_speed=0)
        config_file.close()
        os.remove(f"./config.txt")
        with open("./config.txt", "w+") as config_file:
            for line in config_lines:
                if line.strip() != "" and line != "-":
                    line = f"{line}\n"
                config_file.write(line)
        master_printing_speed = 0


def cache_settings(user, current_user, default_color, print_logs, private_mode, error_color, **kwargs):
    """Allows user to modify cache_settings.txt in a similar fashion to @config_settings"""
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
        if graphic_mode:
            layout = [[gui.Text(f"{gui_translate('1. Auto Sync:')} {autosync}")], [gui.Text(f"{gui_translate('2. Max Personal Cache Size:')} {max_size}")], [gui.Text(gui_translate("Select option to modify")), gui.InputText(key="cache_setting")], [
                gui.Button(gui_translate("Edit"), key="Edit", bind_return_key=True), gui.Button(gui_translate("Return to Cache Menu"), key="Return")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
            window = gui.Window(title=gui_translate(f"FiEncrypt - Cache Settings (Logged in as: {get_current_user()})"), layout=layout,
                                margins=(100, 50), font="Courier 20")
            event, values = window.read()
            if event == "Edit":
                choice = values.get("cache_setting", None)
            elif event == "Return":
                choice = "3"
            window.close()
        else:
            animated_print(f"1. Auto Sync: {autosync}")
            animated_print(f"2. Max Personal Cache Size: {max_size}")
            animated_print(f"3. Return to Cache Menu")
            choice = privacy_input(f"What setting would you like to modify", private_mode)
        if choice == None:
            escape = True
        elif choice == "1":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("True/False")), gui.InputText(key="autosync")],
                          [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Autosync (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Update":
                    autosync = values.get("autosync", False)
                window.close()
            else:
                autosync = privacy_input(f"True/False", private_mode)
            old_cache_settings[2] = f"auto-sync = {to_boolean(autosync)}"
        elif choice == "2":
            valid_size = False
            while not valid_size:
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("Enter size in MB or GB")), gui.InputText(
                        key="max_size")], [gui.Button(gui_translate("Update"), key="Update", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Personal Cache Size (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Update":
                        max_size = values.get("max_size", "2GB")
                    window.close()
                else:
                    max_size = privacy_input(f"Enter size in MB or GB", private_mode)
                if not max_size.strip().lower().endswith("mb") and not max_size.strip().lower().endswith("gb"):
                    if len(max_size.strip()) <= 2 or "." in max_size.strip():
                        assumed_type = "GB"
                    else:
                        assumed_type = "MB"
                    if graphic_mode:
                        gui.Popup(gui_translate(
                            f"Data unit not declared... assuming {assumed_type}"), title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    else:
                        animated_print(
                            f"WARNING: Data unit not declared... assuming {assumed_type}", error=True, reset=True)
                        Colors(default_color)
                    try:
                        if "." in max_size or assumed_type == "gb":
                            max_size = float(max_size.strip())
                        else:
                            max_size = int(max_size.strip())
                        valid_size = True
                        old_cache_settings[3] = f"max_size = {max_size}{assumed_type.upper()}"
                    except:
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid personal cache size!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: Invalid personal cache size!",
                                           error=True, reset=True)
                            Colors(default_color)
                else:
                    if max_size.strip().lower().endswith("gb"):
                        requested_size = substring(max_size.lower(), "gb", 0)
                        unit = substring(max_size.lower(), "gb", 1)
                    elif max_size.strip().lower().endswith("mb"):
                        requested_size = substring(max_size.lower(), "mb", 0)
                        unit = substring(max_size.lower(), "mb", 1)
                    else:
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid data unit... assuming MB"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(
                                f"WARNING: Invalid data unit... assuming MB", error=True, reset=True)
                            Colors(default_color)
                        unit = "mb"
                    try:
                        if "." in requested_size or unit == "gb":
                            requested_size = float(requested_size.strip())
                        else:
                            requested_size = int(requested_size.strip())
                        valid_size = True
                        old_cache_settings[3] = f"max_size = {requested_size}{unit.upper()}"
                    except:
                        if graphic_mode:
                            gui.Popup(gui_translate("Invalid personal cache size!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(f"WARNING: Invalid personal cache size!",
                                           error=True, reset=True)
                            Colors(default_color)
        elif choice == "3":
            escape = True
        else:
            if graphic_mode:
                gui.Popup(gui_translate("Invalid Option!"), title=gui_translate(
                    "Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Invalid option!", error=True, reset=True)
                Colors(default_color)
        with open(f"./cache_settings.txt", "w+") as new_cache_file:
            for line in old_cache_settings:
                line = line.replace("\n", "").strip()
                new_cache_file.write(f"{line}\n")
        log("Cache settings updated!", "fileManager", get_current_user(), None)


def manage_cache(user, current_user, default_color, print_logs, private_mode, error_color, **kwargs):
    """Allows user to directly interface with the cache directory and the data within"""
    enter_home_directory()
    straight_to_menu, old_files = kwargs.get("menu", False), kwargs.get("files", None)
    os.chdir(f"./cache")
    if len([filenum for filenum in os.listdir(".")]) > 0:
        if not straight_to_menu:
            if not graphic_mode:
                animated_print("Dumping cache...")
        for root, dirs, files in os.walk("./cache", topdown=False):
            if not straight_to_menu:
                if graphic_mode:
                    temp_files = str(files).replace(
                        "[", "").replace("]", "").replace("'", "").strip()
                    gui.Popup(temp_files.replace(",", "\n"),
                              title=gui_translate(f"FiEncrypt - Public Cache (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(files)
        enter_home_directory()
        if len([filenum for filenum in os.listdir(f"./{hash_value(get_current_user().lower().strip())}/files")]) > 0:
            menu_state = ["", "", "", "", "", ""]
        else:
            if not straight_to_menu:
                if graphic_mode:
                    gui.Popup(gui_translate("Private cache is empty!"), title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    menu_state = ["", "", "", "*Unavailable* ", "*Unavailable* ", ""]
                else:
                    animated_print(f"WARNING: Private cache is empty!", error=True, reset=True)
                    Colors(default_color)
                    menu_state = ["", "", "", "\033[9m", "\033[9m", ""]
    else:
        files = None
        enter_home_directory()
        if len([filenum for filenum in os.listdir(f"./{hash_value(get_current_user().lower().strip())}/files")]) > 0:
            if not straight_to_menu:
                if graphic_mode:
                    gui.Popup(gui_translate("Public cache is empty!"), title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    menu_state = ["*Unavailable* ", "*Unavailable* ", "*Unavailable* ", "", "", ""]
                else:
                    animated_print(f"WARNING: Public cache is empty!", error=True, reset=True)
                    Colors(default_color)
                    menu_state = ["\033[9m", "\033[9m", "\033[9m", "", "", ""]
        else:
            if not straight_to_menu:
                if graphic_mode:
                    gui.Popup(gui_translate("Private and Public caches are empty!"),
                              title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    menu_state = ["*Unavailable* ", "*Unavailable* ",
                                  "*Unavailable* ", "*Unavailable* ", "*Unavailable* ", ""]
                else:
                    animated_print(f"WARNING: Public and Private caches are empty!",
                                   error=True, reset=True)
                    Colors(default_color)
                    menu_state = ["\033[9m", "\033[9m", "\033[9m", "\033[9m", "\033[9m", ""]
    if graphic_mode:
        layout = [[gui.Text(gui_translate(f"{menu_state[0]}1. Archive public cache"))], [gui.Text(gui_translate(f"{menu_state[1]}2. Delete from public cache"))], [gui.Text(gui_translate(f"{menu_state[2]}3. Empty public cache"))], [gui.Text(gui_translate(f"{menu_state[3]}4. View private cache"))], [
            gui.Text(gui_translate(f"{menu_state[4]}5. Empty private cache"))], [gui.Text(gui_translate(f"{menu_state[5]}6. Cache settings"))], [gui.Text(gui_translate("Select an option")), gui.InputText(key="cache_option"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Button(gui_translate("Return to Main Menu"), key="Return")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
        window = gui.Window(title=gui_translate(f"FiEncrypt - Cache manager (Logged in as: {get_current_user()})"), layout=layout,
                            margins=(100, 50), font="Courier 20")
    else:
        animated_print(f"{menu_state[0]}1. Archive public cache\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"{menu_state[1]}2. Delete from public cache\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"{menu_state[2]}3. Empty public cache\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"{menu_state[3]}4. View private cache\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"{menu_state[4]}5. Empty private cache\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"{menu_state[5]}6. Cache settings\033[0m", speed=0.01)
        Colors(default_color)
        animated_print(f"7. Return to main menu", speed=0.01)
    valid_choice = False
    while not valid_choice:
        if graphic_mode:
            event, values = window.read()
            if event == "Launch!":
                cache_option = values.get("cache_option", "").strip()
            elif event == "Return":
                cache_option = 7
            window.close()
        else:
            cache_option = privacy_input("Select an option", private_mode)
        try:
            cache_option = int(cache_option)
            valid_choice = True
        except:
            if graphic_mode:
                gui.Popup(gui_translate("Invalid Selection!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            animated_print(f"WARNING: Invalid selection!", error=True, reset=True)
            Colors(default_color)
    if cache_option == 1:
        if menu_state[0].strip() == "":
            enter_home_directory()
            autosync, max_size = cache_settings(
                user, current_user, default_color, print_logs, private_mode, error_color, mode="read")
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
            for path, dirs, temp_files in os.walk(f"./{hash_value(get_current_user().lower().strip())}/files"):
                for temp_file in temp_files:
                    personal_cache_total_size += os.path.getsize(
                        f"./{hash_value(get_current_user().lower().strip())}/files/{temp_file}")
            os.chdir(f"./{hash_value(get_current_user().lower().strip())}/files")
            if pass_os == "win32":
                copy = "copy"
            else:
                copy = "cp"
                file = file.strip().replace(" ", "\ ").replace(
                    "'", "\\'").replace("(", "\\(").replace(")", "\\)")
            if (int(cache_total_size) + int(personal_cache_total_size)) > max_size:
                if graphic_mode:
                    gui.Popup(gui_translate(
                        "Size of files in public cache exceeds max allocated size of your private cache!"), title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(
                        f"WARNING: Size of files in public cache exceeds max allocated size of your private cache!", error=True, reset=True)
                    Colors(default_color)
            else:
                try:
                    for file in files:
                        if "voice_message.wav" not in file:
                            if pass_os() == "win32":
                                file = file.replace("/", "\\")
                                os.system(f"{copy} ..\\..\\cache\\{file} {file}")
                                file = file.replace("\\", "/")
                            else:
                                os.system(f"{copy} ../../cache/{file} {file}")
                except UnboundLocalError:
                    if old_files != None:
                        for file in old_files:
                            if "voice_message.wav" not in file:
                                if pass_os() == "win32":
                                    file = file.replace("/", "\\")
                                    os.system(f"{copy} ..\\..\\cache\\{file} {file}")
                                    file = file.replace("\\", "/")
                                else:
                                    os.system(f"{copy} ../../cache/{file} {file}")
                        files = old_files
                    else:
                        if graphic_mode:
                            gui.Popup(gui_translate("Files in public cache no longer accessible!"),
                                      title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
                            animated_print(
                                f"WARNING: Files in public cache no longer accessible!", error=True, reset=True)
                            Colors(default_color)
                        files = None
        else:
            if graphic_mode:
                gui.Popup(gui_translate("Option not available!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Option not available!", error=True, reset=True)
                Colors(default_color)
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
            if graphic_mode:
                gui.Popup(gui_translate("Option not available!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Option not available!", error=True, reset=True)
                Colors(default_color)
    elif cache_option == 3:
        if menu_state[2].strip() == "":
            if graphic_mode:
                layout = [[gui.Text(gui_translate("Delete public cache?"))], [
                    gui.Button(gui_translate("Confirm"), key="Confirm", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Empty Public Cache (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                events, values = window.read()
                if events == "Confirm":
                    confirm = "y"
                else:
                    confirm = "n"
                window.close()
            else:
                confirm = privacy_input(f"Are you sure? [Y|N]", private_mode)
            if "y" in confirm.lower():
                clear_cache()
            else:
                pass
        else:
            if graphic_mode:
                gui.Popup(gui_translate("Option not available!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Option not available!", error=True, reset=True)
                Colors(default_color)
    elif cache_option == 4:
        if menu_state[3].strip() == "":
            enter_home_directory()
            if graphic_mode:
                username, password = "", ""
                while username == None or username.strip() == "" or password == None or password.strip() == "":
                    layout = [[gui.Text(gui_translate("Please confirm your login"))], [gui.Text(gui_translate("Username")), gui.InputText(
                        key="username")], [gui.Text(gui_translate("Password")), gui.InputText(key="password", password_char="*")], [gui.Button(gui_translate("Login"), key="Login", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate("FiEncrypt - Login Confirmation"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Login":
                        username = values.get("username", None)
                        password = values.get("password", None)
                        if username == None or username.strip() == "":
                            gui.Popup(gui_translate("Username cannot be blank!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        elif password == None or password.strip() == "":
                            gui.Popup(gui_translate("Password cannot be blank!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    window.close()
            else:
                animated_print(f"Please confirm your login: ")
                username = privacy_input("Username", private_mode)
                password = privacy_input("Password", 1)
            valid = validate_login(username, password)
            current_valid = username.lower().strip() == get_current_user().lower().strip()
            if valid and current_valid:
                os.chdir(f"./{hash_value(username.lower().strip())}/files")
                for root, dirs, files in os.walk("./", topdown=False):
                    if not graphic_mode:
                        for file in files:
                            animated_print(file)
                    else:
                        temp_files = str(files).replace(
                            "[", "").replace("]", "").replace("'", "").strip()
                        gui.Popup(temp_files.replace(",", "\n"),
                                  title=gui_translate(f"FiEncrypt - Private Cache (Logged in as: {get_current_user()})"), font="Courier 20", auto_close=True, auto_close_duration=5)
            else:
                if graphic_mode:
                    gui.Popup(gui_translate("Access Denied!"), title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(f"WARNING: Access Denied!", error=True, reset=True)
                    Colors(default_color)
        else:
            if graphic_mode:
                gui.Popup(gui_translate("Option not available!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Option not available!", error=True, reset=True)
                Colors(default_color)
    elif cache_option == 5:
        if menu_state[4].strip() == "":
            enter_home_directory()
            if graphic_mode:
                username, password = "", ""
                while username == None or username.strip() == "" or password == None or password.strip() == "":
                    layout = [[gui.Text(gui_translate("Please confirm your login"))], [gui.Text(gui_translate("Username")), gui.InputText(
                        key="username")], [gui.Text(gui_translate("Password")), gui.InputText(key="password", password_char="*")], [gui.Button(gui_translate("Login"), key="Login", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate("FiEncrypt - Login Confirmation"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                    event, values = window.read()
                    if event == "Login":
                        username = values.get("username", None)
                        password = values.get("password", None)
                        if username == None or username.strip() == "":
                            gui.Popup(gui_translate("Username cannot be blank!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                        elif password == None or password.strip() == "":
                            gui.Popup(gui_translate("Password cannot be blank!"), title=gui_translate("Warning"),
                                      text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    window.close()
            else:
                animated_print(f"Please confirm your login: ")
                username = privacy_input("Username", private_mode)
                password = privacy_input("Password", 1)
            valid = validate_login(username, password)
            current_valid = username.lower().strip() == get_current_user().lower().strip()
            if valid and current_valid:
                os.chdir(f"./{hash_value(username.lower().strip())}")
                shutil.rmtree("./files")
                os.mkdir("./files")
            else:
                if graphic_mode:
                    gui.Popup(gui_translate("Access Denied!"), title=gui_translate("Warning"),
                              text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                else:
                    animated_print(f"WARNING: Access Denied!", error=True, reset=True)
                    Colors(default_color)
        else:
            if graphic_mode:
                gui.Popup(gui_translate("Option not available!"), title=gui_translate("Warning"),
                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"WARNING: Option not available!", error=True, reset=True)
                Colors(default_color)
    elif cache_option == 6:
        if menu_state[5].strip() == "":
            enter_home_directory()
            cache_settings(user, current_user, default_color, print_logs,
                           private_mode, error_color, mode="edit")
    elif cache_option == 7:
        print("")
        menu(user, False, print_logs, default_color,
             private_mode, error_color, print_speed=0)
    else:
        pass
    print("")
    enter_home_directory()
    os.chdir(f"./cache")
    if len([filenum for filenum in os.listdir(f"../{hash_value(get_current_user().lower().strip())}/files")]) == 0 or len([filenum for filenum in os.listdir(".")]) == 0:
        manage_cache(user, current_user, default_color, print_logs,
                     private_mode, error_color, files=files)
    else:
        manage_cache(user, current_user, default_color, print_logs,
                     private_mode, error_color, menu=True, files=files)


def assisted_menu():
    """Attains all necessary variables to execute @menu indepent of @initiate and what not"""
    home_directory, operating_system, user = enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, color_enabled, default_color, auto_code, voice_record_time, gui_theme, translation, lang, override_port = retrieve_config_settings()
    error_color = "\033[91m"
    menu(user, display_initiate, print_logs, default_color, private_mode, error_color)


def menu(user, display_initiate, print_logs, default_color, private_mode, error_color, **print_speed):
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
    if graphic_mode:
        pass
    else:
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
            if graphic_mode:
                if display_initiate:
                    layout = [[gui.Text(gui_translate("1. Encrypt New Message"))], [gui.Text(gui_translate("2. Decrypt Message"))], [gui.Text(gui_translate("3. Show Current Code"))], [gui.Text(gui_translate("4. Request Random Code"))], [gui.Text(gui_translate("5. Initiate Filesystem"))], [gui.Text(gui_translate("6. Encryption Helper"))], [gui.Text(gui_translate("7. Secret Code"))], [gui.Text(gui_translate("8. Open Inbound Server"))], [
                        gui.Text(gui_translate("9. Invite to Conversation"))], [gui.Text(gui_translate("10. Check Mailbox"))], [gui.Text(gui_translate("11. Manage Contacts"))], [gui.Text(gui_translate("12. Config Settings"))], [gui.Text(gui_translate("13. Manage Cache"))], [gui.Text(gui_translate("Select one of these functions")), gui.InputText(key="func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Button(gui_translate("Reload"), key="Reload"), gui.Button(gui_translate("Quit"), key="Quit")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                else:
                    layout = [[gui.Text(gui_translate("1. Encrypt New Message"))], [gui.Text(gui_translate("2. Decrypt Message"))], [gui.Text(gui_translate("3. Show Current Code"))], [gui.Text(gui_translate("4. Request Random Code"))], [gui.Text(gui_translate("5. Encryption Helper"))], [gui.Text(gui_translate("6. Secret Code"))], [gui.Text(gui_translate("7. Open Inbound Server"))], [gui.Text(gui_translate("8. Invite to Conversation"))], [
                        gui.Text(gui_translate("9. Check Mailbox"))], [gui.Text(gui_translate("10. Manage Contacts"))], [gui.Text(gui_translate("11. Config Settings"))], [gui.Text(gui_translate("12. Manage Cache"))], [gui.Text(gui_translate("Select one of these functions")), gui.InputText(key="func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Button(gui_translate("Reload"), key="Reload"), gui.Button(gui_translate("Quit"), key="Quit")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title=gui_translate(f"FiEncrypt - Main Menu (Logged in as: {get_current_user()})"), layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Launch!":
                    func = values.get("func", 0)
                elif event == "Quit":
                    if display_initiate:
                        func = 15
                    else:
                        func = 14
                elif event == "Reload":
                    if display_initiate:
                        func = 14
                    else:
                        func = 13
                window.close()
            else:
                func = privacy_input(f"Select one of these functions", private_mode)
        except KeyboardInterrupt:
            print("")
            maybe_quit()
            Colors(default_color)
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
                user, capitalize_user(get_current_user()), False, private_mode, print_logs, default_color, error_color)
            try:
                backup_code = code
            except:
                pass
        elif func == 1:
            # ?Sometimes @backup_code is not defined, and if it is, @showcode() module will be called, returning the @code to be used for the module being called
            try:
                newmessage(code, user, recipient_ip, None, prefix, None,
                           talking_to_self, error_color, default_color, private_mode, print_logs, mailing, display_initiate, auto_code)
            except UnboundLocalError:
                try:
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                except:
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_color, error_color, auto_code=True)
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                newmessage(code, user, recipient_ip, None, prefix, None,
                           talking_to_self, error_color, default_color, private_mode, print_logs, mailing, display_initiate, auto_code)
        elif func == 2:
            try:
                retrievemessage(backup_code, user, capitalize_user(get_current_user()), prefix, recipient_ip, None, timestamp,
                                None, talking_to_self, default_color, print_logs, private_mode, error_color, None, display_initiate)
            except UnboundLocalError:
                try:
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                except:
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_color, error_color, auto_code=True)
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                retrievemessage(code, user, capitalize_user(get_current_user()), prefix, recipient_ip, None, timestamp,
                                None, talking_to_self, default_color, print_logs, private_mode, error_color, None, display_initiate)
        elif func == 3:
            showcode(user, capitalize_user(get_current_user()), private_mode,
                     print_logs, error_color, default_color)
        # ?If display_initiate is set to true, the user will see this option, although it should only need to be run once
        elif func == 5:
            # *The same number will perform differently based on this condition
            if display_initiate:
                establish_tree()
            else:
                helper("all", get_current_user(), backup_user)
                func = 0
        elif func == 6:
            if display_initiate:
                helper("all", get_current_user(), backup_user)
                func = 0
            else:
                secretcode(user, capitalize_user(get_current_user()), default_color,
                           print_logs, private_mode, error_color)
        elif func == 7:
            if display_initiate:
                secretcode(user, capitalize_user(get_current_user()), default_color,
                           print_logs, private_mode, error_color)
            else:
                try:
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                except:
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_color, error_color, auto_code=True)
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                date = timestamp.split("|")
                date = date[1]
                server_recieve(user, code, capitalize_user(get_current_user()), None, recipient_ip, timestamp, prefix,
                               date, default_color, print_logs, private_mode, error_color, display_initiate)
        elif func == 8:
            if display_initiate:
                try:
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                except:
                    randomcode(user, current_user, True, private_mode,
                               print_logs, default_color, error_color, auto_code=True)
                    code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                       print_logs, error_color, default_color)
                date = timestamp.split("|")
                date = date[1]
                server_recieve(user, code, capitalize_user(get_current_user()), None, recipient_ip, timestamp, prefix,
                               date, default_color, print_logs, private_mode, error_color, display_initiate)
            else:
                send_conversation_invite(
                    user, capitalize_user(get_current_user()), default_color, private_mode, error_color, print_logs, display_initiate)
        elif func == 9:
            if display_initiate:
                send_conversation_invite(
                    user, capitalize_user(get_current_user()), default_color, private_mode, error_color, print_logs, display_initiate)
            else:
                try:
                    check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                                  error_color, default_color, display_initiate, print_logs, private_mode)
                except UnboundLocalError:
                    code, prefix, timestamp = showcode(user, 1, private_mode,
                                                       print_logs, error_color, default_color)
                    check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                                  error_color, default_color, display_initiate, print_logs, private_mode)
        elif func == 10:
            if display_initiate:
                check_mailbox(user, capitalize_user(get_current_user()), None, mailing, timestamp,
                              error_color, default_color, display_initiate, print_logs, private_mode)
            else:
                code, prefix, timestamp = showcode(capitalize_user(get_current_user()), 1, private_mode,
                                                   print_logs, error_color, default_color)
                contact_func = 0
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("1. Add Contact"))], [gui.Text(gui_translate("2. Remove Contact"))], [gui.Text(gui_translate("3. Search For Contact"))], [gui.Text(gui_translate("4. List All Contacts"))], [gui.Text(gui_translate("Select a function")), gui.InputText(
                        key="contact_func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Button(gui_translate("Return to Main Menu"), key="Return")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Contact Manager (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                else:
                    animated_print(f"Contact manager:")
                    animated_print(f"1. Add Contact")
                    animated_print(f"2. Remove Contact")
                    animated_print(f"3. Search For Contact")
                    animated_print(f"4. List All Contacts")
                    animated_print(f"5. Return To Main Menu")
                while contact_func not in range(1, 6):
                    try:
                        if graphic_mode:
                            event, values = window.read()
                            if event == "Launch!":
                                contact_func = values.get("contact_func", 0)
                            elif event == "Return":
                                contact_func = 5
                            window.close()
                        else:
                            contact_func = privacy_input(f"Select function", 0)
                    except KeyboardInterrupt:
                        print("")
                        menu(user, display_initiate, print_logs,
                             default_color, private_mode, error_color, print_speed=0)
                    try:
                        contact_func = int(contact_func)
                    except ValueError:
                        if contact_func == None:
                            menu(user, display_initiate, print_logs,
                                 default_color, private_mode, error_color, print_speed=0)
                        else:
                            contact_func = 0
                    contact_manager = Contacts(user, get_current_user().lower(
                    ).strip(), print_logs, default_color, error_color, private_mode)
                    agreed, temp_override_port = None, None
                    if contact_func == 1:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter contact name here")), gui.InputText(key="new_name")], [gui.Text(gui_translate("Enter MAC address here")), gui.InputText(
                                key="new_ip")], [gui.Text(gui_translate("Set agreed encryption code")), gui.Button(gui_translate("Yes"), key="yes"), gui.Button(gui_translate("No"), key="no"), gui.InputText(key="agreed_code")], [gui.Text(gui_translate("Set port for dedicated communication")), gui.InputText(key="override_port")], [gui.Text(gui_translate("Enter any additional details here")), gui.InputText(key="new_details")], [gui.Button(gui_translate("Save"), key="Save", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - New Contact (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            while True:
                                event, values = window.read()
                                if event == "no":
                                    agreed = "n"
                                elif event == "yes":
                                    agreed = "y"
                                elif event == "Cancel":
                                    func = 0
                                    break
                                    window.close()
                                    break
                                elif event == "Save":
                                    new_name, new_ip, new_details, set_code, temp_override_port = values.get("new_name", ""), values.get(
                                        "new_ip", ""), values.get("new_details", ""), values.get("agreed_code", None), values.get("override_port", None)
                                    if agreed == None:
                                        agreed = "n"
                                    break
                            window.close()
                        else:
                            new_name = privacy_input(
                                f"Enter contact name here", private_mode)
                            new_ip = privacy_input(
                                f"Enter MAC address here (or leave blank)", private_mode)
                            agreed = privacy_input(f"Do you want to store current code as agreed code? [Y|N]", private_mode)
                            if "y" in agreed.lower():
                                set_code = privacy_input(f"Set the agreed code (or leave blank to apply current code)", private_mode)
                                if set_code.strip() == "":
                                    set_code = None
                            else:
                                set_code = None
                            temp_override_port = privacy_input(f"Enter dedicated port for commuication", private_mode)
                            new_details = privacy_input(
                                f"Enter any additional details here", private_mode)
                        if temp_override_port != None and temp_override_port.strip() != "":
                            try:
                                temp_override_port = int(temp_override_port)
                            except:
                                temp_override_port = None
                        else:
                            temp_override_port = None
                        if "y" in agreed.lower() and (set_code != None and set_code.strip() != ""):
                            agreed_code = set_code.strip()
                        elif "y" in agreed.lower():
                            agreed_code = f"{timestamp}_{code}_{prefix}"
                        else:
                            agreed_code = None
                        if new_details.strip() == "" or new_details == None:
                            new_details = "\n"
                        if agreed_code != None:
                            if graphic_mode:
                                gui.Popup(f"The agreed code with {new_name} is {agreed_code}", title=f"FiEncrypt - Agreed Code (Logged in as {get_current_user()})", font="Courier 20")
                            else:
                                animated_print(f"The agreed code with {new_name} is {agreed_code}")
                        if new_name.strip() != "":
                            contact_manager.add(new_name, new_ip, agreed_code, new_details, temp_override_port)
                        else:
                            if graphic_mode:
                                gui.Popup(gui_translate("Contact name cannot be blank!"), title=gui_translate("Warning"),
                                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(
                                    f"WARNING: Contact name cannot be blank!", error=True, reset=True)
                                Colors(default_color)
                        contact_func = 0
                    elif contact_func == 2:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter name of contact to be removed")), gui.InputText(
                                key="target_name")], [gui.Button(gui_translate("Delete"), key="Delete", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate("FiEncrypt - Delete Contact"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Delete":
                                target_name = values.get("target_name", "")
                            window.close()
                        else:
                            target_name = privacy_input(
                                f"Enter name of contact to be removed", private_mode)
                        if target_name.strip() != "":
                            contact_manager.remove(target_name)
                        else:
                            if graphic_mode:
                                gui.Popup(gui_translate("Contact name cannot be blank!"), title=gui_translate("Warning"),
                                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(
                                    f"WARNING: Contact name cannot be blank!", error=True, reset=True)
                                Colors(default_color)
                        contact_func = 0
                    elif contact_func == 3:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter the contact name here")), gui.InputText(key="search")], [
                                gui.Button(gui_translate("Search"), key="Search", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate("FiEncrypt - Search for contact"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Search":
                                search = values.get("search", "")
                            window.close()
                        else:
                            search = privacy_input(
                                f"Enter the contact name here", private_mode)
                        result = contact_manager.check_for(search)
                        if graphic_mode:
                            if result != None:
                                result = str(result).replace("\\n", "").replace(
                                    "(", "").replace(")", "").split(",")
                                gui.Popup(
                                    gui_translate(f"{result[0].strip()}\n{result[1].strip()}\n{result[2]}\n{result[3]}"), title=gui_translate(f"FiEncrypt - Search Result (Logged in as: {get_current_user()})"), font="Courier 20")
                            else:
                                gui.Popup(gui_translate(
                                    f"No contact matching {search} found!"), title=gui_translate(f"FiEncrypt - Search Result (Logged in as: {get_current_user()})"), font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
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
                             default_color, private_mode, error_color, print_speed=0)
                    else:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("1. Add Contact"))], [gui.Text(gui_translate("2. Remove Contact"))], [gui.Text(gui_translate("3. Search For Contact"))], [gui.Text(gui_translate("4. List All Contacts"))], [
                                gui.Text(gui_translate("5. Return to Main Menu"))], [gui.Text(gui_translate("Select a function")), gui.InputText(key="contact_func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Contact Manager (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                        else:
                            animated_print(
                                f"Inavlid option selected!")
        elif func == 11:
            if display_initiate:
                contact_func = 0
                if graphic_mode:
                    layout = [[gui.Text(gui_translate("1. Add Contact"))], [gui.Text(gui_translate("2. Remove Contact"))], [gui.Text(gui_translate("3. Search For Contact"))], [gui.Text(gui_translate("4. List All Contacts"))], [
                        gui.Text(gui_translate("5. Return to Main Menu"))], [gui.Text(gui_translate("Select a function")), gui.InputText(key="contact_func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                    window = gui.Window(title=gui_translate(f"FiEncrypt - Contact Manager (Logged in as: {get_current_user()})"),
                                        layout=layout, margins=(100, 50), font="Courier 20")
                else:
                    animated_print(f"Contact manager:")
                    animated_print(f"1. Add Contact")
                    animated_print(f"2. Remove Contact")
                    animated_print(f"3. Search For Contact")
                    animated_print(f"4. List All Contacts")
                    animated_print(f"5. Return To Main Menu")
                while contact_func not in range(1, 6):
                    try:
                        if graphic_mode:
                            event, values = window.read()
                            if event == "Launch!":
                                contact_func = values.get("contact_func", 0)
                            window.close()
                        else:
                            contact_func = privacy_input(f">> ", 0)
                    except KeyboardInterrupt:
                        print("")
                        menu(user, display_initiate, print_logs,
                             default_color, private_mode, error_color, print_speed=0)
                    try:
                        contact_func = int(contact_func)
                    except ValueError:
                        if contact_func == None:
                            menu(user, display_initiate, print_logs,
                                 default_color, private_mode, error_color, print_speed=0)
                        else:
                            contact_func = 0
                    contact_manager = Contacts(user, get_current_user().lower(
                    ).strip(), print_logs, default_color, error_color, private_mode)
                    agreed, temp_override_port = None, None
                    if contact_func == 1:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter contact name here")), gui.InputText(key="new_name")], [gui.Text(gui_translate("Enter MAC address here")), gui.InputText(
                                key="new_ip")], [gui.Text(gui_translate("Set agreed encryption code")), gui.Button(gui_translate("Yes"), key="yes"), gui.Button(gui_translate("No"), key="no"), gui.InputText(key="agreed_code")], [gui.Text(gui_translate("Set port for dedicated communication")), gui.InputText(key="override_port")], [gui.Text(gui_translate("Enter any additional details here")), gui.InputText(key="new_details")], [gui.Button(gui_translate("Save"), key="Save", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - New Contact (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            while True:
                                event, values = window.read()
                                if event == "no":
                                    agreed = "n"
                                elif event == "yes":
                                    agreed = "y"
                                elif event == "Cancel":
                                    func = 0
                                    break
                                    window.close()
                                    break
                                elif event == "Save":
                                    new_name, new_ip, new_details, set_code, temp_override_port = values.get("new_name", ""), values.get(
                                        "new_ip", ""), values.get("new_details", ""), values.get("agreed_code", None), values.get("override_port", None)
                                    if agreed == None:
                                        agreed = "n"
                                    break
                            window.close()
                        else:
                            new_name = privacy_input(
                                f"Enter contact name here", private_mode)
                            new_ip = privacy_input(
                                f"Enter MAC address here (or leave blank)", private_mode)
                            agreed = privacy_input(f"Do you want to store current code as agreed code? [Y|N]", private_mode)
                            if "y" in agreed.lower():
                                set_code = privacy_input(f"Set the agreed code (or leave blank to apply current code)", private_mode)
                                if set_code.strip() == "":
                                    set_code = None
                            else:
                                set_code = None
                            new_details = privacy_input(
                                f"Enter any additional details here", private_mode)
                            temp_override_port = privacy_input(f"Enter dedicated port for commuication", private_mode)
                        if temp_override_port != None and temp_override_port.strip() != "":
                            try:
                                temp_override_port = int(temp_override_port)
                            except:
                                temp_override_port = None
                        else:
                            temp_override_port = None
                        if "y" in agreed.lower():
                            agreed_code = code
                        else:
                            agreed_code = None
                        if new_details.strip() == "" or new_details == None:
                            new_details = "\n"
                        if agreed_code != None:
                            if graphic_mode:
                                gui.Popup(f"The agreed code with {new_name} is {agreed_code}", title=f"FiEncrypt - Agreed Code (Logged in as {get_current_user()})", font="Courier 20")
                            else:
                                animated_print(f"The agreed code with {new_name} is {agreed_code}")
                        if new_name.strip() != "":
                            contact_manager.add(new_name, new_ip, agreed_code, new_details, temp_override_port)
                        else:
                            if graphic_mode:
                                gui.Popup(gui_translate("Contact name cannot be blank!"), title=gui_translate("Warning"),
                                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(
                                    f"WARNING: Contact name cannot be blank!", error=True, reset=True)
                                Colors(default_color)
                        contact_func = 0
                    elif contact_func == 2:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter name of contact to be removed")), gui.InputText(
                                key="target_name")], [gui.Button(gui_translate("Delete"), key="Delete", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Delete Contact (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Delete":
                                target_name = values.get("target_name", "")
                            window.close()
                        else:
                            target_name = privacy_input(
                                f"Enter name of contact to be removed", private_mode)
                        if target_name.strip() != "":
                            contact_manager.remove(target_name)
                        else:
                            if graphic_mode:
                                gui.Popup(gui_translate("Contact name cannot be blank!"), title=gui_translate("Warning"),
                                          text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                            else:
                                animated_print(
                                    f"WARNING: Contact name cannot be blank!", error=True, reset=True)
                                Colors(default_color)
                        contact_func = 0
                    elif contact_func == 3:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("Enter the contact name here")), gui.InputText(key="search")], [
                                gui.Button(gui_translate("Search"), key="Search", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Search for contact (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                            event, values = window.read()
                            if event == "Search":
                                search = values.get("search", "")
                            window.close()
                        else:
                            search = privacy_input(
                                f"Enter the contact name here", private_mode)
                        result = contact_manager.check_for(search)
                        if graphic_mode:
                            if result != None:
                                result = str(result).replace("\\n", "").replace(
                                    "(", "").replace(")", "").split(",")
                                gui.Popup(gui_translate(
                                    f"{result[0].strip()}\n{result[1].strip()}\n{result[2]}\n{result[3]}"), title=gui_translate(f"FiEncrypt - Search Result (Logged in as: {get_current_user()})"), font="Courier 20")
                            else:
                                gui.Popup(gui_translate(
                                    f"No contact matching {search} found!"), title=gui_translate(f"FiEncrypt - Search Result (Logged in as: {get_current_user()})"), font="Courier 15", auto_close=True, auto_close_duration=5)
                        else:
                            if result != None:
                                animated_print(result)
                            else:
                                animated_print(
                                    f"No contact matching {search} found!", font="Courier 15")
                        contact_func = 0
                    elif contact_func == 4:
                        contact_manager.list_all()
                        contact_func = 0
                    elif contact_func == 5:
                        menu(user, display_initiate, print_logs,
                             default_color, private_mode, error_color, print_speed=0)
                    else:
                        if graphic_mode:
                            layout = [[gui.Text(gui_translate("1. Add Contact"))], [gui.Text(gui_translate("2. Remove Contact"))], [gui.Text(gui_translate("3. Search For Contact"))], [gui.Text(gui_translate("4. List All Contacts"))], [
                                gui.Text(gui_translate("5. Return to Main Menu"))], [gui.Text(gui_translate("Select a function")), gui.InputText(key="contact_func"), gui.Button(gui_translate("Launch!"), key="Launch!", bind_return_key=True)], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                            window = gui.Window(title=gui_translate(f"FiEncrypt - Contact Manager (Logged in as: {get_current_user()})"),
                                                layout=layout, margins=(100, 50), font="Courier 20")
                        else:
                            animated_print(
                                f"Inavlid option selected!")
            else:
                config_settings(user, capitalize_user(get_current_user()), default_color,
                                print_logs, private_mode, error_color)
        elif func == 12:
            if display_initiate:
                config_settings(user, capitalize_user(get_current_user()), default_color,
                                print_logs, private_mode, error_color)
            else:
                manage_cache(user, capitalize_user(get_current_user()), default_color,
                             print_logs, private_mode, error_color)
        elif func == 13:
            if display_initiate:
                manage_cache(user, capitalize_user(get_current_user()), default_color,
                             print_logs, private_mode, error_color)
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
            if graphic_mode:
                gui.Popup(gui_translate("Invalid Function!"),
                          title=gui_translate("Warning"), font="Courier 20", text_color="red", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"Invalid Fuction!")
                for _ in range(2):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")


def login(display_initiate, user_account_name, error_color, default_color, print_logs, private_mode, auto_code, **kwargs):
    """Login portal, referring to CREDENTIALS.txt for validation"""
    access, attempts, username_input, password_input, saved_attempts = False, 3, "", "", kwargs.get(
        "attempts", 3)
    if saved_attempts <= 3:
        attempts = saved_attempts
    if not graphic_mode:
        animated_print(
            f"Welcome to FiEncrypt! Enter your credientials below!")
    while not access:
        if graphic_mode:
            while username_input == None or username_input.strip() == "" or password_input == None or password_input.strip() == "":
                layout = [[gui.Text(gui_translate("Welcome to FiEncrypt! Enter your credientials below!"))], [gui.Text(gui_translate("Username")), gui.InputText(
                    key="username")], [gui.Text(gui_translate("Password")), gui.InputText(key="password", password_char="*")], [gui.Button(gui_translate("Login"), key="Login", bind_return_key=True), gui.Button(gui_translate("Cancel"), key="Cancel")], [gui.Text("FiEncrypt (C) le_firehawk 2021", font="Courier 10", text_color="grey")]]
                window = gui.Window(title="FiEncrypt", layout=layout,
                                    margins=(100, 50), font="Courier 20")
                event, values = window.read()
                if event == "Login":
                    username_input = values.get("username", None)
                    password_input = values.get("password", None)
                    if username_input == None or username_input.strip() == "":
                        gui.Popup(gui_translate("Username cannot be blank!"), title=gui_translate("Warning"),
                                  text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                    elif password_input == None or password_input.strip() == "":
                        gui.Popup(gui_translate("Password cannot be blank!"), title=gui_translate("Warning"),
                                  text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                elif event == "Cancel":
                    window.close()
                    maybe_quit()
                window.close()
        else:
            while username_input == None or username_input.strip() == "":
                username_input = privacy_input(f"Username", is_private())
                if username_input == None or username_input.strip() == "":
                    animated_print(
                        f"WARNING: Username cannot be blank!", error=True, reset=True)
                    Colors(default_color)
                    for _ in range(2):
                        sys.stdout.write("\033[F")
                else:
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
                    break
            while password_input == None or password_input.strip() == "":
                password_input = privacy_input(f"Password", 1)
                if password_input == None or password_input.strip() == "":
                    animated_print(
                        f"WARNING: Password cannot be blank!", error=True, reset=True)
                    Colors(default_color)
                    for _ in range(2):
                        sys.stdout.write("\033[F")
                    sys.stdout.flush()
                else:
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
                    break
        access = validate_login(username_input, password_input)
        if attempts == 0:
            if graphic_mode:
                gui.Popup(gui_translate("0 Attempts left! Game over brother!"),
                          title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                animated_print(f"0 Attempts left! Game over brother!")
            self_terminate(True)
        elif access:
            if graphic_mode:
                if private_mode:
                    gui.popup_no_wait(gui_translate(f"Access granted! Welcome @Anonymous!"),
                                      title=gui_translate("FiEncrypt - Access Granted!"), font="Courier 15", auto_close=True, auto_close_duration=5)
                else:
                    gui.popup_no_wait(gui_translate(
                        f"Access granted! Welcome @{capitalize_user(username_input)}"), title=gui_translate("FiEncrypt - Access Granted!"), font="Courier 15", auto_close=True, auto_close_duration=5)
            else:
                if private_mode:
                    animated_print(f"Access granted! Welcome @Anonymous!")
                else:
                    animated_print(f"Access granted! Welcome @{capitalize_user(username_input)}")
            current_user = get_current_user(new_user=username_input)
            menu(pass_user(), display_initiate, print_logs,
                 default_color, private_mode, error_color, auto_code=auto_code)
            current_user = username_input
        else:
            if graphic_mode:
                gui.Popup(gui_translate(
                    f"Incorrect Login! {attempts} attempts left! Try again!"), title=gui_translate("Warning"), text_color="red", font="Courier 15", auto_close=True, auto_close_duration=5)
                try:
                    window.close()
                except:
                    pass
            else:
                if int(attempts) < 3:
                    for _ in range(3):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                else:
                    for _ in range(2):
                        sys.stdout.write("\033[F")
                        sys.stdout.write("\033[K")
                animated_print(
                    f"WARNING: Incorrect Login! {attempts} attempts left! Try again!", error=True, reset=True)
                Colors(default_color)
            log(f"Login attempt Success? False Attempts left: {str(attempts)}",
                "loginManager", username_input, print_logs)
            username_input, password_input = None, None
            attempts -= 1


def initiate():
    """Startup script for FiEncrypt"""
    global graphic_mode, gui_theme, translation, TranslationManager, override_port
    ImportStructure("logic")
    ImportStructure("system")
    log("--== FiEncrypt Warming Up! ==--", "", get_current_user(), False)
    log("Logic modules imported!", "moduleManager", get_current_user(), False)
    log("System modules imported!", "moduleManager", get_current_user(), False)
    ImportStructure("string")
    log("String modules imported!", "moduleManager", get_current_user(), False)
    ImportStructure("network")
    log("Network modules imported!", "moduleManager", get_current_user(), False)
    ImportStructure("gui")
    log("GUI module imported!", "moduleManager", get_current_user(), False)
    home_directory, operating_system, user = enter_home_directory()
    print_logs, display_initiate, graphic_mode, private_mode, color_enabled, default_color, auto_code, voice_record_time, gui_theme, translation, lang, override_port = retrieve_config_settings()
    protect_tree()
    if translation:
        TranslationManager = Translate(lang)
    else:
        TranslationManager = None
    error_color = "\033[91m"
    if color_enabled:
        Colors(default_color)
    else:
        Colors(None)
    apply_theme(gui_theme)
    graphic_mode = to_boolean(graphic_mode)
    clear_cache()
    try:
        os.mkdir("cache")
    except:
        pass
    with open(f"./CREDENTIALS.txt", "r+") as credentials:
        credential_lines = credentials.readlines()
        if len(credential_lines) < 2:
            if not graphic_mode:
                animated_print(
                    f"Welcome to FiEncrypt! Please create a user account by entering a username and password below!")
            add_new_user()
    login(display_initiate, user, error_color,
          default_color, print_logs, private_mode, auto_code)


initiate()
