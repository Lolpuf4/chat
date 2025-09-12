import socket
import threading
import json
from protocol import*
from errors import*
HOST = "62.60.178.229"
PORT = 10002

def execute_command(command, user, password, database = ""):
    socket_test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_test_client.connect((HOST, PORT))
    if "/" in command and database == "":
        raise NoDatabaseError()
    try:
        send_text(socket_test_client, user)
        send_text(socket_test_client, password)
        send_text(socket_test_client, database)
        send_text(socket_test_client, command)

        information = recv(socket_test_client)
        if information[0] == "TXT":
            return information[1]
        elif information[0] == "ERR":
            raise DataBaseError(information[1])
        elif information[0] == "JSN":
            file = open(information[1], "r", encoding="UTF-8")
            file_info = json.load(file)
            file.close()
            return file_info
    except DataBaseError as e:
        print(e)
    finally:
        socket_test_client.close()





