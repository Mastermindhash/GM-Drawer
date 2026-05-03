# -------------- imports --------------------8

import tkinter as tk
from PIL import Image, ImageDraw
from tkinter import filedialog, colorchooser

# ------------------- Classes ---------------

class Action(object) :

    def draw(self, canvas) :
        pass
    
    def draw_pil(self, pil_draw) :
        pass

class Shape(Action) :
    def __init__(self, shape_type, x0, y0, x1, y1, color) :
        self.shape_type = shape_type
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.color = color 
        self.canvas_id = None

    def draw(self, canvas) : 
        if self.shape_type == 'rectangle' :
            if self.canvas_id is not None: 
                canvas.delete(self.canvas_id)
            self.canvas_id = canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1,
                                                          fill=self.color, outline=self.color)
            return  

        elif self.shape_type == 'oval' :
            if self.canvas_id is not None: 
                canvas.delete(self.canvas_id)
            self.canvas_id = canvas.create_oval(self.x0, self.y0, self.x1, self.y1,
                                                     fill=self.color, outline=self.color)
            return
            
    def draw_pil(self, pil_draw) :
        if self.shape_type == 'rectangle' :
            pil_draw.rectangle((self.x0, self.y0, self.x1, self.y1),
                               fill=self.color, outline=self.color)
            return  

        elif self.shape_type == 'oval' :
            pil_draw.ellipse((self.x0, self.y0, self.x1, self.y1),
                              fill=self.color, outline=self.color)
            return
            
    def move(self, A: tuple, B: tuple, canvas) :
        """Translation by vector U = B - A"""
        dx = B[0] - A[0]
        dy = B[1] - A[1]
        self.x0 += dx;  self.y0 += dy
        self.x1 += dx;  self.y1 += dy
        canvas.move(self.canvas_id, dx, dy)  

class Freehand(Action) :
    def __init__(self, x0, y0, x1, y1, s_width, col, stroke_type):
        self.stroke_type = stroke_type
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.col = col 
        self.w = s_width

    def draw(self, canvas):
        if self.stroke_type in ('line', '') :
            canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill=self.col, width=self.w)
        elif self.stroke_type == 'pixel' :
            x0, y0 = min(self.x0, self.x1), min(self.y0, self.y1)
            x1, y1 = max(self.x0, self.x1), max(self.y0, self.y1)
            canvas.create_rectangle(x0, y0, x1, y1,
                                         fill=self.col, outline=self.col, width=self.w)
        elif self.stroke_type == 'bubble' :
            x0, y0 = min(self.x0, self.x1), min(self.y0, self.y1)
            x1, y1 = max(self.x0, self.x1), max(self.y0, self.y1)
                
            canvas.create_oval(x0, y0, x1, y1,
                                              fill=self.col, outline=self.col, width=self.w)
        elif self.stroke_type == 'eraser' :
            canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill=self.bg_col, width=15)

    def draw_pil(self, pil_draw):
        if self.stroke_type in ('line', '') :
            pil_draw.line((self.x0, self.y0, self.x1, self.y1), fill=self.col, width=self.w)
        elif self.stroke_type == 'pixel' :
            x0, y0 = min(self.x0, self.x1), min(self.y0, self.y1)
            x1, y1 = max(self.x0, self.x1), max(self.y0, self.y1)
            pil_draw.rectangle((x0, y0, x1, y1),
                                          fill=self.col, outline=self.col, width=self.w)
        elif self.stroke_type == 'bubble' :
            x0, y0 = min(self.x0, self.x1), min(self.y0, self.y1)
            x1, y1 = max(self.x0, self.x1), max(self.y0, self.y1)
            pil_draw.ellipse((x0, y0, x1, y1),
                                              fill=self.col, outline=self.col, width=self.w)        
        elif self.stroke_type == 'eraser' :
            pil_draw.line((self.x0, self.y0, self.x1, self.y1), fill=self.bg_col, width=15)



class DrawingCanvas(object) :
    def __init__(self, window) :
        # tk.Canvas widget
        self.bg_col = 'white'
        Action.bg_col = self.bg_col
        self.wid_width, self.wid_height = 800, 600
        self.widget = tk.Canvas(window, width=self.wid_width, height=self.wid_height, bg=self.bg_col)
        self.widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.current_tool = ''
        self.col = 'red'
        self.w = 1


        # PIL backing image 
        self.pil_image = Image.new("RGB", (self.wid_width, self.wid_height), self.bg_col)
        self.pil_draw  = ImageDraw.Draw(self.pil_image)

        # History
        self.history = []   # committed strokes + shapes
        self.mirai   = []   # redo stack
        self.pile    = []   # shapes (Scene objects)

        # Bindings
        self._bind()
   
    def _get_canvas_size(self) :
        self.widget.update_idletasks() 
        return self.widget.winfo_width(), self.widget.winfo_height() 

    def set_tool(self, tool_name) :
        self.current_tool = tool_name

    def _bind(self):
        self.widget.bind("<Button-1>",        self.on_press)
        self.widget.bind("<B1-Motion>",       self.on_drag)
        self.widget.bind("<ButtonRelease-1>", self.on_release)

    def _hit_test(self, x, y) :
        """Returns the topmost shape containing (x, y), or None if no shape contains it."""
        for shape in reversed(self.pile):
            if (min(shape.x0, shape.x1) <= x <= max(shape.x0, shape.x1)
                 and min(shape.y0, shape.y1) <= y <= max(shape.y0, shape.y1)):
                return shape
        return None       

    def on_press(self, event) :
        self.lx, self.ly, self.current_stroke, self.preview_id =  event.x, event.y, [], None
        self.selected = self._hit_test(event.x, event.y)

    def on_drag(self, event):
        if not event:
            return

        if self.selected is not None:
            self.selected.move((self.lx, self.ly), (event.x, event.y), self.widget)
            self.lx, self.ly = event.x, event.y
            return
        
    # --- Rubber-band shapes ---
        if self.current_tool == 'rectangle':
            if self.preview_id is not None:
                self.widget.delete(self.preview_id)
            self.preview_id = self.widget.create_rectangle(self.lx, self.ly, event.x, event.y,
                                                           fill='', outline=self.col, width=self.w)
            return

        if self.current_tool == 'oval':
            if self.preview_id is not None:
                self.widget.delete(self.preview_id)
            self.preview_id = self.widget.create_oval(self.lx, self.ly, event.x, event.y,
                                                       fill='', outline=self.col, width=self.w)
            return

    # --- Freehand tools ---
        stroke = Freehand(self.lx, self.ly, event.x, event.y, self.w, self.col, self.current_tool)
        stroke.draw(self.widget)
        stroke.draw_pil(self.pil_draw)
        self.current_stroke.append(stroke)
        self.lx, self.ly = event.x, event.y
    

    def on_release(self, event):
        if self.selected is not None:
            self.redraw(self.history)
            self.selected = None
            return
        
        if self.current_tool in ('rectangle', 'oval') and self.preview_id is not None : 
            # Commit final shape to canvas + PIL
            self.widget.delete(self.preview_id)
            self.preview_id = None
            x0, y0 = min(self.lx, event.x), min(self.ly, event.y)
            x1, y1 = max(self.lx, event.x), max(self.ly, event.y)
            shape = Shape(self.current_tool, x0, y0, x1, y1, self.col)
            shape.draw(self.widget) 
            shape.draw_pil(self.pil_draw)
            self.pile.append(shape)
            self.history.append([shape])

        elif self.current_stroke:
            self.history.append(self.current_stroke) 
        self.current_stroke = []

    def redraw(self, pile) :
        self.widget.delete(tk.ALL) 
        self.wid_width, self.wid_height = self._get_canvas_size()
        self.pil_image = Image.new("RGB", (self.wid_width, self.wid_height), self.bg_col)
        self.pil_draw = ImageDraw.Draw(self.pil_image)  
        for action in pile:      # each item is a list
            for stroke in action:        # each stroke is a Freehand or Shape
                if isinstance(stroke, Shape):
                    stroke.canvas_id = None
                stroke.draw(self.widget)   
                stroke.draw_pil(self.pil_draw)      

    def undo(self) :
        if not self.history:
            return
        last = self.history.pop()
        self.mirai.append(last)
        for stroke in last :
            if isinstance(stroke, Shape) and stroke in self.pile :
                self.pile.remove(stroke)
            
        self.redraw(self.history)

    def redo(self) :
        if not self.mirai :
            return 
        last = self.mirai.pop()
        self.history.append(last)
        for stroke in last :
            if isinstance(stroke, Shape) :
                self.pile.append(stroke)
        self.redraw(self.history) 

    def clear(self) :
        self.mirai = self.history.copy()
        self.pile.clear()
        self.history.clear()
        self.widget.delete(tk.ALL)
        self.wid_width, self.wid_height = self._get_canvas_size()
        self.pil_image = Image.new("RGB", (self.wid_width, self.wid_height), self.bg_col)
        self.pil_draw  = ImageDraw.Draw(self.pil_image)

    def saver(self) :
        fichier = filedialog.asksaveasfilename(
        defaultextension=".png",                                    
        filetypes=[("Image PNG", "*.png"), ("Image JPEG", "*.jpg")])
        if fichier:
            self.pil_image.save(fichier) 


class DrawingApp(object) :
    def __init__(self) :
        self.window = tk.Tk()
        self.window.title("GM_Drawer")
        self.canvas = DrawingCanvas(self.window)
        self._build_ui()
        self.window.mainloop()
        
    def _build_ui(self):
        self.frame = tk.Frame(self.window)
        self.frame.pack(side=tk.TOP, pady=2, padx=2, fill=tk.X)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)

        for i in range(7):
            self.frame.columnconfigure(i, weight=1)
        for i in range(3):
            self.frame.rowconfigure(i, weight=1)

    # --- Outils de dessin ---
        tk.Label(self.frame, text='Outils :', font=('Arial', 8, 'bold')).grid(
            row=0, column=2, columnspan=2)

        self._add_button('Simple',    lambda: self.canvas.set_tool('line'),     
                          row=1, column=2, rowspan=1, columnspan=2, bg='#FFA500')
        self._add_button('Pixelise',  lambda: self.canvas.set_tool('pixel'),    
                          row=2, column=2, rowspan=1, columnspan=1, bg='#FFA500')
        self._add_button('Bulles',    lambda: self.canvas.set_tool('bubble'),   
                          row=2, column=3, rowspan=1, columnspan=1, bg='#FFA500')
        self._add_button('Rectangle', lambda: self.canvas.set_tool('rectangle'), 
                         row=1, column=4, rowspan=1, columnspan=1, bg='#FFD700')
        self._add_button('Ellipse',   lambda: self.canvas.set_tool('oval'),      
                         row=2, column=4, rowspan=1, columnspan=1, bg='#FFD700')

    # --- Actions ---
        self._add_button('Undo',         self.canvas.undo, 
                          row=1, column=0, rowspan=1, columnspan=1, bg='#87CEEB')
        self._add_button('Redo',         self.canvas.redo,  
                         row=1, column=1, rowspan=1, columnspan=1, bg='#87CEEB')
        self._add_button('Couleur',      self.choose_color, 
                         row=1, column=5, rowspan=1, columnspan=1, bg='#87CEEB')
        self._add_button('Gomme',        lambda: self.canvas.set_tool('eraser'),
                          row=2, column=5, rowspan=1, columnspan=1, bg='#90EE90')
        self._add_button('Effacer TOUT', self.canvas.clear,
                          row=2, column=1, rowspan=1, columnspan=1, bg='#90EE90')

    # --- Fichier ---
        self._add_button('Enregistrer', self.canvas.saver,   
                          row=2, column=0, rowspan=1, columnspan=1, bg='#87CEFA')
        self._add_button('Quitter',     self.window.destroy, 
                          row=1, column=6, rowspan=2, columnspan=1, bg='#FF6347')

    def _add_button(self, text, command, row, column, rowspan, columnspan, bg=None) :
            button = tk.Button(self.frame, text=text, command=command, width=14, bg=bg)
            button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=2, pady=2, sticky="nsew")
            return button
    
    def choose_color(self) :
        result = colorchooser.askcolor(title="Choisir la couleur")
        if result[1] is not None :
            self.canvas.col = result[1] 
    
if __name__ == "__main__":
    DrawingApp()    
