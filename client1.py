import socket
import threading
import os
import datetime
import json

from errors import*
from protocol import*
from os.path import exists


def connect():
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
            username = input("enter a username for yourself ")
            password = input("enter a password for yourself ")

    else:
        username = input("enter a username for yourself ")
        password = input("enter a password for yourself ")
    send_text(socket_test_client, username)
    send_text(socket_test_client, password)
    information = recv(socket_test_client)
    if information[0] == "ERR":
        raise ServerError(information[1])
    elif information[0] == "TXT":
        file = open("cookie.json", "w", encoding = "UTF-8")
        file_info = {"username":username, "password" : password, "date": datetime.date.today().strftime("%Y/%m/%d")}
        json.dump(file_info, file)
        file.close()
        print("you logged on.")

def choose_DM():
    information = recv(socket_test_client)[1]
    print(information)
    num = input("enter a number of the user you would like to DM ")
    send_text(socket_test_client, num)

def get_old_chat():
    information = recv(socket_test_client)[1]
    print(information)

def getdata(client):
    while True:

        information = recv(client)[1].encode()
        if information == b"" or information == b"1":
            break
        print("\n" + information.decode())
def send_data():
    while True:
        msg = input("")
        if msg == "":
            send_error(socket_test_client, "1")

        else:
            send_text(socket_test_client, msg)


HOST = "62.60.178.229"
PORT = 10001
while True:
    socket_test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_test_client.connect((HOST, PORT))

    connect()
    choose_DM()
    get_old_chat()

    get_data = threading.Thread(target = getdata, args = [socket_test_client])
    get_data.start()
    try:
        send_data()
    except ConnectionAbortedError:
        print("bye")


    socket_test_client.close()


