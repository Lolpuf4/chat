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

            datetime1 = datetime.datetime(date1[2], date1[1], date1[0], time1[0], time1[1], time1[2])
            datetime2 = datetime.datetime(date2[2], date2[1], date2[0], time2[0], time2[1], time2[2])


            if datetime1 > datetime2:
                temp = msgs[j]
                msgs[j] = msgs[j+1]
                msgs[j+1] = temp


def organize_list(username):
    ans = {}
    senderID = execute_command(f"SELECT id FROM users WHERE username = {username};", "admin", "123", "messenger")[0]["id"]
    for DM_user in get_usernames(username):

        receiverID = execute_command(f"SELECT id FROM users WHERE username = {DM_user};", "admin", "123", "messenger")[0]["id"]

        old_msgs_sender = execute_command(
            f"SELECT * FROM message_history JOIN users ON message_history.senderID = users.id "
            f"JOIN messages ON message_history.msgID = messages.id WHERE message_history.receiverID = {receiverID} AND message_history.senderID = {senderID};",
            "admin", "123", "messenger")

        old_msgs_receiver = execute_command(
            f"SELECT * FROM message_history JOIN users ON message_history.senderID = users.id "
            f"JOIN messages ON message_history.msgID = messages.id WHERE message_history.receiverID = {senderID} AND message_history.senderID = {receiverID};",
            "admin", "123", "messenger")

        old_msgs = old_msgs_sender + old_msgs_receiver

        sort_chat_msgs(old_msgs)

        new_old_msgs = {"msgs": old_msgs, "senderID": senderID}
        ans[DM_user] = new_old_msgs
    return ans



socket_user = {}
user_DMuser = {}
def get_username(client):
    username = ""
    attempts = 0
    for i in range(3):
        username = recv(client)[1]
        password = recv(client)[1]
        if not execute_command(f"SELECT username FROM users WHERE username = {username} AND password = {password};", "admin", "123", "messenger"):
            send_error(client, "authentication failed")
            attempts +=1
            if attempts == 3:
                return None

        else:
            send_text(client, "1")

            break

    return username


def get_usernames(username):
    DMs = []
    for i in execute_command(f"SELECT username FROM users WHERE username != {username};", "admin", "123", "messenger"):
        DMs.append(i["username"])
    return DMs



def send_msg(client, username):
    while True:

        information = recv(client)

        print("information", information)
        if information[0] == "ERR" and information[1] == "1":
            print("stopped receiving information")
            send_error(client, "1")
            break
        elif information[0] == "DIC":
            data = json.loads(information[1])
            DM_user = data["user"]
            original_message = data["msg"]

        date = datetime.datetime.now().strftime("%d/%m/%y")
        time = datetime.datetime.now().strftime("%H:%M:%S")

        msgID = execute_command(f"INSERT INTO messages (text, date, time) VALUES ({original_message}, {date}, {time});", "admin", "123", "messenger")
        senderID = execute_command(f"SELECT id FROM users WHERE username = {username};", "admin", "123", "messenger")[0]["id"]
        receiverID = execute_command(f"SELECT id FROM users WHERE username = {DM_user};", "admin", "123", "messenger")[0]["id"]
        execute_command(f"INSERT INTO message_history (senderID, receiverID, msgID) VALUES ({senderID}, {receiverID}, {msgID});", "admin", "123", "messenger")

        last_msg = execute_command(
            f"SELECT * FROM message_history JOIN users ON message_history.senderID = users.id "
            f"JOIN messages ON message_history.msgID = messages.id WHERE message_history.receiverID = {receiverID} AND message_history.senderID = {senderID} AND messages.id = {msgID};",
            "admin", "123", "messenger")[0]

        if DM_user in socket_user:
            print(f"socket user: {socket_user}")
            recv_socket = socket_user[DM_user]
            file = open("recv_files/last_msg.json", "w", encoding = "UTF-8")
            json.dump(last_msg, file)
            file.close()
            send_file(recv_socket, "recv_files/last_msg.json", "JSN")
def handle_client(client, address):
    print(f"working on: {address}")
    username = get_username(client)
    if not username:
        return

    socket_user[username] = client
    while True:
        all_chat_history = organize_list(username)
        print(all_chat_history)

        file = open("temp.json", "w", encoding="UTF-8")
        json.dump(all_chat_history, file)
        file.close()

        send_file(client, "temp.json", "JSN")


        send_msg(client, username)
    # finally:
    #     del socket_user[username]
    #     del user_DMuser[username]
    #     client.close()


#HOST = "0.0.0.0"
HOST = "127.0.0.1"
PORT = 10008

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