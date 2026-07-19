document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll('input[name="nivel_radio"]').forEach(radio => {

        radio.addEventListener('change', function () {

            let nivelesco = '';

            if (this.value === '1') nivelesco = 'PREBAS';
            if (this.value === '2') nivelesco = 'PRIMAR';
            if (this.value === '3') nivelesco = 'BACHIL';

            cargarDatos(nivelesco);

            
            /*
            fetch(`/get_grados_por_nivel?nivelesco=${nivelesco}`)
                .then(response => response.json())
                .then(data => {

                    const select = document.getElementById('cualgrado');
                    select.innerHTML = '<option value="">Seleccione grado --</option>';
 

                    //data.forEach(grado => {

                    data.grados.forEach(grado => {

                        const option = document.createElement('option');
                        option.value = grado.codegrad;
                        option.textContent = grado.gradox;

                        select.appendChild(option);

                    });
                        // ====== LLENAR RANGOS ======

                        const selectRango = document.getElementById('cualrango');

                        selectRango.innerHTML = '<option value="">Seleccione rango --</option>';

                        data.rangos.forEach(rango => {

                        const option = document.createElement('option');
                        //option.value = rango.rangoini;
                        //option.textContent = rango.rangoini;
                        option.value = rango.rangoini;

                        option.textContent = `${rango.rangoini} - ${rango.notatt}`;

                    selectRango.appendChild(option);
                    });
                           

                
                });
        
            });*/
        });
    });

});

