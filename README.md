FiEncrypt, property of le_firehawk is pure Python, peer-to-peer communication software intended for personal use only.
Copyright (C) 2020 le_firehawk

FiEncrypt is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

FiEncrypt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

To contact the owner of FiEncrypt, use the following:
Email: firehawk@opayq.net

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>

Thanks for downloding FiEncrypt! Read the following guide for additional details:

--Python pip
You will need any version of Python 3 with the pip module.
-! For most Linux users this can be done by running the following command in bash
sudo apt-get install python3-pip
-! For Windows users, you're on your own. However you choose to install Python,
you'll have to ensure the path functions in connection to pip installed modules
(you often end up with multiple Python installs, and you must run all pip installs
on the Python interpreter linked to CMD terminal)

--Pip modules
The plyer module needs to be installed, along with ntfy to unlock full
functionality of FiEncrypt and the associated listener.py (designed to run in
background)
Execute the following commands in the OS-specific terminal:
python -m pip install plyer
python -m pip install ntfy
python -m pip install scapy
-!The syntax of these commands may vary based on your Python install, python
can be substituted for python3, python3.8, etc... pip can be swapped with pip3
-! Linux users will also need to install the netifaces module to enable network
functionality
python -m pip install netifaces

--Running the program
You will need to use the credentials given to log into FiEncrpyt, or if you
are dedicated enough you could re-write all the validation that is done.
FiEncrpyt does support colours, but as of current they only function in Visual
Studio Code or the GNU/Linux terminal.

--Function 1: Encrypt New Message 
Takes two inputs, a code entered by the user for encryption and the message 
they wish to send. Once both are filled, the message will be stored in 
encrypted form. You will then be prompted if you wish to send the message 
over the network. 

Entering n or no will inform you the message has been
saved to the messageout.txt file, and the code will be printed for you to 
give to the recipient. 

Entering y or yes will prompt you for the IP address of the recipient, after
which FiEncrypt will automatically attempt to send the message. Any error related
to the connection timing out or being refused will prompt if you want to leave
the message.

Invoking the leave message will re-send the same message on a different port, on
which the listener.py file will be active. Upon recieving a transmission, listener
produces a notificiation for both Windows and Linux users through the ntfy module.
This message will be stored in the inbox.txt file and can be read through Function
9: Check Mailbox.

--Function 2: Decrypt Message
Takes one input, the code to be used for decryption. As for the message, it is 
automatically retrieved from the messagein.txt file, although this functionality
may be expanded in later iterations. The decrypted text will be printed and you
will be prompted if the decryption was successful.

Entering y or yes will prompt FiEncrypt to delete the encryption code from
code.txt (only if code input was left blank).

Entering n or no will execute Function 5/6: Encryption Helper (currently inactive)
You will then be taken back to the main menu.

--Function 3: Show Current Code
Takes no input, printing out any content saved in the code.txt file

--Function 4: Request Random Code
Takes one input asking if you want an automatic UUID code to be made.

Entering n or no will allow you to enter the main segment of the encryption
code *Must be even number of characters. The other segments of the code will still
be automatically generated.

Enter y or yes will automatically generate a full encryption code.

The code will then be saved to code.txt.

--Function 5: Encryption Helper (or Initiate Filesystem)
The output of the menu depends on a condition in the config.txt file, referred to
as display_initiate. If it is True, Initiate Filesystem will be shown as the
fifth menu option. 

Encryption Helper is a collection of scripts meant to automatically resolve errors
commonly found on FiEncrypt. It will accept a tree of issues to assist in diagnosis
or run the scripts that do provide the solutions. Currently, the function is not
operating.

Initiate Filesystem simply runs the establish_tree() module, recreating the files
that allow FiEncrypt to function normally.

*All functions below will be listed as if display_initiate is not true

--Function 6: Secret Code
Accepts a number of codes as an input, allowing for a number of easter eggs to execute
(if you read the source code for secret_code you will spoil the secret).

--Function 7: Open Inbound Server
Running this function will open port 9999 on your current IP, and messages sent to you
will be processed and passed on to the retrieve_message module. Any TCP packet sent
through, that is invalid, will result in the program crashing.

--Function 8: Invite To Conversation
Allows a request to be sent to another client running the listener.py file, prompting
them to respond via Function 1 of FiEncrypt, with the sender's IP also being displayed.

--Function 9: Check Mailbox
Refers to the inbox.txt file located within FiEncrypt directory, which messages handled
by listener.py will be saved in, displaying the timestamp along with the decrypted message.

--Function 10: Contact Manager
Opens contact interface, providing several sub-functions
1. Add new contact
Prompts for a name under which to save the new contact, used as the file name of the text file.
Prompts for a MAC address associated with the contact, allowing the new_message module to
automatically resolve the IP associated to said MAC address, using ARP resolution through
the python scapy module..
Prompts for additional details, to describe the contact
2. Remove contact
Prompts for a contact name to remove, employing sub-function 3 to locate the relevant
contact file and delete the file.
3. Search for contact
Prompts for a contact name, calling the relevant contact file and printing out all content
within the file.
4. List all contact
Walks through the Contacts directory and one-by-one, printing each contact file as part
of a loop.
5. Return to main menu
Returns to main menu?

--Function 11: Config Settings
Prints all modifyable entries within the config file, prompting for a numerical input 
based on the lines printed. The selected option allows relevant state (text or boolean)
and updates all lines in the config file based on the changes. Requesting a reload may
be required for changes to take effect.

--Function 12: Reload
Calls the initiate module, applying all changes made (requires another login).

--Function 13: Exit
Smooth exit of FiEncrypt. Running CTRL+C should yield similar results

--listener.py
Entirely passive program, intended to allow messages to be saved without using the CPU
resources FiEncrpyt does. NOTE: Changing network (and in turn IP address) or suspending
the system will prevent proper reception of new messages.
