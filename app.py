from customtkinter import *
from CTkMessagebox import CTkMessagebox
from tkinter.ttk import *
import csv
from os.path import isfile
from PIL import Image
import sqlite3


#main voting function loop
def vote_e():
    res = []
    curr = 0

    #adds the selected option to a list and goes to the next frame when the next button is clicked 
    def next():
        nonlocal curr
        res.append(choose.get())
        frames[curr].pack_forget()
        curr+=1
        frames[curr].pack(fill="both", expand=True)
      

    
    #adds the list with the selected options to the database and gives option to vote again
    def submit():
        res.append(choose.get())
        msg = CTkMessagebox(master=vt, title="Vote Successful!", message="Vote Successful!\nDo you want to vote again?", icon="check", option_1="Yes", option_2="No")
        
        if msg.get() == "Yes":
            frames[curr].pack_forget()
            vto()
        else:
            vt.destroy()
        
        for i in res:
            cursor.execute("update main set count = count + 1 where name = '{}'".format(i))
        conn.commit()
        
    #checks if the checkbox is selected and allows the user to click the button and go to the next option
    def next_button_state(*args):    
        if choose.get():
            for widgets in frames[curr].winfo_children():
                widgets.configure(state=NORMAL)

    #initially shows the first frame initially and after choosing to vote again in submit it starts the vote loop
    def vto():
        nonlocal curr
        curr = 0

        try:
            frames[curr].pack(fill="both", expand=True)
        except:
            vt.destroy()
            CTkMessagebox(master=root, title="Warning message!", message="No candidates added", icon="warning", option_1="Ok")


    cursor.execute("select name, position from main")
    position_dict = {}
    rows = cursor.fetchall()

    for row in rows:
        name, position = row
        if position in position_dict:
            position_dict[position] += (name,)
        else:
            position_dict[position] = (name,)

 
    vt = CTkToplevel(root)
    vt.after(10, vt.lift)
    vt.geometry(str(root.winfo_screenwidth())+"x"+str(root.winfo_screenheight()))
    vt.state('zoomed')
    vt.attributes('-fullscreen',True)

    choose = StringVar()
    frames = []
    

    for i in position_dict:

        frame = CTkFrame(vt, fg_color="transparent")
        postitle = CTkLabel(frame, text=f"For the position of {i}", font=('Futura', 30, 'bold'))
        postitle.grid(row=0, column=0, pady=15, columnspan=2)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        for c, j in enumerate(position_dict[i]):
            votebutton = CTkRadioButton(frame, text=j, value=j, variable=choose, font=('Futura', 25))

            if useimg:
                try:
                    img = CTkImage(Image.open(f"images/{j}.png"), size=(100, 100))
                except:
                    img = CTkImage(Image.open("images/def.png"), size=(100, 100))

                imglab = CTkLabel(frame, text="", image=img)
                votebutton.grid(row=c+1, column=0, pady=20, padx=10, sticky=E)
                imglab.grid(row=c+1, column=1, pady=10, sticky=W)

            else:
                votebutton.grid(row=c+1, column=0, pady=20, padx=10, columnspan=2)


            frame.grid_rowconfigure(c+1, weight=1)
            

        if len(frames)+1 == len(position_dict): 
            confirmbutton = CTkButton(frame, text="Submit", command=lambda: submit(), state=DISABLED, height=50, width=150)
            confirmbutton.grid(row=c+2, column=1, padx=20, pady=20, sticky=SE)
        else:
            switchbutton = CTkButton(frame, text="Next", command=lambda: next(), state=DISABLED, height=50, width=150)  
            switchbutton.grid(row=c+2, column=1, padx=20, pady=20, sticky=SE) 
            frame.grid_rowconfigure(c+2, weight=2)
    

        frames.append(frame)
        


    vto()
    choose.trace_add("write", next_button_state)


#dispalys the results of the voting
def result_e():
    re = CTkToplevel(root)
    re.after(10, re.lift)
    re.geometry('1920x1080')
    re.state('zoomed')
    re.title('Results')
    cursor.execute("SELECT DISTINCT position FROM main")
    positions = cursor.fetchall()

    scf = CTkScrollableFrame(re, fg_color="transparent", width=1920, height=1080)
    scf.pack()
    
 

    for i in positions:
        posframe = CTkFrame(scf)
        posframe.pack(pady=10)

        position_label = CTkLabel(posframe, text=i[0], font=('Futura', 21, 'bold'))
        position_label.grid(row=0, column=0, columnspan=2)

        name_header = CTkLabel(posframe, text="Name", font=('Futura', 19, 'bold'))
        name_header.grid(row=1, column=0, padx=10)

        count_header = CTkLabel(posframe, text="Count", font=('Futura', 19, 'bold'))
        count_header.grid(row=1, column=1, padx=10)

        cursor.execute("SELECT name, count FROM main WHERE position='{}'".format(i[0]))
        names_counts = cursor.fetchall()

        for i, (name, count) in enumerate(names_counts):
            name_label = CTkLabel(posframe, text=name, padx=10, font=('Futura', 17))
            name_label.grid(row=i + 2, column=0)
            count_label = CTkLabel(posframe, text=count, padx=10, font=('Futura', 17))
            count_label.grid(row=i + 2, column=1)
        



# adding/removing candidates/positions from the voting database
def add_e():

    #function for adding new entries to the listbox and the database
    def proceed():
        nam = nameentry.get()
        pos = posentry.get()
        strpos = pos.strip()

        for i in nam.split(","):
            strname = i.strip()
            if strname == "" or strpos == "":
                CTkMessagebox(master=ad, title="Error", message="names can't be blank", icon="cancel", option_1="Ok")
                return
            listbox.insert("", "end", values=(pos, i))
            cursor.execute("insert into main (position, name) values('{}', '{}')".format(pos, i))
            conn.commit()

        listbox.yview_moveto(1)
        listbox.focus(listbox.get_children()[-1])
        listbox.selection_set(listbox.get_children()[-1])

        posentry.delete(0, END)
        nameentry.delete(0, END)

        CTkMessagebox(master=ad, title="Item(s) added", message="Item(s) successfully added!", icon="check", option_1="Ok")

    #used for getting the change in the textbox or if a value in the listbox is selected
    def update(*args):
        if listbox.selection():
            deletebutton.configure(state="normal")
        else:
            deletebutton.configure(state="disabled")

        if posentry.get() and nameentry.get():
            proceedbutton.configure(state="normal")
        else:
            proceedbutton.configure(state="disabled")

    #used to delete values from listbox and database
    def delete():
        selectedItem = listbox.selection()[0]
        pos = str(listbox.item(selectedItem)['values'][0])
        nam = str(listbox.item(selectedItem)['values'][1])

        cursor.execute("delete from main where name='{}' and position='{}'".format(nam, pos))
            
        conn.commit()
        deletebutton.configure(state="disabled")
        show()


    #called to update the listbox with values from the database
    def show():
        for item in listbox.get_children():
            listbox.delete(item)

        cursor.execute("select position, name from main")
        for i in cursor.fetchall():
            listbox.insert("", "end", values=i)

    #converts csv file to database
    def impcsv():
        file_path = filedialog.askopenfilename(parent=ad, title="Select a File", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if file_path == "" or file_path[-4:] != ".csv":
            return
        
        with open (file_path, newline="") as cf:
            cr = csv.reader(cf)
            for i in cr:
                cursor.execute("insert into main (position, name) values{}".format(tuple(i)))

        conn.commit()
        show()
        CTkMessagebox(master=ad, title="item(s) added", message="Item(s) successfully added!", icon="check", option_1="Ok")
        listbox.yview_moveto(1)
        listbox.focus(listbox.get_children()[-1])
        listbox.selection_set(listbox.get_children()[-1])

    #toggles candidates images
    def imgtoggle():
        global useimg
        global imgvar
        imgvar = imgswitch.get()
        if imgswitch.get() == 1:
            useimg = True
        else:
            useimg = False
        


    ad = CTkToplevel(root)
    ad.geometry('850x600')
    ad.after(10, ad.lift)
    ad.title('Create a new poll')

    posvar = StringVar()
    namevar = StringVar()
    posvar.trace("w", update)
    namevar.trace("w", update)


    poslabel = CTkLabel(ad, text='Enter Position: ', font=('Futura', 20, 'bold'))
    namelabel = CTkLabel(ad,text='Candidate names: ', font=('Futura', 20, 'bold'))
    posentry = CTkEntry(ad,width=600, textvariable=posvar)
    nameentry = CTkEntry(ad, width=600, textvariable=namevar)

    info1 = CTkLabel(ad,text='To delete', font=('Futura', 18, 'bold'))
    info2 = CTkLabel(ad,text='Click on the entry you \nwant to delete and \npress the delete button', font=('Futura', 15))
    info3 = CTkLabel(ad,text='To add', font=('Futura', 18, 'bold'))
    info4 = CTkLabel(ad,text='Enter the position and then enter the \ncandidate names one by one \nseperated by comma', font=('Futura', 15))
    info5 = CTkLabel(ad,text='To import CSV', font=('Futura', 18, 'bold'))
    info6 = CTkLabel(ad,text='To import a CSV file \nuse the format \nposition,name', font=('Futura', 15))
    info7 = CTkLabel(ad,text='To use Images', font=('Futura', 18, 'bold'))
    info8 = CTkLabel(ad,text='To use images put photos \nof candidates with the format \ncandidatename.png \nin the folder images', font=('Futura', 15))
    
    proceedbutton = CTkButton(ad,text='Add',command=proceed, state="disabled", height=50, width=144)
    deletebutton = CTkButton(ad,text='Delete',command=delete, state="disabled", height=50, width=144)
    csvbutton = CTkButton(ad,text='Import csv',command=impcsv, height=50, width=144)

    listbox = Treeview(ad, columns=["position", "name"], show='headings', height=10)

    imgswitch = CTkSwitch(ad, text="", switch_width=60, switch_height=30, command=lambda: imgtoggle())

    if int(imgvar) == 1:
        imgswitch.select()
    if not isfile("images/def.png"):
        imgswitch.configure(state=DISABLED)
 


    poslabel.grid(row=0,column=0, padx="10", pady="10")
    namelabel.grid(row=1,column=0, padx="10" , pady="10")
    posentry.grid(row=0, column=1, pady="5", columnspan=3)
    nameentry.grid(row=1, column=1, pady="5", columnspan=3)
    info1.grid(row=2,column=0, columnspan=1, padx=5)
    info2.grid(row=3,column=0, columnspan=1, padx=5, pady=5)
    info3.grid(row=2,column=1, columnspan=1, padx=5)
    info4.grid(row=3,column=1, columnspan=1, padx=5, pady=5)
    info5.grid(row=2,column=2, columnspan=1, padx=5)
    info6.grid(row=3,column=2, columnspan=1, padx=5, pady=5)
    info7.grid(row=2,column=3, columnspan=1, padx=5)
    info8.grid(row=3,column=3, columnspan=1, padx=5, pady=5)
    deletebutton.grid(row=8, column=0, padx=10, pady=5)
    proceedbutton.grid(row=8, column=1, padx=10, pady=5)
    csvbutton.grid(row=8, column=2, padx=10, pady=5)
    listbox.grid(row=11, column=0, columnspan=4, pady=10)
    imgswitch.grid(row=8, column=3, padx=10, pady=5)

    
    listbox.heading("position", text="Position")
    listbox.heading("name", text="Name")
    listbox.column("position", width=350, anchor="center")
    listbox.column("name", width=350, anchor="center")
    listbox.bind('<ButtonRelease-1>',update)

    style = Style(listbox)    
    style.theme_use("clam")
    
    style.configure('Treeview.Heading', font=('Futura', 20, 'bold'), rowheight=35)
    style.configure('Treeview', font=('Futura', 15, 'normal'), rowheight=35)
    style.map("Treeview", background=[("selected", "#408cd4")])

    show()


conn = sqlite3.connect("poll")
cursor=conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS main(position varchar(50), name varchar(50), count int DEFAULT 0)")


root = CTk()
root.title("Elecshion")
root.geometry("720x500")
set_appearance_mode("light")


label = CTkLabel(text="School Voting Software", master=root, anchor="center",font=('Futura', 30, 'bold'))
vote_b = CTkButton(master=root, text="Vote!", command=vote_e, width=140, height=40)
result_b = CTkButton(master=root, text="Results", command=result_e, width=140, height=40)
add_b = CTkButton(master=root, text="Add/Remove people", command=add_e, width=140, height=40)


label.pack(padx=10, pady=10)
vote_b.pack(padx=10, pady=10)
result_b.pack(padx=10, pady=10)
add_b.pack(padx=10, pady=10)

useimg = False
imgvar = 0

root.mainloop()

cursor.close()
conn.close()
