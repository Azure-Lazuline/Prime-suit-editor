import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter.colorchooser import askcolor
from PIL import ImageTk, Image
import json
import time
import os
from custom_suit_color import recolor_all_suits

root = tk.Tk()
#root.geometry('500x280')
root.resizable(False, False)
root.title('Metroid Prime suit editor')
icon=PhotoImage(file="./img/logo.png")
root.iconphoto(True,icon)

allpreviews = []
allcolorbuttons = []
bottomwidgets = []

fusionsuitenabled = tk.StringVar()
normalsuittabs = None
fusionsuittabs = None

currentfile = None
exportdirectory = None

#default colors
#these aren't 100% accurate but should be very close.

powerheadcolor = [255, 50, 1]
powermaincolor = [227, 135, 0]
powerchestcolor = [227, 150, 0]
powermisccolor = [255, 255, 50]

variaheadcolor = [249, 67, 1]
variamaincolor = [255, 144, 47]
variachestcolor = [227, 150, 0]
variamisccolor = [50, 100, 255]

powervariavisorcolor = [157, 255, 48]

gravityheadcolor = [249, 67, 1]
gravitymaincolor = [66, 53, 122]
gravitychestcolor = [248, 181, 0]
gravityvisorcolor = [33, 211, 214]

phazonheadcolor = [105, 105, 105]
phazonmaincolor = [105, 105, 105]
phazonvisorcolor = [255, 0, 0]
phazonmisccolor = [255, 230, 0]

#---

fusionpowerheadcolor = [244, 20, 104]
fusionpowermaincolor = [11, 182, 209]
fusionpowerchestcolor = [255, 251, 91]

fusionvariaheadcolor = [244, 20, 104]
fusionvariamaincolor = [224, 255, 16]
fusionvariachestcolor = [238, 87, 197]

fusiongravityheadcolor = [244, 20, 104]
fusiongravitymaincolor = [112, 75, 146]
fusiongravitychestcolor = [35, 190, 155]

fusionphazonheadcolor = [246, 58, 44]
fusionphazonmaincolor = [249, 158, 0]
fusionphazonchestcolor = [250, 233, 27]

fusionallvisorcolor = [40, 157, 201]
fusionallmisccolor = [178, 122, 236]

#end defaults


#pointers for each suit, for what the list of colors will be. There can be duplicates if a color is shared between suits.
#the "None"s help line things up for pasting palettes between suits.
suit_pointers=[
    [powerheadcolor, powermaincolor, powerchestcolor, powervariavisorcolor, powermisccolor],
    [variaheadcolor, variamaincolor, variachestcolor, powervariavisorcolor, variamisccolor],
    [gravityheadcolor, gravitymaincolor, gravitychestcolor, gravityvisorcolor, None],
    [phazonheadcolor, phazonmaincolor, None, phazonvisorcolor, phazonmisccolor]
],[
    [fusionpowerheadcolor, fusionpowermaincolor, fusionpowerchestcolor, fusionallvisorcolor, fusionallmisccolor],
    [fusionvariaheadcolor, fusionvariamaincolor, fusionvariachestcolor, fusionallvisorcolor, fusionallmisccolor],
    [fusiongravityheadcolor, fusiongravitymaincolor, fusiongravitychestcolor, fusionallvisorcolor, fusionallmisccolor],
    [fusionphazonheadcolor, fusionphazonmaincolor, fusionphazonchestcolor, fusionallvisorcolor, fusionallmisccolor],
]

#pointers to each adjustable color, exactly once. This is the same order as the top of custom_suit_color.py
suit_parameters=[
    powerheadcolor, powermaincolor, powerchestcolor, powermisccolor,
    variaheadcolor, variamaincolor, variachestcolor, variamisccolor,
    powervariavisorcolor,
    gravityheadcolor, gravitymaincolor, gravitychestcolor, gravityvisorcolor,
    phazonheadcolor, phazonmaincolor, phazonvisorcolor, phazonmisccolor,
    fusionpowermaincolor, fusionpowerheadcolor, fusionpowerchestcolor,
    fusionvariamaincolor, fusionvariaheadcolor, fusionvariachestcolor,
    fusiongravitymaincolor, fusiongravityheadcolor, fusiongravitychestcolor,
    fusionphazonmaincolor, fusionphazonheadcolor, fusionphazonchestcolor,
    fusionallvisorcolor, fusionallmisccolor
]

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def update_button_colors():
    for button in allcolorbuttons:
        button['bg'] = rgb_to_hex((button.colorpointer[0], button.colorpointer[1], button.colorpointer[2]))
        button['activebackground'] = button['bg']
        
def update_previews():
    for data in allpreviews:
        data[1] = tk.PhotoImage(file = data[2])
        data[0]['image'] = data[1]

def save_file():
    global currentfile
    if currentfile == None:
        save_as()
        return
    with open(currentfile, 'w') as outfile:
        json.dump((fusionsuitenabled.get(), suit_pointers), outfile)
        
def save_as():
    ftypes = [('Json files', '*.json'), ('All files', '*')]
    dialog = filedialog.SaveAs(root, filetypes = ftypes,
            initialdir="./saved",
            defaultextension=".json")
    file = dialog.show()

    if file == '' or file == None:
        return
    
    global currentfile
    currentfile = file
    save_file()
        
def export():
    global exportdirectory
    initialdir = "./"


    if exportdirectory == None or exportdirectory == "":
        infostr = "Select Dolphin's \"User\" directory.\n\n"
        infostr += "You can find it with \"File -> Open User Folder\" in Dolphin. On Windows, this is most likely in AppData, but it can vary depending on settings and OS."
        messagebox.showinfo(title="Export Textures", message=infostr)
    
    if exportdirectory != None: initialdir = exportdirectory
    
    dir = filedialog.askdirectory(initialdir=initialdir, title="Select Dolphin's \"User\" directory")
    if dir == "": return

    if len(dir) == 0: return

    originaldir = dir

    while True:
        if isUserDir(dir):
            #found the dolphin user directory at some part of the directory tree. Fill in the rest and export
            exportdirectory = dir
            dir = dir + "/Load/Textures/GM8E01/"
            if not os.path.exists(dir):
                os.makedirs(dir)
            save_settings()

            recolor_all_suits([True, True, True, True, True, True, True, True], True, dir, *suit_parameters)
            messagebox.showinfo(title="Success", message="Textures exported!\n\nMake sure to turn on \"Load Custom Textures\" in Dolphin's graphic settings, and set all suit cosmetics to 0 in Randovania.")
            return
        if dir.rfind("/Load/Textures/GM8") >= 0:
            #probably exporting to the textures folder directly, possibly for a different game ID. Don't add the rest of the path
            dir = originaldir + "/"
            exportdirectory = dir
            save_settings()
            recolor_all_suits([True, True, True, True, True, True, True, True], True, dir, *suit_parameters)
            messagebox.showinfo(title="Success", message="Textures exported!\n\nMake sure to turn on \"Load Custom Textures\" in Dolphin's graphic settings, and set all suit cosmetics to 0 in Randovania.")
            return
        #not found, try up by one directory
        split = dir.rfind("/")
        if split == -1:
            #messagebox.showerror(title="Error", message="Dolphin's user directory not found.\n\nYou can locate it with \"File -> Open User Folder\" in Dolphin.")
            answer = messagebox.askyesno(title="Error", message="Dolphin's user directory not found.\nYou can locate it with \"File -> Open User Folder\" in Dolphin.\n\nDo you want to export to this directory anyway?")
            if answer:
                #export anyway
                dir = originaldir + "/"
                exportdirectory = dir
                save_settings()
                recolor_all_suits([True, True, True, True, True, True, True, True], True, dir, *suit_parameters)
                messagebox.showinfo(title="Success", message="Textures exported!\n\nOnce you move them to the correct directory, make sure to also turn on \"Load Custom Textures\" in Dolphin's graphic settings, and set all suit cosmetics to 0 in Randovania.")
                
            return
        dir = dir[0 : split]


def isUserDir(dir):
    #a bit hackish, but the directory itself can have many names depending on OS and such
    if not os.path.exists(dir + "/Load/"): return False
    if not os.path.exists(dir + "/ScreenShots/"): return False
    if not os.path.exists(dir + "/StateSaves/"): return False
    if not os.path.exists(dir + "/GC/"): return False
    if not os.path.exists(dir + "/GBA/"): return False
    if not os.path.exists(dir + "/Config/"): return False
    return True

def save_settings():
    global exportdirectory
    with open("./saved/settings", 'w') as outfile:
        json.dump({"exportdirectory" : exportdirectory}, outfile)    

def load_settings():
    try:
        global exportdirectory
        if os.path.exists("./saved/settings"):
            with open("./saved/settings", 'r') as infile:
                data = json.load(infile)
                exportdirectory = data['exportdirectory']
    except:            
        return

def create_main_window():
    def load_dialog():
        ftypes = [('Json files', '*.json'), ('All files', '*')]
        dialog = filedialog.Open(root, filetypes = ftypes,
            initialdir="./saved")
        file = dialog.show()

        if file == '' or file == None:
            return
        
        try:
            global currentfile
            currentfile = file
            
            with open(file, 'r') as infile:
                data = json.load(infile)
                fusionsuitenabled.set(data[0])
                #copy manually to check shape match, since otherwise a malformed file would seriously screw things up later
                colors = data[1]
                for dim1 in range(0, len(colors)):
                    for dim2 in range(0, len(colors[dim1])):
                        for dim3 in range(0, len(colors[dim1][dim2])):
                            newcolor = colors[dim1][dim2][dim3]
                            oldcolor = suit_pointers[dim1][dim2][dim3]
                            if not (newcolor == None or oldcolor == None):
                                if type(newcolor) == type(oldcolor) and len(newcolor) == 3:
                                    oldcolor[0] = newcolor[0]
                                    oldcolor[1] = newcolor[1]
                                    oldcolor[2] = newcolor[2]

            update_button_colors()
            recalc_tabs()
            global suit_parameters
            recolor_all_suits([True, True, True, True, True, True, True, True], False, None, *suit_parameters)
            update_previews()

        except:
            currentfile = None
            return
    def recalc_tabs():
        global root
        normalsuittabs.pack_forget()
        fusionsuittabs.pack_forget()
        if fusionsuitenabled.get()=="off": normalsuittabs.pack(padx=8, pady=0)
        if fusionsuitenabled.get()=="on": fusionsuittabs.pack(padx=8, pady=0)

        global bottomwidgets
        for widget in bottomwidgets: widget.pack_forget()
        bottomwidgets = []

        bottomframe = ttk.Frame(root)
        bottomframe.pack()
        bottomwidgets.append(bottomframe)
        button = ttk.Button(
           bottomframe, 
           text="Open", 
           command=load_dialog
        )
        button.pack(padx=0, pady=8, expand=True, side=tk.LEFT)
        bottomwidgets.append(button)

        button = ttk.Button(
           bottomframe, 
           text="Save", 
           command=save_file
        )
        button.pack(padx=20, pady=8, expand=True, side=tk.LEFT)
        bottomwidgets.append(button)

        button = ttk.Button(
           bottomframe, 
           text="Save As", 
           command=save_as
        )
        button.pack(padx=0, pady=8, expand=True, side=tk.LEFT)
        bottomwidgets.append(button)
        
        button = ttk.Button(
           root, 
           text="Export textures", 
           command=export
        )
        button.pack(padx=18, pady=8, anchor="e")
        bottomwidgets.append(button)

    def create_tabs(isfusionsuit):
        def create_suit_tab(parent, suit):
            colorbuttonframe = None
            colorbuttons = []

            def color_button(i):
                def change_color(i):
                    currentcolor = (button.colorpointer[0], button.colorpointer[1], button.colorpointer[2])
                    newcolor = askcolor(rgb_to_hex(currentcolor))
                    if newcolor[1] != None:
                        rgb = hex_to_rgb(newcolor[1])
                        button.colorpointer[0] = rgb[0]
                        button.colorpointer[1] = rgb[1]
                        button.colorpointer[2] = rgb[2]

                        suits_to_recolor = [False, False, False, False, False, False, False, False]
                        for checkfusion in range(0, 2):
                            for checksuit in range(0, 4):
                                if button.colorpointer in suit_pointers[checkfusion][checksuit]:
                                    suits_to_recolor[checkfusion * 4 + checksuit] = True
                        
                        recolor_all_suits(suits_to_recolor, False, None, *suit_parameters)

                        update_button_colors()
                        update_previews()
                        
                #color_button
                global suit_pointers
                if suit_pointers[isfusionsuit][suit][i] == None:
                    return

                frame = tk.Frame(colorbuttonframe, width=30, height=30)
                frame.grid_propagate(False)
                frame.columnconfigure(0, weight=1)
                frame.rowconfigure(0,weight=1)
                
                frame.pack(expand=True, side=tk.LEFT, padx=2, pady=2)

                button = tk.Button(frame,
                    command=lambda:change_color(i))

                button.colorpointer = suit_pointers[isfusionsuit][suit][i]

                button.grid(sticky="wens")

                global allcolorbuttons
                allcolorbuttons.append(button)
                colorbuttons.append(button)

            def copy_palette(event):
                str = "("
                global suit_pointers
                for color in suit_pointers[isfusionsuit][suit]:
                    if color == None:
                        str = str + "#ffffff "
                    else:
                        color2 = (color[0], color[1], color[2])
                        str = str + rgb_to_hex(color2) + " "
                str = str.strip() + ")"
                root.clipboard_clear()
                root.clipboard_append(str)
                copybutton['text'] = copybuttontextcopied
                copybutton.after(3000, copy_palette_2)
            def copy_palette_2():
                copybutton['text'] = copybuttontextdefault


            def paste_palette(event):
                valid = True
                try:
                    paste = root.clipboard_get().strip()
                    numvalues = len(suit_pointers[isfusionsuit][suit])
                    
                    if (not isinstance(paste, str)) or len(paste) != numvalues * 8 + 1: valid = False
                    else:
                        colorstrings = []
                        for i in range(0, numvalues):
                            substr = paste[i * 8 + 1 : i * 8 + 1 + 7].lower()
                            if substr[0] != "#": valid = False
                            for digit in range(1, 7):
                                if not (substr[digit] in "1234567890abcdef"): valid = False
                            colorstrings.append(substr)
                except:
                    valid = False

                if valid:
                    for i in range(0, numcolors):
                        color = hex_to_rgb(colorstrings[i])
                        pointer = suit_pointers[isfusionsuit][suit][i]
                        if pointer != None:
                            pointer[0] = color[0]
                            pointer[1] = color[1]
                            pointer[2] = color[2]

                    if not isfusionsuit:
                        recolor_all_suits([True,True,True,True,False,False,False,False], False, None, *suit_parameters)
                    else:
                        recolor_all_suits([True,True,True,True,True,True,True,True], False, None, *suit_parameters)
                    update_button_colors()
                    update_previews()
                else:
                    messagebox.showwarning(title="Paste failed", message="Incorrect format on clipboard.")

               
            #create_suit_tab
            frame= ttk.Frame(suittabs)

            preview = ttk.Label(frame)
            previewstr = "saved/preview-"
            previewstr = previewstr + ['normal-', 'fusion-'][isfusionsuit]
            previewstr = previewstr + ['1', '2', '3', '4'][suit]
            previewstr = previewstr + ".png"
            
            preview.pack()

            global allpreviews
            allpreviews.append([preview, None, previewstr])

            colorbuttonframe = ttk.Frame(frame)
            colorbuttonframe['padding'] = (0, 5, 0, 0)
            #colorbuttonframe['borderwidth'] = 2
            #colorbuttonframe['relief'] = 'solid'
            colorbuttonframe.pack()

            global suit_pointers
            numcolors = len(suit_pointers[isfusionsuit][suit])

            for i in range(0, numcolors):
                color_button(i)

            infotext1 = ""
            infotext2 = ""
            if isfusionsuit: infotext1 = "Visor and crystal colors are shared between all suits."
            if (not isfusionsuit) and (suit == 0 or suit == 1):
                infotext1 = "Visor color is shared between Power and Varia suits."
            if (not isfusionsuit) and (suit == 0 or suit == 1):
                infotext2 = "The last color is Morph Ball glow."

            extrainfo = ttk.Label(frame)
            extrainfo['text'] = infotext1
            extrainfo.pack()

            extrainfo = ttk.Label(frame)
            extrainfo['text'] = infotext2
            extrainfo.pack()

            copybuttontextdefault = "Copy palette to clipboard"
            copybuttontextcopied = "Palette copied!"
            copybutton = ttk.Label(frame, text=copybuttontextdefault,
                                   font=('TkDefaultFont', 10),
                                   foreground='blue', cursor="hand2")
            copybutton.bind("<Button-1>", copy_palette)
            f = font.Font(copybutton, copybutton.cget("font"))
            f.configure(underline = True)
            copybutton.configure(font=f)
            copybutton.pack(pady=6, padx=8, anchor="w", side=tk.LEFT)

            pastebutton = ttk.Label(frame, text="Paste palette",
                                   font=('TkDefaultFont', 10),
                                   foreground='blue', cursor="hand2")
            pastebutton.bind("<Button-1>", paste_palette)
            pastebutton.configure(font=f)
            pastebutton.pack(pady=6, padx=8, anchor="e", side=tk.RIGHT)

            return frame

        #create_tabs
        suittabs = ttk.Notebook(root)

        for suit in range(0, 4):
            frame = create_suit_tab(root, suit)
            
            frame.pack(fill='both', expand=True)
            text = [' Power Suit ', ' Varia Suit ', ' Gravity Suit ', ' Phazon Suit '][suit]
            suittabs.add(frame, text=text)

            update_button_colors()
            
        return suittabs

    #main init

    if not os.path.exists("./saved"):
        os.makedirs("./saved")

    fusionsuitenabled.set("off")

    load_settings()
    
    fusionbutton = ttk.Checkbutton(root,
                    text='Fusion Suit',
                    command=recalc_tabs,
                    variable=fusionsuitenabled,
                    onvalue='on',
                    offvalue='off').pack(padx=8,pady=4,anchor="w")

    global normalsuittabs, fusionsuittabs
    normalsuittabs = create_tabs(0)
    fusionsuittabs = create_tabs(1)

    recalc_tabs()

    global suit_parameters
    recolor_all_suits([True, True, True, True, True, True, True, True], False, None, *suit_parameters)

    update_previews()

    root.mainloop()

if __name__ == "__main__":
    create_main_window()

