# import socket
#
# HOST = "127.0.0.1"
# PORT = 10000
#
# socket_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# socket_test.bind((HOST, PORT))
# socket_test.listen(1)
# print("server working")
# info = socket_test.accept()
# socket_client = info[0]
# address = info[1]
# print(address)
# full_msg = b""
# while True:
#     information = socket_client.recv(2)
#     if information == b"":
#         print("stopped receiving information")
#         break
#     print("got bytes:" + str(len(information)))
#     full_msg += information
# print(full_msg.decode())
#
# socket_client.close()
# socket_test.close()



import socket
import threading
import datetime
import json

from DBhelper import execute_command
from protocol import*

def sort_chat_msgs(msgs):
    for i in range(len(msgs)):
        for j in range(len(msgs) - 1):
            time1 = msgs[j]["messages.time"]
            time2 = msgs[j + 1]["messages.time"]
            date1 = msgs[j]["messages.date"]
            date2 = msgs[j + 1]["messages.date"]

            time1 = list(map(int, time1.split(":")))
            time2 = list(map(int, time2.split(":")))
            date1 = list(map(int, date1.split("/")))
            date2 = list(map(int, date2.split("/")))

            # time1 = datetime.time(time1[0], time1[1], time1[2])
            # time2 = datetime.time(time2[0], time2[1], time2[2])
            # date1 = datetime.date(date1[0], date1[1], date1[2])
            # date2 = datetime.date(date2[0], date2[1], date2[2])

            datetime1 = datetime.datetime(date1[0], date1[1], date1[2], time1[0], time1[1], time1[2])
            datetime2 = datetime.datetime(date2[0], date2[1], date2[2], time2[0], time2[1], time2[2])

            if datetime1 > datetime2:
                temp = msgs[j]
                msgs[j] = msgs[j+1]
                msgs[j+1] = temp




socket_user = {}
user_DMuser = {}
def get_username(client):
    username = recv(client)[1]
    print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",username)
    password = recv(client)[1]


    if not execute_command(f"SELECT username FROM users WHERE username = {username} AND password = {password};", "admin", "123", "messenger"):
        send_error(client, "authentication failed")
        return None
    else:
        send_text(client, "1")

        return username





def choose_DM(username, client):
    choose_DM_msg = ""
    DMs = {}
    num = 1
    for i in execute_command(f"SELECT username FROM users WHERE username != {username};", "admin", "123", "messenger"):
        DMs[num] = i["username"]
        choose_DM_msg += f"{num}: {i["username"]}\n"
        num += 1

    send_text(client, choose_DM_msg)

    information = recv(client)[1]
    DM_user = DMs[int(information)]
    return DM_user

def send_msg(DM_user, client, username):
    while True:

        information = recv(client)[1].encode()

        print("information", information)
        if information == b"1":
            print("stopped receiving information")
            send_error(client, "1")

            del user_DMuser[username]
            break
        date = datetime.datetime.now().strftime("%d/%m/%y")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        original_message = information.decode()
        full_message = date + "   " + time + ":   " + original_message

        msgID = execute_command(f"INSERT INTO messages (text, date, time) VALUES ({original_message}, {date}, {time});", "admin", "123", "messenger")
        senderID = execute_command(f"SELECT id FROM users WHERE username = {username};", "admin", "123", "messenger")[0]["id"]
        receiverID = execute_command(f"SELECT id FROM users WHERE username = {DM_user};", "admin", "123", "messenger")[0]["id"]
        execute_command(f"INSERT INTO message_history (senderID, receiverID, msgID) VALUES ({senderID}, {receiverID}, {msgID});", "admin", "123", "messenger")

        if DM_user in socket_user and user_DMuser[DM_user] == username:
            recv_user = socket_user[DM_user]
            send_text(recv_user, full_message)
def handle_client(client, address):
    print(f"working on: {address}")
    username = get_username(client)
    if not username:
        return
    while True:
        socket_user[username] = client
        DM_user = choose_DM(username, client)
        user_DMuser[username] = DM_user
        senderID = execute_command(f"SELECT id FROM users WHERE username = {username};", "admin", "123", "messenger")[0]["id"]
        receiverID = execute_command(f"SELECT id FROM users WHERE username = {DM_user};", "admin", "123", "messenger")[0]["id"]

        old_msgs_sender = execute_command(f"SELECT * FROM message_history JOIN users ON message_history.senderID = users.id "
                                   f"JOIN messages ON message_history.msgID = messages.id WHERE message_history.receiverID = {receiverID} AND message_history.senderID = {senderID};", "admin", "123", "messenger")

        old_msgs_receiver = execute_command(
            f"SELECT * FROM message_history JOIN users ON message_history.senderID = users.id "
            f"JOIN messages ON message_history.msgID = messages.id WHERE message_history.receiverID = {senderID} AND message_history.senderID = {receiverID};",
            "admin", "123", "messenger")

        old_msgs = old_msgs_sender + old_msgs_receiver


        sort_chat_msgs(old_msgs)

        amount_of_spaces = 10

        chat = ""

        for record in old_msgs:
            if record["message_history.receiverID"] == receiverID:
                chat += f"                       {record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"
            else:
                chat += f"{record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"

        send_text(client, chat)


        send_msg(DM_user, client, username)
    # finally:
    #     del socket_user[username]
    #     del user_DMuser[username]
    #     client.close()


#HOST = "0.0.0.0"
HOST = "127.0.0.1"
PORT = 10001

socket_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket_test.bind((HOST, PORT))
socket_test.listen(1)

users = []
print("server working")
try :
    while True:
        info = socket_test.accept()
        socket_client = info[0]
        address = info[1]

        thread = threading.Thread(target = handle_client, args=[socket_client, address])

        thread.start()

except KeyboardInterrupt:
    print("closing")

finally:
    socket_test.close()