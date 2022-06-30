import socket
from sys import argv
import threading
import time
import datetime


PORT = 1373
MESSAGE_LENGTH = 64
ENCODING = 'ascii'
sub_list = {}


def Send(server, msg):
    message = msg.encode(ENCODING)
    msg_length = len(message)
    msg_length = str(msg_length).encode(ENCODING)
    msg_length += b' ' * (MESSAGE_LENGTH - len(msg_length))
    server.send(msg_length)
    server.send(message)


def Subscribe(conn, subjects):
    for subject in subjects:
        if subject in sub_list.keys():
            if conn not in sub_list[subject]:
                sub_list[subject].append(conn)
        else:
            sub_list[subject] = [conn]
    msg = "Subscribing on :"
    for subject in sub_list.keys():
        if conn in sub_list[subject]:
            msg += " " + subject
    Send(conn, msg)


def publish(subject, msg):
    message = "New Message Published! => [{}]".format(subject)
    for m in msg:
        message += " " + m
    for t in sub_list.keys():
        if t == subject:
            for conn in sub_list[t]:
                Send(conn, message)
            break



now = datetime.datetime.now()
print(now.year, now.month, now.day, now.hour, now.minute, now.second)


def ping_controller(start_ping, cnn_shdown, ping_lst, conn, address):
    while True:
        if (time.time() - start_ping) >= 15.0:
            if len(ping_lst) != 0:
                print("[No response to Ping!] {} time(s): {}".format(len(ping_lst), address))
            if len(ping_lst) == 3:
                break
            start_ping = time.time()

            Send(conn, "Ping")
            ping_lst.append(1)
        if len(cnn_shdown) > 0:
            break


def general_Handler(conn, address):
    print("[New Connection] {}".format(address))
    start_ping = time.time()
    cnn_shdown = []
    ping_lst = []
    t = threading.Thread(target=client_handler, args=(conn, address, cnn_shdown, ping_lst))
    t.start()
    ping_controller(start_ping, cnn_shdown, ping_lst, conn, address)

    for subscriber in sub_list.keys():
        if conn in sub_list[subscriber]:
            sub_list[subscriber].remove(conn)
    Send(conn, "closed")

    print("[Connection Closed] {}".format(address))


def client_handler(conn, address, cnn_shdown, ping_answer):
    while True:
        try:
            fromClient = conn.recv(MESSAGE_LENGTH).decode(ENCODING)
            msg_length = int(fromClient)
            msg = conn.recv(msg_length).decode(ENCODING)
        except:
            print("Connection has been interrupted!".format(address))
            break
        now = datetime.datetime.now()
        print("[ Recieved {}] [{}] {}".format(((str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))),
                                                     address, msg))
        msg = msg.split()
        if msg[0] == "Pong":
            del ping_answer[:]

        elif msg[0] == "Publish":
            try:
                publish(msg[1], msg[2:])
                Send(conn, "Published")
            except:
                Send(conn, "Publishing ERROR")
        elif msg[0] == "Subscribe":
            try:
                Subscribe(conn, msg[1:])
                Send(conn, "Subscribed".format(msg[1:]))
            except:
                Send(conn, "Subscribing Failed")

        elif msg[0] == "Ping":
            Send(conn,"Pong")

        elif msg[0] == "Quit":
            cnn_shdown.append(1)
            break


def startServer(server):
    server.listen()
    while True:
        conn, address = server.accept()
        thread = threading.Thread(target=general_Handler, args=(conn, address))
        thread.start()


def main():
    address = socket.gethostbyname(socket.gethostname())
    host_information = (address, PORT)
    print(host_information)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(host_information)
        startServer(server)


if __name__ == '__main__':
    main()