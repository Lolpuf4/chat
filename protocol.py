HEADER_SIZE = 24
def get_info(socket, size:int):
    left_to_get = size
    information = b""
    while left_to_get != 0:
        temp_info = socket.recv(left_to_get)
        if len(temp_info) == 0:
            raise ConnectionError ("didn't get enough information")
        left_to_get -= len(temp_info)
        information += temp_info
    return information

def recv(socket):
    header = get_info(socket, HEADER_SIZE)
    header = header.decode()
    header_split = header.split(",")
    data_type = header_split[0]
    size = header_split[1]
    file_name = header_split[2]
    information = get_info(socket, int(size))
    file_name = file_name.replace("*", "")[:-1]

    if data_type == "TXT" or data_type == "ERR":
        return [data_type, information.decode()]
    else:
        file = open(f"recv_files/{file_name}", "wb")
        file.write(information)
        file.close()
        return [data_type, f"recv_files/{file_name}"]


def _send(socket_recv, data:bytes, file_path:str, type):
    data_size = len(data)
    len_data_size = len(str(data_size))
    len_path = len(file_path)
    if len_data_size > 8:
        raise ConnectionError("text too large")
    header = f"{type},{(8 - len_data_size) * "0" + str(data_size)},{(10 - len_path) * "*" + file_path}:"
    socket_recv.sendall(header.encode())
    socket_recv.sendall(data)


def send_text(socket_recv, text:str):
    _send(socket_recv, text.encode(), "", "TXT")

def send_error(socket_recv, text:str):
    _send(socket_recv, text.encode(), "", "ERR")

def send_file(socket_recv, file_path:str, type:str):
    file = open(file_path, "rb")
    data = file.read()
    _send(socket_recv, data, file_path, type)
    file.close()