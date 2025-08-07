import socket
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os  

HOST = '0.0.0.0'
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for connection...")

conn, addr = server.accept()
print(f"Connected by {addr}")

root = tk.Tk()
root.title("Server - Tic Tac Toe")

board = [""] * 9
buttons = []
my_turn = True
game_over = False

chat_frame = tk.Frame(root)
chat_frame.pack()

chat_box = tk.Text(chat_frame, height=10, width=50)
chat_box.pack()

entry = tk.Entry(chat_frame, width=40)
entry.pack(side=tk.LEFT)

def send_chat():
    msg = entry.get()
    if msg:
        chat_box.insert(tk.END, f"Server: {msg}\n")
        try:
            conn.send(f"chat:{msg}".encode())
        except:
            pass
        entry.delete(0, tk.END)

tk.Button(chat_frame, text="Send", command=send_chat).pack(side=tk.RIGHT)

def check_winner():
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] != "":
            return board[a]
    if all(board):
        return "Draw"
    return None

def end_game(winner):
    global game_over
    game_over = True
    print("Inside end_game. Winner:", winner)  
    if winner == "X":
        messagebox.showinfo("Game Over", "Server wins!")
        log_winner("Server")
    elif winner == "O":
        messagebox.showinfo("Game Over", "Client wins!")
        log_winner("Client")
    else:
        messagebox.showinfo("Game Over", "It's a draw!")
        log_winner("Draw")
    try:
        conn.send(f"gameover:{winner}".encode())
    except:
        pass

def log_winner(winner):
    try:
        print("Logging winner:", winner) 
        path = os.path.abspath("game_log.txt")
        print("Writing to:", path)  # Shows file path
        with open("game_log.txt", "a") as f:
            f.write(f"{datetime.now()} - Winner: {winner}\n")
        print("Log write successful.")  # Confirm write
    except Exception as e:
        print("Log write failed:", e)  #  Show error if any

def click(i):
    global my_turn, game_over
    if not my_turn or board[i] or game_over:
        return
    board[i] = "X"
    buttons[i].config(text="X", state=tk.DISABLED)
    try:
        conn.send(f"move:{i}".encode())
    except:
        pass
    winner = check_winner()
    if winner:
        end_game(winner)
    else:
        my_turn = False

def receive():
    global my_turn, game_over
    while True:
        try:
            data = conn.recv(1024).decode()
        except:
            break
        if data.startswith("move:"):
            idx = int(data.split(":")[1])
            board[idx] = "O"
            buttons[idx].config(text="O", state=tk.DISABLED)
            winner = check_winner()
            if winner:
                end_game(winner)
            else:
                my_turn = True
        elif data.startswith("chat:"):
            msg = data.split(":",1)[1]
            chat_box.insert(tk.END, f"Client: {msg}\n")
        elif data.startswith("restart:"):
            restart_game()
        elif data.startswith("exit:"):
            messagebox.showinfo("Info", "Client has exited the game.")
            try:
                conn.close()
            except:
                pass
            root.destroy()
            break

def restart_game():
    global board, game_over, my_turn
    board = [""] * 9
    game_over = False
    my_turn = True
    for button in buttons:
        button.config(text="", state=tk.NORMAL)

def on_exit():
    try:
        conn.send("exit:".encode())
        conn.close()
    except:
        pass
    root.destroy()

threading.Thread(target=receive, daemon=True).start()

frame = tk.Frame(root)
frame.pack()
for i in range(9):
    b = tk.Button(frame, text="", width=10, height=4, command=lambda i=i: click(i))
    b.grid(row=i//3, column=i%3)
    buttons.append(b)

tk.Button(root, text="Restart Game", command=lambda: [restart_game(), conn.send("restart:".encode())]).pack(pady=5)
tk.Button(root, text="Exit Game", command=on_exit).pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
