from tkinter import *
from tkinter.ttk import Progressbar
from record_audio import record
import numpy as np
from linearity import linealidad
import sys
import pandas as pd
import os

cwd = os.getcwd()
os.chdir(cwd)


global my_entries

root = Tk()
root.title("Test de linealidad")
root.geometry("580x500")
root.iconbitmap('logo.ico')

my_entries = []

def calcular():
    """Una vez obtenidos los audios, paso a calcular linealidad"""
    global cal
    global data
    global sr

    auricular = clicked.get()

    test = linealidad(cal, data, sr, auricular)

    file_name = file_name_entry.get()

    writer = pd.ExcelWriter( file_name + '.xlsx', engine='xlsxwriter')

    test.to_excel(writer, sheet_name='Linealidad')

    writer.save()

    cartel_guardado = Tk()
    cartel_guardado.iconbitmap('logo.ico')
    Frame(cartel_guardado, width=350, height=20).pack()
    cartel_guardado.title('Cálculo')
    string_var = Label(cartel_guardado, text='Listo! valores guardados en '+file_name+'.xlsx')
    string_var.pack()

def record_cal():
    """Grabar calibración para baja ganancia"""
    global cal #Defino la calibración como variable global

    root_bar = Tk()
    root_bar.iconbitmap('logo.ico')
    Frame(root_bar, width=250, height=8).pack()
    root_bar.title('Calculando...')
    Label(root_bar, text='Grabando calibración!').pack()
    progress = Progressbar(root_bar, orient = HORIZONTAL, length = 100, mode = 'determinate')
    
    progress['value'] = 20
    root_bar.update_idletasks()
    progress.pack()

    
    
    progress['value'] = 40
    root_bar.update_idletasks()
    progress.pack()

    cal, sr = record(RECORD_SECONDS=2) #Grabo la calibración
    
    progress['value'] = 100
    root_bar.update_idletasks()
    progress.pack()

    root_bar.destroy()
    print('Calibración cargada!')

def record_data():
    global data
    global sr

    root_bar = Tk()
    root_bar.iconbitmap('logo.ico')
    Frame(root_bar, width=250, height=8).pack()
    root_bar.title('Calculando...')
    string_var = Label(root_bar, text='Grabando a baja ganancia!')
    string_var.pack()
    progress = Progressbar(root_bar, orient = HORIZONTAL, length = 100, mode = 'determinate')

    progress['value'] = 10
    root_bar.update_idletasks()
    progress.pack()

    # La variable record_seconds va a tener que ser 2*Cantidad_De_Pasos_En_Cada_Frecuencia
    record_seconds = 11*2 # [saltos_de_nivel]*[segundos_por_paso]
                          # [125,250...,8000]*[ 2[s] ]

    cant_de_frecuencias = 11
    print(f'Se grabaran {record_seconds*cant_de_frecuencias} [s] de audio')

    progress['value'] = 15
    root_bar.update_idletasks()
    progress.pack()

    data = []

    for i in range(cant_de_frecuencias):
        data_aux, sr = record(RECORD_SECONDS=record_seconds)

        data.append(data_aux)

    progress['value'] = 100
    root_bar.update_idletasks()
    progress.pack()

    root_bar.destroy()

    print('Audio grabado!')

#Nombres de las columnas
frec_name = Label(root, text='Frecuencia [Hz]')
frec_name.grid(row=0, column=0, pady=8, padx=5)

min_name = Label(root, text='Mínimo app [dBHL]')
min_name.grid(row=0, column=1, pady=8, padx=5)

max_name = Label(root, text='Máximo app [dBHL]')
max_name.grid(row=0, column=2, pady=8, padx=5)

#Cuadros de mínimos y máximos

min_max_default = [[-10,40],[-10,40],[-10,40],[-10,40],[-10,40],[-10,40],
                   [-10,40],[-10,40],[-10,40],[-10,40],[-10,40]] #Cargo valores por default de mínimos y máximos de dBHL

#Row Loop
for y in range(11):
    #Column Loop
    for x in range(2):
        default_min_max = StringVar()
        default_min_max.set(min_max_default[y][x])
        my_entry = Entry(root, justify=RIGHT, textvariable=default_min_max)
        my_entry.grid(row=y+1, column=x+1, pady=5, padx=5)
        my_entries.append(my_entry)

#Nombre de las filas (las frecuencias)
frec_name = ['125 Hz', '250 Hz', '500 Hz', '750 Hz','1000 Hz', '1500 Hz',
            '2000 Hz', '3000 Hz', '4000 Hz', '6000 Hz', '8000 Hz']

for x in range(11):
    my_label = Label(root, text=frec_name[x])
    my_label.grid(row=x+1, column=0, pady=8, padx=5)

clicked = StringVar()
clicked.set("Supraural (ej: JBL600)")

recomendacion0 = Label(root, text='Seleccione el tipo de auricular:')
recomendacion0.grid(row=1, column=3, pady=5, padx=10)
tipo_auricular = OptionMenu(root, clicked, "Supraural (ej: JBL600)", "Circumaural (ej: JBL750)")
tipo_auricular.grid(row=2, column=3, pady=5, padx=10)


recomendacion1 = Label(root, text='Recomendado: 1 kHz @ 65 dBHL')
recomendacion1.grid(row=4, column=3, pady=5, padx=10)

cal_low = Button(root, text="Calibración", command=record_cal)
cal_low.grid(row=5, column=3, pady=5, padx=10)

record_low = Button(root, text="Grabar test", command=record_data)
record_low.grid(row=6, column=3, pady=5, padx=10)

file_name_recomendacion = Label(root, text='Nombre del archivo:')
file_name_recomendacion.grid(row=8, column=3, pady=5, padx=10)

file_name_entry = Entry(root, justify=LEFT, textvariable='Nombre del excel')
file_name_entry.grid(row=9, column=3, pady=5, padx=10)

calculate = Button(root, text="Calcular", command=calcular)
calculate.grid(row=10, column=3, pady=5, padx=10)

root.mainloop()