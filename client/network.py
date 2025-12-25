# client/network.py
import socket
import threading
import json
from .constants import SERVER_IP, PORT

class NetworkClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #Tạo socket IPv4 + TCP
        self.client.settimeout(3)
        self.connected = False
        self.my_id = None
        self.room_id = None
        self.turn = None
        self.msg_queue = []   # Hàng đợi tin nhắn từ server
