document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll('input[name="nivel_radio"]').forEach(radio => {

        radio.addEventListener('change', function () {

            let nivelesco = '';

            if (this.value === '1') nivelesco = 'PREBAS';
            if (this.value === '2') nivelesco = 'PRIMAR';
            if (this.value === '3') nivelesco = 'BACHIL';

            fetch(`/get_grados_por_nivel?nivelesco=${nivelesco}`)
                .then(response => response.json())
                .then(data => {

                    const select = document.getElementById('cualgrado');


                    select.innerHTML = '<option value="">Seleccione grado --</option>';


                    data.grados.forEach(grado => {

                        const option = document.createElement('option');
                        option.value = grado.codegrad;
                        option.textContent = grado.gradox;

                        select.appendChild(option);

     

                    });

                });

        });

    });

});