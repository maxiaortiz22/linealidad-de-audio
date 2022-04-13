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

"""La variable RECORD_SECONDS va a tener que ser 2*Cantidad_De_Pasos_En_Cada_Frecuencia 
Tengo el dato que de 50 dB para arriba grabo los de ganancia baja de la placa y de
45 para abajo grabo los de ganancia máxima de la placa. Puedo aprovechar este valor y los pasos
van a se de 50 al máximo para uno y de 45 al mínimo para el otro. En cada caso tendría que obtener
el get del cuadrito de cada frecuencia que corresponda!!! Posiiblemente tenga que hacer un record()
por cada frecuencia!!!!!!!!!"""



global my_entries

root = Tk()
root.title("Test de linealidad")
root.geometry("580x500")
root.iconbitmap('logo.ico')

my_entries = []

def calcular():
    """Una vez obtenidos los audios, paso a calcular linealidad"""
    global cal
    global record_seconds
    global data
    global sr

    test = linealidad(cal, data, record_seconds, sr)

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

def record():
    global data
    global record_seconds
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

    record_seconds = 11*11*2 # [saltos_de_nivel]*[frecuencias]*[segundos_por_paso]
                             # [40,35,30...,-10]*[125,250...,8000]*[ 2[s] ]

    print(f'Se grabaran {record_seconds} [s] de audio')

    progress['value'] = 15
    root_bar.update_idletasks()
    progress.pack()

    data, sr = record(RECORD_SECONDS=record_seconds)

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


recomendacion1 = Label(root, text='Recomendado: 1 kHz @ 65 dBHL')
recomendacion1.grid(row=1, column=3, pady=5, padx=10)

cal_low = Button(root, text="Calibración baja ganancia", command=record_cal)
cal_low.grid(row=2, column=3, pady=5, padx=10)

record_low = Button(root, text="Grabar a baja ganancia", command=record)
record_low.grid(row=3, column=3, pady=5, padx=10)

file_name_recomendacion = Label(root, text='Nombre del archivo:')
file_name_recomendacion.grid(row=6, column=3, pady=5, padx=10)

file_name_entry = Entry(root, justify=LEFT, textvariable='Nombre del excel')
file_name_entry.grid(row=7, column=3, pady=5, padx=10)

calculate = Button(root, text="Calcular", command=calcular)
calculate.grid(row=8, column=3, pady=5, padx=10)

root.mainloop()