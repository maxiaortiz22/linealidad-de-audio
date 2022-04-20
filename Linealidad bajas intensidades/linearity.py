import numpy as np
import pandas as pd

#Recomendable: calibrar con un tono de 65 dBHL a 1kHz


def RMS(y):
    """ Calcula el valor RMS de una señal """
    rms = np.sqrt(np.mean(y**2))
    #rms=np.mean(y**2)
    return rms

def RMS_cal(y, nivel_dBHL, auricular):
    """ Calcula el valor RMS de una señal de calibración de cualquier nivel y lo paso a 94 dBSPL,
        lo que equivale a 1 Pa """

    if auricular == 'Supraural (ej: JBL600)':
        comp = 7.5 #Compensación en 1 kHz para supraural
    elif auricular == "Circumaural (ej: JBL750)":
        comp = 5.5 #Compensación en 1 kHz para circumaural
    else:
        raise TypeError("No cargaste ningún auricular")

    rms = np.sqrt(np.mean(y**2)) #Obento el RMS al nivel que fue grabado

    rms_1Pa = rms / (20*10**(-6) * 10**((nivel_dBHL+comp)/20)) #Paso le RMS a 1 Pa
    
    return rms_1Pa

def linealidad(cal, data, sr, auricular):
    """Esta función hace el cálculo de linealidad. Primero todo todo el audio grabado y lo
    separo por banda sabiendo cuánto dura la grabación de cada una. Después de eso hago todo el
    calculo de linealidad. Luego tengo que saber cuánto es el máximo y el mínimo de nivel medido
    para crear el cuadro de linealidad"""

    calibration = RMS_cal(y=cal, nivel_dBHL=65, auricular=auricular) # Lo dejo para 65 dBHL (testear esto)

    frec = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000] #Frequencies to analyze

    #Creo diccionarios con los audios grabados, la key de cada diccionario es la frecuencia grabada
    audios = {}
    
    i=0
    recorte = int(11*2*sr) #[pasos][segundos_grabacion][sr] = [muestras_por_frecuencia] no sera 12?
    for f in frec:
        #Separo la data por frecuencia y los calibro a dBSPL:
        audios[str(f)] = data[int(i) : int(i + recorte)] / calibration

        i+=recorte

    
    #Recorto los audios en partes de dos segundos
    i=0
    trimm = {}
    for key in audios.keys():
        n_cut = round(len(audios[key])/(sr*2),0) #cantidad de cortes
        #print(n_cut)
        cut = int(len(audios[key])/n_cut)
        for t in range(0,int(n_cut)):
            i+=1
            trimm[key+'_'+str(i)] = audios[key][int(cut*t) : int(cut*(t+1))] #recorte de dos segundos
            trimm[key+'_'+str(i)] = trimm[key+'_'+str(i)][int(0.5*sr) : int(-0.5*sr)] #testear si funciona
                                                                                      #mejor con este recorte
        i=0

    trimm_global_dB = {'125': [],
                       '250': [],
                       '500': [],
                       '750': [],
                       '1000': [],
                       '1500': [],
                       '2000': [],
                       '3000': [], 
                       '4000': [],
                       '6000': [],
                       '8000': []}

    for key in trimm.keys():
        trimm_global_dB[key.split('_')[0]].append(20*np.log10(RMS(trimm[key]) / (20*10**(-6))))


    supraural_comp = {'125': 45,
                      '250': 27,
                      '500': 13.5,
                      '750': 9,
                      '1000': 7.5,
                      '1500': 7.5,
                      '2000': 9,
                      '3000': 11.5, 
                      '4000': 12,
                      '6000': 16,
                      '8000': 15.5}

    circumaural_comp = {'125': 30.5,
                        '250': 18,
                        '500': 11,
                        '750': 6,
                        '1000': 5.5,
                        '1500': 5.5,
                        '2000': 4.5,
                        '3000': 2.5, 
                        '4000': 9.5,
                        '6000': 17,
                        '8000': 17.5}


    trimm_global_dB_norm = {}
    aux = []
    for key in trimm_global_dB.keys():
        if auricular == 'Supraural (ej: JBL600)':
            for i in range(len(trimm_global_dB[key])):
                aux.append(np.round_(trimm_global_dB[key][i] - supraural_comp[key]))
            trimm_global_dB_norm[key+' Hz'] = aux
        elif auricular == "Circumaural (ej: JBL750)":
            for i in range(len(trimm_global_dB[key])):
                aux.append(np.round_(trimm_global_dB[key][i] - circumaural_comp[key]))
            trimm_global_dB_norm[key+' Hz'] = aux
        else:
            raise TypeError("No cargaste ningún auricular")
        
        aux = []

    INDEX = ['40 dBHL', '35 dBHL', '30 dBHL', '25 dBHL', "20 dBHL",
             '15 dBHL', '10 dBHL', '5 dBHL' , '0 dBHL' , "-5 dBHL", "-10 dBHL"]

    test = pd.DataFrame(data=trimm_global_dB_norm, index=INDEX)

    print(test)

    return test

