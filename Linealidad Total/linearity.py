import numpy as np
import pandas as pd

# De 50 dB para arriba grabo los de ganancia baja de la placa.
# Desde 45 para abajo grabo los de ganancia máxima de la placa.

#Recomendable: grabar un tono de 65 dBHL a 1kHz


def RMS(y):
    """ Calcula el valor RMS de una señal """
    rms = np.sqrt(np.mean(y**2))
    #rms=np.mean(y**2)
    return rms

def linealidad(cal_low, low, audio_seconds_low, max_values, cal_high, high, audio_seconds_high, min_values, sr):
    """Esta función hace el cálculo de linealidad. Primero todo todo el audio grabado y lo
    separo por banda sabiendo cuánto dura la grabación de cada una. Después de eso hago todo el
    calculo de linealidad. Luego tengo que saber cuánto es el máximo y el mínimo de nivel medido
    para crear el cuadro de linealidad"""

    rms_low = RMS(cal_low) #np.sqrt(np.mean(cal_low**2))
    rms_high = RMS(cal_high) #np.sqrt(np.mean(cal_high**2))

    frec = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000] #Frequencies to analyze

    #Creo diccionarios con los audios grabados a alta ganancia y a baja ganancia, la key de cada
    #diccionario es la frecuencia grabada
    audios_low = {}
    audios_high = {}

    i_low=0
    i_high=0
    count=0
    for f in frec:
        recorte_low = int(audio_seconds_low[count]*sr)
        recorte_high = int(audio_seconds_high[count]*sr)

        audios_low[str(f)] = low[int(i_low) : int(i_low + recorte_low)] / rms_low
        audios_high[str(f)] = high[int(i_high) : int(i_high + recorte_high)] / rms_high

        i_low = audio_seconds_low[count]*sr
        i_high = audio_seconds_high[count]*sr

        count+=1

    #Junto los audios según su banda
    audio = {}
    for key in audios_low.keys():
        audio[key] = np.append(audios_low[key], audios_high[key])

    
    #Recorto los audios en partes de dos segundos
    i=0
    trimm = {}
    for key in audio.keys():
        n_cut = round(len(audio[key])/(sr*2),0) #cantidad de cortes
        #print(n_cut)
        cut = int(len(audio[key])/n_cut)
        for t in range(0,int(n_cut)):
            i+=1
            trimm[key+'_'+str(i)] = audio[key][int(cut*t) : int(cut*(t+1))]
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
        #trimm_global_dB[key.split('_')[0]] = 20*np.log10(RMS(trimm[key]))


    trimm_global_dB_norm = {}
    for key in trimm_global_dB.keys():
        trimm_global_dB_norm[key+' Hz'] = trimm_global_dB[key] - trimm_global_dB[key][0]
        trimm_global_dB_norm[key+' Hz'] = np.round_(trimm_global_dB_norm[key+' Hz'], decimals=2)
    
    """Hago que todos los vectores tengan el mismo largo"""
    for i in range(len(max_values)):
        max_values[i] = int(max_values[i])
        min_values[i] = int(min_values[i])

    max_value = max(max_values)
    min_value = min(min_values)

    to_append_max = []
    for i in range(len(max_values)):
        to_append_max.append( np.abs((max_values[i]-max_value)/5) )
    
    to_append_min = [] 
    for i in range(len(min_values)):
        to_append_min.append( np.abs((min_values[i]-min_value)/5) )

    i=0
    for key in trimm_global_dB_norm.keys():
        trimm_global_dB_norm[key] = np.pad(trimm_global_dB_norm[key],                      #array
                                            (int(to_append_max[i]),int(to_append_min[i])), #agrego a la izquierda y a la derecha
                                            mode='constant',                               #de forma constante
                                            constant_values=(np.nan,np.nan))               #agrego NaN donde no hay valor
        i+=1
    #np.set_printoptions(suppress=True)
    #print('Valores a 8kHz:')
    #print(trimm_global_dB_norm['8000']) # notar que estoy metiendo los raw y scale a la vez
    #print(trimm_global_dB_norm)

    INDEX = []
    for i in range(max_value, min_value -5, -5):
        INDEX.append(str(i)+' dBHL')


    test = pd.DataFrame(data=trimm_global_dB_norm, index=INDEX)

    print(test)

    return test

