from flask import Flask, request, render_template, jsonify
from predicciones import (tipos_interes,generar_datos_simulados,predecir_falla_en_tiempo_real,modelo,y,time,determinar_estado)
import threading
from queue import Queue
import numpy as np
import random

app = Flask(__name__)
maquinas = []
notificaciones = []



# Inicializa contadores de estados por tipo de falla
contadores_estados = {tipo: {'estado_actual': None, 'contador': 0} for tipo in tipos_interes}

# Definir un diccionario para almacenar el tiempo de la última alerta por tipo de falla
ultima_alerta_tiempo = {tipo: 0 for tipo in tipos_interes}

# Función para verificar y activar la alerta para estados específicos
def verificar_alerta(tipo, estado,product_id):
    estados_alerta = ['Ligero', 'Promedio', 'Grave']
    tiempo_entre_alertas = 10  # Intervalo de tiempo mínimo entre alertas en segundos

    tiempo_actual = time.time()
    tiempo_ultima_alerta = ultima_alerta_tiempo[tipo]

    if estado in estados_alerta and (tiempo_actual - tiempo_ultima_alerta) >= tiempo_entre_alertas:
        if contadores_estados[tipo]['estado_actual'] == estado:
            contadores_estados[tipo]['contador'] += 1
            if contadores_estados[tipo]['contador'] >= 3:
                mensaje_alerta = f'Maquina "{product_id}": Se ha detectado el estado "{estado}" para la falla {tipo} tres veces seguidas.'
                ultima_alerta_tiempo[tipo] = tiempo_actual  # Actualizar el tiempo de la última alerta
                notificaciones.append(mensaje_alerta)
                ultima_alerta_tiempo[tipo] = tiempo_actual  # Actualizar el tiempo de la última alerta
                # Aquí puedes agregar la lógica para enviar una alerta o tomar alguna acción necesaria
        else:
            contadores_estados[tipo]['estado_actual'] = estado
            contadores_estados[tipo]['contador'] = 1
    else:
        # Si el estado no está en la lista de estados para alertar o el tiempo mínimo entre alertas no ha pasado
        contadores_estados[tipo]['estado_actual'] = None
        contadores_estados[tipo]['contador'] = 0

# Función para actualizar los gráficos
def actualizar_datos():
    while True:
        for maquina in maquinas:
            if maquina['estado_sensor']:
                if maquina['contador_tiempo'] <= 5:

                    datos_simulados = generar_datos_simulados(maquina['product_id'], n=1)
                    predicciones = predecir_falla_en_tiempo_real(datos_simulados, modelo)
                    

                else:
                    fallas_tipos = ['TWF', 'HDF', 'PWF', 'OSF']
                    tipo_seleccionado = random.choice(fallas_tipos)
                    datos_simulados = generar_datos_simulados(maquina['product_id'],  n=1)
                    if tipo_seleccionado == 'TWF':
                        if maquina['ultimo_tool_wear'] is not None and time.time() - maquina['start_time_tool_temp'] >= 4:
                            num1 = np.random.uniform(0.5, 0.8, 1)
                            maquina['ultimo_tool_wear'] += num1
                            maquina['start_time_tool_temp']= time.time()

                        datos_simulados['Air temperature [K]'] = maquina['ultimo_air_temp']
                        datos_simulados['Torque [Nm]'] = maquina['ultimo_torque_temp']
                        datos_simulados['Tool wear [min]'] = maquina['ultimo_tool_wear']
                        datos_simulados['Rotational speed [rpm]'] = maquina['ultimo_root_speed']
                    if tipo_seleccionado == 'HDF':
                        if maquina['ultimo_air_temp'] is not None and time.time() - maquina['start_time_air_temp'] >= 3:
                            num2 = np.random.uniform(10, 15.5, 1)
                            maquina['ultimo_air_temp'] += num2
                            maquina['start_time_air_temp'] = time.time()
                        if maquina['ultimo_torque_temp'] is not None and time.time() - maquina['start_time_torque_temp'] >=3:
                            num3 = np.random.uniform(0.5, 2.5, 1)
                            maquina['ultimo_torque_temp'] += num3
                            maquina['start_time_torque_temp'] = time.time()
                        datos_simulados['Air temperature [K]'] = maquina['ultimo_air_temp']
                        datos_simulados['Torque [Nm]'] = maquina['ultimo_torque_temp']
                        datos_simulados['Tool wear [min]'] = maquina['ultimo_tool_wear']
                        datos_simulados['Rotational speed [rpm]'] = maquina['ultimo_root_speed']
                    if tipo_seleccionado == 'PWF':
                        if maquina['ultimo_torque_temp'] is not None and time.time() - maquina['start_time_torque_temp'] >= 4:
                            num3 = np.random.uniform(0.5, 1, 1)
                            maquina['ultimo_torque_temp'] += num3
                            maquina['start_time_torque_temp'] = time.time()
                        if maquina['ultimo_root_speed'] is not None and time.time() - maquina['start_time_root_temp'] >=4:
                            num4 = np.random.uniform(5, 10, 1)
                            maquina['ultimo_root_speed'] += num4
                            maquina['start_time_root_temp'] = time.time()
                        datos_simulados['Air temperature [K]'] = maquina['ultimo_air_temp']
                        datos_simulados['Torque [Nm]'] = maquina['ultimo_torque_temp']
                        datos_simulados['Tool wear [min]'] = maquina['ultimo_tool_wear']
                        datos_simulados['Rotational speed [rpm]'] = maquina['ultimo_root_speed']
                    if tipo_seleccionado == 'OSF':
                        if maquina['ultimo_tool_wear'] is not None and time.time() - maquina['start_time_tool_temp'] >= 4:
                            num1 = np.random.uniform(0.5, 0.8, 1)
                            maquina['ultimo_tool_wear'] += num1
                            maquina['start_time_tool_temp'] = time.time()
                        if maquina['ultimo_torque_temp'] is not None and time.time() - maquina['start_time_torque_temp'] >= 4:
                            num3 = np.random.uniform(0.5, 1.5, 1)
                            maquina['ultimo_torque_temp'] += num3
                            maquina['start_time_torque_temp'] = time.time()
                        datos_simulados['Air temperature [K]'] = maquina['ultimo_air_temp']
                        datos_simulados['Torque [Nm]'] = maquina['ultimo_torque_temp']
                        datos_simulados['Tool wear [min]'] = maquina['ultimo_tool_wear']
                        datos_simulados['Rotational speed [rpm]'] = maquina['ultimo_root_speed']

                predicciones = predecir_falla_en_tiempo_real(datos_simulados, modelo)

                # Recuperar el último valor de tool_wear cuando contador_datos_simulados es 10
                if maquina['contador_tiempo'] == 5:
                    maquina['ultimo_tool_wear'] = datos_simulados['Tool wear [min]']
                    maquina['ultimo_root_speed'] = datos_simulados['Rotational speed [rpm]']
                    maquina['ultimo_air_temp'] =  datos_simulados['Air temperature [K]']
                    maquina['ultimo_torque_temp'] = datos_simulados['Torque [Nm]']

                # Incrementar el contador de datos simulados
                maquina['contador_datos_simulados'] += 1
                maquina['contador_tiempo'] += 1

                
                estados = determinar_estado(predicciones[0], tipos_interes)
                for tipo, estado in estados:
                    verificar_alerta(tipo, estado,maquina['product_id'])
                maquina['datos_simulados'] = datos_simulados.to_dict(orient='records')[0]
                maquina['predicciones'] = {column: float(round(probabilidad, 2)) for column, probabilidad in zip(y.columns, predicciones[0])}
                maquina['estado'] = estados
        time.sleep(1)            

# Iniciar el hilo de actualización
threading.Thread(target=actualizar_datos, daemon=True).start()

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    posicion = data['posicion']

    return jsonify({'datos_simulados': maquinas[posicion]['datos_simulados'], 'predicciones': maquinas[posicion]['predicciones'] ,  'estado': maquinas[posicion]['estado'] })

####################################
@app.route('/')
def index():
    return render_template('index.html', maquinas=maquinas)

@app.route('/maquina_detalle.html')
def maquina_detalle():
    # Puedes utilizar estos valores para renderizar maquina_detalle.html o realizar otras acciones
    return render_template('maquina_detalle.html')

# Ruta para obtener el estado del sensor
@app.route('/obtener_estado_sensor', methods=['POST'])
def obtener_estado_sensor():
    data = request.get_json()
    product_id = data['product_id']
    
    # Busca la máquina por product_id en tu lista de maquinas
    for maquina in maquinas:
        if maquina['product_id'] == product_id:
            
            return jsonify({'estado_sensor': maquina['estado_sensor']})

    return jsonify({'estado_sensor': False})  # Si no se encuentra, se asume que está apagado

# Ruta para actualizar el estado del sensor
@app.route('/actualizar_sensor', methods=['POST'])
def actualizar_sensor():
    data = request.get_json()
    product_id = data['product_id']

    # Busca la máquina por product_id en tu lista de maquinas
    for maquina in maquinas:
        if maquina['product_id'] == product_id:
            posicion= maquina['index']
            maquina['estado']=[('TWF', 'Apagado'), ('HDF', 'Apagado'), ('PWF', 'Apagado'), ('OSF', 'Apagado'), ('RNF', 'Apagado')]
            maquina['estado_sensor'] = not maquina['estado_sensor']
            
            return jsonify({'estado_sensor': maquina['estado_sensor'],'index':posicion})

    return jsonify({'estado_sensor': False})

@app.route('/agregar_maquina', methods=['POST'])
def agregar_maquina():
    data = request.get_json()
    product_id = data['product_id']
    id_sensor = data['id_sensor']
    fecha_inicio = data['fecha_inicio']
    ultima_revision = data['ultima_revision']
    estado_inicial=[('TWF', 'Apagado'), ('HDF', 'Apagado'), ('PWF', 'Apagado'), ('OSF', 'Apagado'), ('RNF', 'Apagado')]
    # Verificar si ya existe una máquina con el mismo product_id
    if any(maquina['product_id'] == product_id for maquina in maquinas):
        return jsonify({'message': 'Ya existe una máquina con el mismo Product ID.'})

    nueva_maquina = {'product_id': product_id, 'id_sensor': id_sensor, 'estado_sensor': False,'fecha_inicio':fecha_inicio,'ultima_revision':ultima_revision,'index':len(maquinas),'estado': estado_inicial, 'contador_datos_simulados': 0, 'contador_tiempo': 0, 'ultimo_tool_wear': None, 'ultimo_root_speed': None, 'ultimo_air_temp': None, 'ultimo_process_temp': None, 'ultimo_torque_temp': None, 'start_time_tool_temp': time.time(), 'start_time_root_temp': time.time(), 'start_time_air_temp': time.time(), 'start_time_proces_temp': time.time(), 'start_time_torque_temp': time.time()}

    maquinas.append(nueva_maquina)

    return jsonify({'message': 'Máquina agregada con éxito'})

@app.route('/fechar_revision', methods=['POST'])
def fechar_revision():
    data = request.get_json()

    # Verificar que 'product_id' y 'fecha_actual' estén presentes en el JSON
    if 'product_id' not in data or 'ultima_revision' not in data:
        return jsonify({'message': 'Campos faltantes en los datos JSON'}), 400

    product_id = data['product_id']
    ultima_revision = data['ultima_revision']

    # Verificar si ya existe una máquina con el mismo product_id y actualizar su 'ultima_revision'
    for maquina in maquinas:
        if product_id == maquina['product_id']:
            maquina['ultima_revision'] = ultima_revision
            return jsonify({'message': 'Fecha de revisión actualizada con éxito'})

    return jsonify({'message': 'Máquina no encontrada'}), 404

@app.route('/lista_maquinas', methods=['GET'])
def lista_maquinas():
    maquinas_simplificadas = []
    for maquina in maquinas:
        maquina_simplificada = {
            'product_id': maquina['product_id'],
            'estado_sensor': maquina['estado_sensor'],
            'fecha_inicio': maquina.get('fecha_inicio'),  # Usa get para manejar claves que podrían no estar presentes
            'ultima_revision': maquina.get('ultima_revision'),
            'id_sensor': maquina['id_sensor'],
            'estado': maquina['estado']
        }
        maquinas_simplificadas.append(maquina_simplificada)
    
    return jsonify({'maquinas': maquinas_simplificadas,'notificaciones':notificaciones})


@app.route('/regresar', methods=['GET'])
def regresar():
    return render_template('index.html', maquinas=maquinas)


if __name__ == '__main__':
    app.run(debug=True,port= 5005)
