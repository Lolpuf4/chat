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
    file = open(information, "r", encoding="UTF-8")
    data = json.load(file)
    file.close()
    while True:
        full_msg = ""

        for id in data:
            full_msg += f"{id}: {data[id]}\n"
        print(full_msg)

        num = input("enter a number of the user you would like to DM ")
        if num in data or num == "exit":
            send_text(socket_test_client, num)

            return num, data.get(num)
        else:
            print("wrong number")


def get_old_chat():
    information = recv(socket_test_client)[1]

    file = open(information, "r", encoding = "UTF-8")
    data = json.load(file)
    file.close()
    print(data)
    chat_data = data[DM_name]

    chat = ""
    for record in chat_data["msgs"]:
        if record["message_history.senderID"] == chat_data["senderID"]:
            chat += f"                       {record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"
        else:
            chat += f"{record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"

    print(chat)


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
    time.sleep(0.5)


#HOST = "62.60.178.229"
HOST = "127.0.0.1"
PORT = 10008

socket_test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_test_client.connect((HOST, PORT))

connect()
while True:

    DM_id, DM_name = choose_DM()
    if DM_id == "exit":
        break

    get_old_chat()

    get_data = threading.Thread(target = getdata, args = [socket_test_client])
    get_data.start()
    try:
        send_data()
    except ConnectionAbortedError:
        print("bye")


socket_test_client.close()


