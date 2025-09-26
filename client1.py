import socket
import threading
import os
import datetime
import json
import time


from errors import*
from protocol import*
from os.path import exists


def get_username_and_password():
    username = input("enter a username for yourself ")
    password = input("enter a password for yourself ")
    return username, password


def connect():
    log_in_tries = 3
    result = exists("cookie.json")
    if result:
        file = open("cookie.json", "r", encoding="UTF-8")
        data = json.load(file)
        file.close()
        last_login_date = datetime.date(*list(map(int, data["date"].split("/"))))
        today = datetime.date.today()
        print((today - last_login_date).days < 8)
        if (today - last_login_date).days < 8:
            username = data["username"]
            password = data["password"]
        else:
            username, password = get_username_and_password()

    else:
        username = input("enter a username for yourself ")
        password = input("enter a password for yourself ")
    for i in range(3):
        send_text(socket_test_client, username)
        send_text(socket_test_client, password)
        information = recv(socket_test_client)
        if information[0] == "ERR":
            print(i)
            log_in_tries -= 1
            print(f"you have {log_in_tries} tries left.")
            if log_in_tries > 0:
                username, password = get_username_and_password()
            else:
                raise ConnectionError("Authentication Error")

        elif information[0] == "TXT":
            file = open("cookie.json", "w", encoding = "UTF-8")
            file_info = {"username":username, "password" : password, "date": datetime.date.today().strftime("%Y/%m/%d")}
            json.dump(file_info, file)
            file.close()
            print("you logged on.")
            break

def choose_DM():
    information = recv(socket_test_client)[1]
    while True:
        print(information)
        num = input("enter a number of the user you would like to DM ")
        send_text(socket_test_client, num)
        ans = recv(socket)
        if ans[0]== "ERR":
            print(ans[1])
        else:
            return num

def get_old_chat():
    information = recv(socket_test_client)[1]
    print(information)

def getdata(client):
    while True:
        information = recv(client)[1].encode()
        if information == b"1":
            break
        elif information == b"":
            continue
        print("\n" + information.decode())
def send_data():
    while True:
        msg = input("")
        if msg == "exit":
            send_error(socket_test_client, "1")
            break
        else:
            send_text(socket_test_client, msg)
    time.sleep(0.4)


HOST = "62.60.178.229"
#HOST = "127.0.0.1"
PORT = 10006

socket_test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_test_client.connect((HOST, PORT))

connect()
while True:

    if choose_DM() == "exit":
        break

    get_old_chat()

    get_data = threading.Thread(target = getdata, args = [socket_test_client])
    get_data.start()
    try:
        send_data()
    except ConnectionAbortedError:
        print("bye")


socket_test_client.close()


