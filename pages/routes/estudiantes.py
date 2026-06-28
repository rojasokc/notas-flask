from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date, datetime

from flask import current_app

#SCODEEMP = "31"
#from config import (
#    ALECTIVO_ACTUAL,
#    PERIODO_ACTUAL,
#    SCODEEMP,
#    NIVELESCO
#)



#SCODEEMP = current_app.config.get("SCODEEMP")
#NIVELESCO = current_app.config.get("NIVELESCO")

#from flask import g

#def alguna_funcion():
#ALECTIVO_ACTUAL = g.config["ALECTIVO_ACTUAL"]
#PERIODO_ACTUAL = g.config["PERIODO_ACTUAL"]
#SCODEEMP = "31"
#NIVELESCO = "BACHIL"


estudiantes_bp = Blueprint(
    'estudiantes',
    __name__,
    url_prefix='/estudiantes'
)

@estudiantes_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM estudents")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("onlycreaalumnx.html") ##, estudents=data)

#@app.route('/onlycreaalumnx')
#def onlycreaalumnx():
#    return render_template('onlycreaalumnx.html')

@estudiantes_bp.route('/save_estudiante', methods=['POST'])
def save_estudiante():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Datos del formulario
    fechmatri1 = date.today().strftime("%m/%d/%Y")

    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")


    alectivo1 = ALECTIVO_ACTUAL
    codeint1  = "NN" #request.form.get("codeint", "").strip()
    scodeemp1 = SCODEEMP

    names1       = request.form.get('nombre',"").upper()
    lastn1    = request.form.get('apellido',"").upper()
    lastn21      = request.form.get('secapel',"").upper()
    #tel         = request.form.get('telf')

    # ===== RADIO BUTTONS genero=====
    genmf = request.form.get("genmf")
    genero1 = None
    if genmf == "1":
        genero1 = "M"
    elif genmf == "2":
        genero1 = "F"


    rhtipo1 = request.form.get("opcionsrh", "").strip()

    # ===== RADIO BUTTONS desplazado=====
    dezpl = request.form.get("dezpl")
    desplaza1 = None
    if dezpl == "1":
        desplaza1 = "SI"
    elif dezpl == "2":
        desplaza1 = "NO"


    email11     = request.form.get('email')
    IDTIcc1  = request.form.get('tidcc')
    eps1      = request.form.get('eps').upper()
    telf1   = request.form.get('telcel')
    #fechnac1  = request.form.get("fechnac", "").strip()

    fechnac_raw = request.form.get("fechnac", "").strip()

    fechnac1 = None
    if fechnac_raw:
        fechnac1 = datetime.strptime(fechnac_raw, "%Y-%m-%d").strftime("%m/%d/%Y")

    grade1   = request.form.get('gradoact')


    direc1   = request.form.get('dircc')
    city1   = request.form.get('ciudad')
    state1   = request.form.get('dpto')

    padre1   = request.form.get('padre').upper()
    #acudpa1   = request.form.get('acudpa')
    acudpa1 = "SI" if request.form.get('acudpa') else "NO"
    telpadr1   = request.form.get('celphp')

    madre1   = request.form.get('madre').upper()
    #acudma1   = request.form.get('acudma')
    acudma1 = "SI" if request.form.get('acudma') else "NO"
    telmadr1   = request.form.get('celphm')

    login1   = request.form.get('tidcc') ## request.form.get('nlogin') ## poner tidcc
    password1   = request.form.get('tidcc') ## request.form.get('npass') ##usar tidcc

    fotof1   = "NA"
    statusNY1 = "OPEN"
    gradeny1 = ""
    codegrad1 = request.form.get('campo2_hidden') 

        # ===== RADIO BUTTONS inscrito matriculado=====
    insmatri = request.form.get("insmatri")

    status1 = "MATRICUL"
    if insmatri == "1":
        #dezplsn = "SI"
        statusNY1 = "INSC-NY"
        gradeny1 = codegrad1 #gradeny y codegrad son lo mismo
        status1 = "NUEVO"
    elif insmatri == "2":
        #dezplsn = "NO"
        statusNY1 = "MATR-NY"
        gradeny1 = codegrad1
        status1 = "MATRICUL"
    else:
        dezplsn = None

    campos_obligatorios = {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "secapel": "Segundo apellido",
        "genmf": "Género",
        "opcionsrh": "Tipo RH",
        "dezpl": "Desplazado",
        "email": "Email",
        "tidcc": "TID/CC",
        "eps": "EPS",
        "telcel": "Teléfono",
        "fechnac": "Fecha de nacimiento",
        "gradoact": "Grado",
        "dircc": "Dirección",
        "ciudad": "Ciudad",
        "dpto": "Departamento",
        "padre": "Padre",
        "madre": "Madre",
        "insmatri": "Estado inscripción"
    }
    
    errores = []

    for campo, nombre in campos_obligatorios.items():
        valor = request.form.get(campo)
        if not valor or not valor.strip():
            errores.append(nombre)

    if errores:
        flash(
            "Faltan campos obligatorios: " + ", ".join(errores),
            "danger"
        )
        return redirect(url_for('estudiantes.index'))

    sql = """
        INSERT INTO estudents (
            cupoNY, fotof, gradeny, statusNY, fechmatri, alectivo, status,
            lastn2, codeint, padre, telpadr, madre, telmadr,
            names, lastn, telf, email1, codegrad, direc, city, state,
            login, password, scodeemp, fechnac, genero, rhtipo,
            acudpa, acudma, idticc, eps, desplaza, grade
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s, %s
        )
    """
    values = (
        "YES", fotof1, gradeny1, statusNY1, fechmatri1, alectivo1, status1,
        lastn21, codeint1, padre1, telpadr1, madre1, telmadr1,
        names1, lastn1, telf1, email11, codegrad1, direc1, city1, state1,
        login1, password1, scodeemp1, fechnac1, genero1, rhtipo1,
        acudpa1, acudma1, IDTIcc1, eps1, desplaza1, grade1
    )    


    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    return render_template("onlycreaalumnx.html")

@estudiantes_bp.route('/onlybuscaestu', methods=['GET', 'POST'])
def onlybuscaestu():
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchestu = request.args.get("searchestu", "").strip()
    scodeest1 = request.args.get('scodeest')

    #lastname1 = request.args.get('lastname', '')
    if searchestu:
        cursor.execute("""
            SELECT *, concat(lastn, ' ' , lastn2, ' ' , names) as namesestu
            FROM estudents
            WHERE concat(lastn, ' ' , lastn2, ' ' , names) LIKE %s 
            ORDER BY lastn, lastn2, names
        """, (f"{searchestu}%",
              #f"{searchestu}%",
              #f"{searchestu}%",
              ))   # ← empieza por la letra or lastn2 LIKE %s or names LIKE %s
    else:
        cursor.execute("""
            SELECT *
            FROM estudents
            where lastn = "zzzzz"
            ORDER BY lastn, lastn2, names
        """)


    estudentsfound = cursor.fetchall()

    # REGISTRO SELECCIONADO
    estu_sel = None
    if scodeest1:
        cursor.execute("""
            SELECT * FROM estudents
            WHERE scodeest = %s
        """, (scodeest1,))
        estu_sel = cursor.fetchone()

    if estu_sel and estu_sel['fechnac']:
        try:
            estu_sel['fechnac'] = datetime.strptime(
                estu_sel['fechnac'], "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
        except ValueError:
            estu_sel['fechnac'] = ""

    cursor.close()
    conn.close()

    return render_template("onlycreaalumnx.html", searchestu = searchestu, estudentsfound = estudentsfound, estu_sel = estu_sel)

@estudiantes_bp.route('/update_estudiante/<scodeest>', methods=['POST'])
def update_estudiante(scodeest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

        # Datos del formulario
    fechmatri1 = date.today().strftime("%m/%d/%Y")
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    alectivo1 = ALECTIVO_ACTUAL
    codeint1  = "NN" #request.form.get("codeint", "").strip()
    scodeemp1 = SCODEEMP

    
    names1       = request.form.get('nombre',"").upper()
    lastn1    = request.form.get('apellido',"").upper()
    lastn21      = request.form.get('secapel',"").upper()
    

    # ===== RADIO BUTTONS genero=====
    genmf = request.form.get("genmf")
    genero1 = None
    if genmf == "1":
        genero1 = "M"
    elif genmf == "2":
        genero1 = "F"


    rhtipo1 = request.form.get("opcionsrh", "").strip()

    # ===== RADIO BUTTONS desplazado=====
    dezpl = request.form.get("dezpl")
    desplaza1 = None
    if dezpl == "1":
        desplaza1 = "SI"
    elif dezpl == "2":
        desplaza1 = "NO"


    email11     = request.form.get('email')
    IDTIcc1  = request.form.get('tidcc')
    eps1      = request.form.get('eps').upper()
    telf1   = request.form.get('telcel')
    #fechnac1  = request.form.get("fechnac", "").strip()

    fechnac_raw = request.form.get("fechnac", "").strip()

    fechnac1 = None
    if fechnac_raw:
        fechnac1 = datetime.strptime(fechnac_raw, "%Y-%m-%d").strftime("%m/%d/%Y")

    grade1   = request.form.get('gradoact')


    direc1   = request.form.get('dircc')
    city1   = request.form.get('ciudad')
    state1   = request.form.get('dpto')

    padre1   = request.form.get('padre').upper()
    acudpa1 = "SI" if request.form.get('acudpa') else "NO"
    telpadr1   = request.form.get('celphp')

    madre1   = request.form.get('madre').upper()
    acudma1 = "SI" if request.form.get('acudma') else "NO"
    telmadr1   = request.form.get('celphm')

    login1   = request.form.get('tidcc') ## request.form.get('nlogin') ## poner tidcc
    password1   = request.form.get('tidcc') ## request.form.get('npass') ##usar tidcc

    fotof1   = "NA"
    statusNY1 = "OPEN"
    gradeny1 = ""
    codegrad1 = request.form.get('campo2_hidden') 

        # ===== RADIO BUTTONS inscrito matriculado=====
    insmatri = request.form.get("insmatri")

    status1 = "MATRICUL"
    if insmatri == "1":
        #dezplsn = "SI"
        statusNY1 = "INSC-NY"
        gradeny1 = codegrad1 #gradeny y codegrad son lo mismo
        status1 = "NUEVO"
    elif insmatri == "2":
        #dezplsn = "NO"
        statusNY1 = "MATR-NY"
        gradeny1 = codegrad1
        status1 = "MATRICUL"
    else:
        dezplsn = None


    try:
        cursor.execute("""
            UPDATE estudents
            SET                        
                cupoNY=%s, 
                fotof=%s, 
                gradeny=%s, 
                statusNY=%s, 
                fechmatri=%s, 
                alectivo=%s, 
                status=%s,
                lastn2=%s, 
                codeint=%s, 
                padre=%s, 
                telpadr=%s, 
                madre=%s, 
                telmadr=%s,
                names=%s, 
                lastn=%s, 
                telf=%s, 
                email1=%s, 
                codegrad=%s, 
                direc=%s, 
                city=%s, 
                state=%s,
                login=%s, 
                password=%s, 
                scodeemp=%s, 
                fechnac=%s, 
                genero=%s, 
                rhtipo=%s,
                acudpa=%s, 
                acudma=%s, 
                idticc=%s, 
                eps=%s, 
                desplaza=%s, 
                grade=%s
                       

            WHERE scodeest=%s
        """, (
            
            "YES", fotof1, gradeny1, statusNY1, fechmatri1, alectivo1, status1,
            lastn21, codeint1, padre1, telpadr1, madre1, telmadr1,
            names1, lastn1, telf1, email11, codegrad1, direc1, city1, state1,
            login1, password1, scodeemp1, fechnac1, genero1, rhtipo1,
            acudpa1, acudma1, IDTIcc1, eps1, desplaza1, grade1, scodeest

        ))
        conn.commit()
        flash("Estudiante actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar estudiante: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('estudiantes.index', scodeest=scodeest))

def obtener_estudiantes_por_grado(codegrad):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    print(f'aqui estoy por la grid')

    cursor.execute("""
        SELECT estudents.*, 
            CONCAT(lastn, ' ', lastn2, ', ', names ) as totname,
            CONCAT(lastn, ' ', lastn2, ', ', names ) as nombre  
        FROM estudents 
        WHERE codegrad = %s
        AND trim(scodeemp) = %s
        AND status = 'MATRICUL'
        AND estudents.alectivo = %s
        ORDER BY totname
    """, (codegrad, SCODEEMP, ALECTIVO_ACTUAL))

    estudiantesxgrado = cursor.fetchall()

    cursor.close()
    conn.close()

    return estudiantesxgrado

@estudiantes_bp.route('/callestudiante/<codegrad>', methods=['GET', 'POST'])
def callestudiante(codegrad):

    estudiantesxgrado = obtener_estudiantes_por_grado(codegrad)
    
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    #ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    #SCODEEMP = current_app.config.get("SCODEEMP")

    #scodeemp1 = SCODEEMP  # o como lo estés manejando
    #alectivo = ALECTIVO_ACTUAL

    #cualgrado  = request.form.get('cualgrado')
    #chk_cualgrado = bool(request.args.get("chk_cualgrado"))
    

    #cursor.execute("""
                   
    #    SELECT estudents.*, 
    #        CONCAT(lastn, ' ', lastn2, ', ', names ) as totname 
    #        FROM estudents 
    #3        where codegrad =%s 
    #        and trim(scodeemp) = %s 
    #        and status = 'MATRICUL' 
    #        and estudents.alectivo = %s 
    #        order by totname
    #""", (codegrad, scodeemp1,alectivo))
    #estudiantesxgrado = cursor.fetchall()

    #cursor.close()
    #conn.close()
    return jsonify(estudiantesxgrado)

    

@estudiantes_bp.route('/notasxestudiante/', methods=['GET'])
def notasxestudiante():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    periodo = PERIODO_ACTUAL

    codeestu = request.args.get("cualestudiante")
    codegrad = request.args.get('cualgrado')
    chk_cualgrado = bool(request.args.get("chk_cualgrado"))
    chk_cualestudiante = bool(request.args.get("chk_cualestudiante"))
    
    print(f'periodo: ', periodo)
    print(f'codeestu: ', codeestu)
    print(f'codegrad: ', codegrad)
    
    cursor.execute("""
                   
        SELECT left(metsncomp.metaapr,50) as metaapr,
            left(metsncomp.comptlab,50) as comptlab,
            left(calimate.rempe4,50) as rempe4, 
            metsncomp.periodo, materia.nombre, materia.keymate, calimate.* 
            FROM materia
                JOIN calimate 
                ON materia.codemate = calimate.codemate        
                JOIN metsncomp
                ON metsncomp.codemate = calimate.codemate
            WHERE calimate.codegrad = %s 
            and codeestu = %s 
            and trim(materia.scodeemp) = %s 
            and UCASE(metsncomp.periodo) = %s

            order by materia.keymate
                   
    """, (codegrad, codeestu, scodeemp1, periodo))
    notasxestudiantesxgrado = cursor.fetchall()

        #    from calimate,materia,metsncomp 
        #    where materia.codemate = calimate.codemate 
        #    and metsncomp.codemate = calimate.codemate 
        #    and calimate.codegrad = %s 
        #    and codeestu = %s 
        #    and trim(materia.scodeemp) = %s 
        #    and UCASE(metsncomp.periodo) = %s
    
    cursor.close()
    conn.close()
    #return render_template(
    #"estudiantes/onlynotasestudiantespp.html",
    #notasxestudiantesxgrado=notasxestudiantesxgrado
    #)
    #return jsonify(notasxestudiantesxgrado)
    return render_template("onlynotasestudiantepp.html", notasxestudiantesxgrado = notasxestudiantesxgrado)

@estudiantes_bp.route('/ajax_notas_estudiante')
def ajax_notas_estudiante():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    cualperiodoonxe = request.args.get("codeperiodo")
    
    scodeemp1 = SCODEEMP
    periodo = cualperiodoonxe#PERIODO_ACTUAL

    chk_verhabilita = bool(request.args.get("chk_verhabilita"))

    cualestudiante = request.args.get("cualestudiante")
    
    codeestu = request.args.get("codeestu")
    codegrad = request.args.get("codegrad")

    print(f'codeestu: ', codeestu)
    print(f'codegrad: ', codegrad)
    print(f'periodo: ', periodo)

    cursor.execute("""
		SELECT
            LEFT(metsncomp.metaapr,50) as metaapr,
            LEFT(metsncomp.comptlab,50) as comptlab,
            LEFT(calimate.rempe4,50) as rempe4,
            metsncomp.periodo,
            materia.nombre,
            materia.keymate,
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
    """, (codegrad, codeestu, scodeemp1, periodo))

    notasyasignaturasact = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "estudiantes/_filas_notas.html",
        notasyasignaturasact=notasyasignaturasact,
        periodo=periodo,
        cualestudiante=cualestudiante,
        chk_verhabilita=chk_verhabilita
        
    )

#esta es la info del nuevo grado
@estudiantes_bp.route('/asignatxgradonew/<codegrad>')
def asignatxgradonew(codegrad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    periodo = PERIODO_ACTUAL


    cursor.execute("""
        SELECT materia.* 
            from materia 
            where materia.codegrad = %s
            and trim(materia.scodeemp) = %s
        """, (codegrad, scodeemp1))
    asignaturasnuevas = cursor.fetchall()
                   
    return render_template("estudiantes/_asignaturasgrado.html", asignaturasnuevas=asignaturasnuevas)

    #aqui estoy leyendo la grid nueva

@estudiantes_bp.route('/compara')
def compara():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP
    periodo = PERIODO_ACTUAL

    codeestu = request.args.get("codeestu")
    codegrad = request.args.get("codegrad")
    codegradnew = request.args.get("codegradnew") # esto esta bien, viene de script
    

    print(f"codeestu envia: {codeestu}")
    print("codegrad envia: ", codegrad)
    print("codegrad nuevo: ", codegradnew)

    # ===============================
    # 1️⃣ asignaturas actuales
    # ===============================

    cursor.execute("""
        SELECT 
            materia.codemate,
            materia.nombre,
            calimate.*
        FROM materia
        JOIN calimate 
            ON materia.codemate = calimate.codemate        
        WHERE calimate.codegrad = %s
        AND calimate.codeestu = %s
        AND TRIM(materia.scodeemp) = %s
        ORDER BY materia.keymate
    """, (codegrad, codeestu, scodeemp1))

    notasyasignaturasact = cursor.fetchall()

    # ===============================
    # 2️⃣ asignaturas grado nuevo
    # ===============================

    cursor.execute("""
        SELECT *
        FROM materia
        WHERE codegrad = %s
        AND TRIM(scodeemp) = %s
    """, (codegradnew, scodeemp1))

    notasyasignaturasnuevas = cursor.fetchall()

    #aqui saco el nombre del grado
    cursor.execute("SELECT name FROM colgrados WHERE codegrad = %s", (codegradnew,))
    grado = cursor.fetchone()
    nombre_gradonew = grado["name"] if grado else None

    # ===============================
    # 3️⃣ recorrer diccionario actual
    # ===============================

    print("ASIGNATURAS ACTUALES")

    for r in notasyasignaturasact:

        codemate = r["codemate"]
        nombre = r["nombre"]

        print(codemate, nombre)

    # ===============================
    # 4️⃣ recorrer diccionario nuevo
    # ===============================

    print("ASIGNATURAS NUEVAS")

    for n in notasyasignaturasnuevas:

        codemate = n["codemate"]
        nombre = n["nombre"]

        print(codemate, nombre)

    #aqui 
    for r in notasyasignaturasact:
        codemateact = r["codemate"]
        nombreact = r["nombre"]

        for n in notasyasignaturasnuevas:
            codematenew = n["codemate"]
            nombrenew = n["nombre"]

            if nombreact == nombrenew:
                print(f'cambio grado actu: {codegrad} por grado: {codegradnew} asigna: {nombreact} code: {codemateact} por: {codematenew}' )

                cursor.execute("""
                UPDATE calinotas 
                SET codemate =%s, 
                    codegrad =%s 
                    where codeestu = %s 
                    and codegrad = %s 
                    and codemate = %s
                """, ( codematenew,codegradnew, codeestu, codegrad, codemateact))
                conn.commit()
                #flash("Estudiante movido a otro grado.", "success")

                cursor.execute("""
                UPDATE calimate 
                SET codemate =%s, 
                    codegrad =%s 
                    where codeestu = %s 
                    and codegrad = %s 
                    and codemate = %s
                """, ( codematenew,codegradnew, codeestu, codegrad, codemateact))
                conn.commit()
        
                cursor.execute("""
                UPDATE caliarea 
                SET codegrad =%s 
                    where codeestu = %s 
                    and codegrad = %s
                """, ( codegradnew, codeestu, codegrad))
                conn.commit()

    cursor.execute("""
    UPDATE estudents 
    SET codegrad =%s, 
        gradeNY =%s, 
        grade =%s 
        where scodeest = %s
    """, ( codegradnew,codegradnew, nombre_gradonew, codeestu))
    conn.commit()

    cursor.close()
    conn.close()

    return "ok"


@estudiantes_bp.route('/ajax_notasarea_estudiante')
def ajax_notasarea_estudiante():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    cualperiodoonxe = request.args.get("codeperiodo")
    
    scodeemp1 = SCODEEMP
    periodo = cualperiodoonxe#PERIODO_ACTUAL

    chk_verhabilita = bool(request.args.get("chk_verhabilita"))

    cualestudiante = request.args.get("cualestudiante")
    
    codeestu = request.args.get("codeestu")
    codegrad = request.args.get("codegrad")

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
                   
    """, (codegrad, codeestu, scodeemp1))
    notasyareasact = cursor.fetchall()


    cursor.close()
    conn.close()
    return render_template(
        "estudiantes/_filas_areas.html",
        notasyareasact=notasyareasact,
        periodo=periodo
        )

