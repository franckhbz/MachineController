function verDetalles(product_id, id_sensor) {
    // Redirige al usuario a maquina_detalle.html con los parámetros en la URL
   window.open(`/maquina_detalle.html?product_id=${product_id}&id_sensor=${id_sensor}`, '_blank');

}

document.addEventListener("DOMContentLoaded", function () {
    const agregarMaquinaModal = document.getElementById("agregarMaquinaModal");
    const maquinaForm = document.getElementById("maquinaForm");
    const maquinasDiv = document.getElementById("maquinas");

    document.getElementById("agregarMaquina").addEventListener("click", function () {
        agregarMaquinaModal.style.display = "block";
    });

    maquinaForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const product_id = document.getElementById("product_id").value;
        const id_sensor = document.getElementById("id_sensor").value;

        const maquina = {
            product_id: product_id,
            id_sensor: id_sensor,
            estado_sensor: false,
        };

        // Enviar los datos al servidor
        fetch('/agregar_maquina', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(maquina),
        })
            .then(response => response.json())
            .then(data => {
                if (data.message === 'Máquina agregada con éxito') {
                    // Actualizar la lista de máquinas con los datos recibidos del servidor
                    actualizarListaMaquinas();
                    agregarMaquinaModal.style.display = "none";
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    // Función para actualizar el estado del sensor en tiempo real
    function actualizarEstadoSensor(productID, estadoSensor) {
        // Encuentra el elemento del estado del sensor por su ID único
        const estadoSensorElement = document.getElementById(`estadoSensor_${productID}`);

        if (estadoSensorElement) {
            // Actualiza el estado y la apariencia
            estadoSensorElement.textContent = `Sensor ${estadoSensor ? 'Encendido' : 'Apagado'}`;
            estadoSensorElement.className = `badge badge-${estadoSensor ? 'success' : 'danger'} ml-2`;
        }
    }

    // Función para obtener y actualizar la lista de máquinas desde el servidor
    function actualizarListaMaquinas() {
        fetch('/lista_maquinas', {
            method: 'GET',
        })
            .then(response => response.json())
            .then(data => {
                // Limpiar el contenedor de máquinas
                maquinasDiv.innerHTML = '';

                // Agregar las máquinas actualizadas al contenedor
                data.maquinas.forEach(maquina => {
                    agregarMaquina(maquina);
                    // Llama a la función para actualizar el estado del sensor
                    actualizarEstadoSensor(maquina.product_id, maquina.estado_sensor);
                });
            })
            .catch(error => {
                console.error('Error al obtener la lista de máquinas:', error);
            });
    }


    // Función para agregar una máquina al contenedor
    function agregarMaquina(maquina) {
        const maquinaDiv = document.createElement("div");
        maquinaDiv.className = "card mt-2";
        maquinaDiv.innerHTML = `
    <div class="card-body">
        <h5 class="card-title">Product ID: ${maquina.product_id}</h5>
        <h6 class="card-subtitle mb-2 text-muted">ID Sensor: ${maquina.id_sensor}</h6>
        <span class="badge badge-${maquina.estado_sensor ? 'success' : 'danger'} ml-2">
            Sensor ${maquina.estado_sensor ? 'Encendido' : 'Apagado'}
        </span>
        <button class="btn btn-info btn-sm ml-2" onclick="verDetalles('${maquina.product_id}','${maquina.id_sensor}')">Ver Detalles</button>
    </div>
`;

        maquinasDiv.appendChild(maquinaDiv);
    }

    // Llama a la función para obtener la lista de máquinas al cargar la página
    actualizarListaMaquinas();
});