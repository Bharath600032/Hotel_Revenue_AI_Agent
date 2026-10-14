import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('0.0.0.0', 8000))
    print("SUCCESS: Port 8000 can be bound!")
    s.close()
except Exception as e:
    print("FAILED to bind port 8000:", e)
