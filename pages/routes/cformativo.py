from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date, datetime
from flask import jsonify
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

cformativo_bp = Blueprint(
    'cformativo',
    __name__,
    url_prefix='/cformativo'
)

def obtener_nivelesco(valor):
    return {
        "1": "PREBAS",
        "2": "PRIMAR",
        "3": "BACHIL"
    }.get(valor)

@cformativo_bp.route('/', methods=['GET', 'POST'])
def index():

    nivelesco1 = None 
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp = SCODEEMP
    nivel_radio = request.args.get("nivel_radio")
    nivelesco1 = obtener_nivelesco(nivel_radio)

    codearea = request.args.get("searcharea")
    nombrearea = request.args.get("nombrearea")

    #codearea1 = request.args.get("codearea")

        # Determinar nivel escolar
    #nivelesco1 = None
    #if nivel_radio == "1":
    #        nivelesco1 = "PREBAS"
    #elif nivel_radio == "2":
    #        nivelesco1 = "PRIMAR"
    #elif nivel_radio == "3":
    #        nivelesco1 = "BACHIL"

    searcharea = request.args.get("searcharea", "").strip()
    niveldesem1 = request.args.get("niveldesem", "").strip()
    codeform1 = request.args.get("codeform", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)


    #nivelesco1 = "BACHIL"
    
          
    data = []
    cformati = []
    observa_rows = []
    

    params = []
    query = """
        SELECT formativo.* 
        FROM formativo 
        WHERE trim(scodeemp) = %s
    """
    params.append(scodeemp)

    if searcharea:

        if nivelesco1:
                query += " AND nivelesco = %s"
                params.append(nivelesco1)

        if niveldesem1:
                query += " AND notatt = %s"
                params.append(niveldesem1)

        if searcharea:
                query += " AND trim(codearea) LIKE %s"
                params.append(f"{searcharea}%")

        query += " ORDER BY nombre"
    else:
        query += ' AND nivelesco = "zzzzz"'

    cursor.execute(query, params)
    cformati = cursor.fetchall()

                #cursor.execute(query, (SCODEEMP, nivelesco1, codearea1)) --             AND TRIM(codearea) = %s

    # Seleccionamos el area
    cursor.execute("""
            SELECT *
            FROM areasxmate
            WHERE TRIM(scodeemp) = %s
            ORDER BY codearea
        """, (scodeemp,))

    areasxmate = cursor.fetchall()

    # Seleccionamos la asignatura
    #cursor.execute("""
    #        SELECT *
    #        FROM materiamas
    #        WHERE TRIM(scodeemp) = %s
    #    """, (scodeemp,))

    if searcharea and nivelesco1:
        cursor.execute("""
            SELECT materia.*, colgrados.nivelgrado, colgrados.name as pp 
                from materia inner join colgrados 
                on materia.name = colgrados.name 
                where codearea = %s AND materia.nivelesco = %s 
                group by nombre
        """, (f"{searcharea}",nivelesco1))
    else:
        materxmate = []

    materxmate = cursor.fetchall()

    # Seleccionamos la Nivel de desmpeño
    if nivelesco1:
        cursor.execute("""
            SELECT observa.* FROM observa
            WHERE TRIM(observa.scodeemp) = %s
            AND nivelesco = %s
            AND CHAR_LENGTH(notatt) > 1
            ORDER BY rangoini DESC
            """,(scodeemp, nivelesco1))
        
    else:
        cursor.execute("""
            SELECT observa.* FROM observa
            WHERE TRIM(observa.scodeemp) = %s
            AND notatt = "zzzzz"
            ORDER BY rangoini DESC
        """,(scodeemp,))
    observa_rows = cursor.fetchall()

    areaelecta =[]
    areaelecta1 = []

    if searcharea:
        cursor.execute("""
            SELECT nombre 
            FROM areasxmate
            WHERE codearea = %s
            LIMIT 1
        """, (searcharea,))
        areaelecta = cursor.fetchone()
    if areaelecta:
            areaelecta1 = areaelecta["nombre"]

    # REGISTRO SELECCIONADO
    forma_sel = None
    if codeform1:
        cursor.execute("""
            SELECT formativo.*, areasxmate.nombre as areanombre
            FROM formativo inner join areasxmate
            on formativo.codearea = areasxmate.codearea
            WHERE codeform = %s
        """, (codeform1,))
        forma_sel = cursor.fetchone()

    
    cursor.close()
    conn.close()

    return render_template(
        "onlycreaformativo.html",
        cformati=cformati,
        areasxmate=areasxmate,
        materxmate=materxmate,
        observa_rows=observa_rows,
        areaelecta=areaelecta1,
        forma_sel=forma_sel,
        searcharea=searcharea,
        niveldesem=niveldesem1,
        nivel_radio=nivel_radio,
        nombrearea=nombrearea
        )
    

@cformativo_bp.route('/materias_por_area')
def materias_por_area():
    codearea = request.args.get("codearea")
    nivel_radio = request.args.get("nivel_radio")
    nivelesco1 = obtener_nivelesco(nivel_radio)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT materia.nombre, materia.codemate
        FROM materia
        WHERE codearea = %s AND nivelesco = %s
        GROUP BY nombre
    """, (codearea, nivelesco1))

    materias = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(materias)

@cformativo_bp.route('/save_formativo', methods=['POST'])
def save_formativo():
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP
    alectivo1 = ALECTIVO_ACTUAL

    conn = get_db_connection()
    cursor = conn.cursor()

    nivel_radio = request.form.get('nivel_radio')
    if nivel_radio == "1":
        nivelesco1 = "PREBAS"
    elif nivel_radio == "2":
        nivelesco1 = "PRIMAR"
    elif nivel_radio == "3":
        nivelesco1 = "BACHIL"
    else:
        nivelesco1 = None

    # ====== Datos del formulario ======
    
    codemate1   = request.form.get('nivelasignaturat_hidden')   # codigo de materia
    nombre1   = request.form.get('nivelasignaturat') 
    notatt1   = request.form.get('niveldesemt') # nivel de desempeño
    codeobse1   = request.form.get('niveldesemt_hidden') # nivel de desempeño , codigo
    concepto1   = request.form.get('campo2') # concepto formativo
    codearea1   = request.form.get('nivelareat_hidden')   #code área
    nivelmate1 = str(codearea1).strip() + "1"

    cursor.execute("""
        INSERT INTO formativo 
        ( codemate, nombre, notatt, codeobse, nivelesco,scodeemp,
        alectivo,concepto,nivelmate,codearea 
        ) VALUES ( 
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            codemate1,
            nombre1,
            notatt1,
            codeobse1,
            nivelesco1,
            scodeemp1,
            alectivo1,
            concepto1,
            nivelmate1,
            codearea1,

        ))

   

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('cformativo.index'))

@cformativo_bp.route('/delete_formativo/<codeform>', methods=['POST'])
def delete_formativo(codeform):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchform = request.form.get('searchform', '')
    
    try:
        cursor.execute("DELETE FROM formativo WHERE codeform = %s", (codeform,))
        conn.commit()
        flash("Registro eliminado correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cformativo.index', searchform=searchform))

@cformativo_bp.route('/update_formativo/<codeform>', methods=['POST'])
def update_formativo(codeform):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1=SCODEEMP
    alectivo1=ALECTIVO_ACTUAL

    searcharea = request.form.get("searcharea", "").strip()
    niveldesem1 = request.form.get("niveldesem", "").strip()
    nivel_radio = request.form.get("nivel_radio")
    nombrearea = request.form.get("nombrearea")


    nivelesco1 = ""
    if request.method == 'POST':
        if request.form.get('nivel_radio') == '1':
            nivelesco1 = "PREBAS"
        elif request.form.get('nivel_radio') == '2':
            nivelesco1 = "PRIMAR"
        elif request.form.get('nivel_radio') == '3':
            nivelesco1 = "BACHIL"


    codemate1   = request.form.get('nivelasignaturat_hidden')   # codigo de materia
    nombre1   = request.form.get('nivelasignaturat') 
    notatt1   = request.form.get('niveldesemt') # nivel de desempeño
    codeobse1   = request.form.get('niveldesemt_hidden') # nivel de desempeño , codigo
    concepto1   = request.form.get('campo2') # concepto formativo
    codearea1   = request.form.get('nivelareat_hidden')   #code área
    nivelmate1 = str(codearea1).strip() + "1"


    try:
        cursor.execute("""
            UPDATE formativo
            SET codemate=%s,
                nombre=%s,
                notatt=%s,
                codeobse=%s,
                concepto=%s,
                codearea=%s,
                nivelmate=%s,
                scodeemp=%s,
                alectivo=%s,
                nivelesco=%s


            WHERE codeform=%s
        """, (
            codemate1, nombre1, notatt1, codeobse1, concepto1,
            codearea1, nivelmate1, scodeemp1, alectivo1,
            nivelesco1, codeform
        ))
        conn.commit()
        flash("Formativo actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar registro: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('cformativo.index', 
                            searcharea=searcharea,
                            niveldesem=niveldesem1,
                            nivel_radio=nivel_radio,
                            nombrearea=nombrearea,
                            codeform=codeform))