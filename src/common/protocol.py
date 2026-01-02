import socket

HOST = '127.0.0.1'
PORT = 65432
FORMAT = 'utf-8'

HEADER_SIZE = 1024
CHUNK_SIZE = 4096 # Nếu file quá lớn (6GB), bạn có thể tăng lên 65536 (64KB) để nhanh hơn

CMD_LOGIN    = "LOGIN"
CMD_LIST     = "LIST"
CMD_UPLOAD   = "UPLOAD"
CMD_DOWNLOAD = "DOWNLOAD"
CMD_EXIT     = "EXIT"

SEPARATOR = "|"