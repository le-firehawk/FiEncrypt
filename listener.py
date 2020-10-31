# This file is part of FiEncrypt

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


import sys
import socket
import urllib.request
import os
import subprocess
from plyer import notification


def display_license():
    print("""This file is part of FiEncrypt\n\nFiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.\nCopyright (C) 2020 le_firehawk\n\nFiEncrypt is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nFiEncrypt is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nTo contact the owner of FiEncrypt, use the following:\nEmail: firehawk@opayq.net\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>\n\n""")


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
        maybe_quit()
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


def main():
    display_license()
    valid = False
    print(f"FiEncrypt Listener starting up!")
    home_directory, os, user = enter_home_directory()
    while not valid:
        username = privacy_input("Username", 0)
        password = privacy_input("Password", 1)
        valid = validate_login(username, password)
        if not valid:
            username, password = None, None
            animated_print(
                f"Incorrect Login! Try again!")

    if os == "linux":
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
    elif os == "win32":
        ip = socket.gethostbyname(socket.gethostname())
        src = f"./anarchy2.ico"
    print(f"Link bound to {ip}:19507")
    print(f"Messages not recieved by FiEncrypt will be saved to mailbox!")
    print(f"You can view mailbox through function 9 on FiEncrypt!")
    max_letters = 0
    try:
        link = socket.socket()
        link.bind((ip, 19507))
        link.listen(10)
    except KeyboardInterrupt:
        print(F"\nFiEncrypt Listener shutting down! You will no longer have messages saved to your mailbox!")
        exit()
    except OSError:
        print(f"\033[91mWARNING: Link address already in use! Perhaps another instance of FiEncrypt Listener is running?\033[0m")
        exit()
    while True:
        try:
            sc, address = link.accept()
            info = sc.recv(1024)
        except KeyboardInterrupt:
            print(F"\nFiEncrypt Listener shutting down! You will no longer have messages saved to your mailbox!")
            try:
                sc.close()
                link.close()
            except:
                pass
            exit()
        try:
            message = info.decode()
            message = message.split(" | ")
            message[2] = message[2].split(" |||| ")
            message[0] = message[0].split(":")
            message[1] = message[1].split(":")
            message[2][0] = message[2][0].split(":")
            print(message)
            with open(f"./{hash_current_user(username)}/messages.txt", "r+") as mailbox:
                letters = mailbox.readlines()
                private_mode = get_privacy_mode()
                for i, line in enumerate(letters):
                    try:
                        line = int(line)
                        max_letters = len(letters)
                    except ValueError:
                        pass
                if str(message[2][1]).startswith("b'") or str(message[2][1]).startswith("b\"") or str(message[2][1]).startswith("b\\"):
                    message[2][1] = message[2][1][2:int(len(message[2][1]))]
                    message[2][1] = message[2][1][0:int(len(message[2][1])-1)]
                elif str(message[2][1]).startswith("b\\'"):
                    message[2][1] = message[2][1][3:int(len(message[2][1]))]
                    message[2][1] = message[2][1][0:int(len(message[2][1])-2)]
                if str(message[2][2]).startswith("b'") or str(message[2][2]).startswith("b\""):
                    message[2][2] = message[2][2][2:int(len(message[2][2]))]
                    message[2][2] = message[2][2][0:int(len(message[2][2])-1)]
                if private_mode or message[2][0][1].strip() == "":
                    message[2][0][1] = "Anonymous"
                mailbox.write(
                    f"{max_letters}\n{message[2][1]} - {message[2][2]} From: {message[2][0][1]}@{message[1][1]}\n")
                hide_tree()
            notification.notify(
                title='New Message!',
                message=f'{message[2][0][1].capitalize()} has sent you a message! Check your FiEncrypt inbox!',
                app_name='FiEncrypt',
                app_icon=src,
                timeout=50
            )
        except:
            try:
                message = info.decode()
                message = message.split(" ")
                ip = message[1].split(":")
                ip = ip[1]
                name = message[2].split(":")
                name = name[1]
                if "True" in message[0]:
                    notification.notify(
                        title='Conversation Request!',
                        message=f'{name.capitalize()} has invited you to a conversation! \nUse IP {ip}!',
                        app_name='FiEncrypt',
                        app_icon=src,
                        timeout=50
                    )
                else:
                    pass
            except:
                pass
    sc.close()
    link.close()


main()
