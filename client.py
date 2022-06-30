from multiprocessing.connection import wait
import socket
import sys
import threading
import datetime

PORT = 1373
MESSAGE_LENGTH_SIZE = 64
ENCODING = 'ascii'
ping_response = True
Alive = False

def send_msg(client, msg):
    message = msg.encode(ENCODING)
    msg_length = len(message)
    msg_length = str(msg_length).encode(ENCODING)
    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
    client.send(msg_length)
    client.send(message)


def publish(client, topic, body):
    msg = "Publish " + topic
    for b in body:
        msg += " " + b
    send_msg(client, msg)


def subscribe(client, topics):
    message = "Subscribe"
    for topic in topics:
        message += " " + topic
    send_msg(client, message)


def quit(client):
    global Alive
    message = "Quit"
    send_msg(client, message)
    Alive = False


def pingServer(client):
    send_msg(client, "Ping")


def pingpong(client):
    global ping_response
    global Alive

    while Alive== True :
        try:
            received = client.recv(MESSAGE_LENGTH_SIZE).decode(ENCODING)
            msg_length = int(received)
            msg = client.recv(msg_length).decode(ENCODING)
        except:
            print("Connection Interrupted")
            break
        if msg == "Ping" and ping_response:
            send_msg(client, "Pong")
        elif msg == "closed":
            print("[Connection Closed]")
            client.close()
            break
        now = datetime.datetime.now()
        print("[Recieved {}] {}".format(((str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))), msg))
    #connectionSetup()


def input_args_handler(client):
    global ping_response
    global Alive
    while Alive==True :
        print("Enter your command: ")
        print("- Subscribe Topic")
        print("- Publish Topic Message")
        print("- Quit")
        print("- NACK ping")
        print("- ACK ping")
        print("- Ping ")
        input_args = input().split()
        print(f'Command is : {input_args[0]} ')
        command = input_args[0]
        if len(input_args) == 0:
            print("len is 0")
            continue
        if command == "Subscribe":
            if len(input_args) == 1:
                print("Invalid Format!Enter Subscribe Topic")
                continue
            subscribe(client, input_args[1:])
        else:
            if command == "Publish":
                if len(input_args) == 1 or len(input_args) == 2:
                    print("Invalid Format! Enter Publish Topic Message")
                    continue
                publish(client, input_args[1], input_args[2:])
            else:
                if command == "NACK ping":
                    ping_response = False
                else:
                    if command == "ACK ping":
                        ping_response = True
                    else:
                        if command == "Quit":
                            quit(client)
                        else:
                            if command == "Ping":
                                print("Pinging Server...")
                                pingServer(client)


def connectionSetup():
    global Alive
    try:
        address = socket.gethostbyname(socket.gethostname())
        host_information = (address, PORT)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(host_information)
        Alive = True
        thread = threading.Thread(target=pingpong, args=(client,))
        thread.start()
        print("Connected to Server")
        input_args_handler(client)
    except Exception as e:
        print(e)
        print("Failed to connect..trying again")
        connectionSetup()


def main():
    address = socket.gethostbyname(socket.gethostname())
    try:
        if len(sys.argv) == 1:
            connectionSetup()
    except Exception as e:
        print(e)
        connectionSetup()


if __name__ == '__main__':
    main()
