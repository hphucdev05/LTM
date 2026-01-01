import socket
import threading
import json
import random

HOST = '0.0.0.0' # Nghe tất cả IP để LAN chơi được
PORT = 65432

rooms = {}
# Cấu trúc rooms:
# rooms[rid] = {
#    "type": "public"/"private",
#    "players": { pid: { "conn": conn, "ships": [], "hits_left": 0 } },
#    "turn": pid,
#    "state": "waiting"/"playing"
# }

def send_msg(conn, data):
    try:
        message = json.dumps(data).encode('utf-8')
        length = len(message)
        conn.sendall(length.to_bytes(4, 'big') + message)
    except Exception as e:
        print(f"[SERVER] Failed to send message: {e}")

def broadcast(room_id, data, exclude=None):
    if room_id not in rooms:
        return
    for pid, p_data in rooms[room_id]["players"].items():
        if pid != exclude:
            send_msg(p_data["conn"], data)

def handle_client(conn, addr):
    print(f"New connection: {addr}")
    player_id = str(random.randint(1000, 9999))
    current_room = None
    
    try:
        send_msg(conn, {"action": "id", "player_id": player_id})
        
        buffer = b''
        while True:
            try:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk

                while len(buffer) >= 4:
                    length = int.from_bytes(buffer[:4], 'big')
                    if len(buffer) >= 4 + length:
                        msg_data = buffer[4:4 + length]
                        buffer = buffer[4 + length:]

                        try:
                            msg = json.loads(msg_data.decode('utf-8'))
                            action = msg.get("action")

                            # ===== XỬ LÝ ACTION =====
                            if action == "create_room":
                                room_id = str(random.randint(1000, 9999))
                                rooms[room_id] = {
                                    "type": "private",
                                    "players": { player_id: {"conn": conn, "ships": [], "hits_left": 0} },
                                    "turn": None,
                                    "state": "waiting"
                                }
                                current_room = room_id
                                send_msg(conn, {"action": "room_created", "room_id": room_id, "room_type": "private"})

                            elif action == "join_room":
                                rid = msg.get("room_id")
                                if rid in rooms and len(rooms[rid]["players"]) < 2:
                                    rooms[rid]["players"][player_id] = {"conn": conn, "ships": [], "hits_left": 0}
                                    current_room = rid
                                    room_type = rooms[rid].get("type", "public")
                                    send_msg(conn, {"action": "match_found", "room_id": rid, "room_type": room_type})
                                    broadcast(rid, {"action": "match_found", "room_id": rid})
                                else:
                                    send_msg(conn, {"action": "error", "msg": "Phòng đầy hoặc không tồn tại"})

                            elif action == "random_match":
                                found = False
                                # Tìm phòng PUBLIC, < 2 người, và đang WAITING
                                for rid, r_data in rooms.items():
                                    if r_data.get("type", "public") == "public" and len(r_data["players"]) < 2 and r_data["state"] == "waiting":
                                        r_data["players"][player_id] = {"conn": conn, "ships": [], "hits_left": 0}
                                        current_room = rid
                                        send_msg(conn, {"action": "match_found", "room_id": rid, "room_type": "public"})
                                        broadcast(rid, {"action": "match_found", "room_id": rid})
                                        found = True
                                        break
                                if not found:
                                    # Tạo phòng mới
                                    rid = str(random.randint(1000, 9999))
                                    rooms[rid] = {
                                        "type": "public",
                                        "players": { player_id: {"conn": conn, "ships": [], "hits_left": 0} },
                                        "turn": None,
                                        "state": "waiting"
                                    }
                                    current_room = rid
                                    send_msg(conn, {"action": "room_created", "room_id": rid, "room_type": "public"})

                            elif action == "ready":
                                if current_room:
                                    client_ships = msg.get("ships", [])
                                    total_health = 0
                                    parsed_ships = []
                                    for s in client_ships:
                                        parsed_ships.append({
                                            "cells": [tuple(c) for c in s["cells"]],
                                            "hits": []
                                        })
                                        total_health += len(s["cells"])
                                    
                                    rooms[current_room]["players"][player_id]["ships"] = parsed_ships
                                    rooms[current_room]["players"][player_id]["hits_left"] = total_health

                                    players = rooms[current_room]["players"]
                                    if len(players) == 2:
                                        all_ready = all(p["hits_left"] > 0 for p in players.values())
                                        if all_ready:
                                            rooms[current_room]["state"] = "playing"
                                            starter = list(players.keys())[0]
                                            rooms[current_room]["turn"] = starter
                                            broadcast(current_room, {"action": "game_start", "turn": starter})

                            elif action == "fire":
                                if not current_room: continue
                                room_data = rooms[current_room]
                                if room_data["turn"] != player_id:
                                    continue

                                x, y = msg["x"], msg["y"]
                                # Tìm ID đối thủ
                                target_ids = [pid for pid in room_data["players"] if pid != player_id]
                                if not target_ids: continue # Phòng khi đối thủ out giữa chừng
                                target_id = target_ids[0]

                                target_data = room_data["players"][target_id]
                                
                                status = "miss"
                                for ship in target_data["ships"]:
                                    if (x, y) in ship["cells"]:
                                        if (x, y) not in ship["hits"]:
                                            ship["hits"].append((x, y))
                                            target_data["hits_left"] -= 1
                                            status = "hit"
                                            if len(ship["hits"]) == len(ship["cells"]):
                                                status = "sunk"
                                        else:
                                            status = "hit" # Bắn lại chỗ đã trúng
                                        break 
                                
                                room_data["turn"] = target_id
                                broadcast(current_room, {
                                    "action": "update_board",
                                    "x": x, "y": y,
                                    "status": status,
                                    "shooter": player_id,
                                    "turn": target_id
                                })

                                if target_data["hits_left"] <= 0:
                                    broadcast(current_room, {
                                        "action": "game_over",
                                        "winner": player_id
                                    })
                                    # Reset trạng thái về waiting để chơi ván mới
                                    room_data["state"] = "waiting"
                                    room_data["turn"] = None
                                    for p in room_data["players"].values():
                                        p["hits_left"] = 0
                                        p["ships"] = []

                            elif action == "leave_room":
                                if current_room and current_room in rooms:
                                    broadcast(current_room, {"action": "opponent_left"}, exclude=player_id)
                                    
                                    if player_id in rooms[current_room]["players"]:
                                        del rooms[current_room]["players"][player_id]
                                    
                                    # Nếu phòng trống thì xóa
                                    if not rooms[current_room]["players"]:
                                        del rooms[current_room]
                                    else:
                                        # [QUAN TRỌNG] Nếu còn người, reset trạng thái về waiting để người đó được match
                                        rooms[current_room]["state"] = "waiting"
                                        rooms[current_room]["turn"] = None
                                        # Reset data người ở lại (tùy chọn, để họ phải ready lại)
                                        for p in rooms[current_room]["players"].values():
                                            p["hits_left"] = 0
                                            p["ships"] = []
                                    
                                    current_room = None

                        except Exception as e:
                            print(f"[SERVER] Error parsing message: {e}")
                            continue
                    else:
                        break
            except Exception as e:
                print(f"[SERVER] Connection error: {e}")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # XỬ LÝ NGẮT KẾT NỐI ĐỘT NGỘT (Tắt app)
        print(f"Client disconnected: {player_id}")
        conn.close()
        if current_room and current_room in rooms:
            broadcast(current_room, {"action": "opponent_left"}, exclude=player_id)
            
            if player_id in rooms[current_room]["players"]:
                del rooms[current_room]["players"][player_id]
            
            if not rooms[current_room]["players"]:
                del rooms[current_room]
            else:
                # [QUAN TRỌNG] Reset về waiting cho người ở lại
                rooms[current_room]["state"] = "waiting"
                rooms[current_room]["turn"] = None
                for p in rooms[current_room]["players"].values():
                    p["hits_left"] = 0
                    p["ships"] = []

# Main Server Loop
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
except Exception as e:
    print(f"Server startup error: {e}")