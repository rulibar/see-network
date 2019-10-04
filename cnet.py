"""
cnet.py (see network)

Check to see if you are connected to the internet and make sure your ip address
is in the set ip_whitelist.

(Originally designed for Linux Mint MATE v19.1.)
"""

import socket
import subprocess
import time
import logging

ip_whitelist = set()
#ip_whitelist.add('')

def internet(host = '8.8.8.8', port = 53, timeout = 3) -> bool:
    """
    Check if I have an internet connection.

    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logger.error(ex)
        return False

def my_public_ip():
    """
    Get my public IP using ifconfig. If unable, then return 0.0.0.0.

    When you call subprocess.check_output, it prints stuff to term. If you use
    shell=True it will disable these logs, but for some reason it doesn't
    recognize the curl command.
    """
    try:
        pipe_out = subprocess.check_output('curl ifconfig.me'.split(), timeout=5)
        return pipe_out.decode('utf8')
    except Exception as e:
        logger.error("Failed to determine public IP address.")
        logger.error(e)
        return "0.0.0.0"

def restart_connection():
    """
    Restart network manager.

    Sleep for 5 seconds to give time for restart.
    """
    cmd = 'sudo service network-manager restart'
    logger.info("Restarting network manager..."); logger.info(cmd)
    subprocess.call(cmd.split())
    time.sleep(5)

"""
Set up logger
"""
log_format = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(filename = '/home/ryan/Downloads/cnet.log',
    level = logging.DEBUG,
    format = log_format)
logger = logging.getLogger()
logger.info('~'*10 + ' cnet.py ' + '~'*10)

"""
Start checking connection
"""
status = 0
logger.info('Now ready to check the internet connection.')
while True:
    if internet():
        tries = 0
        while tries < 3:
            my_ip = my_public_ip()
            tries += 1
            if my_ip != "0.0.0.0": break
        if my_ip not in ip_whitelist:
            logger.warning("IP address not recognized. Attempting a restart.")
            restart_connection()
        else: status = 0
    else:
        if status == 0:
            status = 1
            logger.error("Unable to connect...")
            time.sleep(1)
            logger.error("Trying again...")
        elif status == 1:
            status = 2
            logging.error("Failed to connect twice. Attempting a restart.")
            restart_connection()
        else:
            status = 0
            logging.critical("Failed to connect three times.")
            logging.critical("Waiting 30 seconds and starting over...")
            time.sleep(30)
