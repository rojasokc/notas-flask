from flask import render_template, Response
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date, datetime
from flask import current_app
from decimal import Decimal, ROUND_HALF_UP
from routes.estudiantes import obtener_estudiantes_por_grado
#from weasyprint import HTML



boletin_bp = Blueprint(
    'boletin',
    __name__,
    url_prefix='/boletin'
)

@boletin_bp.route('/boletines_grado', methods=['POST'])
def boletines_grado():

    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)

    scodeemp = current_app.config.get("SCODEEMP")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    
    codeestu = request.form.get('cualestudiante')
    codegrad = request.form.get('cualgrado')
    periodo = request.form.get('cualperiodoonxe')

    chk_cualestudiante = request.form.get('chk_cualestudiante')
    chk_cualgrado = request.form.get('chk_cualgrado')

    if chk_cualestudiante:
        boletin = construir_boletin(scodeemp, alectivo, codeestu, codegrad, periodo )
    
        return render_template(
            "boletin.html",
            **boletin
        )
    else:
        if chk_cualgrado and not chk_cualestudiante:

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT scodeest
                FROM estudents
                WHERE codegrad = %s
                ORDER BY lastn, lastn2, names
            """, (codegrad,))

            estudiantes = cursor.fetchall()

            cursor.close()
            conn.close()

            html_total = ""

            for est in estudiantes:

                boletin = construir_boletin(
                    scodeemp,
                    alectivo,
                    est["scodeest"],
                    codegrad,
                    periodo
                )

                html = render_template(
                    "boletin.html",
                    **boletin
                )

                html_total += html

                html_total += """
                <div style="page-break-after: always;"></div>
                """
    return html_total #hasta aqui se genera el boletin en html


            #esta parte es para generar el pdf
            #pdf = HTML(string=html_total).write_pdf()

            #return Response(
            #    pdf,
            #    mimetype='application/pdf',
            #    headers={
            #        'Content-Disposition': 'inline; filename=boletines.pdf'
            #    }
            #)
        


def construir_boletin(scodeemp, alectivo, codeestu, codegrad, periodo):
#@boletin_bp.route('/test_boletin')
#def test_boletin():    

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    #scodeemp = current_app.config.get("SCODEEMP")
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    
    #codeestu = request.form.get('cualestudiante')
    #codegrad = request.form.get('cualgrado')
    #periodo = request.form.get('cualperiodoonxe')

    #codeestu = request.args.get('cualestudiante')
    #codegrad = request.args.get('cualgrado')
    #periodo = request.args.get('cualperiodoonxe')

    fechahoy = date.today().strftime("%d/%m/%Y")

    cursor.execute("SELECT * FROM empcole where scodeemp = %s", (scodeemp,))
    datacole = cursor.fetchone()

    cursor.execute("""
            SELECT 
                CONCAT(names, ' ', lastn, ' ', lastn2) AS estuname, 
                estudents.* 
                   FROM estudents where scodeest = %s
            """, (codeestu,))
    dataestu = cursor.fetchone()

    cursor.execute("""
            SELECT 
                colgrados.* 
                   FROM colgrados where codegrad = %s
            """, (codegrad,))
    datagrado = cursor.fetchone()

    cursor.execute("""
            SELECT 
                allparam.* 
                   FROM allparam where scodeemp = %s
            """, (scodeemp,))
    dataallparam = cursor.fetchone()

    cursor.execute("""
            SELECT 
                estustat.* 
                   FROM estustat where codeestu = %s and codegrad = %s
                   group by codeestu
            """, (codeestu, codegrad))
    datapromedio = cursor.fetchone()
    #print(f'promedio de {codeestu} es {datapromedio["promxgp2"]}')

    ##desde aqui empieza la generacion.
    

    cursor.execute("""
        SELECT areasxmate.nombre, caliarea.*,
                obs1.notatt as obstext1,
                obs2.notatt as obstext2,
                obs3.notatt as obstext3,
                obs4.notatt as obstext4,
                obspro1.notatt as obstextpro1,
                obspro2.notatt as obstextpro2,
                obspro3.notatt as obstextpro3,
                obspro4.notatt as obstextpro4                    
            from caliarea join areasxmate 
                ON areasxmate.codearea = caliarea.codearea
                left JOIN observa AS obs4
                    ON obs4.codeobse = caliarea.obspe4            
                left JOIN observa AS obs3
                    ON obs3.codeobse = caliarea.obspe3 
                left JOIN observa AS obs2
                    ON obs2.codeobse = caliarea.obspe2 
                left JOIN observa AS obs1
                    ON obs1.codeobse = caliarea.obspe1
                left JOIN observa AS obspro4
                    ON obspro4.codeobse = caliarea.obsnfinal4                
                left JOIN observa AS obspro3
                    ON obspro3.codeobse = caliarea.obsnfinal3 
                left JOIN observa AS obspro2
                    ON obspro2.codeobse = caliarea.obsnfinal2 
                left JOIN observa AS obspro1
                    ON obspro1.codeobse = caliarea.obsnfinal 
            where caliarea.codegrad = %s 
            and caliarea.codeestu = %s 
            and trim(caliarea.scodeemp) = %s
                    
        """, (codegrad, codeestu, scodeemp))
    dataarea = cursor.fetchall()

    cursor.execute("""
            SELECT
                        LEFT(metsncomp.metaapr,50) as metaapr,
                        LEFT(metsncomp.comptlab,50) as comptlab,
                        LEFT(calimate.rempe4,50) as rempe4,
                        metsncomp.periodo,
                        materia.codearea,
                        materia.nombre,
                        materia.keymate,
                        materia.valorm,
                    CONCAT(profesors.names, ' ', profesors.lastname, ' ', profesors.lastname2) as nombreprof,
                        obs1.notatt as obstxt1,
                        obs2.notatt as obstxt2,
                        obs3.notatt as obstxt3,
                        obspro1.notatt as obstxtpro1,
                        obspro2.notatt as obstxtpro2,
                        obspro3.notatt as obstxtpro3,
                        calimate.*
                    FROM materia
                    JOIN calimate 
                        ON materia.codemate = calimate.codemate    
                    JOIN profesors
                        on profesors.codeprof = materia.codeprof    
                    JOIN metsncomp
                        ON metsncomp.codemate = calimate.codemate
                    left JOIN observa AS obs3
                        ON obs3.codeobse = calimate.obspe3 
                    left JOIN observa AS obs2
                        ON obs2.codeobse = calimate.obspe2 
                    left JOIN observa AS obs1
                        ON obs1.codeobse = calimate.obspe1 
                    left JOIN observa AS obspro3
                        ON obspro3.codeobse = calimate.obsprom3 
                    left JOIN observa AS obspro2
                        ON obspro2.codeobse = calimate.obsprom2 
                    left JOIN observa AS obspro1
                        ON obspro1.codeobse = calimate.obsprom 
                    WHERE calimate.codegrad = %s 
                    AND codeestu = %s 
                    AND TRIM(materia.scodeemp) = %s 
                    AND UCASE(metsncomp.periodo) = %s
                                
                    ORDER BY materia.keymate;
            """, (codegrad, codeestu, scodeemp, periodo))

    dataasignatura = cursor.fetchall()

    areas_dict = {}
    
                ## hasta aqui 

    if periodo == 'PER1':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "nivelpro": area.get('obstext1'),
                "notafinal": area.get('NotaFinal'),
                "nivelprofin": area.get('obstextpro1'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt1'),
                    "promedio": asig.get('promedio'),
                    "nivelperf": asig.get('obstxtpro1'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista
    if periodo == 'PER2':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "per2": area.get('per2'),
                "nivelpro": area.get('obstext2'),
                "notafinal": area.get('NotaFinal'),
                "notafinal2": area.get('notafinal2'),
                "nivelprofin": area.get('obstextpro2'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "nota2": asig.get('nota2'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt2'),
                    "promedio": asig.get('promedio'),
                    "promedio2": asig.get('promedio2'),
                    "nivelperf": asig.get('obstxtpro2'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista

    if periodo == 'PER3':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "per2": area.get('per2'),
                "per3": area.get('per3'),
                "nivelpro": area.get('obstext3'),
                "notafinal": area.get('NotaFinal'),
                "notafinal2": area.get('notafinal2'),
                "notafinal3": area.get('notafinal3'),
                "nivelprofin": area.get('obstextpro3'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "nota2": asig.get('nota2'),
                    "nota3": asig.get('nota3'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt3'),
                    "promedio": asig.get('promedio'),
                    "promedio2": asig.get('promedio2'),
                    "promedio3": asig.get('promedio3'),
                    "nivelperf": asig.get('obstxtpro3'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista
    notas = list(areas_dict.values())

    cursor.close()
    conn.close()

    return {
        "alectivo": alectivo,
        "dataallparam": dataallparam,
        "periodo": periodo,
        "datacole": datacole,
        "dataestu": dataestu,
        "datagrado": datagrado,
        "dataarea": dataarea,
        "dataasignatura": dataasignatura,
        "fechahoy": fechahoy,
        "datapromedio": datapromedio,
        "notas": notas
    }


@boletin_bp.route('/test_boletin', methods=['POST'])
def test_boletin():

    scodeemp = current_app.config.get("SCODEEMP")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    codeestu = request.form.get('cualestudiante')
    codegrad = request.form.get('cualgrado')
    periodo = request.form.get('cualperiodoonxe')

    boletin = construir_boletin(
        scodeemp,
        alectivo,
        codeestu,
        codegrad,
        periodo
    )

    return render_template(
        "boletin.html",
        **boletin
    )

@boletin_bp.route('/test_boletinORI', methods=['POST'])
def test_boletinORI():
#@boletin_bp.route('/test_boletin')
#def test_boletin():    

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    scodeemp = current_app.config.get("SCODEEMP")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    
    codeestu = request.form.get('cualestudiante')
    codegrad = request.form.get('cualgrado')
    periodo = request.form.get('cualperiodoonxe')

    #codeestu = request.args.get('cualestudiante')
    #codegrad = request.args.get('cualgrado')
    #periodo = request.args.get('cualperiodoonxe')

    fechahoy = date.today().strftime("%d/%m/%Y")

    cursor.execute("SELECT * FROM empcole where scodeemp = %s", (scodeemp,))
    datacole = cursor.fetchone()

    cursor.execute("""
            SELECT 
                CONCAT(names, ' ', lastn, ' ', lastn2) AS estuname, 
                estudents.* 
                   FROM estudents where scodeest = %s
            """, (codeestu,))
    dataestu = cursor.fetchone()

    cursor.execute("""
            SELECT 
                colgrados.* 
                   FROM colgrados where codegrad = %s
            """, (codegrad,))
    datagrado = cursor.fetchone()

    cursor.execute("""
            SELECT 
                allparam.* 
                   FROM allparam where scodeemp = %s
            """, (scodeemp,))
    dataallparam = cursor.fetchone()

    cursor.execute("""
            SELECT 
                estustat.* 
                   FROM estustat where codeestu = %s and codegrad = %s
                   group by codeestu
            """, (codeestu, codegrad))
    datapromedio = cursor.fetchone()
    #print(f'promedio de {codeestu} es {datapromedio["promxgp2"]}')

    ##desde aqui empieza la generacion.
    chk_cualestudiante = request.form.get("chk_cualestudiante")
    chk_cualgrado = request.form.get("chk_cualgrado")
    
    if chk_cualestudiante:

        cursor.execute("""
        SELECT areasxmate.nombre, caliarea.*,
                obs1.notatt as obstext1,
                obs2.notatt as obstext2,
                obs3.notatt as obstext3,
                obs4.notatt as obstext4,
                obspro1.notatt as obstextpro1,
                obspro2.notatt as obstextpro2,
                obspro3.notatt as obstextpro3,
                obspro4.notatt as obstextpro4                    
            from caliarea join areasxmate 
                ON areasxmate.codearea = caliarea.codearea
                left JOIN observa AS obs4
                    ON obs4.codeobse = caliarea.obspe4            
                left JOIN observa AS obs3
                    ON obs3.codeobse = caliarea.obspe3 
                left JOIN observa AS obs2
                    ON obs2.codeobse = caliarea.obspe2 
                left JOIN observa AS obs1
                    ON obs1.codeobse = caliarea.obspe1
                left JOIN observa AS obspro4
                    ON obspro4.codeobse = caliarea.obsnfinal4                
                left JOIN observa AS obspro3
                    ON obspro3.codeobse = caliarea.obsnfinal3 
                left JOIN observa AS obspro2
                    ON obspro2.codeobse = caliarea.obsnfinal2 
                left JOIN observa AS obspro1
                    ON obspro1.codeobse = caliarea.obsnfinal 
            where caliarea.codegrad = %s 
            and caliarea.codeestu = %s 
            and trim(caliarea.scodeemp) = %s
                    
        """, (codegrad, codeestu, scodeemp))
        dataarea = cursor.fetchall()

        cursor.execute("""
            SELECT
                        LEFT(metsncomp.metaapr,50) as metaapr,
                        LEFT(metsncomp.comptlab,50) as comptlab,
                        LEFT(calimate.rempe4,50) as rempe4,
                        metsncomp.periodo,
                        materia.codearea,
                        materia.nombre,
                        materia.keymate,
                        materia.valorm,
                    CONCAT(profesors.names, ' ', profesors.lastname, ' ', profesors.lastname2) as nombreprof,
                        obs1.notatt as obstxt1,
                        obs2.notatt as obstxt2,
                        obs3.notatt as obstxt3,
                        obspro1.notatt as obstxtpro1,
                        obspro2.notatt as obstxtpro2,
                        obspro3.notatt as obstxtpro3,
                        calimate.*
                    FROM materia
                    JOIN calimate 
                        ON materia.codemate = calimate.codemate    
                    JOIN profesors
                        on profesors.codeprof = materia.codeprof    
                    JOIN metsncomp
                        ON metsncomp.codemate = calimate.codemate
                    left JOIN observa AS obs3
                        ON obs3.codeobse = calimate.obspe3 
                    left JOIN observa AS obs2
                        ON obs2.codeobse = calimate.obspe2 
                    left JOIN observa AS obs1
                        ON obs1.codeobse = calimate.obspe1 
                    left JOIN observa AS obspro3
                        ON obspro3.codeobse = calimate.obsprom3 
                    left JOIN observa AS obspro2
                        ON obspro2.codeobse = calimate.obsprom2 
                    left JOIN observa AS obspro1
                        ON obspro1.codeobse = calimate.obsprom 
                    WHERE calimate.codegrad = %s 
                    AND codeestu = %s 
                    AND TRIM(materia.scodeemp) = %s 
                    AND UCASE(metsncomp.periodo) = %s
                                
                    ORDER BY materia.keymate;
            """, (codegrad, codeestu, scodeemp, periodo))

        dataasignatura = cursor.fetchall()

        areas_dict = {}
    else:
        if chk_cualgrado == "1" and not chk_cualestudiante:
            print(f'NO selecciono un estudiante VAMOS por el grupo')
                ## hasta aqui 

    if periodo == 'PER1':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "nivelpro": area.get('obstext1'),
                "notafinal": area.get('NotaFinal'),
                "nivelprofin": area.get('obstextpro1'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt1'),
                    "promedio": asig.get('promedio'),
                    "nivelperf": asig.get('obstxtpro1'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista
    if periodo == 'PER2':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "per2": area.get('per2'),
                "nivelpro": area.get('obstext2'),
                "notafinal": area.get('NotaFinal'),
                "notafinal2": area.get('notafinal2'),
                "nivelprofin": area.get('obstextpro2'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "nota2": asig.get('nota2'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt2'),
                    "promedio": asig.get('promedio'),
                    "promedio2": asig.get('promedio2'),
                    "nivelperf": asig.get('obstxtpro2'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista

    if periodo == 'PER3':
        # 🔹 Crear estructura base de áreas
        for area in dataarea:
            areas_dict[area['codearea']] = {
                "nombre": area['nombre'],
                "per1": area.get('per1'),
                "per2": area.get('per2'),
                "per3": area.get('per3'),
                "nivelpro": area.get('obstext3'),
                "notafinal": area.get('NotaFinal'),
                "notafinal2": area.get('notafinal2'),
                "notafinal3": area.get('notafinal3'),
                "nivelprofin": area.get('obstextpro3'),
                "asignaturas": []            
                
            }

        # 🔹 Agregar asignaturas a cada área
        for asig in dataasignatura:
            codearea = asig.get('codearea')

            if codearea in areas_dict:
                areas_dict[codearea]["asignaturas"].append({
                    "nombre": asig['nombre'],
                    "nota1": asig.get('nota1'),
                    "nota2": asig.get('nota2'),
                    "nota3": asig.get('nota3'),
                    "valorm": asig.get('valorm'),
                    "nivel": asig.get('obstxt3'),
                    "promedio": asig.get('promedio'),
                    "promedio2": asig.get('promedio2'),
                    "promedio3": asig.get('promedio3'),
                    "nivelperf": asig.get('obstxtpro3'),
                    "metaapr": asig.get('metaapr'),
                    "comptlab": asig.get('comptlab'),
                    "nombreprof": asig.get('nombreprof')
                })

        # 🔹 Convertir a lista
    notas = list(areas_dict.values())

    cursor.close()
    conn.close()

    return render_template("boletin.html", 
        alectivo=alectivo,
        dataallparam=dataallparam,
        periodo=periodo,
        datacole=datacole, 
        dataestu=dataestu, 
        datagrado=datagrado, 
        dataarea=dataarea, 
        dataasignatura=dataasignatura,
        fechahoy=fechahoy,
        datapromedio=datapromedio,
        notas=notas)




@boletin_bp.route('/pre_boletin')
def pre_boletin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    scodeemp = current_app.config.get("SCODEEMP")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    return render_template("preboletin.html")

@boletin_bp.route('/promedio_boletin', methods=['POST'])
def promedio_boletin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    nivel_radio = request.form.get("nivel_radio", "")
    if nivel_radio:
        if nivel_radio == "1":
            nivelesco = "PREBAS"
            #totareas1 = "7"
        elif nivel_radio == "2":
            nivelesco = "PRIMAR"
            #totareas1 = "11"
        elif nivel_radio == "3":
            nivelesco = "BACHIL"
            #totareas1 = "10"

    cualperiodoonxe = request.form.get("cualperiodoonxe")
    chk_cualgrado = request.form.get("chk_cualgrado")
    chk_cualestudiante = request.form.get("chk_cualestudiante")

    scodeemp = current_app.config.get("SCODEEMP")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")

    codeestu = request.form.get('cualestudiante')
    codegrad = request.form.get('cualgrado')
    periodo = request.form.get('cualperiodoonxe')

    ##esta parte recarga el grado seleccionado
    cursor.execute("""
            SELECT codegrad, name
                FROM colgrados
                WHERE TRIM(nivelesco) = %s
                ORDER BY codegrad
            """, (nivelesco,))
    lista_grados_persist = cursor.fetchall()

    cursor.execute("""
               SELECT codegrad, name
                FROM colgrados
                WHERE codegrad = %s
            """, (codegrad,))
    grado_sel = cursor.fetchone()

    ##esta parte recarga el estudiante seleccionado, se llama a una funcion definida en estudiantes.py
    estudiantesxgrado = []
    estudiantesxgrado = obtener_estudiantes_por_grado(codegrad)
    
    #for est in estudiantesxgrado:
    #    print(est["nombre"])

    cursor.execute("""
               SELECT scodeest,  CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre 
                FROM estudents
                WHERE codegrad = %s and scodeest = %s
            """, (codegrad, codeestu))
    estudentsfound = cursor.fetchone()

    ## hasta aqui


    #print(f'entre a promedio_boletin: {codegrad}')
    campo_nota = {
        'PER1': 'notafinal',
        'PER2': 'notafinal2',
        'PER3': 'notafinal3',
        'PER4': 'notafinal4'
        }[periodo]

    campo_prom = {
            'PER1': 'promxgp1',
            'PER2': 'promxgp2',
            'PER3': 'promxgp3',
            'PER4': 'promxgp4'
        }[periodo]

    campo_puesto = {
            'PER1': 'puestop1',
            'PER2': 'puestop2',
            'PER3': 'puestop3',
            'PER4': 'puestop4'
        }[periodo]


    query = f"""
        UPDATE estustat e
        JOIN (
            SELECT 
                codeestu,
                codegrad,
                scodeemp,
                ROUND(AVG({campo_nota}), 1) AS promedio,

                DENSE_RANK() OVER (
                    ORDER BY ROUND(AVG({campo_nota}), 1) DESC
                ) AS puesto

            FROM caliarea
            WHERE codegrad = %s
            AND scodeemp = %s

            GROUP BY codeestu, codegrad, scodeemp
        ) t

        ON e.codeestu = t.codeestu
        AND e.codegrad = t.codegrad
        AND e.scodeemp = t.scodeemp

        SET 
            e.{campo_prom} = t.promedio,
            e.{campo_puesto} = t.puesto

        WHERE e.codegrad = %s
        AND e.scodeemp = %s
        AND e.alectivo = %s
        """
    cursor.execute(query, (
            codegrad,
            scodeemp,
            codegrad,
            scodeemp,
            alectivo
        ))

    

    if codegrad:
        estudiantesxgrado = obtener_estudiantes_por_grado(codegrad)

    return render_template("preboletin.html",
        cualgrado=codegrad,
        cualestudiante=codeestu,
        cualperiodoonxe=periodo,
        nivel_radio=nivel_radio,
        gradomx_sel=grado_sel,
        lista_grados_persist=lista_grados_persist,
        estudiantesxgrado=estudiantesxgrado,
        estudentsfound=estudentsfound,
        chk_cualgrado=chk_cualgrado,
        chk_cualestudiante=chk_cualestudiante
        )
    #return redirect(url_for(
    #    'boletin.test_boletin',
    #    cualgrado=codegrad,
    #    cualestudiante=codeestu,
    #    cualperiodoonxe=periodo
    #))