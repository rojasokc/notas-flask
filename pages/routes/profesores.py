from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection   # ajusta el import según tu proyecto

from flask import current_app

#SCODEEMP = "31"
#from config import (
#    ALECTIVO_ACTUAL,
#    PERIODO_ACTUAL,
#    SCODEEMP,
#    NIVELESCO
#)

#from flask import g

#def alguna_funcion():
#ALECTIVO_ACTUAL = g.config["ALECTIVO_ACTUAL"]
#PERIODO_ACTUAL = g.config["PERIODO_ACTUAL"]

#ALECTIVO_ACTUAL = g.config["ALECTIVO_ACTUAL"]
#PERIODO_ACTUAL = g.config["PERIODO_ACTUAL"]
#SCODEEMP = "31"
#NIVELESCO = "BACHIL"

profesores_bp = Blueprint(
    'profesores',
    __name__,
    url_prefix='/profesores'
)

@profesores_bp.route('/')
def profesores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profesors")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("profesores.html", profesores=data)


@profesores_bp.route('/save_profesor', methods=['POST'])
def save_profesor():
    conn = get_db_connection()
    cursor = conn.cursor()

    #ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    # Datos del formulario

    names       = request.form.get('campo1',"").upper()
    lastname    = request.form.get('campo2',"").upper()
    lastname2   = request.form.get('campo3',"").upper()
    tel         = request.form.get('campo4')
    email1     = request.form.get('campo5')
    profesion  = request.form.get('campo6')
    cargo      = request.form.get('campo7')
    contacto   = request.form.get('campo8')
    login      = request.form.get('campo9')
    password   = request.form.get('campo11')

    if not login or len(login) < 6:
        return render_template("onlycreaprofx.html", error="Login inválido", mensaje="NO se creo el registro login error")

    if not password or len(password) < 6:
        return render_template("onlycreaprofx.html", error="Password inválido", mensaje="NO se creo el registro login error")


    # Datos fijos / sistema
    codeintp = None           # o genera uno
    dir1     = ''
    city1    = ''
    state1   = ''
    zip1     = ''
    pais1    = ''
    scodeemp = SCODEEMP       # variable global que ya usas

    sql = """
        INSERT INTO profesors (
            codeintp, contacto, names, lastname, lastname2,
            dir, tel, email1, city, state, zip, pais,
            profesion, cargo, login, password, scodeemp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        codeintp, contacto, names, lastname, lastname2,
        dir1, tel, email1, city1, state1, zip1, pais1,
        profesion, cargo, login, password, scodeemp
    )

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    return render_template("onlycreaprofx.html", mensaje="Profesor guardado correctamente")

@profesores_bp.route('/delete_profesor/<codeprof>', methods=['POST'])
def delete_profesor(codeprof):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = request.form.get('search', '')
    
    try:
        cursor.execute("DELETE FROM profesors WHERE codeprof = %s", (codeprof,))
        conn.commit()
        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro de profesor: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlycreaprofx', search=search))

@profesores_bp.route('/update_profesor/<codeprof>', methods=['POST'])
def update_profesor(codeprof):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # datos del form
    names      = request.form.get('campo1')
    lastname   = request.form.get('campo2')
    lastname2  = request.form.get('campo3')
    tel        = request.form.get('campo4')
    email1    = request.form.get('campo5')
    profesion = request.form.get('campo6')
    cargo     = request.form.get('campo7')
    contacto  = request.form.get('campo8')
    login     = request.form.get('campo9')

    try:
        cursor.execute("""
            UPDATE profesors
            SET names=%s,
                lastname=%s,
                lastname2=%s,
                tel=%s,
                email1=%s,
                profesion=%s,
                cargo=%s,
                contacto=%s,
                login=%s
            WHERE codeprof=%s
        """, (
            names, lastname, lastname2, tel, email1,
            profesion, cargo, contacto, login,
            codeprof
        ))
        conn.commit()
        flash("Profesor actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar profesor: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlycreaprofx', codeprof=codeprof))