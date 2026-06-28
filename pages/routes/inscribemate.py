from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import jsonify
from db import get_db_connection   # ajusta el import según tu proyecto
from routes.services_notas import chckNOTASxMatriinsCRITA
from routes.services_notas import savematri
from routes.services_notas import savenotasxmatri
from routes.services_notas import savepuntajesxmatri

from routes.services_notas import savenotasxarea
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

addmaterias_bp = Blueprint(
    'addmaterias',
    __name__,
    url_prefix='/addmaterias'
)

@addmaterias_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #lista_grados_persist = []
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1=SCODEEMP

    cursor.execute("SELECT * FROM estudents")
    data = cursor.fetchall()

    
    cursor.close()
    conn.close()
    return render_template("onlybusmtins.html") ##, estudents=data)


@addmaterias_bp.route('/ajax_muestra_asignaturas')
def ajax_muestra_asignaturas():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP
    periodo = PERIODO_ACTUAL

    cualestudiante = request.args.get("cualestudiante")
    
    codeestu = request.args.get("codeestu")
    codegrad = request.args.get("codegrad")

    print(f'codeestu: ', codeestu)
    print(f'codegrad: ', codegrad)
    print(f'periodo: ', periodo)

    cursor.execute("""
        select estudents.names,estudents.lastn,estudents.lastn2,
            estudents.scodeest,estudents.codeint,estudents.codegrad, 
            calinotas.codemate, 
            materia.nombre, materia.codemate,
            colgrados.name, 
            estudents.alectivo, 
            CONCAT(profesors.names, ' ', profesors.lastname, ' ', profesors.lastname2) as profname 
            from calinotas join estudents
                on calinotas.codeestu = estudents.scodeest
                join materia
                on materia.codemate = calinotas.codemate
                join colgrados
                on estudents.codegrad = colgrados.codegrad
                join profesors 
                on materia.codeprof = profesors.codeprof
            where calinotas.codeestu = %s   
            AND calinotas.codegrad = %s  
            group by calinotas.codemate 
            order by materia.codemate
    """, (codeestu, codegrad))

    asignaturasact = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "inscribemate/_filas_asinaturas_inscritas.html", 
        asignaturasact=asignaturasact,
        periodo=periodo,
        cualestudiante=cualestudiante,
        
    )



@addmaterias_bp.route('/ajax_muestra_areas')
def ajax_muestra_areas():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP
    periodo = PERIODO_ACTUAL

    chk_verhabilita = bool(request.args.get("chk_verhabilita"))

    cualestudiante = request.args.get("cualestudiante")
    
    codeestu = request.args.get("codeestu")
    codegrad = request.args.get("codegrad")

    cursor.execute("""
    SELECT areasxmate.nombre, caliarea.* 
        from caliarea join areasxmate 
            ON areasxmate.codearea = caliarea.codearea 
        where caliarea.codegrad = %s 
        and caliarea.codeestu = %s 
        and trim(caliarea.scodeemp) = %s
                   
    """, (codegrad, codeestu, scodeemp1))
    notasyareasact = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "estudiantes/_filas_areas.html",
        notasyareasact=notasyareasact)


@addmaterias_bp.route('/inscribematxest/', methods=['POST'])
def inscribematxest():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando

    periodo = PERIODO_ACTUAL

    data = request.get_json()
    codegrad = data.get('codegrad')
    codeestu = data.get('codeestu')

    #codegrad = request.args.get('cualgrado')
    #codeestu = request.args.get('cualestudiante') 
    

    cursor.execute("""
        SELECT * FROM materia 
            where codegrad = %s 
            and scodeemp = %s
    """, (codegrad, scodeemp1))
    chckttmate = cursor.fetchall()

    

    ## con esta variable chckttmate hago el for 
    #y tengo que sacar estas dos variables:
    # TextBox27.Text = dt.Rows(ii - 1).Item("codemate") ''saca codigo de materia
    # TextBox1.Text = dt.Rows(ii - 1).Item("keymate") ''saca keycode
    #print(f'antes del for: {codegrad}')
    #print(f"TOTAL MATERIAS: {len(chckttmate)}")
    try:
        #i=0
        for n in chckttmate:
            #i= i + 1
            codemate = n["codemate"]
            keymate = n["keymate"]
            #print(f'codemate: {codemate}')
            #print(f'keymate: {keymate}')
            cursor.execute("""
                SELECT * FROM calimate 
                    where codegrad = %s 
                    and scodeemp = %s 
                    and codeestu = %s 
                    and codemate = %s
            """, (codegrad, scodeemp1, codeestu, codemate))
            chckttmateinscrita = cursor.fetchone()
            if chckttmateinscrita:
                ##verifica el proceso con:
                notas = chckNOTASxMatriinsCRITA(cursor, codeestu, codegrad, codemate)
                if notas:
                    print(f'tiene asg, cargadas')
                else:
                    ##PRIMERO VERIFICA SI EXISTE LA MATERIA YA INSCRITA SI SI, NO GRABA, SI NO CREA
                    #print(f'NOO tiene notas hay que ejecutar dos rtuinas: saveNOTASxMatri() y savepuntajesxmatri() ')
                    savenotasxmatri(cursor, codeestu, codegrad, codemate)
                #    if i == 0:
                    savepuntajesxmatri(cursor, codeestu, codegrad, codemate)
            else:
                #''PRIMERO VERIFICA SI EXISTE LA MATERIA YA INSCRITA SI SI, NO GRABA, SI NO CREA
                
                #print(f'NOO tiene nada inscrito hay que ejecutar tres rtuinas: saveMatri() y saveNOTASxMatri() y savepuntajesxmatri() ')
                savematri(cursor, codeestu, codegrad, codemate, keymate)
                savenotasxmatri(cursor, codeestu, codegrad, codemate)
                #if i == 0:
                savepuntajesxmatri(cursor, codeestu, codegrad, codemate)

        #aqui iria la parte de area
        #aqui finaliza

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return "Error en proceso", 500
    finally:
        cursor.close()
        conn.close()        

    #AQUI LLAMO LA FUNCION DE CARGAR DATOS

    #aqui se guarda areas
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    #aqui iba el codigo
    cursor.execute("""
        SELECT * FROM materia 
            where codegrad = %s 
            and scodeemp = %s
    """, (codegrad, scodeemp1))
    chckttareas = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM estudents 
                    where scodeest = %s 
    """, (codeestu,))
    chckareainscrita = cursor.fetchone()
    nombret = f"{chckareainscrita['names']} {chckareainscrita['lastn']} {chckareainscrita['lastn2']}"
 
    for n in chckttareas:
        #print(f'entre al for de area')
        codearea = n["codearea"]
        codemate = n["codemate"]
        #keymate = n["keymate"]
        cursor.execute("""
            SELECT * FROM caliarea 
                where codearea = %s 
                and codegrad = %s 
                and scodeemp = %s 
                and codeestu = %s

        """, (codearea, codegrad, scodeemp1, codeestu))
        chckareainscrita = cursor.fetchone()

        if not chckareainscrita:
            #print(f'NOO tiene nada inscrito hay que ejecutar una rtuinas: saveNOTASxArea() ')
            savenotasxarea(cursor, codeestu, codegrad, codemate, codearea, nombret)

    conn.commit()
    cursor.close()
    conn.close() 

    #cursor.close()
    #conn.close()
    return jsonify({"status": "ok"})
