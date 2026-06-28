
function renderGridNotas(notas, periodo) {

    if (notas.length === 0) {
        document.getElementById("gridNotasxestudiantexasignatura").innerHTML = "<p>No hay notas registradas.</p>";
        return;
    }

    // -------------------------------
    // ARMAR ENCABEZADO SEGÚN PERIODO
    // -------------------------------
    let columns = `
        <th>Code</th>
        <th>Materia</th>
    `;

    if (periodo == "PER1"){
        columns += `
        <th>1erPer</th>
        <th>Obspe1</th>
        `;
    }

        if (periodo === "PER2") {
        columns += `
        <th>1erPer</th>
        <th>2doPer</th>
        <th>Obspe2</th>
        `;
    }

    if (periodo === "PER3") {
        columns += `
        <th>1erPer</th>
        <th>2doPer</th>
        <th>3erPer</th>
        <th>Obspe3</th>`;
    }

    columns += `
        
    `;

    if (periodo === "PER1") {
        columns += `
        <th>Promedio1</th>
        <th>Obsprom</th>
        `;
    }
    
    if (periodo === "PER2") {
        columns += `
        <th>Promedio1</th>
        <th>Promedio2</th>
        <th>Obsprom2</th>`;
    }

    if (periodo === "PER3") {
        columns += `
            <th>Promedio1</th>
            <th>Promedio2</th>
            <th>Promedio3</th>
            <th>Obsprom3</th>
        `;
    }


    // -------------------------------
    // ARMAR CUERPO
    // -------------------------------

    let rows = "";

    notas.forEach(n => {

        // concepto formativo depende del periodo
        const conceptoFormativo = (periodo === "PER2") ? (n.rempe2 || "") : (n.rempe3 || "");

        rows += `
            <tr>
                <td>${n.codemate}</td>
                <td>${n.nombre}</td>
        `;

        if (periodo === "PER1") {
            rows += `
            <td>${n.nota1 || ""}</td>
            <td>${n.obstxt1 || ""}</td>
            `;
        }

        if (periodo === "PER2") {
            rows += `
            <td>${n.nota1 || ""}</td>
            <td>${n.nota2 || ""}</td>
            <td>${n.obstxt2 || "" }</td>
            `;
        }

        if (periodo === "PER3") {
            rows += `
            <td>${n.nota1 || ""}</td>
            <td>${n.nota2 || ""}</td>
            <td>${n.nota3 || ""}</td>
            <td>${n.obstxt3 || "" }</td>
            `;
        }

        rows += `


            
        `;

        if (periodo === "PER1") {
            rows += `
            <td>${n.promedio || ""}</td>
            <td>${n.obstxtpro1 }</td>
            `;
        }

        if (periodo === "PER2") {
            rows += `
            <td>${n.promedio || ""}</td>
            <td>${n.promedio2 || ""}</td>
            <td>${n.obstxtpro2 }</td>
            `;
        }

        if (periodo === "PER3") {
            rows += `
                <td>${n.promedio || ""}</td>
                <td>${n.promedio2 || ""}</td>
                <td>${n.promedio3 || ""}</td>
                <td>${n.obstxtpro3 }</td>
            `;
        }


    });

    // -------------------------------
    // TABLA FINAL
    // -------------------------------
    let html = `
        <table class="table table-striped table-bordered">
            <thead class="table-dark">
                <tr>${columns}</tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;

    document.getElementById("gridNotasxestudiantexasignatura").innerHTML = html;
}




function renderGridNotasArea(notasxarea, periodo) {

    //const periodo = window.periodoGlobal;  // ← Debe tener PER1, PER2 o PER3.

    if (!notasxarea || notasxarea.length === 0) {
        document.getElementById("gridNotasxestudiantexarea").innerHTML =
            "<p>No hay notas por área.</p>";
        return;
    }

    let rows = "";

    notasxarea.forEach(a => {
        rows += `
            <tr>
                <td>${a.codearea}</td>
                <td>${a.nombre}</td>
                <td>${a.per1 || ""}</td>
        `;

        // PER2 o PER3 muestran Per2
        if (periodo === "PER2") {
            rows += `<td>${a.per2 || ""}</td>`;
        }

        // solo PER3 muestra Per3
        if (periodo === "PER3") {
            rows += `
            <td>${a.per2 || ""}</td>
            <td>${a.per3 || ""}</td>`;
        }

        // NotaFinalP1 SIEMPRE
        rows += `<td>${a.NotaFinal || ""}</td>`;

        // NotaFinalP2 solo PER2 o PER3
        if (periodo === "PER2") {
            rows += `<td>${a.notafinal2 || ""}</td>`;
        }

        // NotaFinalP3 solo PER3
        if (periodo === "PER3") {
            rows += `
            <td>${a.notafinal2 || ""}</td>
            <td>${a.notafinal3 || ""}</td>`;
        }

        rows += `</tr>`;
    });

    // ENCABEZADO
    let header = `
        <tr>
            <th>Código</th>
            <th>Área</th>
            <th>Per1</th>
    `;

    if (periodo === "PER2" ) {
        header += `<th>Per2</th>`;
    }

    if (periodo === "PER3") {
        header += `
        <th>Per2</th>
        <th>Per3</th>`;
    }

    header += `<th>NotaFinalP1</th>`;

    if (periodo === "PER2") {
        header += `<th>NotaFinalP2</th>`;
    }

    if (periodo === "PER3") {
        header += `
        <th>NotaFinalP2</th>
        <th>NotaFinalP3</th>`;
    }

    header += `</tr>`;

    // TABLA COMPLETA
    let html = `
        <table class="table table-striped table-bordered">
            <thead class="table-dark">
                ${header}
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;

    document.getElementById("gridNotasxestudiantexarea").innerHTML = html;
}
