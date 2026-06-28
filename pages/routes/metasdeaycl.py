from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date, datetime

from flask import current_app

#SCODEEMP = "31"
#from config import (
    #ALECTIVO_ACTUAL,
    #PERIODO_ACTUAL,
#    SCODEEMP,
#    NIVELESCO
#)

#from flask import g

#def alguna_funcion():
#ALECTIVO_ACTUAL = g.config["ALECTIVO_ACTUAL"]
#PERIODO_ACTUAL = g.config["PERIODO_ACTUAL"]
#SCODEEMP = "31"
#NIVELESCO = "BACHIL"

metasdea_bp = Blueprint(
    'metasdea',
    __name__,
    url_prefix='/metasdea'
)

NIVEL_MAP = {
    "1": "PREBAS",
    "2": "PRIMAR",
    "3": "BACHIL"
}

PERIODO_MAP = {
    "1": "PER1",
    "2": "PER2",
    "3": "PER3",
    "4": "PER4",
    "5": "PER5"
}

@metasdea_bp.route('/', methods=["GET", "POST"])
def index():

    registros = []

    grado_sel = None
    nivel_radio = None
    nivel_per = None
    codegrad1 = None
    lista_grados_persist = [] # Nueva variable para persistir el select

    #nivelesco1 = NIVEL_MAP.get(nivel_radio)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP #session.get("scodeemp")   # o desde config
    alectivo1 = ALECTIVO_ACTUAL
    periodo = PERIODO_ACTUAL

    codegrad1 = request.form.get("campo2_hidden")  # si viene oculto
    

    # ===== NIVEL ESCOLAR =====
    nivel_radio = request.form.get("nivel_radio")
    nivelesco1 = NIVEL_MAP.get(nivel_radio)

    # ===== PERIODO =====
    nivel_per = request.form.get("nivel_per")
    periodo1 = PERIODO_MAP.get(nivel_per)
    
    #if nivelesco1:
    #    # Aquí usa la misma lógica que tu ruta '/get_grados_por_nivel'
    #    cursor.execute("SELECT codegrad, name FROM colgrados WHERE nivelesco = %s", (nivelesco1,))
    #    lista_grados_persist = cursor.fetchall()

    if request.method == "POST":
        nivel_radio = request.form.get("nivel_radio")
        nivel_per   = request.form.get("nivel_per")
        codegrad1 = request.form.get("campo2_hidden")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if nivelesco1:
            # Aquí usa la misma lógica que tu ruta '/get_grados_por_nivel'
            cursor.execute("SELECT codegrad, name FROM colgrados WHERE nivelesco = %s", (nivelesco1,))
            lista_grados_persist = cursor.fetchall()

        if codegrad1:
            

            cursor.execute("""
                SELECT codegrad, name
                FROM colgrados
                WHERE codegrad = %s
            """, (codegrad1,))

            grado_sel = cursor.fetchone()

        if nivelesco1 and periodo1:

            #conn = get_db_connection()
            #cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT metsncomp.*
                FROM metsncomp
                WHERE TRIM(metsncomp.scodeemp) = %s
                  AND metsncomp.codegrad = %s
                  AND periodo = %s
                  AND alectivo = %s
            """, (scodeemp1, codegrad1, periodo1, alectivo1))

            registros = cursor.fetchall()

            cursor.close()
            conn.close()

    return render_template(
        "onlyeditmetascf.html",
        registros=registros,
        gradosxm_sel=grado_sel,
        nivel_radio=nivel_radio,
        nivel_per=nivel_per,
        lista_grados_persist=lista_grados_persist
    )


@metasdea_bp.route('/ajax_grid', methods=['POST'])
def ajax_grid():
    data = request.get_json()
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP
    alectivo = ALECTIVO_ACTUAL
    periodo = PERIODO_ACTUAL

    codegrad1 = data.get('codegrad')
    nivel_radio = data.get('nivel_radio')
    nivel_per = data.get('nivel_per')

    nivelesco1 = NIVEL_MAP.get(nivel_radio)
    periodo1   = PERIODO_MAP.get(nivel_per)

    registros = []

    if nivelesco1 and periodo1 and codegrad1:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT metsncomp.*
            FROM metsncomp
            WHERE TRIM(scodeemp) = %s
              AND codegrad = %s
              AND periodo = %s
              AND alectivo = %s
        """, (scodeemp1, codegrad1, periodo1, alectivo)) #aqui era ALECTIVO_ACTUAL

        registros = cursor.fetchall()
        nivel_grado = registros[0]["nivelgrado"] if registros else ""

        cursor.close()
        conn.close()

    return render_template(
        "partials/grid_metas.html",
        registros=registros,
        nivel_grado=nivel_grado
    )


@metasdea_bp.route('/update_metasdea', methods=['POST'])
def update_metasdea():
    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        total = int(request.form.get("total_filas", 0))
        guardar_por_nivel = request.form.get("chk_pornivel") == "1"

        periodo1 = PERIODO_MAP.get(request.form.get("nivel_per"))
        nivelgrado1 = request.form.get("nivel_grado")

        for i in range(1, total + 1):
            codemeco = request.form.get(f"codemeco_{i}")
            metaapr  = request.form.get(f"metaapr_{i}")
            comptlab = request.form.get(f"comptlab_{i}")
            nombre   = request.form.get(f"nombre_{i}")

            if not codemeco:
                continue

            if guardar_por_nivel:
                # 🔁 UPDATE por nivel (legacy 2)
                cursor.execute("""
                    UPDATE metsncomp
                    SET metaapr = %s,
                        comptlab = %s
                    WHERE nombre = %s
                    AND UPPER(periodo) = %s
                    AND nivelgrado = %s
                """, (metaapr, comptlab, nombre, periodo1, nivelgrado1))

            else:
                # 🎯 UPDATE puntual (legacy 1)
                cursor.execute("""
                    UPDATE metsncomp
                    SET metaapr = %s,
                        comptlab = %s
                    WHERE codemeco = %s
                """, (metaapr, comptlab, codemeco))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(ok=True)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

    #flash("Metas actualizadas correctamente", "success")
    #return redirect(url_for('metasdea.index'))