from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os.path

import parsing              # модуль парсинга
import sentiment_process    # модуль сентимент анализа

bg_color = '#B0C4DE'
disabled = '#DCDCDC'
white = '#FFFFFF'

pos_coms_arr = []
neg_coms_arr = []

# Основное окно
root = Tk()
root['bg'] = bg_color
root.title('Анализ комментариев из социальных сетей')
root.geometry('1150x520')
root.resizable(width=True, height=False)

# Рисование графика
def draw_diagr(data):
    f = Figure(figsize=(4,4.6), dpi=90)
    ax = f.add_subplot(111)
    indexes = [0,1]
    width = .6
    ax.set_xticks(indexes, ['Positive', 'Negative'])
    bar = ax.bar(indexes, data, width)
    bar[0].set_color('g')
    bar[0].set_label('Положительные отзывы')
    bar[1].set_color('r')
    bar[1].set_label('Негативные отзывы')
    f.legend(loc=2)

    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(anchor="w", x=750, y=246)

# Основная кнопка "Анализировать"
def button_main():
    val_choose = choose.get()
    
    if val_choose == comment:    
        text.set(str(InputCom_widjet.get("1.0", END)))
        val_text = text.get()
        if val_text.isspace():
            showerror(message="Пустой комментарий")
            return None
        label = sentiment_process.single_comment(val_text)

        show_single_result(label)

        
    if val_choose == domain:
        label3.place_forget()
        label_pos.place_forget()
        label_neg.place_forget()

        label3['text'] = "Количество спарсенных комментариев: "
        label_pos['text'] = "Количество положительных комментариев: "
        label_neg['text'] = "Количество негативных комментариев: "

        text.set(str(InputDomain_widjet.get()))
        val_domain = text.get()
        
        comments_count = 0
        if (os.path.isfile(r"pars_comments/" + val_domain + ".csv")):
            pars = messagebox.askyesno("Такой файл уже существует", "Ранее был произведен парсинг по этому домену. Спарсить заново?")
            if pars:
                comments_count = parsing.main(val_domain)

        else:          
            comments_count = parsing.main(val_domain)
        
        pos_arr, neg_arr, pos_count, neg_count = sentiment_process.more_comments(val_domain)

        if comments_count == 0:
            comments_count = pos_count + neg_count

        draw_diagr((pos_count, neg_count))

        global pos_coms_arr, neg_coms_arr
        pos_coms_arr = pos_arr
        neg_coms_arr = neg_arr

        label3['text'] += str(comments_count)
        label3.place(anchor='w', x=20, y=380)

        label_pos['text'] += str(pos_count)
        label_neg['text'] += str(neg_count)

        label_pos.place(anchor='w', x=20, y=410)
        label_neg.place(anchor='w', x=20, y=440)
            
        

        btn_show_pos.place(anchor='w', x=600, y=480, width=250, height=30)
        btn_show_neg.place(anchor='w', x=890, y=480, width=250, height=30)

# Закрытие топ-левел окон
def window_dismiss(window):
    window.grab_release()
    window.destroy()

# Функция показать результат анализа для одиночного комментария
def show_single_result(label):
    window = Toplevel()
    window.title("Результат Анализа")
    window.geometry("400x150+550+260")
    window.protocol("WM_DELETE_WINDOW", lambda: window_dismiss(window)) # перехватываем нажатие на крестик

    label_single_pos = Label(window, text="ПОЛОЖИТЕЛЬНЫЙ", font=("Calibri", 18, "bold"), foreground='green')
    label_single_neg = Label(window, text="НЕГАТИВНЫЙ", font=("Calibri", 18, "bold"), foreground='red')

    if label == 1:
        label_single_pos.pack(anchor="center", expand=1)
    else:
        label_single_neg.pack(anchor="center", expand=1)

    window.grab_set()   # Захватываем пользовательский ввод

# Показать список положительных комментариев
def show_pos():
    window = Toplevel()
    window.title("Положительные комментарии")
    window.geometry("800x300")
    window.protocol("WM_DELETE_WINDOW", lambda: window_dismiss(window)) # перехватываем нажатие на крестик

    list_var = StringVar(value = pos_coms_arr)

    listbox = Listbox(window, listvariable=list_var, font=("Calibri", 14))
    scrollbar_y = ttk.Scrollbar(window, orient="vertical", command=listbox.yview)
    scrollbar_x = ttk.Scrollbar(window, orient="horizontal", command=listbox.xview)

    scrollbar_x.pack(side=BOTTOM, fill=X)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar_y.pack(side=RIGHT, fill=Y)

    listbox["yscrollcommand"]=scrollbar_y.set
    listbox["xscrollcommand"]=scrollbar_x.set
    window.grab_set()   # Захватываем пользовательский ввод

# Показать список негативных комментариев
def show_neg():
    window = Toplevel()
    window.title("Негативные комментарии")
    window.geometry("800x300")
    window.protocol("WM_DELETE_WINDOW", lambda: window_dismiss(window)) # перехватываем нажатие на крестик

    list_var = StringVar(value = neg_coms_arr)

    listbox = Listbox(window, listvariable=list_var, font=("Calibri", 14))
    scrollbar_y = ttk.Scrollbar(window, orient="vertical", command=listbox.yview)
    scrollbar_x = ttk.Scrollbar(window, orient="horizontal", command=listbox.xview)

    scrollbar_x.pack(side=BOTTOM, fill=X)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar_y.pack(side=RIGHT, fill=Y)
    
    listbox["yscrollcommand"]=scrollbar_y.set
    listbox["xscrollcommand"]=scrollbar_x.set
    window.grab_set()   # Захватываем пользовательский ввод

# Обработчик изменения значения choose
def choose_input(*args):
    value = choose.get()
    if value == comment:
        InputDomain_widjet.delete(0, END)
        InputDomain_widjet['state'] = 'disabled'
        InputCom_widjet['state'] = 'normal'
        InputCom_widjet['bg'] = white
        
    if value == domain:
        InputCom_widjet.delete('1.0', END)
        InputCom_widjet['state'] = 'disabled'
        InputDomain_widjet['state'] = 'normal'
        InputCom_widjet['bg'] = disabled    

# Различные виджет
btn_show_pos = ttk.Button(text="Показать положительные", command=show_pos)
btn_show_neg = ttk.Button(text="Показать негативные", command=show_neg)
label3 = Label(text="Количество спарсенных комментариев: ", background=bg_color, font=("Calibri", 14))
label_pos = Label(text="Количество положительных комментариев: ", background=bg_color, font=("Calibri", 14), foreground='green')
label_neg = Label(text="Количество негативных комментариев: ", background=bg_color, font=("Calibri", 14), foreground='red')
InputCom_widjet = ScrolledText(font=("Calibri", 16), wrap="word", height=7, width=60, borderwidth=3)
InputDomain_widjet = Entry(font=("Calibri", 16), borderwidth=3)
InputDomain_widjet['state'] = 'disabled'

# ttk стили
style = ttk.Style()
style.configure('TRadiobutton', background = bg_color, font = ("Calibri", 14))
style.configure('TButton', font=("Calibri", 16), background = white, borderwidth=2)

# переменные
text = StringVar()
comment = "comment"
domain = "domain"
choose = StringVar(value="comment")
choose.trace_add("write", choose_input)

# Базовые виджеты
label1 = Label(text="Введите текст комментария", background=bg_color, font=("Calibri", 16, "bold"))
choose_com = ttk.Radiobutton(text="Ввод комментария", value=comment, variable=choose)
choose_domain = ttk.Radiobutton(text="Ввод ссылки на группу", value=domain, variable=choose)
label2 = Label(text="Введите домен группы vk.com", background=bg_color, font=("Calibri", 16, "bold"))
btn = ttk.Button(text="Анализировать", command=button_main)

# Размещение базовых виджетов
label1.place(anchor='nw', x=220, y= 10)
InputCom_widjet.place(anchor='nw', x = 20, y= 40)
choose_com.place(anchor='w', x=150, y=260)
choose_domain.place(anchor='w', x=350, y=260)
label2.place(anchor='w', x=220, y=310)
InputDomain_widjet.place(anchor='w', x=20, y=340, width=670, height=30)
btn.place(anchor='w', x=220, y=480, width=300, height=50)


root.mainloop()
