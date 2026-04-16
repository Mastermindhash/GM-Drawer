#------------- IMPORTATIONS -----------------

import tkinter as tk
from PIL import Image, ImageDraw
from tkinter import filedialog, colorchooser
  
#-------------- Programme Principal ---------

lx, ly, col = None, None, 'pink'
ID = []
history, mirai = [], []
current_action, actions = [], []
canvas_w, canvas_h = 500, 400 
current_tool = ''
w = 1
bg_col = 'white'
preview_id = None

image = Image.new("RGB", (canvas_w, canvas_h), bg_col)
draw = ImageDraw.Draw(image)


fen = tk.Tk()
fen.title("----------------------------------------GM-Drawer------------------------------------- ")
can = tk.Canvas(fen, width=canvas_w, height=canvas_h, bg=bg_col)
can.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


#------------- fonctions -------------------

def get_canvas_size():
    can.update_idletasks()
    return can.winfo_width(), can.winfo_height()


def set_tool(tool):
    global current_tool, w
    current_tool = tool
   

def start_draw(event):
    global lx, ly, current_action, preview_id
    lx, ly = event.x, event.y
    current_action = []
    preview_id = None 


def Draw(event):
    global lx, ly, col, current_tool, current_action, w, image, draw, preview_id

    if not event:
        return

    if current_tool == 'rectangle':
        if preview_id is not None:
            can.delete(preview_id)
        preview_id = can.create_rectangle(lx, ly, event.x, event.y, fill='', outline='blue', width=w  )
        return  
       
    if current_tool == 'oval' :
        if preview_id is not None:
            can.delete(preview_id)
        preview_id = can.create_oval(lx, ly, event.x, event.y, fill='', outline='blue', width=w  )
        return  

    if current_tool == 'line' or current_tool == '':
        can.create_line(lx, ly, event.x, event.y, fill=col, width=w)
        draw.line((lx, ly, event.x, event.y), fill=col, width=w)

    elif current_tool == 'pixel':
        x0, y0 = min(lx, event.x), min(ly, event.y)
        x1, y1 = max(lx, event.x), max(ly, event.y)
        can.create_rectangle(lx, ly, event.x, event.y, fill=col, outline=col, width=w)
        draw.rectangle((x0, y0, x1, y1), fill=col, outline=col, width=w)

    elif current_tool == 'bubble':
        x0, y0 = min(lx, event.x), min(ly, event.y)
        x1, y1 = max(lx, event.x), max(ly, event.y)
        can.create_oval(lx, ly, event.x, event.y, fill=col, outline=col, width=w)
        draw.ellipse((x0, y0, x1, y1), fill=col, outline=col, width=w)

    elif current_tool == 'eraser':
        can.create_line(lx, ly, event.x, event.y, fill=bg_col, width=15)
        draw.line((lx, ly, event.x, event.y), fill=bg_col, width=15)

    current_action.append((current_tool or 'line', lx, ly, event.x, event.y, col, w))
    lx, ly = event.x, event.y


def end_draw(event):
    global history, current_action, preview_id  

    if current_tool == 'rectangle' and preview_id is not None:
        can.delete(preview_id)
        preview_id = None
        # Commit final shape to canvas + PIL
        x0, y0 = min(lx, event.x), min(ly, event.y)
        x1, y1 = max(lx, event.x), max(ly, event.y)
        can.create_rectangle(x0, y0, x1, y1, fill=col, outline=col, width=w)
        draw.rectangle((x0, y0, x1, y1), fill=col, outline=col, width=w)  
        current_action.append(('rectangle', x0, y0, x1, y1, col, w))  

    if current_tool == 'oval' and preview_id is not None :
        can.delete(preview_id)
        preview_id = None
        # Commit final shape to canvas + PIL
        x0, y0 = min(lx, event.x), min(ly, event.y)
        x1, y1 = max(lx, event.x), max(ly, event.y) 
        can.create_oval(x0, y0, x1, y1, fill=col, outline=col, width=w)    
        draw.ellipse((x0, y0, x1, y1), fill=col, outline=col, width=w)
        current_action.append(('oval', x0, y0, x1, y1, col, w)) 

    if current_action:
        history.append(current_action)
    current_action = []


def _rebuild_image(pile, width, height):
    img = Image.new('RGB', (width, height), bg_col)
    d = ImageDraw.Draw(img)
    for action in pile:
        for tool, x0, y0, x1, y1, c, stroke_w in action:
            if tool in ('line', ''):
                d.line((x0, y0, x1, y1), fill=c, width=stroke_w)
            elif tool in ('pixel', 'rectangle'):
                d.rectangle((x0, y0, x1, y1), fill=c, outline=c, width=stroke_w)
            elif tool == 'bubble':
                d.ellipse((x0, y0, x1, y1), fill=c, outline=c, width=stroke_w)
            elif tool == 'eraser':
                d.line((x0, y0, x1, y1), fill=bg_col, width=15)
    return img, d


def redraw(pile):
    global image, draw
    can.delete(tk.ALL)
    cw, ch = get_canvas_size()
    image, draw = _rebuild_image(pile, cw, ch)
    for action in pile:
        for tool, x0, y0, x1, y1, c, stroke_w in action:
            if tool in ('line', ''):
                can.create_line(x0, y0, x1, y1, fill=c, width=stroke_w)
            elif tool in ('pixel', 'rectangle'):
                can.create_rectangle(x0, y0, x1, y1, fill=c, outline=c, width=stroke_w)
            elif tool in ('bubble', 'oval') :
                can.create_oval(x0, y0, x1, y1, fill=c, outline=c, width=stroke_w)


def choosecolor():
    global col
    couleur = colorchooser.askcolor(title="Choisissez une couleur")
    if couleur[1] is not None:
        col = couleur[1]


def clear():
    global image, draw, history, mirai
    can.delete(tk.ALL)
    cw, ch = get_canvas_size()
    image = Image.new("RGB", (cw, ch), bg_col)
    draw = ImageDraw.Draw(image)
    mirai = history
    history = []


def undo():
    global mirai, history
    if not history:
        return
    mirai.append(history.pop())
    redraw(history)


def redo():
    global mirai, history
    if not mirai:
        return
    history.append(mirai.pop())
    redraw(history)


def saver():
    fichier = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Image PNG", "*.png"), ("Image JPEG", "*.jpg")]
    )
    if fichier:
        cw, ch = get_canvas_size()
        export_img, _ = _rebuild_image(history, cw, ch)
        export_img.save(fichier)


can.bind("<Button-1>", start_draw)
can.bind("<B1-Motion>", Draw)
can.bind("<ButtonRelease-1>", end_draw)

#--------------- User Interface ---------------------

frame = tk.Frame(fen)
frame.pack(side=tk.TOP, pady=2, padx=2)

fen.columnconfigure(0, weight=1)
fen.rowconfigure(0, weight=1)
fen.rowconfigure(1, weight=1)

for i in range(6):
    frame.columnconfigure(i, weight=1)

for i in range(3):
    frame.rowconfigure(i, weight=1)

# TOOLS
outil_label = tk.Label(frame, text='Outils de dessin :', font=('Arial', 8, 'bold'))
outil_label.grid(row=0, column=2, columnspan=2, pady=0)

bou1 = tk.Button(frame, text='Simple', command=lambda: set_tool('line'), width=14, bg='#FFA500')
bou1.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=0)

bou2 = tk.Button(frame, text='Pixelise', command=lambda: set_tool('pixel'), width=14, bg='#FFA500')
bou2.grid(row=2, column=2, padx=0, sticky="nsew")

bou3 = tk.Button(frame, text='Bulles', command=lambda: set_tool('bubble'), width=14, bg='#FFA500')
bou3.grid(row=2, column=3, padx=0, sticky="nsew")

bou_rect = tk.Button(frame, text='Rectangle', command=lambda: set_tool('rectangle'), width=14, bg='#FFD700')
bou_rect.grid(row=1, column=4, padx=0, sticky="nsew")

bou_oval = tk.Button(frame, text='Ellipse', command=lambda: set_tool('oval'), width=14, bg='#FFD700')
bou_oval.grid(row=2, column=4, padx=0, sticky="nsew")

change_c = tk.Button(frame, text='Choisir la couleur', command=choosecolor, width=14, bg='#87CEEB')
change_c.grid(row=1, column=5, padx=0, sticky="nsew")

# Actions
undo_btn = tk.Button(frame, text='Undo', command=undo, width=14, bg='#87CEEB')
undo_btn.grid(row=1, column=0, padx=0, sticky="nsew")

redo_btn = tk.Button(frame, text='Redo', command=redo, width=14, bg='#87CEEB')
redo_btn.grid(row=1, column=1, padx=0, sticky="nsew")

eff = tk.Button(frame, text='Effacer TOUT', command=clear, width=14, bg='#90EE90')
eff.grid(row=2, column=1, padx=0, sticky="nsew")

gomme = tk.Button(frame, text='Gomme', command=lambda: set_tool('eraser'), width=14, bg='#90EE90')
gomme.grid(row=2, column=5, padx=0, sticky="nsew")

# Fichier
bou4 = tk.Button(frame, text='Enregistrer', command=saver, width=14, bg='#87CEFA')
bou4.grid(row=2, column=0, padx=0, sticky="nsew")

quitter = tk.Button(frame, text='Quitter', command=fen.destroy, width=14, bg='#FF6347')
quitter.grid(row=1, column=6, rowspan=2, sticky="nsew", padx=0)

fen.mainloop()