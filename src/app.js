$(document).ready(function () {
    $("#agregarMaquina").click(function () {
        $("#agregarMaquinaModal").modal("show");
    });

    $("#guardarMaquina").click(function () {
        $.ajax({
            url: '/agregar_maquina',
            type: 'POST',
            data: $("#maquinaForm").serialize(),
            success: function (response) {
                alert(response.message);
                $("#agregarMaquinaModal").modal("hide");
                obtenerMaquinas();
            }
        });
    });

    function obtenerMaquinas() {
        $.ajax({
            url: '/obtener_maquinas',
            type: 'GET',
            success: function (response) {
                mostrarMaquinas(response.maquinas);
            }
        });
    }

    function mostrarMaquinas(maquinas) {
        var maquinasHTML = '';
        maquinas.forEach(function (maquina) {
            maquinasHTML += `
                <div class="card mt-2">
                    <div class="card-body">
                        <h5 class="card-title">Product ID: ${maquina.product_id}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">ID Sensor: ${maquina.id_sensor}</h6>
                        <p class="card-text">Estado del Sensor: ${maquina.estado_sensor}</p>
                    </div>
                </div>`;
        });

        $("#maquinas").html(maquinasHTML);
    }

    obtenerMaquinas();
});
