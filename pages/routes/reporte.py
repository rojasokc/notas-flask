from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date, datetime
from flask import current_app
from config_loader import cargar_parametros


#SCODEEMP = "31"
#from config import (
#    #ALECTIVO_ACTUAL,
#    #PERIODO_ACTUAL,
#    SCODEEMP,
#    NIVELESCO
#)

#from flask import g

#def alguna_funcion():
#ALECTIVO_ACTUAL = g.config["ALECTIVO_ACTUAL"]
#PERIODO_ACTUAL = g.config["PERIODO_ACTUAL"]
#SCODEEMP = "31"
#NIVELESCO = "BACHIL"


reporte_bp = Blueprint(
    'reporte',
    __name__,
    url_prefix='/reporte'
)

#config = cargar_parametros()

#P1 = config["PORC_PER1"]
#P2 = config["PORC_PER2"]
#P3 = config["PORC_PER3"]
#P4 = config["PORC_PER4"]
#P5 = config["PORC_PER5"]



@reporte_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    lista_grados_persist = []
    #ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    #temporal
    periodo = "PER2"

    scodeemp1=SCODEEMP
    grado_sel = None
    cualgen = None
    estudents = None
    having4 = ""
    totareas1=1
    nivelesco = None

    nivel_radio = request.args.get("nivel_radio", "")
    #aqui saca los grados por nivel academico, BACHIL, PRIMAR; PRESBAS
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
   
    #totareas1=int(totareas1)
    #para saber el toto de areas dinamicamente
    codegrad1 = request.args.get("cualgrado", "").strip()
    print(f' code grado: {codegrad1}')
    #SELECT * FROM tucodata.caliarea where codegrad = '104000' group by codearea;
    if codegrad1:
        cursor.execute("""
            SELECT codearea
            FROM caliarea
            WHERE codegrad = %s group by codearea
            """, (codegrad1,))
        lista_grados_persist  = cursor.fetchall()
        totareas1 = len(lista_grados_persist )

    #print(f' total registros: {totareas1}')

    #fin

    cursor.execute("""
            SELECT codegrad, name
                FROM colgrados
                WHERE TRIM(nivelesco) = %s
                ORDER BY codegrad
            """, (nivelesco,))
    lista_grados_persist = cursor.fetchall()

    


    nivel_min3p = request.args.get("nivel_min3p", "")
    if nivel_min3p:
        if nivel_min3p == "1":
            #print("maria")
            having4 = " ORDER BY materia.codemate,estudents.lastn "
        if nivel_min3p == "2":
            #print("maria2")
            having4 = " ORDER BY nombre,materia.codemate "

    
    cualperiodotot = request.args.get("cualperiodotot", "") ## trae el periodo para prom toto por per
    if cualperiodotot == "PER1":
        campo_periodo = "caliarea.per1"
    elif cualperiodotot == "PER2":
        campo_periodo = "caliarea.per2"
    elif cualperiodotot == "PER3":
        campo_periodo = "caliarea.per3"
    else:
        campo_periodo = "caliarea.per1"
    
    #estas dos lineas son para ver el consolidado_notas_estudiante.html
    #codegrad = request.args.get("codegrad")
    #codeestu = request.args.get("codeestu")

    

    #mostrar_iframe = False
    #iframe_url = ""
    #codegrad1 = request.args.get("cualgrado", "").strip()
    #chk_cualestudiante = request.args.get("chk_cualestudiante")
    #codeestu = request.args.get("cualestudiante")
    #periodo="PER2"

    #print(f'este codegrad viene de reporte1: {codegrad1}')
    #print(f'este codeestu viene de reporte1: {codeestu}')
    #print(f'este periodo viene de reporte1: {periodo}')

    #if chk_cualestudiante and codeestu:
    #    mostrar_iframe = True
    #    iframe_url = (
    #        f"/consolidado_notas_estudiante"
    #        f"?codegrad={codegrad1}"
    #        f"&codeestu={codeestu}"
    #    )

    areasxgrado = request.args.get("areasxgrado", "")
    
    

    chk_pornivel = request.args.get("chk_pornivel", "")
    

    chk_TICC = request.args.get("chk_TICC")
    chk_EPS = request.args.get("chk_EPS")
    chk_despla = request.args.get("chk_despla")
    chk_rh = request.args.get("chk_rh")
    chk_padre = request.args.get("chk_padre")
    chk_telpadre = request.args.get("chk_telpadre")
    chk_madre = request.args.get("chk_madre")
    chk_telmadre = request.args.get("chk_telmadre")

    

    chckgrado = request.args.get("chk_pornivel", "").strip()
    cualgen = request.args.get("cualgen", "").strip()
    chk_gen = bool(request.args.get("chk_gen", ""))
    edadmayorq = request.args.get("edadmayorq", "").strip()
    chk_emayorq = bool(request.args.get("chk_emayorq", ""))
    edadmenorq = request.args.get("edadmenorq", "").strip()
    chk_emenorq = bool(request.args.get("chk_emenorq", ""))
    
    cualnivelgrado = request.args.get("cualnivelgrado", "").strip()

    chk_pornivelogrado = request.args.get("chk_pornivelogrado", "")

    chk_nivelxgrado = bool(request.args.get("chk_nivelxgrado", ""))
    chk_promxgrado = bool(request.args.get("chk_promxgrado", ""))
    chk_min3erper = bool(request.args.get("chk_min3erper", ""))

    cualrango = request.args.get("cualrango", "").strip()
    

    chk_promtotxest = bool(request.args.get("chk_promtotxest"))
    
    prommayorq = request.args.get("prommayorq", "")
    chk_prommayorq = bool(request.args.get("chk_prommayorq"))
    prommenorq = request.args.get("prommenorq", "")
    chk_prommenorq = bool(request.args.get("chk_prommenorq"))

    
    chk_cualperiodotot = bool(request.args.get("chk_cualperiodotot"))
    promtotxpermayorq = request.args.get("promtotxpermayorq", "")
    chk_promtotxpermayorq = bool(request.args.get("chk_promtotxpermayorq"))
    promtotxpermenor = request.args.get("promtotxpermenor", "")
    chk_promtotxpermenor = bool(request.args.get("chk_promtotxpermenor"))
    

    cualperiodoasig = request.args.get("cualperiodoasig", "") ## trae el periodo
    if cualperiodoasig == "PER1":
        nota_periodo = "calimate.nota1"
    elif cualperiodoasig == "PER2":
        nota_periodo = "calimate.nota2"
    elif cualperiodoasig == "PER3":
        nota_periodo = "calimate.nota3"
    else:
        nota_periodo = "calimate.nota1"
    chk_cualperiodoasig = bool(request.args.get("chk_cualperiodoasig"))
    promxperasigmayorq = request.args.get("promxperasigmayorq", "") ##nota mayor que
    if promxperasigmayorq:
        promxperasigmayorqF = float(promxperasigmayorq)

    chk_promxperasigmayorq = bool(request.args.get("chk_promxperasigmayorq"))
    promxperasigmenor = request.args.get("promxperasigmenor", "") ##nota menor que
    if promxperasigmenor:
        promxperasigmenorF = float(promxperasigmenor)
    chk_promxperasigmenor = bool(request.args.get("chk_promxperasigmenor"))
    cualasignaxgrado = request.args.get("cualasignaxgrado", "") #code keymate
    chk_cualasignaxgrado = bool(request.args.get("chk_cualasignaxgrado"))
    
    cualperiodoarea = request.args.get("cualperiodoarea", "") ## trae el area
    if cualperiodoarea == "PER1":
        nota_periodoar = "(caliarea.per1)/1"
    elif cualperiodoarea == "PER2":
        nota_periodoar = "(caliarea.per1 + caliarea.per2 )/2 " 
    elif cualperiodoarea == "PER3":
        nota_periodoar = "(caliarea.per1 + caliarea.per2 + caliarea.per3)/3"
    else:
        nota_periodoar = "(caliarea.per1)/1"
    
    chk_cualperiodoarea = bool(request.args.get("chk_cualperiodoarea"))
    promxperareamayorq = request.args.get("promxperareamayorq", "") ##nota mayor que
    chk_promxperareamayorq = bool(request.args.get("chk_promxperareamayorq"))
    promxperareamenor = request.args.get("promxperareamenor", "") ##nota menor que
    chk_promxperareamenor = bool(request.args.get("chk_promxperareamenor"))
    cualareanaxgrado = request.args.get("cualareanaxgrado", "")
    chk_cualareanaxgrado = bool(request.args.get("chk_cualareanaxgrado"))
    
    chk_cualAHR = bool(request.args.get("chk_cualAHR"))
    chk_aprobo = bool(request.args.get("chk_aprobo"))
    chk_reprobo = bool(request.args.get("chk_reprobo"))
    chk_otrocaso = bool(request.args.get("chk_otrocaso"))
    
    
    print("cualnivelgrado:", cualnivelgrado)
    

    cursor.execute("""
        SELECT rangoini, notatt, nivelesco, codeobse
        FROM observa
        WHERE TRIM(scodeemp) = %s
        AND nivelesco = %s
        AND CHAR_LENGTH(notatt) > 1
        ORDER BY rangoini DESC
    """, (SCODEEMP, nivelesco))

    observa_rango_sel = cursor.fetchall()


    having5 = "" 
    grupo5 = ""

    if codegrad1:
        cursor.execute("""
               SELECT codegrad, name
                FROM colgrados
                WHERE codegrad = %s
            """, (codegrad1,))
        grado_sel = cursor.fetchone()

    cursor.execute("""
        SELECT materia.* 
            FROM materia 
            where trim(materia.scodeemp) = %s AND codegrad = %s AND keymate = %s
    """, (scodeemp1,codegrad1, cualasignaxgrado))
    asignaxgrado_sel = cursor.fetchone()


    cursor.execute("""
        SELECT * 
        FROM colgrados 
        WHERE TRIM(scodeemp) = %s
        group by nivelgrado
                   ;
    """, (scodeemp1,))
    nivelgradoact = cursor.fetchall()

    cursor.execute("""
        SELECT * 
        FROM colgrados 
        WHERE TRIM(scodeemp) = %s and nivelgrado = %s
        group by nivelgrado
                   ;
    """, (scodeemp1, cualnivelgrado))
    nivelgradoact_sel = cursor.fetchone()

    cursor.execute("""
        SELECT * 
        FROM estudents 
        WHERE TRIM(scodeemp) = %s and lastn = "zzzzzz"
    """, (scodeemp1,))
    estudents = cursor.fetchall()
    total_found = len(estudents)

    print("codegrad:", codegrad1)
    print("cualasignaxgrado creo keymate:", cualasignaxgrado)
    cualasignaxgrado
    check5=None
    
    #if chk_promxgrado: ## es el nivel 17
    #    query = """
    #    SELECT 
    #        estudents.*,UCASE(estudents.lastn) as lastn1, 
    #        CONCAT(lastn, ' ', lastn2, ', ', names  ) as nombre,
    #        colgrados.name, colgrados.codeinte, 
    #        DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
    #        TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2,
    #        ((SUM(caliarea.notafinal)/'" & totareas1 & "')/(COUNT(estudents.codegrad)))* 10 as promfinal,
    #        '' as matnombre  
    #        FROM estudents,colgrados,caliarea 
    #        where estudents.codegrad = colgrados.codegrad 
    #        AND estudents.scodeest = caliarea.codeestu 
    #        AND trim(estudents.scodeemp) = %s 
    #        
    #    """
    #    params = [SCODEEMP]
    #print("ANTES de rutina de grado:", codegrad1)
    if chk_pornivelogrado == "grado": ## si se pica el grado  codegrad1: ##
            #print("entrnado a rutina de grado:", codegrad1)
            query = """
                SELECT 
                    estudents.*,
                    UCASE(estudents.lastn) AS lastn1,
                    CONCAT(lastn, ' ', lastn2, ', ', names) AS nombre,
                    colgrados.name,
                    colgrados.codeinte,
                    TIMESTAMPDIFF(YEAR, STR_TO_DATE(fechnac, '%m/%d/%Y'), CURDATE()) AS edad2,
                    '' AS promfinal,
                    '' AS matnombre
                FROM estudents
                INNER JOIN colgrados 
                    ON estudents.codegrad = colgrados.codegrad
                WHERE TRIM(estudents.scodeemp) = %s
            """

            params = [SCODEEMP]

            # filtro equivalente a filter()
            #if codegrad1:
            #    query += " AND TRIM(colgrados.codegrad) = %s"
            #    params.append(codegrad1)

            if chk_pornivelogrado == 'grado':
                query += " AND TRIM(colgrados.codegrad) = %s"
                params.append(codegrad1)

            if chk_gen:
                query += " AND TRIM(estudents.genero) = %s"
                params.append(cualgen)

            if chk_emayorq:
                query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
                params.append(edadmayorq)
                
            if chk_emenorq:
                query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
                params.append(edadmenorq)

            #if chk_nivelxgrado:
            #    query += " AND TRIM(colgrados.nivelgrado) = %s"
            #    params.append(cualnivelgrado)


            query += """
                ORDER BY estudents.lastn,
                        estudents.lastn2,
                        estudents.names
            """

            cursor.execute(query, params)
            estudents = cursor.fetchall()
            total_found = len(estudents)

    if chk_pornivelogrado == "nivelgrado": ##aqui iria el nivel

            query = """
                SELECT 
                    estudents.*,
                    UCASE(estudents.lastn) as lastn1, 
                    CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
                    colgrados.name, colgrados.codeinte, colgrados.nivelgrado,
                    DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
                    TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
                    '' as promfinal,'' as matnombre 
                    FROM estudents
                    INNER JOIN colgrados 
                    ON CAST(estudents.codegrad AS UNSIGNED) = colgrados.codegrad
                    WHERE TRIM(estudents.scodeemp) = %s 
                    
                """
            params = [SCODEEMP]
                        # filtro equivalente a filter()

            if chk_gen:
                query += " AND TRIM(estudents.genero) = %s"
                params.append(cualgen)

            if chk_emayorq:
                query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
                params.append(edadmayorq)
                
            if chk_emenorq:
                query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
                params.append(edadmenorq)

            if chk_pornivelogrado == 'nivelgrado':
                query += " AND TRIM(colgrados.nivelgrado) = %s"
                params.append(cualnivelgrado)

            query += """
                ORDER BY estudents.lastn,
                        estudents.lastn2,
                        estudents.names
            """
            cursor.execute(query, params)
            estudents = cursor.fetchall()
            total_found = len(estudents)
    
    if chk_min3erper:
        # para calcular la nota mínima que debe obtener el estudiante en el tercer período para alcanzar una nota final de 3.0
        # (3 - promedio_actual) / porcentaje_periodo3
        # linea original: SUM(3-((calimate.nota1*.40)+(calimate.nota2*.30)))/.30 as promfinal, 
        P1 = current_app.config["PORC_PER1"]
        P2 = current_app.config["PORC_PER2"]
        P3 = current_app.config["PORC_PER3"]
        P4 = current_app.config["PORC_PER4"]
        P5 = current_app.config["PORC_PER5"]

        query = """
            SELECT 
            estudents.*,
            UCASE(estudents.lastn) as lastn1, CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
            colgrados.name, colgrados.codeinte, 
            DATEDIFF(NOW( ) ,
            STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
            TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
            SUM(%s-((calimate.nota1*%s)+(calimate.nota2*%s)))/%s as promfinal, 
            materia.nombre as matnombre,
            calimate.codecalm 
            FROM estudents,colgrados,calimate,materia,areasxmate 
            where estudents.codegrad = colgrados.codegrad 
            and estudents.scodeest = calimate.codeestu 
            AND calimate.codemate = materia.codemate 
            and materia.codearea = areasxmate.codearea  
            and trim(estudents.scodeemp) = %s 
        """
        ##+ filter() + grupo4 + having4
        params = [cualrango,P1,P2,P3,SCODEEMP]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        ##AQUI SI SE ESCOGE UN ESTUDIANTE
        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)            

        query += """
            group by calimate.codecalm
        """
        query += having4
        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)

    ##aqui opcion PROM TOTAL X estudiante done 
    if chk_promtotxest:
        #solo para la prueba se cambio el totareas1 = 2
        query = """
        SELECT 
            estudents.*,
            UCASE(estudents.lastn) as lastn1, CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
            colgrados.name, colgrados.codeinte, 
            DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
            TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
            ROUND(((SUM(caliarea.notafinal)/%s)/1),2) as promfinal,
            '' AS matnombre 
            FROM estudents
            JOIN colgrados ON estudents.codegrad = colgrados.codegrad
            JOIN caliarea ON estudents.scodeest = caliarea.codeestu
            WHERE TRIM(estudents.scodeemp) = %s 

        """
        params = [totareas1,scodeemp1]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)

        if chk_prommayorq and chk_prommenorq:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) >= %s) AND (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) <= %s) "
            params.append(totareas1)
            params.append(float(prommayorq))
            params.append(totareas1)
            params.append(float(prommenorq))

        if chk_prommayorq and not chk_prommenorq:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) >= %s) "
            params.append(totareas1)
            params.append(float(prommayorq))

        if not chk_prommayorq and chk_prommenorq:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING  (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) <= %s) "
            params.append(totareas1)
            params.append(float(prommenorq))

        if not chk_prommayorq and not chk_prommenorq:
            pass

        ###AQUIIIIIIIIIIIIIIIIIIIIII

        #query += """
        #GROUP BY estudents.scodeest
        #HAVING (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) >= %s) AND (ROUND(((SUM(caliarea.notafinal)/%s)/1),2) <= %s)
        #"""
        #params.append(totareas1)
        #params.append(float(prommayorq))
        

        query += " ORDER BY promfinal, colgrados.name DESC "
        
        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)


    ##aqui opcion PROM TOTAL X PERIODO done
    if chk_cualperiodotot:
        query = f"""
            SELECT estudents.*,
            UCASE(estudents.lastn) as lastn1, 
            CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
            colgrados.name, colgrados.codeinte, 
            DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
            TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
            ROUND(((SUM({campo_periodo})/%s)/1),2) as promfinal,
            '' as matnombre  
            FROM estudents,colgrados,caliarea 
            where estudents.codegrad = colgrados.codegrad 
            AND estudents.scodeest = caliarea.codeestu 
            AND trim(estudents.scodeemp) = %s 
        """
        params = [totareas1, SCODEEMP]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        #if codegrad1:
        #    query += " AND TRIM(colgrados.codegrad) = %s"
        #    params.append(codegrad1)

        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                    
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)

        # desde aqui cambios chk_cualperiodotot

        if chk_promtotxpermayorq and chk_promtotxpermenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal >= %s AND promfinal <= %s) "
            params.append(promtotxpermayorq)
            params.append(promtotxpermenor)
        
        if chk_promtotxpermayorq and not chk_promtotxpermenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal >= %s ) "
            params.append(promtotxpermayorq)

        if not chk_promtotxpermayorq and chk_promtotxpermenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal <= %s) "
            params.append(promtotxpermayorq)

        if not chk_promtotxpermayorq and not chk_promtotxpermenor:
            query += " GROUP BY estudents.scodeest "


        query += " order by promfinal desc"

        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)


    ##aqui opcion PROM X PERIODO x AREA
    if chk_cualperiodoarea:
        ##temporal
        query = f"""
        SELECT estudents.*,
        UCASE(estudents.lastn) as lastn1, 
        CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
        colgrados.name, colgrados.codeinte, 
        DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
        TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
        ROUND(SUM({nota_periodoar}),1) as promfinal,
        areasxmate.nombre as matnombre  
        FROM estudents
            INNER JOIN colgrados
            ON estudents.codegrad = colgrados.codegrad
            INNER JOIN caliarea
            ON estudents.scodeest = caliarea.codeestu
            INNER JOIN areasxmate
            ON caliarea.codearea = areasxmate.codearea
        WHERE trim(estudents.scodeemp) = %s

        """
        params = [ SCODEEMP]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                    
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)


        if chk_cualareanaxgrado:
            query += " and areasxmate.codearea = %s "
            params.append(cualareanaxgrado)

        if chk_promxperareamayorq and chk_promxperareamenor:
            query += " GROUP BY caliarea.codeestu,caliarea.codearea "
            query += " HAVING (promfinal >= %s AND promfinal <= %s) "
            params.append(promxperareamayorq)
            params.append(promxperareamenor)

        
        if chk_promxperareamayorq and not chk_promxperareamenor:
            query += " GROUP BY caliarea.codeestu,caliarea.codearea "
            query += " HAVING (promfinal >= %s ) "
            params.append(promxperareamayorq)

        if not chk_promxperareamayorq and chk_promxperareamenor:
            query += " GROUP BY caliarea.codeestu,caliarea.codearea "
            query += " HAVING (promfinal <= %s) "
            params.append(promxperareamenor)

        if not chk_promxperareamayorq and not chk_promxperareamenor:
            query += " GROUP BY caliarea.codeestu,caliarea.codearea "

        query += " order by promfinal desc"

        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)


    ##aqui opcion PROM X PERIODO x asignatura
    if chk_cualperiodoasig: 

        query = f"""
        SELECT estudents.*,
        UCASE(estudents.lastn) as lastn1, 
        CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
        colgrados.name, colgrados.codeinte, 
        DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
        TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
        ({nota_periodo}) as promfinal, 
        materia.nombre as matnombre, materia.keymate
        FROM estudents
            INNER JOIN colgrados
                ON estudents.codegrad = colgrados.codegrad
            INNER JOIN calimate 
                ON estudents.scodeest = calimate.codeestu
            INNER JOIN materia
                ON calimate.codemate = materia.codemate
            INNER JOIN areasxmate 
                ON materia.codearea = areasxmate.codearea
            WHERE TRIM(estudents.scodeemp) = %s

        """

        #FALTA esta linea:  nivelmate2 = " and materia.keymate = '" + nivelmatePP + "' "
        #nota falta revisar la variable nivelmate1 justo despues de and materia.codearea = areasxmate.codearea  
        params = [ SCODEEMP]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                    
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        #if chk_nivelxgrado:
        #    query += " AND TRIM(colgrados.nivelgrado) = %s"
        #    params.append(cualnivelgrado) 


        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)

        ##aqui el if de asignatura
        if chk_cualasignaxgrado:
            query += " and materia.keymate = %s "
            params.append(cualasignaxgrado)

        if chk_promxperasigmayorq and chk_promxperasigmenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal >= %s AND promfinal <= %s) "
            params.append(promxperasigmayorqF)
            params.append(promxperasigmenorF)
            #print("entre", promxperasigmayorqF, promxperasigmenorF )
        
        if chk_promxperasigmayorq and not chk_promxperasigmenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal >= %s ) "
            params.append(promxperasigmayorqF)

        if not chk_promxperasigmayorq and chk_promxperasigmenor:
            query += " GROUP BY estudents.scodeest "
            query += " HAVING (promfinal <= %s) "
            params.append(promxperasigmenorF)

        if not chk_promxperasigmayorq and not chk_promxperasigmenor:
            query += " GROUP BY estudents.scodeest "


        query += " order by promfinal desc"

        #print("aqui entre")
        #print(f'keymate: {cualasignaxgrado}')

        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)
    
    if chk_cualAHR:

        query = f"""
            SELECT estudents.*,
            UCASE(estudents.lastn) as lastn1, 
            CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre,
            colgrados.name, colgrados.codeinte, 
            DATEDIFF(NOW( ) ,STR_TO_DATE(fechnac, '%m/%d/%Y') )/365 as edad, 
            TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE()) AS edad2, 
            '' as promfinal,
            '' as matnombre 
            FROM estudents,colgrados 
            where estudents.codegrad = colgrados.codegrad  
            AND trim(estudents.scodeemp) = %s  
            

        """
        params = [ SCODEEMP]

        if chk_pornivelogrado == 'grado':
            query += " AND TRIM(colgrados.codegrad) = %s"
            params.append(codegrad1)

        if chk_gen:
            query += " AND TRIM(estudents.genero) = %s"
            params.append(cualgen)

        if chk_emayorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())>= %s"
            params.append(edadmayorq)
                
        if chk_emenorq:
            query += " AND TIMESTAMPDIFF(YEAR,STR_TO_DATE(fechnac, '%m/%d/%Y'),CURDATE())<= %s"
            params.append(edadmenorq)

        if chk_pornivelogrado == 'nivelgrado':
            query += " AND TRIM(colgrados.nivelgrado) = %s"
            params.append(cualnivelgrado)

        if chk_aprobo and chk_reprobo and chk_otrocaso:
            pass
            #query += " AND ((TRIM(estudents.statusARH) = %s OR TRIM(estudents.statusARH) = %s ) OR ( TRIM(estudents.statusARH) <> %s AND TRIM(estudents.statusARH) <> %s))"
            #params.append(siaprobo)
            #params.append(reprobo)
            #params.append("APROBÓ EL GRADO")
            #params.append("REPROBÓ EL GRADO")

        elif chk_aprobo and chk_reprobo:
            siaprobo="APROBÓ EL GRADO"
            reprobo="REPROBÓ EL GRADO"
            query += " AND (TRIM(estudents.statusARH) = %s OR TRIM(estudents.statusARH) = %s )"
            params.append(siaprobo)
            params.append(reprobo)

        elif chk_aprobo and not chk_reprobo:
            siaprobo="APROBÓ EL GRADO"
            query += " AND TRIM(estudents.statusARH) = %s"
            params.append(siaprobo)  

        elif  not chk_aprobo and chk_reprobo:
            reprobo="REPROBÓ EL GRADO"
            query += " AND TRIM(estudents.statusARH) = %s"
            params.append(reprobo)

        elif  chk_otrocaso:
            query += " AND TRIM(estudents.statusARH) <> %s AND TRIM(estudents.statusARH) <> %s"
            params.append("APROBÓ EL GRADO")
            params.append("REPROBÓ EL GRADO")
        
        query += " order by estudents.lastn, estudents.lastn2, estudents.names "


        cursor.execute(query, params)
        estudents = cursor.fetchall()
        total_found = len(estudents)

    ##ESTE QUERY CUENTA EL TOTAL DE REGISTROS DEL GRADO O NIVEL
    query = """
        SELECT estudents.* 
        FROM estudents 
        where trim(estudents.scodeemp) = %s 
        AND codegrad = %s 
        and status = 'MATRICUL'
    """
    paramsg = [ scodeemp1,codegrad1]


    cursor.execute(query, paramsg)
    cuentaestu = cursor.fetchall()

    total_registros = len(cuentaestu)

    if total_registros > 0:
        porcentaje = f"{(total_found * 100) / total_registros:.2f}"
    else:
        porcentaje = "0"

    cursor.close()
    conn.close()

    print("chk_pornivelgrado:", chk_pornivelogrado)

    return render_template("" \
    "reporte1.html", 
    estudents=estudents,
    areasxgrado=areasxgrado,
    nivel_radio=nivel_radio,
    chk_pornivel=chk_pornivel,
    chk_gen=chk_gen,
    chk_emayorq=chk_emayorq,
    chk_emenorq=chk_emenorq,
    cualgrado=codegrad1,
    lista_grados_persist=lista_grados_persist,
    chk_TICC=chk_TICC,
    chk_EPS=chk_EPS,
    chk_despla=chk_despla,
    chk_rh=chk_rh,
    chk_padre=chk_padre,
    chk_telpadre=chk_telpadre,
    chk_madre=chk_madre,
    chk_telmadre=chk_telmadre,
    gradomx_sel=grado_sel,
    cualgen=cualgen,
    edadmayorq=edadmayorq,
    edadmenorq=edadmenorq,
    cualnivelgrado=cualnivelgrado,
    chk_nivelxgrado=chk_nivelxgrado,
    nivelgradoact=nivelgradoact,
    nivelgradoact_sel=nivelgradoact_sel,
    nivel_min3p=nivel_min3p,
    chk_min3erper=chk_min3erper,
    chk_promtotxest=chk_promtotxest,
    prommayorq=prommayorq,
    chk_prommayorq=chk_prommayorq,
    prommenorq=prommenorq,
    chk_prommenorq=chk_prommenorq,
    chk_pornivelogrado=chk_pornivelogrado,
    asignaxgrado_sel=asignaxgrado_sel,
    chk_cualperiodoasig=chk_cualperiodoasig,
    cualperiodoasig=cualperiodoasig,
    promxperasigmayorq=promxperasigmayorq,
    chk_promxperasigmayorq=chk_promxperasigmayorq,
    promxperasigmenor=promxperasigmenor,
    chk_promxperasigmenor=chk_promxperasigmenor,
    cualasignaxgrado=cualasignaxgrado,
    chk_cualasignaxgrado=chk_cualasignaxgrado,
    chk_cualperiodotot=chk_cualperiodotot,
    cualperiodotot=cualperiodotot,
    chk_promtotxpermayorq=chk_promtotxpermayorq,
    promtotxpermayorq=promtotxpermayorq,
    chk_promtotxpermenor=chk_promtotxpermenor,
    promtotxpermenor=promtotxpermenor,
    
    cualperiodoarea=cualperiodoarea,
    chk_cualperiodoarea=chk_cualperiodoarea,
    promxperareamayorq=promxperareamayorq,
    chk_promxperareamayorq=chk_promxperareamayorq,
    promxperareamenor=promxperareamenor,
    chk_promxperareamenor=chk_promxperareamenor,
    cualareanaxgrado=cualareanaxgrado,
    chk_cualareanaxgrado=chk_cualareanaxgrado,
    chk_cualAHR=chk_cualAHR,
    cuentaestu=cuentaestu,
    total_registros=total_registros,
    total_found=total_found,
    porcentaje=porcentaje,
    chk_aprobo=chk_aprobo,
    chk_reprobo=chk_reprobo,
    chk_otrocaso=chk_otrocaso,
    periodo=periodo,
    observa_rango_sel=observa_rango_sel
     
           )


@reporte_bp.route('/get_asigna_por_grado/<codegrad>')
def get_asigna_por_grado(codegrad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")


    scodeemp1 = SCODEEMP  # o como lo estés manejando
    
    cursor.execute("""
        SELECT materia.* 
            FROM materia 
            where trim(materia.scodeemp) = %s AND codegrad = %s 

    """, (scodeemp1,codegrad))
    areasxgrado = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(areasxgrado)

@reporte_bp.route('/get_asigna_por_nivelgrado/<nivelgrado>')
def get_asigna_por_nivelgrado(nivelgrado):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    varpnivel = (nivelgrado) + "_1"
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP

    cursor.execute("""
        SELECT materia.*
        FROM materia
        WHERE trim(materia.scodeemp) = %s
        AND name = %s
    """, (scodeemp1, varpnivel))

    areasxgrado = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(areasxgrado)

@reporte_bp.route('/get_area_por_grado/<codegrad>')
def get_area_por_grado(codegrad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    
    cursor.execute("""
        SELECT materia.codearea,areasxmate.nombre as nombrearea, materia.keymate 
            FROM materia,areasxmate 
            where areasxmate.codearea = materia.codearea 
            and trim(materia.scodeemp) = %s 
            AND codegrad = %s 
            group by materia.codearea;
    """, (scodeemp1,codegrad))
    areasrealxgrado = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(areasrealxgrado)

@reporte_bp.route('/get_area_por_nivelgrado/<nivelgrado>')
def get_area_por_nivelgrado(nivelgrado):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    varpnivel = (nivelgrado) + "_1"
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    
    cursor.execute("""
        SELECT materia.codearea,areasxmate.nombre as nombrearea, materia.keymate 
            FROM materia,areasxmate 
            where areasxmate.codearea = materia.codearea 
            and trim(materia.scodeemp) = %s 
            AND materia.name = %s 
            group by materia.codearea;
    """, (scodeemp1,varpnivel))
    areasrealxgrado = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(areasrealxgrado)