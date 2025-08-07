import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = '127.0.0.1'
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

root = tk.Tk()
root.title("Client - Tic Tac Toe")

board = [""] * 9
buttons = []
my_turn = False
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
        chat_box.insert(tk.END, f"Client: {msg}\n")
        try:
            client.send(f"chat:{msg}".encode())
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
    if winner == "O":
        messagebox.showinfo("Game Over", "Client wins!")
    elif winner == "X":
        messagebox.showinfo("Game Over", "Server wins!")
    else:
        messagebox.showinfo("Game Over", "It's a draw!")

def click(i):
    global my_turn, game_over
    if not my_turn or board[i] or game_over:
        return
    board[i] = "O"
    buttons[i].config(text="O", state=tk.DISABLED)
    try:
        client.send(f"move:{i}".encode())
    except:
        pass
    winner = check_winner()
    if winner:
        try:
            client.send(f"gameover:{winner}".encode())
        except:
            pass
        end_game(winner)
    else:
        my_turn = False

def receive():
    global my_turn, game_over
    while True:
        try:
            data = client.recv(1024).decode()
        except:
            break
        if data.startswith("move:"):
            idx = int(data.split(":")[1])
            board[idx] = "X"
            buttons[idx].config(text="X", state=tk.DISABLED)
            winner = check_winner()
            if winner:
                end_game(winner)
            else:
                my_turn = True
        elif data.startswith("chat:"):
            msg = data.split(":",1)[1]
            chat_box.insert(tk.END, f"Server: {msg}\n")
        elif data.startswith("gameover:"):
            winner = data.split(":")[1]
            end_game(winner)
        elif data.startswith("restart:"):
            restart_game()
        elif data.startswith("exit:"):
            messagebox.showinfo("Info", "Server has exited the game.")
            try:
                client.close()
            except:
                pass
            root.destroy()
            break

def restart_game():
    global board, game_over, my_turn
    board = [""] * 9
    game_over = False
    my_turn = False
    for button in buttons:
        button.config(text="", state=tk.NORMAL)

def on_exit():
    try:
        client.send("exit:".encode())  #NOTIFY THE SERVER TO EXIT
        client.close()       # CLOSE CLIENT SOCKET
    except:
        pass
    root.destroy()             # CLOSES GUI WINDOW

threading.Thread(target=receive, daemon=True).start()

frame = tk.Frame(root)
frame.pack()
for i in range(9):
    b = tk.Button(frame, text="", width=10, height=4, command=lambda i=i: click(i))
    b.grid(row=i//3, column=i%3)
    buttons.append(b)

tk.Button(root, text="Restart Game", command=lambda: [restart_game(), client.send("restart:".encode())]).pack(pady=5)
#CALLING CLOSE 
tk.Button(root, text="Exit Game", command=on_exit).pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_exit)
root.mainloop()
