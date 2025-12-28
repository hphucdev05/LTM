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

    #Hàm kết nối tới server
    def connect(self):
        try:
            self.client.connect((SERVER_IP, PORT))
            self.client.settimeout(None)
            self.connected = True
            threading.Thread(target=self.receive_loop, daemon=True).start()
            return True
        except Exception as e:
            print(f"[NET] Connection error: {e}")
            return False

        #Luồng nhận dữ liệu từ server
        def receive_loop(self):
        buffer = b''     
        while self.connected:
            try:
                data = self.client.recv(4096)  #nhận tối đa 4096 byte
                if not data:
                    break
                buffer += data

                while len(buffer) >= 4:
                    length = int.from_bytes(buffer[:4], 'big')    #độ dài messages
                    if len(buffer) >= 4 + length:
                        msg_data = buffer[4:4 + length]
                        buffer = buffer[4 + length:]
                        try:
                            msg = json.loads(msg_data.decode('utf-8'))
                            self.msg_queue.append(msg)
                        except:
                            pass
                    else:
                        break
            except:
                self.connected = False
                break

    #Dữ liệu từ client lên server
    def send(self, data):
        if self.connected:
            try:
                message = json.dumps(data).encode('utf-8')
                length = len(message)
                self.client.sendall(length.to_bytes(4, 'big') + message)
            except Exception as e:
                print(f"[NET] Send error: {e}")
                self.connected = False
