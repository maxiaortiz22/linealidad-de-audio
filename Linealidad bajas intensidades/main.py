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
root.geometry("300x320")
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
    string_var = Label(root_bar, text='Grabando el test!')
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

    freq = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]

    data = np.array([])

    for i in range(cant_de_frecuencias):
        print(f'Frecuencia a grabar: {freq[i]} Hz')
        data_aux, sr = record(RECORD_SECONDS=record_seconds)
        print(f'Se grabaron {len(data_aux)} muestras en esta iteración')

        print(f'Grabado {freq[i]} Hz')
        data = np.append(data, data_aux)
        print(f'Se acumularon {len(data)} muestras')

    #data = data[:int(11*2*11)]

    progress['value'] = 100
    root_bar.update_idletasks()
    progress.pack()

    root_bar.destroy()

    print('Audio grabado!')


clicked = StringVar()
clicked.set("Supraural (ej: JBL600)")

recomendacion0 = Label(root, text='Seleccione el tipo de auricular:').pack(pady=5, padx=10)
#recomendacion0.grid(row=1, column=0, pady=5, padx=10)
tipo_auricular = OptionMenu(root, clicked, "Supraural (ej: JBL600)", "Circumaural (ej: JBL750)").pack(pady=5, padx=10)
#tipo_auricular.grid(row=2, column=0, pady=5, padx=10)


recomendacion1 = Label(root, text='Recomendado: 1 kHz @ 65 dBHL').pack(pady=5, padx=10)
#recomendacion1.grid(row=4, column=0, pady=5, padx=10)

cal_low = Button(root, text="Calibración", command=record_cal).pack(pady=5, padx=10)
#cal_low.grid(row=5, column=0, pady=5, padx=10)

record_low = Button(root, text="Grabar test", command=record_data).pack(pady=5, padx=10)
#record_low.grid(row=6, column=0, pady=5, padx=10)

file_name_recomendacion = Label(root, text='Nombre del archivo:').pack(pady=5, padx=10)
#file_name_recomendacion.grid(row=8, column=0, pady=5, padx=10)

file_name_entry = Entry(root, justify=LEFT, textvariable='Nombre del excel').pack(pady=5, padx=10)
#file_name_entry.grid(row=9, column=0, pady=5, padx=10)

calculate = Button(root, text="Calcular", command=calcular).pack(pady=5, padx=10)
#calculate.grid(row=10, column=0, pady=5, padx=10)

root.mainloop()