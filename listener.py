# This file is part of FiEncrypt

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


import sys
import socket
import urllib.request
import os
import subprocess
import getpass
import hashlib
import time
from plyer import notification


def display_license():
    print("""This file is part of FiEncrypt\n\nFiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2021 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>\n\n""")


def substring(string, search, state):
    return string.partition(search)[state]


def pass_os():
    return sys.platform


def pass_user():
    home_directory, operating_system, user = enter_home_directory()
    try:
        return user
    except NameError:
        return None


def hide_tree():
    if sys.platform == "win32":
        subprocess.check_call(
            ["attrib", "+H", f"../FiEncrypt"])
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


def get_privacy_mode():
    enter_home_directory()
    with open(f"./config.txt", "r+") as config_file:
        private_mode = config_file.readline(9)
        if "private" in private_mode:
            private_mode = private_mode.split(" = ")
            private_mode = private_mode[1]
            if "True" in private_mode:
                private_mode = True
            else:
                private_mode = False
        else:
            private_mode = False
    return private_mode


def set_home_directory(operating_system):
    if operating_system == "win32":
        file_path = sys.argv[0].split(":\\")
        if ".py" in str(file_path):
            file_path[1] = file_path[1].replace("\\\listener.py", "")
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
    operating_system = pass_os()
    home_directory, user = set_home_directory(operating_system)
    os.chdir(home_directory)
    return home_directory, operating_system, user


def hash_current_user(user):
    hash_user = user.encode("utf-8")
    hash_user = hashlib.sha256(hash_user).hexdigest()
    return hash_user


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
        return None
    except UnboundLocalError:
        privacy_input(string, state)


def validate_login(username, password):
    enter_home_directory()
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


def check_no_credentials():
    enter_home_directory()
    try:
        with open("CREDENTIALS.txt", "r+") as credentials_file:
            lines = credential_lines.read().split("\n")
            if len(lines) <= 1:
                return False
            else:
                return True
    except:
        return False


def login():
    try:
        valid = False
        while not valid:
            username = privacy_input("Username", 0)
            if username == None:
                exit()
            password = privacy_input("Password", 1)
            if username == None or password == None:
                raise KeyboardInterrupt
            else:
                valid = validate_login(username, password)
            if not valid:
                username, password = None, None
                print(
                    f"Incorrect Login! Try again!")
        return valid, username, password
    except KeyboardInterrupt:
        print(f"FiEncrypt listener shutting down!")


def main():
    home_directory, system, user = enter_home_directory()
    no_accounts = check_no_credentials()
    if no_accounts:
        print("You have not created any FiEncrypt accounts! Return to the main program and create one to proceed!")
        exit()
    valid, username, password = login()
    if valid:
        get_current_user(new_user=username)
        if "linux" in sys.platform.lower():
            import netifaces
            interface = netifaces.interfaces()
            for i in interface:
                try:
                    ip = str(netifaces.ifaddresses(i)[netifaces.AF_INET])
                    ip = ip.split()
                    ip = ip[1].replace("'", "").replace(",", "")
                except:
                    pass
            if ip == "":
                ip = input("Enter your IP in dotted decimal format: ")
            src = f"./anarchy.png"
        elif "win32" in sys.platform.lower():
            ip = socket.gethostbyname(socket.gethostname())
            src = f"./anarchy2.ico"
        print(f"Link bound to {ip}:19507")
        print(f"Messages not recieved by FiEncrypt will be saved to mailbox!")
        print(f"You can view mailbox through function 9 on FiEncrypt!")
        max_letters, request = 0, False
        try:
            link = socket.socket()
            link.bind((ip, 19507))
        except KeyboardInterrupt:
            print(F"\nFiEncrypt Listener shutting down! You will no longer have messages saved to your mailbox!")
            exit()
        except OSError:
            print(
                f"\033[91mWARNING: Link address already in use! Perhaps another instance of FiEncrypt Listener is running?\033[0m")
            exit()
        while True:
            enter_home_directory()
            os.chdir(f"./{hash_current_user(username.lower())}/inbox")
            try:
                link.listen(100)
            except OSError:
                pass
            try:
                sc, address = link.accept()
                info = sc.recv(1024)
            except OSError:
                pass
            except KeyboardInterrupt:
                print("\nLogging out...")
                try:
                    sc.close()
                    link.close()
                except:
                    pass
                main()
            try:
                message = info.decode()
                message = message.split(" | ")
                if len(message) == 3:
                    if "request" in message[0].lower():
                        if "True" in message[0] and "target" not in message[-1].lower():
                            request = True
                            ip = message[1].split(":")
                            ip = ip[1].strip()
                            name = message[2].split(":")
                            name = name[1].strip()
                            if name == "" or name == "Anonymous":
                                name = "Anonymous"
                            try:
                                notification.notify(
                                    title='Conversation Request!',
                                    message=f'{name} has invited you to a conversation! \nUse IP {ip}!',
                                    app_name='FiEncrypt',
                                    app_icon=src,
                                    timeout=50
                                )
                            except:
                                pass
                        elif "target" in message[-1].lower() and "True" in message[0]:
                            request = True
                            ip = message[1].split(":")
                            ip = ip[1].strip()
                            message[2] = message[2].split(" |||| ")
                            name = message[2][0].split(":")
                            name = name[1].strip()
                            recipient_name = message[2][1].split(":")
                            recipient_name = recipient_name[1].strip()
                            try:
                                notification.notify(
                                    title='Conversation Request!',
                                    message=f'{name.capitalize()} has invited {recipient_name} to a conversation! \nUse IP {ip}!',
                                    app_name='FiEncrypt',
                                    app_icon=src,
                                    timeout=50
                                )
                            except:
                                pass
                        elif "False" in message[0]:
                            request = False
                            ip = message[1].split(":")
                            ip = ip[1].strip()
                            message[2] = message[2].split(" |||| ")
                            name = message[2][0].split(":")
                            name = name[1].strip()
                            if name == "":
                                name = "Anonymous"
                            code = message[2][2].strip()
                            message = message[2][1].strip()
                            try:
                                notification.notify(
                                    title='New Message!',
                                    message=f'{name.capitalize()} has sent you a message! Check your FiEncrypt inbox!',
                                    app_name='FiEncrypt',
                                    app_icon=src,
                                    timeout=50
                                )
                            except:
                                pass
                elif len(message) == 1:
                    message = message[0].split(" |||| ")
                    target_ip = message[1].strip()
                    target_user = message[0].split("=")
                    target_user = target_user[1].strip()[::-1]
                    # decrypted_target_user, encrypted_target_user = [], []
                    # for i, char in enumerate(target_user):
                    #     encrypted_target_user.append(ord(char))
                    #     decrypted_target_user.append(chr(int(encrypted_target_user[i])-31))
                    # target_user = ""
                    # for char in decrypted_target_user:
                    #     target_user += char
                    if target_user.strip() == hash_current_user(get_current_user().strip().lower()):
                        sc.send(str(True).encode())
                        info = sc.recv(1024)
                        message = info.decode()
                        if message.strip() != "\\exit":
                            request = False
                            message = message.split(" | ")
                            ip = target_ip
                            message[0] = message[0].split(" |||| ")
                            code = message[0][1].strip()
                            name = message[1].strip()
                            if name == "":
                                name = "Anonymous"
                            else:
                                contact_names = []
                                enter_home_directory()
                                os.chdir(f"./{hash_current_user(get_current_user().lower().strip())}/contacts")
                                for root, dirs, files in os.walk(f"."):
                                    for temp_name in files:
                                        contact_names.append(temp_name.replace(".txt", ""))
                                for contact_name in contact_names:
                                    if name.lower().strip() == contact_name.lower().strip():
                                        with open(f"./contact_name", "r+") as contact_file:
                                            contact_lines = contact_file.read().split("\n")
                                        code = contact_lines[3].split(" = ")[1].strip()
                            message = message[0][0].strip()
                            try:
                                notification.notify(
                                    title='New Message!',
                                    message=f'{name.capitalize()} has sent you a message! Check your FiEncrypt inbox!',
                                    app_name='FiEncrypt',
                                    app_icon=src,
                                    timeout=50
                                )
                            except:
                                pass
                            sc.send(str(True).encode())
                        else:
                            sc.close()
                    else:
                        sc.send(str(False).encode())
                        sc.close()
                else:
                    print(message)
                if not request:
                    os.chdir(f"../inbox")
                    with open(f"./messages.txt", "r+") as mailbox:
                        letters = mailbox.readlines()
                        private_mode = get_privacy_mode()
                        for i, line in enumerate(letters):
                            try:
                                line = int(line)
                                max_letters = len(letters)
                            except ValueError:
                                pass
                        if str(message).startswith("b'") or str(message).startswith("b\"") or str(message).startswith("b\\"):
                            message = message[2:int(len(message))]
                            message = message[0:int(len(message)-1)]
                        elif str(message).startswith("b\\'"):
                            message = message[3:int(len(message))]
                            message = message[0:int(len(message)-2)]
                        if str(message).startswith("b'") or str(message).startswith("b\""):
                            message = message[2:int(len(message))]
                            message = message[0:int(len(message)-1)]
                        if private_mode:
                            name = "Anonymous"
                        mailbox.write(
                            f"{max_letters}\n{message} - {code} From: {name}@{ip}\n")
                        hide_tree()
            except:
                raise
        sc.close()
        try:
            link.shutdown(socket.SHUT_RDWR)
            link.close()
        except OSError:
            pass


display_license()
print(f"FiEncrypt Listener starting up!")
main()
