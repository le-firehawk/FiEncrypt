
from setuptools import setup
import sys
version = "1.6.6"
try:
    setup(
        name='FiEncrypt',
        version=version,
        packages=[],
        install_requires=['plyer', 'ntfy', 'scapy',
                          'tqdm', 'Pillow', 'playsound', 'PySimpleGUI', 'textblob', 'netifaces', 'pyaudio'],
        url='https://github.com/le-firehawk/FiEncrypt',
        license='AGPL v3',
        author='le_firehawk',
        author_email='firehawk@opayq.net',
        description='Pure python peer-to-peer communication program'
    )
except exception as e:
    if sys.platform == "win32":
        print("You may recieve an error regarding the installation of pyaudio. It is safe to ignore this, although functionality related to voice messages will be unavailable")
        print("If you wish to report an error, give the following details:")
        print(f"FiEncrypt {version}, running on {sys.platform}")
        print(e)

finally:
    if sys.platform == "win32":
        print("You may recieve an error regarding the installation of pyaudio. It is safe to ignore this, although functionality related to voice messages will be unavailable")
    elif sys.platform == "linux":
        print("PyAudio and Bluetooth (Bluez) will need to be installed from the relevant repository manager. For example, you will need to run sudo apt-get install python3-pyaudio python3-bluetooth")
