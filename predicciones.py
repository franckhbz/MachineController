import json
import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import keras
import time
import matplotlib.pyplot as plt

# Cargar los datos y preprocesarlos
df = pd.read_csv('ai4i2020.csv')

# Codificar variables categóricas
df = pd.get_dummies(df, columns=['Type'])

# Dividir los datos en conjuntos de entrenamiento y prueba
X = df.drop(['UDI', 'Product ID', 'Machine failure',
            'TWF', 'HDF', 'PWF', 'OSF', 'RNF'], axis=1)
y = df[['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)


# Función para generar datos simulados
def generar_datos_simulados(product_id, n=1):
    # Simular datos aleatorios para las características
    air_temperature = np.random.uniform(200, 310, n)
    process_temperature = np.random.uniform(300, 350, n)
    rotational_speed = np.random.uniform(1400, 1600, n)
    torque = np.random.uniform(35, 45, n)
    tool_wear = np.random.randint(0, 250, n)
    tipo = product_id[0]
    tipo_M, tipo_H, tipo_L = 0, 0, 0
    if tipo == 'M':
        tipo_M = 1
    if tipo == 'H':
        tipo_H = 1
    if tipo == 'L':
        tipo_L = 1
    # Crear un DataFrame simulado
    df_simulado = pd.DataFrame({
        'Air temperature [K]': air_temperature,
        'Process temperature [K]': process_temperature,
        'Rotational speed [rpm]': rotational_speed,
        'Torque [Nm]': torque,
        'Tool wear [min]': tool_wear,
        'Type_H': tipo_H,
        'Type_L': tipo_L,
        'Type_M': tipo_M,
    })

    return df_simulado


# Función para realizar predicciones en tiempo real
def predecir_falla_en_tiempo_real(datos_en_tiempo_real, modelo_entrenado):
    # Realizar la predicción usando el modelo
    predicciones = modelo_entrenado.predict(datos_en_tiempo_real)
    return predicciones


# Cargar el modelo previamente entrenado
modelo = keras.models.load_model('modelo_entrenado.h5')
product_id = "M14860"


# Crear una figura con subplots solo para los tipos de interés
tipos_interes = ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']
fig, axs = plt.subplots(len(tipos_interes), 1, figsize=(10, 12))
fig.canvas.mpl_connect(
    'key_press_event', lambda event: event.key == 'q' and plt.close(fig))

# Contador para enumerar los datos simulados
contador_datos_simulados = 0
# Define un diccionario para realizar un seguimiento de las máquinas y sus estados de generación de datos
correr_update_por_maquina = {}

def determinar_estado(predicciones, tipos_interes):
    estados = []
    for i, tipo in enumerate(tipos_interes):
        probabilidad = predicciones[i]
        if 0 <= probabilidad <= 0.02:
            estado = 'Normal'
        elif 0.02 < probabilidad <= 0.40:
            estado = 'Ligero'
        elif 0.40 < probabilidad <= 0.70:
            estado = 'Promedio'
        elif 0.70 < probabilidad <= 1.00:
            estado = 'Grave'
        else:
            estado = 'Desconocido'
        estados.append((tipo, estado))
    return estados

