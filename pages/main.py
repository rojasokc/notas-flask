
import re
from flask import  Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from flask import jsonify
from config_loader import init_config
from config_loader import reload_config
from flask import current_app
from flask import request, Response
from dotenv import load_dotenv 
from config_loader import cargar_parametros

load_dotenv()

import secrets
import string


from routes.profesores import profesores_bp
from routes.estudiantes import estudiantes_bp
from routes.metasdeaycl import metasdea_bp
from routes.cformativo import cformativo_bp
from routes.reporte import reporte_bp
from routes.inscribemate import addmaterias_bp
from routes.voice import voice_bp
from routes.boletin import boletin_bp

from db import get_db_connection

# Crear la aplicación Flask
app = Flask(__name__)

with app.app_context():
    init_config(app)

#ALECTIVO_ACTUAL = app.config.get("ALECTIVO_ACTUAL")
#PERIODO_ACTUAL = app.config.get("PERIODO_ACTUAL")
#SCODEEMP = app.config.get("SCODEEMP")
#NIVELESCO = app.config.get("NIVELESCO")

app.secret_key = "alguna_clave_segura_y_unica_RCP04H"  # cámbiala por algo largo y secreto
app.register_blueprint(profesores_bp)
app.register_blueprint(estudiantes_bp)
app.register_blueprint(metasdea_bp)
app.register_blueprint(cformativo_bp)
app.register_blueprint(reporte_bp)
app.register_blueprint(addmaterias_bp)
app.register_blueprint(voice_bp)
app.register_blueprint(boletin_bp)



#def get_db_connection():
#    return mysql.connector.connect(
#        host="localhost",      # o la IP del servidor MySQL
#        user="root",           # tu usuario MySQL
#        password="Tucodata1!",# tu clave
#        database="tucodata"     # tu base de datos
#    )


# Definir la ruta principal
@app.route("/")
def home():
    # Renderiza el archivo templates/index.html
    return render_template("index.html")

RUTAS_PUBLICAS = ["/voice"]

@app.before_request
def verificar_login():
        # Cargar configuración una vez por petición
    if "CONFIG_CARGADA" not in current_app.config:
        config = cargar_parametros()

        current_app.config["PORC_PER1"] = config["PORC_PER1"]
        current_app.config["PORC_PER2"] = config["PORC_PER2"]
        current_app.config["PORC_PER3"] = config["PORC_PER3"]
        current_app.config["PORC_PER4"] = config["PORC_PER4"]
        current_app.config["PORC_PER5"] = config["PORC_PER5"]

        current_app.config["CONFIG_CARGADA"] = True    

    if request.path in RUTAS_PUBLICAS:
        return
    
    rutas_libres = ["loginvic", "static", "home", "logout"]

    if request.endpoint is None:
        return

    if request.endpoint in rutas_libres:
        return

    if request.endpoint.startswith("static"):
        return

    if "usuario" not in session:
        return redirect(url_for("loginvic"))
    


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('loginvic'))

#MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM



@app.route("/onlycreatepp")
def onlycreatepp():
    return render_template("onlycreate.html")

@app.route("/onlymoduserppal")
def onlymoduserppal():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #cursor.execute("SELECT * FROM empcole where scodeemp = %s ")
    scodeemp = current_app.config.get("SCODEEMP")

    search = request.args.get("search", "").strip()
    userid = request.args.get('userid')

    #lastname1 = request.args.get('lastname', '')
    if search:
        cursor.execute("""
            SELECT *
            FROM profesors
            WHERE lastname LIKE %s or lastname2 LIKE %s or names LIKE %s
            ORDER BY lastname, lastname2, names
        """, (f"{search}%",
              f"{search}%",
              f"{search}%",
              ))   # ← empieza por la letra
    else:
        cursor.execute("""
            SELECT *
            FROM profesors
            where lastname = "zzzzz"
            ORDER BY lastname, lastname2, names
        """)


    profes = cursor.fetchall()

    
    cursor.execute("""
        SELECT admuser.*
        FROM admuser
        WHERE TRIM(scodeemp) = %s
        """, (scodeemp,))

    admusers = cursor.fetchall()

    #cursor.execute("""
    #        SELECT *
    #        FROM profesors
    #        ORDER BY lastname, lastname2, names
    #    """)

    #profes = cursor.fetchall()

    cursor.close()
    conn.close()


    return render_template("onlymoduser.html", admusers=admusers, profes=profes)
    #return render_template("onlymoduser.html")

@app.route("/asignar_admin", methods=["POST"])
def asignar_admin():

    datos = request.get_json()

    codeprof = datos.get("codeprof")
    nivel = datos.get("nivel")
    print(f'el nivel que llega: {nivel}')
    if nivel:
        level = nivel
    else:
        level = 0
    #print(f'codigo de profesor admin: {codeprof}')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM profesors
        WHERE codeprof=%s
    """, (codeprof,))

    prof = cursor.fetchone()

    if not prof:
        return jsonify({
            "mensaje":"Profesor no encontrado"
        })

    from datetime import datetime

    fechahoy = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    cursor.execute("""
        INSERT INTO admuser
        (
            name,
            lastname,
            tel1,
            login,
            password,
            cargo,
            email,
            scodeemp,
            level,
            fechini
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
    """,
    (
        prof["names"],
        prof["lastname"],
        prof["tel"],
        prof["login"],
        prof["password"],
        prof["cargo"],
        prof["email1"],
        prof["scodeemp"],
        level,
        fechahoy
    ))

    conn.commit()

    return jsonify({
        "mensaje":"Administrador creado correctamente"
    })

@app.route('/delete_adminuser/<userid>', methods=['POST'])
def delete_adminuser(userid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = request.form.get('search', '')
    
    cursor.execute("""
        SELECT *
        FROM admuser
        WHERE userid=%s
    """, (userid,))

    auser = cursor.fetchone()

    #print(f'cuando borro: {auser['userid']}')

    if auser['level'] != "5":
        try:
            cursor.execute("DELETE FROM admuser WHERE userid = %s", (userid,))
            conn.commit()
            flash("Usuario eliminado correctamente.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al eliminar el registro de profesor: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        flash("ESTE Usuario no se puede eliminar.", "success")

    return redirect(url_for('onlymoduserppal', search=search))

@app.route('/onlyeditauser', methods=['GET', 'POST'])
def onlyeditauser():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = request.args.get("search", "").strip()
    userid = request.args.get('userid')

    #lastname1 = request.args.get('lastname', '')
    if search:
        cursor.execute("""
            SELECT *
            FROM profesors
            WHERE lastname LIKE %s or lastname2 LIKE %s or names LIKE %s
            ORDER BY lastname, lastname2, names
        """, (f"{search}%",
              f"{search}%",
              f"{search}%",
              ))   # ← empieza por la letra
    else:
        cursor.execute("""
            SELECT *
            FROM profesors
            where lastname = "zzzzz"
            ORDER BY lastname, lastname2, names
        """)


    profes = cursor.fetchall()

    # --- profesor seleccionado (detalle) ---
    #getadmuser = None
    #if userid:
    #    cursor.execute("""
    #        SELECT *
    #        FROM admuser
    #        WHERE userid = %s
    #    """, (userid,))
    #    getadmuser = cursor.fetchone()

    

    cursor.close()
    conn.close()

    #return render_template("onlymoduser.html", profes = profes, search = search, getadmuser = getadmuser) 
    #return render_template("onlymoduser.html", search = search, getadmuser = getadmuser)
    return render_template("onlymoduser.html", profes = profes, search=search)

@app.route('/save_admuser', methods=['POST'])
def save_admuser():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # datos del form
    name = request.form.get('campo1name',"").upper()
    lastname = request.form.get('campo2lastname',"").upper()
    tel1 = request.form.get('campo4tel1',"")
    email = request.form.get('campo5email')
    cargo = request.form.get('campo7cargo')
    city = request.form.get('campo8city')
    login = request.form.get('campo9login')

    userid = request.args.get("userid")

    sql = """
        INSERT INTO admuser (
            name, lastname, tel1,
            email, cargo, city, login
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name, lastname, tel1,
        email, cargo, city, login
    )

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('onlymoduserppal'))

@app.route('/update_admuser', methods=['POST'])
def update_admuser():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # datos del form
    name = request.form.get('campo1name',"").upper()
    lastname = request.form.get('campo2lastname',"").upper()
    tel1 = request.form.get('campo4tel1',"")
    email = request.form.get('campo5email')
    cargo = request.form.get('campo7cargo')
    city = request.form.get('campo8city')
    login = request.form.get('campo9login')

    userid = request.args.get("userid")

    #print(f'el userid: {userid}')
    try:
        cursor.execute("""
            UPDATE admuser
            SET 
                name = %s,
                lastname = %s, 
                tel1 = %s, 
                email = %s,
                cargo = %s, 
                city = %s, 
                login = %s 
                       
            WHERE userid=%s
        """, (
            name, lastname,  tel1, email,
        cargo, city, login, userid
        ))
        conn.commit()
        flash("Usuario actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar instituto: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlymoduserppal', userid=userid))
    #return render_template("onlymoduser.html")

@app.route("/onlyeditempresa")
def onlyeditempresa():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    cursor.execute("""
    SELECT empcole.* FROM empcole 
    """, )

    allemp = cursor.fetchone()
    
    return render_template("onlyeditemp.html", allemp=allemp)

@app.route('/save_empresa', methods=['POST'])
def save_empresa():
    conn = get_db_connection()
    cursor = conn.cursor()

    #ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    #PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    # Datos del formulario

    empresa       = request.form.get('campo1emp',"").upper()
    telef    = request.form.get('campo2tel',"")
    celu   = request.form.get('campo3cel',"")
    dir         = request.form.get('campo4dir')
    ciudad     = request.form.get('campo5ciu')
    depto  = request.form.get('campo6dpt')
    zip   = request.form.get('campo8zip')
    pais      = request.form.get('campo9pai')
    url   = request.form.get('campo10url')

    import random
    rancode = ''.join(str(random.randint(0, 9)) for _ in range(10))

    status = 'A'


    #if not login or len(login) < 6:
    #    return render_template("onlycreaprofx.html", error="Login inválido", mensaje="NO se creo el registro login error")

    #if not password or len(password) < 6:
    #    return render_template("onlycreaprofx.html", error="Password inválido", mensaje="NO se creo el registro login error")


    # Datos fijos / sistema
    #codecole = None           # o genera uno
    emptel     = ''
    emptel2    = ''
    empaddr   = ''
    empcity     = ''
    empst    = ''
    #scodeemp = SCODEEMP       # variable global que ya usas

    sql = """
        INSERT INTO empcole (
            empname, emptel, emptel2,
            empaddr, empcity, empst, empzip, empcountry, dominio, codecole, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        empresa, telef, celu,
        dir, ciudad, depto, zip, pais, url, rancode, status
    )

    cursor.execute(sql, values)
    conn.commit()

    cursor.close()
    conn.close()

    return render_template("onlyeditemp.html", mensaje="Datos de Instituto guardado correctamente")

@app.route('/update_empresa', methods=['POST'])
def update_empresa():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # datos del form
    empresa       = request.form.get('campo1emp',"").upper()
    telef    = request.form.get('campo2tel',"")
    celu   = request.form.get('campo3cel',"")
    dir         = request.form.get('campo4dir')
    ciudad     = request.form.get('campo5ciu')
    depto  = request.form.get('campo6dpt')
    zip   = request.form.get('campo8zip')
    pais      = request.form.get('campo9pai')
    url   = request.form.get('campo10url')

    codecole = request.form.get('codecole')

    try:
        cursor.execute("""
            UPDATE empcole
            SET 
                empname = %s, 
                emptel = %s, 
                emptel2 = %s,
                empaddr = %s, 
                empcity = %s, 
                empst = %s, 
                empzip = %s, 
                empcountry = %s, 
                dominio = %s 

            WHERE codecole=%s
        """, (
            empresa, telef, celu,
        dir, ciudad, depto, zip, pais, url, codecole
        ))
        conn.commit()
        flash("Instituto actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar instituto: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlyeditempresa', codecole=codecole))

    #return render_template("onlyeditemp.html")


#@app.route("/onlyboletines")
#def onlyboletines():
#    return render_template("boletin.html")

@app.route("/onlynotasestudiante")
def onlynotasestudiante():
    return render_template("onlynotasestudiantepp.html")

def generar_token():
    return ''.join(secrets.choice(string.digits) for _ in range(30))

def generar_nombre_param():
    caracteres = string.ascii_letters  # a-zA-Z
    return ''.join(secrets.choice(caracteres) for _ in range(16))

SUPER_USER = "rojasokc"
SUPER_PASS = "yopmipc1"

@app.route("/loginvic", methods=["GET", "POST"])
def loginvic():
    
    if request.method == "POST":
        login1 = request.form["usuario"]
        password1 = request.form["password"]
        tipo = request.form["tipo"]  # admin | profesor | estudiante

                # 🔥 SUPERUSUARIO (HARD-CODE)
        if login1 == SUPER_USER and password1 == SUPER_PASS:
            session.clear()
            session["rol"] = "superadmin"
            session["usuario"] = login1

            return redirect(url_for("onlycreatepp"))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if tipo == "admin":
            query = """
                SELECT admuser.*, empcole.totusers, empcole.empname,
                    empcole.codecole, empcole.emptema
                FROM admuser
                JOIN empcole ON admuser.scodeemp = empcole.scodeemp
                WHERE admuser.login = %s
                AND admuser.password = %s
            """

            cursor.execute(query, (login1, password1))
            user = cursor.fetchone()



            if user:
                # ✅ Guardamos datos clave en sesión
                session["rol"] = "admin"
                session["usuario"] = user["login"]
                session["scodeemp"] = user["scodeemp"]
                session["empname"] = user["empname"]
                session["codecole"] = user["codecole"]
                session["emptema"] = user["emptema"]
                 # 🔑 NIVEL DEL ADMIN
                session["level"] = user["level"]

                return redirect(url_for("opcionesadmin"))

        # 🔹 PROFESOR
        elif tipo == "profesor":


            query = """
                SELECT * FROM profesors
                WHERE login = %s AND password = %s
            """
            cursor.execute(query, (login1, password1))
            user = cursor.fetchone()

            if user:
                token = generar_token()
                param_name = generar_nombre_param() 

                session["rol"] = "profesor"
                session["usuario"] = user["login"]
                session["codeprof"] = user["codeprof"]
                session["token"] = token
                session["param_name"] = param_name

                return redirect(url_for("asignacion", codeprof=user["codeprof"], **{param_name: token}))


            # 🔹 ESTUDIANTE
        elif tipo == "estudiante":
            query = """
                SELECT * FROM estudents
                WHERE login = %s AND password = %s
            """
            cursor.execute(query, (login1, password1))
            user = cursor.fetchone()

            if user:
                session["rol"] = "estudiante"
                session["usuario"] = user["login"]
                session["codestu"] = user["codestu"]

                return redirect(url_for("panel_estudiante"))


        cursor.close()
        conn.close()
        
        flash("❌ Usuario o contraseña incorrectos", "danger")

    
    return render_template("loginvic.html")


@app.route("/panel_profesor")
def panel_profesor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #cursor.execute("SELECT * FROM estudents")
    #data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("panel_profesor.html")


@app.route("/opcionesadmin")
def opcionesadmin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #cursor.execute("SELECT * FROM estudents")
    #data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("opcionesadmin.html")

# Rutas para cada opción del menú
@app.route('/parametros-globales')
def Paramglobal():
    return render_template('parametros_globales.html')


@app.route('/gestion-academica')
def Gestionacade():
    return render_template('gestion_academica.html')


@app.route('/gestion-estudiantes')
def Gestionestu():
    return render_template('gestion_estudiantes.html')

@app.route('/onlyallparam')
def onlyallparam():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    cursor.execute("""
    SELECT allparam.* FROM allparam where trim(scodeemp) = %s
    """, (scodeemp,))

    allparam = cursor.fetchone()

     # Validar y separar per1 
    per11 = allparam.get("per1", "").strip() if allparam else ""
    # Valores por defecto
    desde_per1 = ""
    hasta_per1 = ""
    verhab1 = ""

    if len(per11) > 1 and "*" in per11:
        idx = per11.find("*")
        desde_per1 = per11[:idx]
        hasta_per1 = per11[idx + 1:]

    # Validar y separar per2 
    per12 = allparam.get("per2", "").strip() if allparam else ""
    # Valores por defecto
    desde_per2 = ""
    hasta_per2 = ""

    if len(per12) > 1 and "*" in per12:
        idx = per12.find("*")
        desde_per2 = per12[:idx]
        hasta_per2 = per12[idx + 1:]
    
    # Validar y separar per3 
    per13 = allparam.get("per3", "").strip() if allparam else ""
    # Valores por defecto
    desde_per3 = ""
    hasta_per3 = ""

    if len(per13) > 1 and "*" in per13:
        idx = per13.find("*")
        desde_per3 = per13[:idx]
        hasta_per3 = per13[idx + 1:]
    
    # Validar y separar per4 
    per14 = allparam.get("per4", "").strip() if allparam else ""
    # Valores por defecto
    desde_per4 = ""
    hasta_per4 = ""

    if len(per14) > 1 and "*" in per14:
        idx = per14.find("*")
        desde_per4 = per14[:idx]
        hasta_per4 = per14[idx + 1:]

    # periodos cerrados en bachillerato
    p1 = (allparam.get("closedp1") or "").strip().upper()
    p2 = (allparam.get("closedp2") or "").strip().upper()
    p3 = (allparam.get("closedp3") or "").strip().upper()
    p4 = (allparam.get("closedp4") or "").strip().upper()
    p5 = (allparam.get("closedp5") or "").strip().upper()

    status_periodo = "Periodo CERRADO"
    status_color = "yellow"  # cuando está cerrado

    if p1 == "NO":
        status_periodo = "1er Periodo ABIERTO"
        status_color = "white"
    elif p2 == "NO":
        status_periodo = "2do Periodo ABIERTO"
        status_color = "white"
    elif p3 == "NO":
        status_periodo = "3er Periodo ABIERTO"
        status_color = "white"
    elif p4 == "NO":
        status_periodo = "4to Periodo ABIERTO"
        status_color = "white"
    elif p5 == "NO":
        status_periodo = "5to Periodo ABIERTO"
        status_color = "white"

    # periodos cerrados en Primaria
    pr1 = (allparam.get("closedPR1") or "").strip().upper()
    pr2 = (allparam.get("closedPR2") or "").strip().upper()
    pr3 = (allparam.get("closedPR3") or "").strip().upper()
    pr4 = (allparam.get("closedPR4") or "").strip().upper()
    pr5 = (allparam.get("closedPR5") or "").strip().upper()

    status_periodopr = "Periodo CERRADO"
    status_colorpr = "yellow"  # cuando está cerrado

    if pr1 == "NO":
        status_periodopr = "1er Periodo ABIERTO"
        status_colorpr = "white"
    elif pr2 == "NO":
        status_periodopr = "2do Periodo ABIERTO"
        status_colorpr = "white"
    elif pr3 == "NO":
        status_periodopr = "3er Periodo ABIERTO"
        status_colorpr = "white"
    elif pr4 == "NO":
        status_periodopr = "4to Periodo ABIERTO"
        status_colorpr = "white"
    elif pr5 == "NO":
        status_periodopr = "5to Periodo ABIERTO"
        status_colorpr = "white"

    # periodos cerrados en Nocturna
    pc1 = (allparam.get("closedCI1") or "").strip().upper()
    pc2 = (allparam.get("closedCI2") or "").strip().upper()
    pc3 = (allparam.get("closedCI3") or "").strip().upper()
    pc4 = (allparam.get("closedCI4") or "").strip().upper()
    pc5 = (allparam.get("closedCI5") or "").strip().upper()

    status_periodoci = "Periodo CERRADO"
    status_colorci = "yellow"  # cuando está cerrado

    if pc1 == "NO":
        status_periodoci = "1er Periodo ABIERTO"
        status_colorci = "white"
    elif pc2 == "NO":
        status_periodoci = "2do Periodo ABIERTO"
        status_colorci = "white"
    elif pc3 == "NO":
        status_periodoci = "3er Periodo ABIERTO"
        status_colorci = "white"
    elif pc4 == "NO":
        status_periodoci = "4to Periodo ABIERTO"
        status_colorci = "white"
    elif pc5 == "NO":
        status_periodoci = "5to Periodo ABIERTO"
        status_colorci = "white"

    # periodos cerrados en escuelas asociaras o rurales o veredas
    pru1 = (allparam.get("closedRU1") or "").strip().upper()
    pru2 = (allparam.get("closedRU2") or "").strip().upper()
    pru3 = (allparam.get("closedRU3") or "").strip().upper()
    pru4 = (allparam.get("closedRU4") or "").strip().upper()
    pru5 = (allparam.get("closedRU5") or "").strip().upper()

    status_periodoru = "Periodo CERRADO"
    status_colorru = "yellow"  # cuando está cerrado

    if pru1 == "NO":
        status_periodoru = "1er Periodo ABIERTO"
        status_colorru = "white"
    elif pru2 == "NO":
        status_periodoru = "2do Periodo ABIERTO"
        status_colorru = "white"
    elif pru3 == "NO":
        status_periodoru = "3er Periodo ABIERTO"
        status_colorru = "white"
    elif pru4 == "NO":
        status_periodoru = "4to Periodo ABIERTO"
        status_colorru = "white"
    elif pru5 == "NO":
        status_periodoru = "5to Periodo ABIERTO"
        status_colorru = "white"


    return render_template('onlyallparam.html', allparam = allparam, desde_per1=desde_per1, hasta_per1=hasta_per1, desde_per2=desde_per2, hasta_per2=hasta_per2, desde_per3=desde_per3, hasta_per3=hasta_per3, desde_per4=desde_per4, hasta_per4=hasta_per4, status_periodo = status_periodo, status_periodopr = status_periodopr, status_periodoci = status_periodoci, status_periodoru = status_periodoru)

@app.route('/update_allparam', methods=['POST'])
def update_allparam():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Capturamos los valores del formulario
    alectivo = request.form.get('alectivo')
    calab = request.form.get('calab')
    valporper1 = request.form.get('valporper1')
    valporper2 = request.form.get('valporper2')
    valporper3 = request.form.get('valporper3')
    desde_per1 = request.form.get('desde_per1')
    hasta_per1 = request.form.get('hasta_per1')

    # Suponiendo que SCODEEMP es una constante o variable global
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")
    #scodeemp = SCODEEMP

    per1 = f"{desde_per1}*{hasta_per1}"

    # Actualizamos la tabla
    sql = """
        UPDATE allparam
        SET alectivo = %s,
            calab = %s,
            valporper1 = %s,
            valporper2 = %s,
            valporper3 = %s,
            per1 = %s
        WHERE TRIM(scodeemp) = %s
    """
    cursor.execute(sql, (alectivo, calab, valporper1, valporper2, valporper3, per1, scodeemp))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Parámetros actualizados correctamente.', 'success')

    # Regresa a la página de parámetros
    return redirect(url_for('onlyallparam'))

#abre cierra bachillerato
@app.route('/update_abrecierra', methods=['POST'])
def update_abrecierra():

    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP

    #print(f'verificando periodo bachil cuando entra: {periodo}')

    # 1) Leer los datos del formulario
    periodo_sel = request.form.get('selectPeriodo1')
    estado_radio = request.form.get('abrecie1')

    # Inicializa todos como "SI" (todos cerrados)
    closedp11 = "SI"
    closedp12 = "SI"
    closedp13 = "SI"
    closedp14 = "SI"
    closedp15 = "SI"

    # Si se seleccionó abrir (valor "radioabre1")
    if estado_radio == "radioabre1":
        if periodo_sel == "periodo1":
            closedp11 = "NO"
        elif periodo_sel == "periodo2":
            closedp12 = "NO"
        elif periodo_sel == "periodo3":
            closedp13 = "NO"
        elif periodo_sel == "periodo4":
            closedp14 = "NO"
        # Si no se selecciona periodo o es vacio, se dejan todos cerrados por defecto

    # 2) Ejecutar UPDATE en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE allparam 
        SET closedp1 = %s,
            closedp2 = %s,
            closedp3 = %s,
            closedp4 = %s,
            closedp5 = %s
        WHERE scodeemp = %s
    """
    params = (closedp11, closedp12, closedp13, closedp14, closedp15, scodeemp)

    try:
        cursor.execute(sql, params)
        conn.commit()
        reload_config(current_app)
        #print(f'verificando periodo bachil: {current_app.config.get("PERIODO_ACTUAL")}')
        #periodo = current_app.config.get("PERIODO_ACTUAL")
        #print(f'verificando periodo bachil si cargo variable: {periodo}')
        flash("Cambios guardados correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al guardar cambios: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    # 3) Redirigir a la vista onlyallparam para recargar la página
    return redirect(url_for('onlyallparam'))

#abre cierra primaria
@app.route('/update_abrecierrapr', methods=['POST'])
def update_abrecierrapr():
    scodeemp = current_app.config.get("SCODEEMP")
    #scodeemp = SCODEEMP

    # 1) Leer los datos del formulario
    periodo_sel = request.form.get('selectPeriodo2')
    estado_radio = request.form.get('abrecie2')

    # Inicializa todos como "SI" (todos cerrados)
    closedppr11 = "SI"
    closedppr12 = "SI"
    closedppr13 = "SI"
    closedppr14 = "SI"
    closedppr15 = "SI"

    # Si se seleccionó abrir (valor "radioabre1")
    if estado_radio == "radioabre2":
        if periodo_sel == "periodo1":
            closedppr11 = "NO"
        elif periodo_sel == "periodo2":
            closedppr12 = "NO"
        elif periodo_sel == "periodo3":
            closedppr13 = "NO"
        elif periodo_sel == "periodo4":
            closedppr14 = "NO"
        # Si no se selecciona periodo o es vacio, se dejan todos cerrados por defecto

    # 2) Ejecutar UPDATE en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE allparam 
        SET closedPR1 = %s,
            closedPR2 = %s,
            closedPR3 = %s,
            closedPR4 = %s,
            closedPR5 = %s
        WHERE scodeemp = %s
    """
    params = (closedppr11, closedppr12, closedppr13, closedppr14, closedppr15, scodeemp)

    try:
        cursor.execute(sql, params)
        conn.commit()
        reload_config(current_app)
        flash("Cambios guardados correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al guardar cambios: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    # 3) Redirigir a la vista onlyallparam para recargar la página
    return redirect(url_for('onlyallparam'))

#abre cierra ciclos o nocturna
@app.route('/update_abrecierraci', methods=['POST'])
def update_abrecierraci():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP

    # 1) Leer los datos del formulario
    periodo_sel = request.form.get('selectPeriodo3')
    estado_radio = request.form.get('abrecie3')

    # Inicializa todos como "SI" (todos cerrados)
    closedpci11 = "SI"
    closedpci12 = "SI"
    closedpci13 = "SI"
    closedpci14 = "SI"
    closedpci15 = "SI"

    # Si se seleccionó abrir (valor "radioabre1")
    if estado_radio == "radioabre3":
        if periodo_sel == "periodo1":
            closedpci11 = "NO"
        elif periodo_sel == "periodo2":
            closedpci12 = "NO"
        elif periodo_sel == "periodo3":
            closedpci13 = "NO"
        elif periodo_sel == "periodo4":
            closedpci14 = "NO"
        # Si no se selecciona periodo o es vacio, se dejan todos cerrados por defecto

    # 2) Ejecutar UPDATE en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE allparam 
        SET closedCI1 = %s,
            closedCI2 = %s,
            closedCI3 = %s,
            closedCI4 = %s,
            closedCI5 = %s
        WHERE scodeemp = %s
    """
    params = (closedpci11, closedpci12, closedpci13, closedpci14, closedpci15, scodeemp)

    try:
        cursor.execute(sql, params)
        conn.commit()
        reload_config(current_app)
        flash("Cambios guardados correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al guardar cambios: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    # 3) Redirigir a la vista onlyallparam para recargar la página
    return redirect(url_for('onlyallparam'))

#abre cierra rurales
@app.route('/update_abrecierraru', methods=['POST'])
def update_abrecierraru():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP

    # 1) Leer los datos del formulario
    periodo_sel = request.form.get('selectPeriodo4')
    estado_radio = request.form.get('abrecie4')

    # Inicializa todos como "SI" (todos cerrados)
    closedru11 = "SI"
    closedru12 = "SI"
    closedru13 = "SI"
    closedru14 = "SI"
    closedru15 = "SI"

    # Si se seleccionó abrir (valor "radioabre1")
    if estado_radio == "radioabre4":
        if periodo_sel == "periodo1":
            closedru11 = "NO"
        elif periodo_sel == "periodo2":
            closedru12 = "NO"
        elif periodo_sel == "periodo3":
            closedru13 = "NO"
        elif periodo_sel == "periodo4":
            closedru14 = "NO"
        # Si no se selecciona periodo o es vacio, se dejan todos cerrados por defecto

    # 2) Ejecutar UPDATE en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE allparam 
        SET closedRU1 = %s,
            closedRU2 = %s,
            closedRU3 = %s,
            closedRU4 = %s,
            closedRU5 = %s
        WHERE scodeemp = %s
    """
    params = (closedru11, closedru12, closedru13, closedru14, closedru15, scodeemp)

    try:
        cursor.execute(sql, params)
        conn.commit()
        reload_config(current_app)
        flash("Cambios guardados correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al guardar cambios: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    # 3) Redirigir a la vista onlyallparam para recargar la página
    return redirect(url_for('onlyallparam'))

@app.route('/onlyparam', methods=['GET', 'POST'])
def onlyparam():
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    #aqui
    # 1) Si es POST y editMode está marcado
    if request.method == 'POST' and request.form.get('editMode'):
        conn_w = get_db_connection()
        cursor_w = conn_w.cursor()

        for key, val in request.form.items():
            # Ejemplo de campo: notatt_123
            if "_" in key:
                field, code = key.split("_", 1)

                if field == "notatt":
                    cursor_w.execute("UPDATE observa SET notatt = %s WHERE codeobse = %s",
                                   (val, code))
                elif field == "rangoini":
                    cursor_w.execute("UPDATE observa SET rangoini = %s WHERE codeobse = %s",
                                   (val, code))
                elif field == "rangofin":
                    cursor_w.execute("UPDATE observa SET rangofin = %s WHERE codeobse = %s",
                                   (val, code))
                elif field == "nivelesco":
                    cursor_w.execute("UPDATE observa SET nivelesco = %s WHERE codeobse = %s",
                                   (val, code))

            # **Importante**: commit para guardar los cambios
        conn_w.commit()

        cursor_w.close()
        conn_w.close()

    # Determinar nivel según radio button (POST)
    nivelesco1 = ""
    if request.method == 'POST':
        if request.form.get('radioNivel') == 'PREBAS':
            nivelesco1 = "PREBAS"
        elif request.form.get('radioNivel') == 'PRIMAR':
            nivelesco1 = "PRIMAR"
        elif request.form.get('radioNivel') == 'BACHIL':
            nivelesco1 = "BACHIL"

    # Consulta similar a tu Legacy VB.NET
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT observa.* FROM observa
        WHERE TRIM(observa.scodeemp) = %s
          AND nivelesco = %s
          AND CHAR_LENGTH(notatt) > 1
        ORDER BY rangoini DESC
        """,(scodeemp, nivelesco1))
    observa_rows = cursor.fetchall()


    cursor.close()
    conn.close()
    

    return render_template(
        'onlyparam.html',
        observa_rows=observa_rows,
        nivelesco1=nivelesco1
    )

@app.route('/add_observa', methods=['POST'])
def add_observa():
    # 1) Leer campos del formulario
    new_notatt = request.form.get("new_notatt","").upper()
    new_rangoini = request.form.get("new_rangoini")
    new_rangofin = request.form.get("new_rangofin")

    # 2) Determinar nivel escolar según el radio seleccionado
    nivel = request.form.get("radioNivel") or ""

    # Asegurar que sí haya un nivel seleccionado
    if nivel not in ("PREBAS", "PRIMAR", "BACHIL"):
        flash("Seleccione un nivel escolar antes de agregar.", "warning")
        return redirect(url_for('onlyparam'))

    # 3) Insertar en la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    sql_insert = """
        INSERT INTO observa (scodeemp, notatt, rangoini, rangofin, nivelesco)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (SCODEEMP, new_notatt, new_rangoini, new_rangofin, nivel)

    try:
        cursor.execute(sql_insert, params)
        conn.commit()
        flash("Observación agregada correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al agregar observación: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlyparam'))

@app.route('/delete_observa/<codeobse>', methods=['POST'])
def delete_observa(codeobse):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM observa WHERE codeobse = %s", (codeobse,))
        conn.commit()
        flash("Observación eliminada correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar la observación: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlyparam'))

@app.route('/onlycreaprofx', methods=['GET', 'POST'])
def onlycreaprofx():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = request.args.get("search", "").strip()
    codeprof = request.args.get('codeprof')

    #lastname1 = request.args.get('lastname', '')
    if search:
        cursor.execute("""
            SELECT *
            FROM profesors
            WHERE lastname LIKE %s or lastname2 LIKE %s or names LIKE %s
            ORDER BY lastname, lastname2, names
        """, (f"{search}%",
              f"{search}%",
              f"{search}%",
              ))   # ← empieza por la letra
    else:
        cursor.execute("""
            SELECT *
            FROM profesors
            where lastname = "zzzzz"
            ORDER BY lastname, lastname2, names
        """)


    profes = cursor.fetchall()

    # --- profesor seleccionado (detalle) ---
    profesor = None
    if codeprof:
        cursor.execute("""
            SELECT *
            FROM profesors
            WHERE codeprof = %s
        """, (codeprof,))
        profesor = cursor.fetchone()

    

    cursor.close()
    conn.close()

    return render_template("onlycreaprofx.html", profes = profes, search = search, profesor = profesor)

#@app.route('/save_profesor', methods=['POST'])
#def save_profesor():
#    conn = get_db_connection()
#    cursor = conn.cursor()
#
#    # Datos del formulario
#
#    names       = request.form.get('campo1',"").upper()
#    lastname    = request.form.get('campo2',"").upper()
#    lastname2   = request.form.get('campo3',"").upper()
#    tel         = request.form.get('campo4')
#    email1     = request.form.get('campo5')
#    profesion  = request.form.get('campo6')
#    cargo      = request.form.get('campo7')
#    contacto   = request.form.get('campo8')
#    login      = request.form.get('campo9')
#    password   = request.form.get('campo11')
#
#    if not login or len(login) < 6:
#        return render_template("onlycreaprofx.html", error="Login inválido", mensaje="NO se creo el registro login error")
#
#    if not password or len(password) < 6:
#        return render_template("onlycreaprofx.html", error="Password inválido", mensaje="NO se creo el registro login error")
#
#
#    # Datos fijos / sistema
#    codeintp = None           # o genera uno
#    dir1     = ''
#    city1    = ''
#    state1   = ''
#    zip1     = ''
#    pais1    = ''
#    scodeemp = SCODEEMP       # variable global que ya usas
#
#    sql = """
#        INSERT INTO profesors (
#            codeintp, contacto, names, lastname, lastname2,
#            dir, tel, email1, city, state, zip, pais,
#            profesion, cargo, login, password, scodeemp
#        )
#        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#    """
#
#    values = (
#        codeintp, contacto, names, lastname, lastname2,
#        dir1, tel, email1, city1, state1, zip1, pais1,
#        profesion, cargo, login, password, scodeemp
#    )
#
#    cursor.execute(sql, values)
#    conn.commit()
#
#    cursor.close()
#    conn.close()
#
#    return render_template("onlycreaprofx.html", mensaje="Profesor guardado correctamente")

#@app.route('/delete_profesor/<codeprof>', methods=['POST'])
#def delete_profesor(codeprof):
#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)
#
#    search = request.form.get('search', '')
#    
#    try:
#        cursor.execute("DELETE FROM profesors WHERE codeprof = %s", (codeprof,))
#        conn.commit()
#        flash("Usuario eliminado correctamente.", "success")
#    except Exception as e:
#        conn.rollback()
#        flash(f"Error al eliminar el registro de profesor: {str(e)}", "danger")
#    finally:
#        cursor.close()
#        conn.close()
#
#    return redirect(url_for('onlycreaprofx', search=search))

#@app.route('/update_profesor/<codeprof>', methods=['POST'])
#def update_profesor(codeprof):
#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)
#
#    # datos del form
#    names      = request.form.get('campo1')
#    lastname   = request.form.get('campo2')
#    lastname2  = request.form.get('campo3')
#    tel        = request.form.get('campo4')
#    email1    = request.form.get('campo5')
#    profesion = request.form.get('campo6')
#    cargo     = request.form.get('campo7')
#    contacto  = request.form.get('campo8')
#    login     = request.form.get('campo9')
#
#    try:
#        cursor.execute("""
#            UPDATE profesors
#            SET names=%s,
#                lastname=%s,
#                lastname2=%s,
#                tel=%s,
#                email1=%s,
#                profesion=%s,
#                cargo=%s,
#                contacto=%s,
#                login=%s
#            WHERE codeprof=%s
#        """, (
#            names, lastname, lastname2, tel, email1,
#            profesion, cargo, contacto, login,
#            codeprof
#        ))
#        conn.commit()
#        flash("Profesor actualizado correctamente.", "success")
#
#    except Exception as e:
#        conn.rollback()
#        flash(f"Error al actualizar profesor: {str(e)}", "danger")
#
#    finally:
#        cursor.close()
#        conn.close()
#
#    return redirect(url_for('onlycreaprofx', codeprof=codeprof))

@app.route('/onlycreagradx', methods=['GET', 'POST'])
def onlycreagradx():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp1 = current_app.config.get("SCODEEMP")

    #scodeemp1 = SCODEEMP  # o de sesión
    searchgrado = request.args.get("searchgrado", "").strip()
    codegrad = request.args.get('codegrad')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT profesors.*,
               CONCAT(names, ' ', lastname) AS totname
        FROM profesors
        WHERE TRIM(scodeemp) = %s
        ORDER BY totname
    """, (scodeemp1,))

    directores = cursor.fetchall()

    if request.method == 'POST':
        director_id = request.form.get("campo5")
        # procesar guardado
        pass

    cursor.execute("""
        SELECT * 
        FROM colgrados 
        WHERE TRIM(scodeemp) = %s
        group by nivelgrado
                   ;
    """, (scodeemp1,))
    nivelgrado = cursor.fetchall()

    if request.method == 'POST':
        nivelgrado_id = request.form.get("campo6")
        # procesar guardado
        pass

    cursor.execute("""
        SELECT * 
        FROM colgrados 
        WHERE TRIM(scodeemp) = %s
        group by subnivel
                   ;
    """, (scodeemp1,))
    subnivel = cursor.fetchall()

    if request.method == 'POST':
        subnivel_id = request.form.get("campo7")
        # procesar guardado
        pass

    ###
    search = request.args.get("search", "").strip()
    codeprof = request.args.get('codeprof')

    #lastname1 = request.args.get('lastname', '')
    
    ###
    if searchgrado:

        cursor.execute("""
            SELECT * 
            FROM colgrados 
            WHERE TRIM(scodeemp) = %s and name LIKE %s
        """, (scodeemp1,
              f"{searchgrado}%",
            ))
    else:
        cursor.execute("""
            SELECT * 
            FROM colgrados 
            WHERE TRIM(scodeemp) = %s and name = "zzzzz"
        """, (scodeemp1,
              
            ))
        
    grados = cursor.fetchall()

    # REGISTRO SELECCIONADO
    grado_sel = None
    if codegrad:
        cursor.execute("""
            SELECT * FROM colgrados
            WHERE codegrad = %s
        """, (codegrad,))
        grado_sel = cursor.fetchone()


    return render_template(
        "onlycreagradx.html",
        directores=directores,
        nivelgrado = nivelgrado,
        subnivel = subnivel,
        grados = grados,
        searchgrado = searchgrado,
        grado_sel=grado_sel
    )
    
@app.route('/save_grado', methods=['POST'])
def save_grado():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ===== RADIO BUTTONS =====
    nivel_radio = request.form.get("nivel_radio")

    if nivel_radio == "1":
        nivelesco = "PREBAS"
    elif nivel_radio == "2":
        nivelesco = "PRIMAR"
    elif nivel_radio == "3":
        nivelesco = "BACHIL"
    else:
        nivelesco = None

    # ===== CAMPOS BASE =====
    name = request.form.get("campo2")
    responsable = request.form.get("responsable")
    nivelgradot = request.form.get("nivelgradot")
    subnivelt = request.form.get("subnivelt")
    scodeemp = current_app.config.get("SCODEEMP")
    #scodeemp = SCODEEMP
    codeinte = request.form.get("campo2")

    # ===== CHECKBOX LOGIC =====
    codeprof = request.form.get("codeprof") if request.form.get("chk_director") else None
    nivelgrado = request.form.get("nivelgrado") if request.form.get("chk_nivel") else None
    subnivel = request.form.get("subnivel") if request.form.get("chk_subnivel") else None

    # ===== INSERT =====
    cursor.execute("""
        INSERT INTO colgrados
        (subnivel, nivelesco, name, responsable,
         codeprof, codeinte, scodeemp, nivelgrado)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        subnivelt,
        nivelesco,
        name,
        responsable,
        codeprof,
        codeinte,
        scodeemp,
        nivelgradot
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("onlycreagradx"))


@app.route('/delete_grado/<codegrad>', methods=['POST'])
def delete_grado(codegrad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchgrado = request.form.get('searchgrado', '')
    
    try:
        cursor.execute("DELETE FROM colgrados WHERE codegrad = %s", (codegrad,))
        conn.commit()
        flash("Grado eliminado correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro : {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlycreagradx', searchgrado=searchgrado))
    

@app.route('/update_grado/<codegrad>', methods=['POST'])
def update_grado(codegrad):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # datos del form

    name   = request.form.get('campo2')
    codeinte  = request.form.get('campo3')
    responsable        = request.form.get('responsable')
    nivelgrado    = request.form.get('nivelgradot')
    subnivel = request.form.get('subnivelt')
    nivel_radio = request.form.get('nivel_radio')
    if nivel_radio == "1":
        nivelesco = "PREBAS"
    elif nivel_radio == "2":
        nivelesco = "PRIMAR"
    elif nivel_radio == "3":
        nivelesco = "BACHIL"
    else:
        nivelesco = None


    try:
        cursor.execute("""
            UPDATE colgrados
            SET name=%s,
                codeinte=%s,
                responsable=%s,
                nivelgrado=%s,
                subnivel=%s,
                nivelesco=%s
            WHERE codegrad=%s
        """, (
            name, codeinte, responsable, nivelgrado, subnivel,
            nivelesco,
            codegrad
        ))
        conn.commit()
        flash("Grado actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar grado: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('onlycreagradx', codegrad=codegrad))

@app.route('/creaareas', methods=['GET', 'POST'])
def creaareas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    codearea = request.args.get('codearea')

    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp   = SCODEEMP
    #alectivo = ALECTIVO_ACTUAL


    cursor.execute("""
        SELECT profesors.*,
               CONCAT(names, ' ', lastname) AS totname
        FROM profesors
        WHERE TRIM(scodeemp) = %s
        ORDER BY totname
    """, (scodeemp,))

    jefearealist = cursor.fetchall()
    
    searchareas = request.args.get("searchareas", "").strip()
    codeprof = request.args.get('codeprof')

    #lastname1 = request.args.get('lastname', '')
    if searchareas:
        cursor.execute("""
            SELECT *
            FROM areasxmate
            WHERE nombre LIKE %s 
            ORDER BY codearea
        """, (f"{searchareas}%",
              ))   # ← empieza por la letra
    else:
        cursor.execute("""
            SELECT *
            FROM areasxmate
            WHERE nombre = 'zzzzz'
            ORDER BY codearea
        """)

    areas = cursor.fetchall()
    

    # REGISTRO SELECCIONADO
    area_sel = None
    if codearea:
        cursor.execute("""
            SELECT * FROM areasxmate
            WHERE codearea = %s
        """, (codearea,))
        area_sel = cursor.fetchone()

    ##
    cursor.close()
    conn.close()

    return render_template('onlycreaareas.html', jefearealist = jefearealist, areas = areas, area_sel = area_sel)

@app.route('/save_areas', methods=['POST'])
def save_areas():
    conn = get_db_connection()
    cursor = conn.cursor()
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp   = SCODEEMP
    #alectivo = ALECTIVO_ACTUAL


    nombre     = request.form.get('campo1').upper()
    codeprof   = request.form.get('codejefea')
    jefearea   = request.form.get('jefeareat')
    nivelesco = request.form.get('nivelesco', 'BASICANONE')  # o el valor que aplique

    import random
    rancode = ''.join(str(random.randint(0, 9)) for _ in range(10))
    codemate ="nn"
    cursor.execute("""
        INSERT INTO areasxmate
        (nombre, scodeemp, rancode, codeprof, jefearea, alectivo, nivelesco, codemate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            scodeemp,
            rancode,
            codeprof,
            jefearea,
            alectivo,
            nivelesco,
            codemate
        ))

    conn.commit()
    flash("Área por materia guardada correctamente.", "success")
            
    cursor.close()
    conn.close()
    return redirect(url_for('creaareas'))


@app.route('/delete_area/<codearea>', methods=['POST'])
def delete_area(codearea):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchareas = request.form.get('searchareas', '')
    
    try:
        cursor.execute("DELETE FROM areasxmate WHERE codearea = %s", (codearea,))
        conn.commit()
        flash("Area eliminada correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro : {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creaareas', searchareas=searchareas))


@app.route('/update_area/<codearea>', methods=['POST'])
def update_area(codearea):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Capturar valores del formulario
    nombre = request.form.get('campo1')
    codeprof = request.form.get('codejefeareat')
    jefearea = request.form.get('jefeareat')
    alectivo = request.form.get('alectivo')  # checkbox o hidden
    #codearea = request.form.get('codearea')
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP   # o request.form.get('scodeemp')

    try:
        sql = """
            UPDATE areasxmate
            SET nombre = %s,
                codeprof = %s,
                jefearea = %s,
                alectivo = %s
            WHERE TRIM(scodeemp) = %s
              AND TRIM(codearea) = %s
        """

        cursor.execute(sql, (
            nombre,
            codeprof,
            jefearea,
            alectivo,
            scodeemp,
            codearea
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Error al actualizar área:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creaareas', codearea = codearea))



@app.route('/getallmaterx', methods=['POST'])
def getallmaterx():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    scodeemp = current_app.config.get("SCODEEMP")

    searchg = request.form.get("cualgradop2", "").strip()
    cursor.execute("""
            SELECT materia.*, 
                profesors.names, profesors.lastname, profesors.lastname2, 
                CONCAT(profesors.names, ' ', profesors.lastname, ' ', profesors.lastname2) as nombreprof, 
                areasxmate.nombre as nombreA, areasxmate.codeprof as codejefeA, 
                areasxmate.jefearea, colgrados.nivelgrado 
                FROM colgrados inner join areasxmate 
                   inner join materia 
                   inner join profesors 
                   on materia.codeprof = profesors.codeprof  
                   where trim(materia.scodeemp) = %s 
                   and areasxmate.codearea = CAST(materia.codearea AS UNSIGNED INTEGER) 
                   and colgrados.codegrad = materia.codegrad 
                   AND materia.codegrad LIKE %s 
                   order by nombrea,nombre

        """, (scodeemp, f"{searchg}%" 
              ))   
    allmaterxgrado = cursor.fetchall()

    return render_template('onlycreamaterx.html',  materfilter=allmaterxgrado)
    #return redirect(url_for('creaasignaturas'))

@app.route('/creaasignaturas')
def creaasignaturas():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    codemate = request.args.get('codemate')
    #codearea = request.args.get('codearea')
    #codeprof = request.args.get('codeprof')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search = request.args.get("searchmater", "").strip()
    
    #searchnombreprof = request.args.get('profexmateriat')
    searchnombreprof = request.args.get("profexmateriat", "").strip()
    #nivel_radio = request.args.get('nivel_radio')
    #if nivel_radio == "1":
    #    nivelesco = "PREBAS"
    #elif nivel_radio == "2":
    #    nivelesco = "PRIMAR"
    #elif nivel_radio == "3":
    #    nivelesco = "BACHIL"
    #else:
    #    nivelesco = ""

    
    if search:
        cursor.execute("""
            SELECT m.*,
                CONCAT(p.names, ' ', p.lastname) AS nombreprof
            FROM materia m
                JOIN profesors p
                ON m.codeprof = p.codeprof
            WHERE m.nombre LIKE %s 
                AND CONCAT(p.names, ' ', p.lastname) LIKE %s
            ORDER BY m.nombre, m.name
        """, (f"{search}%", f"{searchnombreprof}%" 
              ))   
    else:
        cursor.execute("""
            SELECT *
            FROM materia
            where nombre = "zzzzz"
            ORDER BY nombre, name
        """)


    materfilter = cursor.fetchall()


    cursor.execute("""
        SELECT profesors.*,
               CONCAT(names, ' ', lastname) AS totname
        FROM profesors
        WHERE TRIM(scodeemp) = %s
        ORDER BY totname
    """, (scodeemp,))

    profexmateria = cursor.fetchall()

    cursor.execute("""
            SELECT *
            FROM areasxmate
            WHERE TRIM(scodeemp) = %s
            ORDER BY codearea
        """, (scodeemp,))

    areasxmate = cursor.fetchall()

    cursor.execute("""
            SELECT *
            FROM materiamas
            WHERE TRIM(scodeemp) = %s
        """, (scodeemp,))

    materxmate = cursor.fetchall()

    # REGISTRO SELECCIONADO
    materxgrado_sel = None
    if codemate:
        cursor.execute("""
            SELECT * FROM materia
            WHERE codemate = %s
        """, (codemate,))
        materxgrado_sel = cursor.fetchone()
        
        
    # REGISTRO SELECCIONADO
        
    if materxgrado_sel:
        codearea = materxgrado_sel['codearea']
        cursor.execute("""
            SELECT *
            FROM areasxmate
            WHERE TRIM(scodeemp) = %s and codearea = %s
            ORDER BY codearea
        """, (scodeemp, codearea))

    areasxmate_sel = cursor.fetchone()

    # REGISTRO SELECCIONADO
    if materxgrado_sel:
        codeprof = materxgrado_sel['codeprof']
        cursor.execute("""
            SELECT profesors.*,
                CONCAT(names, ' ', lastname) AS totname
            FROM profesors
            WHERE TRIM(scodeemp) = %s and codeprof = %s
            ORDER BY totname
        """, (scodeemp, codeprof))

    profexmateria_sel = cursor.fetchone()

    # REGISTRO SELECCIONADO
    if materxgrado_sel:
        codegrad = materxgrado_sel['codegrad']
        cursor.execute("""
            SELECT colgrados.*
                FROM colgrados
            WHERE TRIM(scodeemp) = %s and codegrad = %s
            ORDER BY name
        """, (scodeemp, codegrad))

    gradosxm_sel = cursor.fetchone()

    return render_template('onlycreamaterx.html', profexmateria = profexmateria, areasxmate = areasxmate, materxmate = materxmate, materfilter = materfilter, materxgrado_sel = materxgrado_sel, areasxmate_sel = areasxmate_sel, profexmateria_sel = profexmateria_sel, gradosxm_sel = gradosxm_sel, codemate=codemate)

@app.route('/get_grados_por_nivel')
def get_grados_por_nivel():
    nivelesco = request.args.get('nivelesco')
    
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP  # tu variable global o sesión

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            colgrados.*,
            CONCAT(name) AS gradox,
            CAST(nivelgrado AS UNSIGNED) AS pp
        FROM colgrados
        WHERE TRIM(scodeemp) = %s
          AND TRIM(nivelesco) = %s
        ORDER BY pp DESC, name
    """

    cursor.execute(sql, (scodeemp, nivelesco))
    grados = cursor.fetchall()

    cursor.execute("""
        SELECT rangoini, notatt, nivelesco, codeobse
        FROM observa
        WHERE TRIM(scodeemp) = %s
        AND nivelesco = %s
        AND CHAR_LENGTH(notatt) > 1
        ORDER BY rangoini DESC
    """, (scodeemp, nivelesco))

    observa_rango = cursor.fetchall()


    cursor.close()
    conn.close()

    #return jsonify(grados)
    return jsonify({
        "grados": [
            {
                "codegrad": row["codegrad"],
                "gradox": row["gradox"],
                "nivelgrado": row["nivelgrado"]
            }
            for row in grados
        ],

        "rangos": [
            {
                "rangoini": row["rangoini"],
                "notatt": row["notatt"],
                "nivelesco": row["nivelesco"],
                "codeobse": row["codeobse"]
            }
            for row in observa_rango
        ]
    })

@app.route('/save_materia', methods=['POST'])
def save_materia():
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor()

    import random
    rancode1 = ''.join(str(random.randint(0, 9)) for _ in range(10))

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
    nombre1     = request.form.get('campo1')          # nombre asignatura
    valorm1     = request.form.get('campo1B')         # valor %
    codeprof1   = request.form.get('codeprofemt')     # profesor
    codegrad1 = request.form.get('campo2_hidden')  # código del grado
    nivelgrado = request.form.get('campo3_hidden')  # nivelgrado
    codearea1   = request.form.get('codearealistt')   # área
    nivelmate1 = str(codearea1).strip() + "1"
    name1       = request.form.get('campo2')      # nombre visible 11_1
    keymate1    = request.form.get('codematerlistt', '')     # opcional

    #aqui agrego las validaciones
    # ===== VALIDACIONES =====

    errores = []

    # 1. Radio obligatorio
    if not nivelesco1:
        errores.append("Debe seleccionar un nivel escolar")

    # 2. Selects obligatorios
    if not codegrad1:
        errores.append("Debe seleccionar un grado")

    if not codeprof1:
        errores.append("Debe seleccionar un profesor")

    if not codearea1:
        errores.append("Debe seleccionar un área")

    if not keymate1:
        errores.append("Debe seleccionar una asignatura")

    # 3. Checkbox (si esperas que vengan marcados)
    if not request.form.get('chk_cualgrado'):
        errores.append("Debe activar el grado")

    if not request.form.get('chk_profexmateriat'):
        errores.append("Debe activar el profesor")

    if not request.form.get('chk_arealistt'):
        errores.append("Debe activar el área")

    if not request.form.get('chk_materlistt'):
        errores.append("Debe activar la asignatura")

    # 4. Validar campo1B (valor %)
    try:
        valorm_int = int(valorm1)
        if valorm_int < 1 or valorm_int > 100:
            errores.append("El valor debe estar entre 1 y 100")
    except (TypeError, ValueError):
        errores.append("El valor debe ser un número entero válido")

    # 🚨 Si hay errores → NO guardar
    if errores:
        for e in errores:
            flash(e, "danger")
        return redirect(url_for('creaasignaturas'))

    ##

    try:

        cursor.execute("""
            INSERT INTO materia
            (nombre, nivelesco, codeprof, codegrad, scodeemp, rancode,
            codearea, valorm, nivelmate, name, keymate)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            nombre1,
            nivelesco1,
            codeprof1,
            codegrad1,
            scodeemp,
            rancode1,
            codearea1,
            valorm1,
            nivelmate1,
            name1,
            keymate1
        ))

        codemate = cursor.lastrowid

        #crea las metas de aprendizajo por cada asignatura creada
        sql_insert = """
            INSERT INTO metsncomp 
            ( codegrad, name, codemate, nombre, periodo, scodeemp, alectivo,nivelgrado) 
            VALUES ( %s, %s, %s,%s,%s,%s, %s,%s)
        """
        for i in range(1,5):
            periodo = f"PER{i}"
            params= (codegrad1,name1,codemate, nombre1, periodo, scodeemp, alectivo, nivelgrado)
            cursor.execute(sql_insert, params)
    
        conn.commit()
        flash("Asignatura creada correctamente", "success")
        
    except Exception as e:
        conn.rollback()  # 🔥 clave
        flash(f"Error al guardar: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creaasignaturas'))

@app.route('/delete_mater/<codemate>', methods=['POST'])
def delete_mater(codemate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchmater = request.form.get('searchmater', '')
    
    try:
        cursor.execute("DELETE FROM materia WHERE codemate = %s", (codemate,))
        conn.commit()
        flash("Area eliminada correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro : {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creaasignaturas', searchmater=searchmater))

@app.route('/update_materia/<codemate>', methods=['POST'])
def update_materia(codemate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

   # ====== VALIDACIÓN CHECKBOX ======
    chk_grado   = request.form.get('chk_cualgrado')
    chk_prof    = request.form.get('chk_profexmateriat')
    chk_area    = request.form.get('chk_arealistt')
    chk_materia = request.form.get('chk_materlistt')

    if not all([chk_grado, chk_prof, chk_area, chk_materia]):
        flash("Favor seleccionar cada casilla.", "warning")
        return redirect(url_for('creaasignaturas', codemate=codemate))

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
    nombre1     = request.form.get('campo1')          # nombre asignatura
    valorm1     = request.form.get('campo1B')         # valor %
    #nivelesco1  = request.form.get('nivel_radio')     # nivel escolar PREESCO, PRIMAR, BACHIL
    codeprof1   = request.form.get('codeprofemt')     # profesor
    codegrad1 = request.form.get('campo2_hidden')  # código del grado
    codearea1   = request.form.get('codearealistt')   # área
    nivelmate1 = str(codearea1).strip() + "1"
    name1       = request.form.get('campo2')      # nombre visible 11_1
    keymate1    = request.form.get('codematerlistt', '')     # opcional


    try:
        cursor.execute("""
            UPDATE materia
        SET nombre    = %s,
            nivelesco = %s,
            codeprof  = %s,
            codegrad  = %s,
            codearea  = %s,
            valorm    = %s,
            keymate   = %s,
            nivelmate = %s,
            name      = %s
        WHERE codemate = %s
    """, (nombre1, nivelesco1, codeprof1, codegrad1, codearea1, valorm1, keymate1, nivelmate1, name1 ,codemate
        ))
        conn.commit()
        flash("Registro actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar el registro: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creaasignaturas'))


@app.route('/creatablaasignaturas')
def creatablaasignaturas():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    codematmax = request.args.get("codematmax", "")


    #WWWWWWWWWWWWWWWWWWWWWw


    cursor.execute("""
            SELECT materiamas.*
            FROM materiamas
            WHERE TRIM(scodeemp) = %s
            ORDER BY codematmax
        """, (scodeemp, ))

    tablamateria = cursor.fetchall()

        # REGISTRO SELECCIONADO
    matmae_sel = None
    if codematmax:
        cursor.execute("""
            SELECT * FROM materiamas
            WHERE codematmax = %s
        """, (codematmax,))
        matmae_sel = cursor.fetchone()


    return render_template('creatablaasignaturas.html', tablamateria = tablamateria, matmae_sel = matmae_sel)

@app.route('/save_tablamateria', methods=['POST'])
def save_tablamateria():
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    conn = get_db_connection()
    cursor = conn.cursor()


    # ====== Datos del formulario ======
    nombre1     = request.form.get('nombre').upper()          # nombre asignatura
    keymate1    = request.form.get('keymatetabla', '')     # opcional


    cursor.execute("""
        INSERT INTO materiamas
        (nombre, keymate, scodeemp)
        VALUES (%s,%s,%s)
    """, (
        nombre1,
        keymate1,
        scodeemp
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('creatablaasignaturas'))

@app.route('/delete_tabmat/<codematmax>', methods=['POST'])
def delete_tabmat(codematmax):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    searchtabmat = request.form.get('searchtabmat', '')
    
    try:
        cursor.execute("DELETE FROM materiamas WHERE codematmax = %s", (codematmax,))
        conn.commit()
        flash("Asignatura de tabla maestra eliminada correctamente.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar el registro : {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creatablaasignaturas', searchtabmat=searchtabmat))

@app.route('/update_tablamateria/<codematmax>', methods=['POST'])
def update_tablamateria(codematmax):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    nombre1     = request.form.get('nombre').upper()          # nombre asignatura
    keymate1     = request.form.get('keymatetabla')         # valor %


    try:
        cursor.execute("""
            UPDATE materiamas
        SET nombre    = %s,
            keymate   = %s
        WHERE codematmax = %s
    """, (nombre1, keymate1, codematmax
        ))
        conn.commit()
        flash("Registro actualizado correctamente.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error al actualizar el registro: {str(e)}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('creatablaasignaturas'))
    
#@app.route('/onlycreaalumnx')
#def onlycreaalumnx():
#    return render_template('onlycreaalumnx.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/notaspp')
def notaspp():
    return render_template('notaspp.html')

@app.route("/estudiantes")
def estudiantes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM estudents")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("estudiantes.html", estudiantes=data)

#@app.route("/profesores")
#def profesores():
#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)
#    cursor.execute("SELECT * FROM profesors")
#    data = cursor.fetchall()
#    cursor.close()
#    conn.close()
#    return render_template("profesores.html", profesores=data)

#@app.route("/asignacion/<codeprof>/<token>")
#def asignacion(codeprof, token):

@app.route("/asignacion/<codeprof>")
def asignacion(codeprof):

    # 1️⃣ Debe existir sesión
    if "rol" not in session:
        return redirect(url_for("loginvic"))

    # 2️⃣ Rol correcto
    if session.get("rol") != "profesor":
        return redirect(url_for("loginvic"))

    # 3️⃣ El codeprof debe coincidir
    #if session.get("codeprof") != codeprof:
    #    return redirect(url_for("loginvic"))
    
    if str(session.get("codeprof")) != str(codeprof):
        return redirect(url_for("loginvic"))

    # 4️⃣ Deben existir token y nombre del parámetro
    param_name = session.get("param_name")
    token_session = session.get("token")

    if not param_name or not token_session:
        return redirect(url_for("loginvic"))

    # 5️⃣ El token debe venir en la URL
    token_request = request.args.get(param_name)

    if not token_request:
        return redirect(url_for("loginvic"))

    # 6️⃣ El token debe coincidir EXACTAMENTE
    if token_request != token_session:
        return redirect(url_for("loginvic"))
    
    #session.pop("token", None)
    #session.pop("param_name", None)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    scodeemp = current_app.config.get("SCODEEMP")
    #scodeemp = SCODEEMP

    # Buscamos los grados asociados en colgrados
    #SELECT CONCAT(profesors.names, ' ', profesors.lastname) as totname, colgrados.codegrad, colgrados.name, profesors.fotof, profesors.cargo, profesors.profesion,colgrados.nivelesco,colgrados.subnivel FROM profesors, materia, colgrados where profesors.codeprof=materia.codeprof AND materia.codegrad = colgrados.codegrad AND (profesors.scodeemp) = '" + scodeemp1 + "' and profesors.codeprof = '" + codeprof1 + "' group by materia.codegrad

    cursor.execute("""
        SELECT CONCAT(profesors.names, ' ', profesors.lastname) as totname,
        colgrados.codegrad, colgrados.name, profesors.fotof,
        profesors.cargo, profesors.profesion, colgrados.codeinte,
        colgrados.nivelesco,colgrados.subnivel, materia.nombre, materia.codemate 
        FROM profesors JOIN materia
            ON profesors.codeprof=materia.codeprof
            JOIN colgrados
            ON materia.codegrad = colgrados.codegrad
        WHERE  
            profesors.codeprof = %s 
            group by materia.codegrad

    """, (codeprof,))
    grados = cursor.fetchall()

    # También traemos los datos del profesor
    cursor.execute("SELECT * FROM profesors WHERE codeprof = %s", (codeprof,))
    profesor = cursor.fetchone()
    


    cursor.execute("""
        SELECT colgrados.*, CONCAT(name, ' :: ', codeinte) as gradox 
        FROM colgrados 
        where trim(scodeemp) = %s AND codeprof = %s
    """, (scodeemp, codeprof))
    dirgrado = cursor.fetchall()
    #rows = cursor.fetchall()
    #dirgrado = rows[0] if rows else None

    #aqui se podria cargar el archivo de fechas, de vb.net
    
    cursor.close()
    conn.close()


    return render_template("asignacion.html", 
        profesor=profesor, 
        grados=grados, 
        dirgrado = dirgrado, 
        codeprof=codeprof
        )
    


@app.route("/grado/<codemate>")
def grado(codemate):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    #scodeemp = current_app.config.get("SCODEEMP")

    codeprof = request.args.get("codeprof")

    #periodo = PERIODO_ACTUAL
    #alectivo = ALECTIVO_ACTUAL
    # Obtenemos la información del grado
    cursor.execute("SELECT * FROM materia WHERE codemate = %s", (codemate,))
    grado = cursor.fetchone()

    #desde aqui 
    codegrad = grado["codegrad"]
    scodeemp = grado["scodeemp"]

    # 2️⃣ carga el subnivel por el grado
    cursor.execute("""
        SELECT colgrados.codegrad, colgrados.name,  
            colgrados.nivelesco,colgrados.subnivel, materia.codemate
            FROM profesors join materia
                   ON profesors.codeprof=materia.codeprof
                   JOIN colgrados 
                   ON materia.codegrad = colgrados.codegrad
            WHERE (profesors.scodeemp) = %s 
            AND profesors.codeprof = %s 
            AND materia.codemate = %s
                   
    """, (scodeemp, codeprof, codemate))
    nivelxgrado = cursor.fetchone()

    cursor.execute("SELECT * FROM allparam LIMIT 1")
    p = cursor.fetchone()
    
    alectivo = p["alectivo"]
    #scodeemp = p["scodeemp"]
    nivelesco = nivelxgrado["nivelesco"]
    print(f' alectivo para todos: { alectivo }')
    print(f' scodeemp para todos: { scodeemp }')
    print(f' nivelesco por asignatura: { nivelesco } { codemate }')

    if nivelxgrado and nivelxgrado["subnivel"] == "DIURNA":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        #hace otra consulta
    
        if not p:
            return {}

        if p["closedp1"] == "NO":
            periodo = "PER1"
        elif p["closedp2"] == "NO":
            periodo = "PER2"
        elif p["closedp3"] == "NO":
            periodo = "PER3"
        elif p["closedp4"] == "NO":
            periodo = "PER4"
        elif p["closedp5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None

        print(f' periodo diurno bachil: { periodo }')
    elif nivelxgrado["subnivel"] == "NOCTUR":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedCI1"] == "NO":
            periodo = "PER1"
        elif p["closedCI2"] == "NO":
            periodo = "PER2"
        elif p["closedCI3"] == "NO":
            periodo = "PER3"
        elif p["closedCI4"] == "NO":
            periodo = "PER4"
        elif p["closedCI5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo nocturno bachil: { periodo }')

    elif nivelxgrado["subnivel"] == "RURAL":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedRU1"] == "NO":
            periodo = "PER1"
        elif p["closedRU2"] == "NO":
            periodo = "PER2"
        elif p["closedRU3"] == "NO":
            periodo = "PER3"
        elif p["closedRU4"] == "NO":
            periodo = "PER4"
        elif p["closedRU5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo rural bachil: { periodo }')

    elif nivelxgrado["subnivel"] == "SEDEDOS":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedPR1"] == "NO":
            periodo = "PER1"
        elif p["closedPR2"] == "NO":
            periodo = "PER2"
        elif p["closedPR3"] == "NO":
            periodo = "PER3"
        elif p["closedPR4"] == "NO":
            periodo = "PER4"
        elif p["closedPR5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo primaria bachil: { periodo }')        

    periodo = periodo
    ##hasta aqui
    #hasta aqui

    # Traer encabezados dinámicos desde notastxt
    cursor.execute("SELECT * FROM notastxt WHERE codemate = %s and periodo = %s and alectivo = %s", (codemate,periodo,alectivo))
    notas_headers = cursor.fetchone()
    
    # Convertir los labelX en lista de columnas visibles
    mensaje= None
    columnas = []
    if notas_headers:
        
        for i in range(1, 31):  # suponiendo máximo 30 labels
            label = notas_headers.get(f"label{i}")
            peso = notas_headers.get(f"valor{i}") or 0
            clo = notas_headers.get(f"clo{i}")
            if label:  # solo si no está vacío
                columnas.append({
                        "campo": f"nota{i}", 
                        "etiqueta": label,
                        "peso": peso,
                        "clo": clo
                                })
    if not notas_headers:
        mensaje = "Debe crear la plantilla de notas primero"
    


    # Si quieres listar también los estudiantes de ese grado:
    
    cursor.execute("""
        SELECT 
            estudents.codeint,
            estudents.names,
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) as nombre,
            estudents.lastn2,
            calinotas.*,
            estudents.alectivo,
            estudents.codegrad as codegrad1,
            estudents.scodeest,
            estudents.grade       
        FROM calinotas
        INNER JOIN estudents ON calinotas.codeestu = estudents.scodeest
        WHERE calinotas.codemate = %s
          AND calinotas.alectivo = %s
          AND calinotas.periodo = %s
          AND estudents.status = 'MATRICUL'
        GROUP BY estudents.scodeest
        ORDER BY estudents.lastn, estudents.lastn2, estudents.names
    """, (codemate, alectivo, periodo)) ##aqui estaban los valores con mayuscula

    estudiantes = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("grado.html", 
        grado=grado, 
        estudiantes=estudiantes, 
        codemate=codemate, 
        alectivo=alectivo, 
        periodo=periodo, 
        nivelesco=nivelesco, 
        codeprof=codeprof,
        columnas=columnas, mensaje=mensaje,
        param_name=session.get("param_name"),
        token=session.get("token")
        )


@app.route("/guardar_notas", methods=["POST"])
def guardar_notas():
    codemate = request.form["codemate"]
    alectivo = request.form["alectivo"]
    periodo = request.form["periodo"]
    nivelesco = request.form["nivelesco"]
    codegrad = request.form["codegrad"]
    codearea = request.form["codearea"]
    scodeemp = request.form["scodeemp"]

    #nivelesco = NIVELESCO

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        conn.autocommit = False

        # ----------------------------------------------------------
        # 1. CARGAR SOLO UNA VEZ (ANTES DEL FOR)
        # ----------------------------------------------------------

        # OBSERVA
        cursor.execute("""
            SELECT * FROM observa
            WHERE TRIM(scodeemp) = %s AND TRIM(nivelesco) = %s
        """, (scodeemp, nivelesco))
        rows = cursor.fetchall()

        codeobserva = [r["codeobse"] for r in rows]
        observa    = [str(r["notatt"]).strip() if r["notatt"] else "" for r in rows]
        ranini     = [float(r["rangoini"]) if r["rangoini"] else None for r in rows]
        ranfin     = [float(r["rangofin"]) if r["rangofin"] else None for r in rows]


        # PARAMETROS DE PERIODOS (ANTES DEL FOR)
        cursor.execute("""
           SELECT valporper1, valporper2, valporper3, valporper4, valporper5
           FROM allparam LIMIT 1
        """)
        param = cursor.fetchone() or {}

        def to_dec(v):
            try: return Decimal(str(v).strip())
            except: return Decimal("0")

        per1p, per2p, per3p, per4p, per5p = map(
            to_dec, (
                param.get("valporper1"),
                param.get("valporper2"),
                param.get("valporper3"),
                param.get("valporper4"),
                param.get("valporper5"),
            )
        )

        p12p = per1p + per2p
        p123p = p12p + per3p
        p1234p = p123p + per4p
        p12345p = p1234p + per5p

        # notastxt
        cursor.execute("""
            SELECT * FROM notastxt
            WHERE codemate=%s AND periodo=%s AND alectivo=%s
        """, (codemate, periodo, alectivo))
        config_notas = cursor.fetchone()

        num_labels = sum(
            1 for i in range(1,31)
            if config_notas.get(f"label{i}") not in ("",None," ")
        )

        # lista de estudiantes que cambiaron
        estudiantes = set()

        # ----------------------------------------------------------
        # 2. GUARDAR NOTAS (UPDATE calinotas)
        # ----------------------------------------------------------

        for key, value in request.form.items():
            if key.startswith("nota_"):
                _, scodeest, campo = key.split("_", 2)
                estudiantes.add(scodeest)

                valor = value if value.strip() != "" else 0.0

                cursor.execute(f"""
                    UPDATE calinotas
                    SET {campo} = %s
                    WHERE codeestu=%s AND codemate=%s AND alectivo=%s AND periodo=%s
                """, (valor, scodeest, codemate, alectivo, periodo))

        # ----------------------------------------------------------
        # 3. CARGAR SOLO LOS ESTUDIANTES AFECTADOS
        # ----------------------------------------------------------
        if not estudiantes:
            conn.commit()
            return redirect(request.referrer)

        placeholders = ",".join(["%s"]*len(estudiantes))
        cursor.execute(f"""
            SELECT *
            FROM calinotas
            WHERE codemate=%s AND periodo=%s AND alectivo=%s
              AND codeestu IN ({placeholders})
        """, (codemate, periodo, alectivo, *estudiantes))

        calinotas_dict = {row["codeestu"]: row for row in cursor.fetchall()}

        # función para observación
        def obtener_observacion(v):
            try: val = float(v)
            except: return ""
            for i in range(len(ranini)):
                if ranini[i] is not None and ranfin[i] is not None:
                    if ranini[i] <= val <= ranfin[i]:
                        return codeobserva[i]
            return ""

        # ----------------------------------------------------------
        # 4. RECALCULAR SOLO LOS ESTUDIANTES CAMBIADOS (MUY RÁPIDO)
        # ----------------------------------------------------------

        for scodeest in estudiantes:
            fila = calinotas_dict[scodeest]

            # ---- calcular promfinal ----
            total_peso = Decimal("0")
            suma = Decimal("0")

            for i in range(1, num_labels+1):
                nota = fila.get(f"nota{i}")
                peso = to_dec(config_notas.get(f"valor{i}"))

                if nota and float(nota) > 0 and peso > 0:
                    suma += peso * Decimal(nota)
                    total_peso += peso

            promfinal = round(suma/total_peso, 1) if total_peso > 0 else None

            # guardar promfinal
            cursor.execute("""
                UPDATE calinotas
                SET promfinal=%s
                WHERE codeestu=%s AND codemate=%s AND alectivo=%s AND periodo=%s
            """, (promfinal, scodeest, codemate, alectivo, periodo))

            # ---- actualizar periodo en calimate ----
            if periodo == "PER1": campo = "nota1"
            elif periodo == "PER2": campo = "nota2"
            elif periodo == "PER3": campo = "nota3"
            elif periodo == "PER4": campo = "nota4"
            elif periodo == "PER5": campo = "nota5"
            else: campo = None

            if campo:
                cursor.execute(f"""
                    UPDATE calimate
                    SET {campo}=%s
                    WHERE codeestu=%s AND codemate=%s
                """, (promfinal, scodeest, codemate))

            # ---- obtener notas actuales para promedio acumulado ----
            cursor.execute("""
                SELECT codecalm, nota1, nota2, nota3, nota4, nota5
                FROM calimate
                WHERE codeestu=%s AND codemate=%s
            """, (scodeest, codemate))
            c = cursor.fetchone()
            if not c:
                continue

            n1 = to_dec(c["nota1"])
            n2 = to_dec(c["nota2"])
            n3 = to_dec(c["nota3"])
            n4 = to_dec(c["nota4"])
            n5 = to_dec(c["nota5"])
            codecalm1 = c["codecalm"]

            # ---- calcular promedio acumulado ----
            if periodo == "PER1" and per1p > 0:
                prom = round(n1, 1)
                campo_prom = "promedio"
                campo_obs = "obspe1"
                campo_obspr = "obsprom"
                obspe = obtener_observacion(n1)
                #obsprom = obtener_observacion(promfinal)
                obsprom = obtener_observacion(prom)

            elif periodo == "PER2" and p12p > 0:
                prom = round((n1*per1p + n2*per2p) / p12p,1)
                campo_prom = "promedio2"
                campo_obs = "obspe2"
                campo_obspr = "obsprom2"
                obspe = obtener_observacion(n2)
                #obsprom = obtener_observacion(promfinal)
                obsprom = obtener_observacion(prom)

            elif periodo == "PER3" and p123p > 0:
                prom = round((n1*per1p + n2*per2p + n3*per3p) / p123p,1)
                campo_prom = "promedio3"
                campo_obs = "obspe3"
                campo_obspr = "obsprom3"
                obspe = obtener_observacion(n3)
                #obsprom = obtener_observacion(promfinal)
                obsprom = obtener_observacion(prom)

            elif periodo == "PER4" and p1234p > 0:
                prom = round((n1*per1p + n2*per2p + n3*per3p + n4*per4p) / p1234p,1)
                campo_prom = "promedio4"
                campo_obs = "obspe4"
                campo_obspr = "obsprom4"
                obspe = obtener_observacion(n4)
                #obsprom = obtener_observacion(promfinal)
                obsprom = obtener_observacion(prom)

            elif periodo == "PER5" and p12345p > 0:
                prom = round((n1*per1p + n2*per2p + n3*per3p + n4*per4p + n5*per5p) / p12345p,1)
                campo_prom = "promedio5"
                campo_obs = "obspe5"
                campo_obspr = "obsprom5"
                obspe = obtener_observacion(n5)
                #obsprom = obtener_observacion(promfinal)
                obsprom = obtener_observacion(prom)

            else:
                continue

            cursor.execute(f"""
                UPDATE calimate
                SET {campo_prom}=%s, {campo_obs}=%s, {campo_obspr}=%s
                WHERE codecalm=%s
            """, (prom, obspe, obsprom, codecalm1))

        # ----------------------------------------------------------
        # 5. ACTUALIZAR ÁREA
        # ----------------------------------------------------------
        actualizar_area(periodo, alectivo, codegrad, codearea, scodeemp, nivelesco, conn)

        conn.commit()
        cursor.close()
        conn.close()

        return render_template("grados.html",
                               mensaje="Notas actualizadas correctamente.",
                               periodo=periodo)

    except Exception as e:
        print(e)
        flash(f"Error al guardar notas: {e}", "danger")

    return redirect(request.referrer)

########PRUEBA DE ESTA FUNCION EXTERNA

    ######HASTA AQUI

def actualizar_area(periodo, alectivo, codegrad, codearea, scodeemp, nivelesco, conn):
    

    cursor = conn.cursor(dictionary=True)
    #print(f"aqui comienza guardar area")
    #print(f"pericos: {periodo}")

    #### de esta funcion
    # leyendo la tabla OBSERVA, esta rutina esta dos veces, 
    cursor.execute("""
        SELECT * FROM observa
        WHERE TRIM(scodeemp) = %s AND TRIM(nivelesco) = %s
    """, (scodeemp, nivelesco))
    rows = cursor.fetchall()

    codeobserva = [r["codeobse"] for r in rows]
    observa    = [str(r["notatt"]).strip() if r["notatt"] else "" for r in rows]
    ranini     = [float(r["rangoini"]) if r["rangoini"] else None for r in rows]
    ranfin     = [float(r["rangofin"]) if r["rangofin"] else None for r in rows]

    # función para observación
    def obtener_observacion(v):
        try: val = float(v)
        except: return ""
        for i in range(len(ranini)):
            if ranini[i] is not None and ranfin[i] is not None:
                if ranini[i] <= val <= ranfin[i]:
                    return codeobserva[i]
        return ""
    
    ###fin de la carga


    # 🔸 Leer los porcentajes desde allparam
    cursor.execute("SELECT valporper1, valporper2, valporper3, valporper4, valporper5 FROM allparam LIMIT 1")
    allparam = cursor.fetchone()

    notaparcial1A = "SUM((materia.valorm * calimate.nota1) / 100)"
    notaparcial2A = "SUM((materia.valorm * calimate.nota2) / 100)"
    notaparcial3A = "SUM((materia.valorm * calimate.nota3) / 100)"
    notaparcial4A = "SUM((materia.valorm * calimate.nota4) / 100)"
    notaparcial5A = "SUM((materia.valorm * calimate.nota5) / 100)"

    porper1 = Decimal(allparam["valporper1"] or 0)
    porper2 = Decimal(allparam["valporper2"] or 0)
    porper3 = Decimal(allparam["valporper3"] or 0)
    porper4 = Decimal(allparam["valporper4"] or 0)
    porper5 = Decimal(allparam["valporper5"] or 0)

    if periodo == "PER1":
        #print(f"aqui1")
        por1per = porper1
        if por1per == 0:
            return
        
        realpp1 = porper1 / por1per

    elif periodo == "PER2":
        #print(f"aqui2")
        por1y2per = porper1 + porper2
        if por1y2per == 0:
            return
        
        realpp1 = porper1 / por1y2per
        realpp2 = porper2 / por1y2per
        
    elif periodo == "PER3":
        por1y2y3per = porper1 + porper2 + porper3
        #print(f"leyendo allaram {por1y2y3per}")
        if por1y2y3per == 0:
            return

        realpp1 = porper1 / por1y2y3per
        realpp2 = porper2 / por1y2y3per
        realpp3 = porper3 / por1y2y3per
        #print(f"otros realpp3 {realpp3}")

    elif periodo == "PER4":
        por1y2y3y4per = porper1 + porper2 + porper3 + porper4
        #print(f"leyendo allaram {por1y2y3per}")
        if por1y2y3y4per == 0:
            return

        realpp1 = porper1 / por1y2y3y4per
        realpp2 = porper2 / por1y2y3y4per
        realpp3 = porper3 / por1y2y3y4per
        realpp4 = porper4 / por1y2y3y4per
        #print(f"otros realpp3 {realpp3}")

    elif periodo == "PER5":
        por1y2y3y4y5per = porper1 + porper2 + porper3 + porper4 + porper5
        #print(f"leyendo allaram {por1y2y3per}")
        if por1y2y3y4y5per == 0:
            return

        realpp1 = porper1 / por1y2y3y4y5per
        realpp2 = porper2 / por1y2y3y4y5per
        realpp3 = porper3 / por1y2y3y4y5per
        realpp4 = porper4 / por1y2y3y4y5per
        realpp5 = porper5 / por1y2y3y4y5per
        #print(f"otros realpp3 {realpp3}")


    if periodo == "PER1":
        sql = f"""
        SELECT 
            estudents.codeint, estudents.scodeest, materia.codearea, estudents.codegrad, 
            TRIM(CONCAT(materia.nombre, ' ', materia.valorm, '%')) AS nombrexporje, 
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombret, 
            estudents.lastn2, 
            calimate.*, 
            estudents.alectivo, 
            materia.valorm,  
            {notaparcial1A} AS notaparcial1, 
            '' AS notaparcial2, 
            '' AS notaparcial3, 
            '' AS notaparcial4,
            '' AS notaparcial5, 
            ROUND({notaparcial1A}, 2) AS notafinal, 
            '' AS notafinal2, 
            '' AS notafinal3, 
            '' As notafinal4, '' As notafinal5,
            peson1 AS fechact
        FROM 
            calimate
            JOIN estudents ON calimate.codeestu = estudents.scodeest
            JOIN materia ON calimate.codemate = materia.codemate
        WHERE 
            materia.codearea = %s
            AND calimate.alectivo = %s
            AND estudents.alectivo = %s
            AND estudents.codegrad = %s
        GROUP BY 
            calimate.codeestu
        ORDER BY 
            nombret
        """
        cursor.execute(sql, (codearea, alectivo, alectivo, codegrad))
        resultados = cursor.fetchall()

    if periodo == "PER2":
        
        sql = f"""
        SELECT 
            estudents.codeint, estudents.scodeest, materia.codearea, estudents.codegrad, 
            TRIM(CONCAT(materia.nombre, ' ', materia.valorm, '%')) AS nombrexporje, 
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombret, 
            estudents.lastn2, 
            calimate.*, 
            estudents.alectivo, 
            materia.valorm,  
            {notaparcial1A} AS notaparcial1, 
            {notaparcial2A} AS notaparcial2, 
            '' AS notaparcial3, 
            '' AS notaparcial4,
            '' AS notaparcial5, 
            ROUND({notaparcial1A}, 2) AS notafinal, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2}, 2) AS notafinal2, 
            '' AS notafinal3, 
            '' As notafinal4, '' As notafinal5,
            peson2 AS fechact
        FROM 
            calimate
            JOIN estudents ON calimate.codeestu = estudents.scodeest
            JOIN materia ON calimate.codemate = materia.codemate
        WHERE 
            materia.codearea = %s
            AND calimate.alectivo = %s
            AND estudents.alectivo = %s
            AND estudents.codegrad = %s
        GROUP BY 
            calimate.codeestu
        ORDER BY 
            nombret
        """
        cursor.execute(sql, (codearea, alectivo, alectivo, codegrad))
        resultados = cursor.fetchall()

    if periodo == "PER3":
        sql = f"""
        SELECT 
            estudents.codeint, estudents.scodeest, materia.codearea, estudents.codegrad, 
            TRIM(CONCAT(materia.nombre, ' ', materia.valorm, '%')) AS nombrexporje, 
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombret, 
            estudents.lastn2, 
            calimate.*, 
            estudents.alectivo, 
            materia.valorm,  
            {notaparcial1A} AS notaparcial1, 
            {notaparcial2A} AS notaparcial2, 
            {notaparcial3A} AS notaparcial3, 
            '' AS notaparcial4,
            '' AS notaparcial5, 
            ROUND({notaparcial1A}, 2) AS notafinal, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2}, 2) AS notafinal2, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3}, 2) AS notafinal3, 
            '' As notafinal4, '' As notafinal5,
            peson3 AS fechact
        FROM 
            calimate
            JOIN estudents ON calimate.codeestu = estudents.scodeest
            JOIN materia ON calimate.codemate = materia.codemate
        WHERE 
            materia.codearea = %s
            AND calimate.alectivo = %s
            AND estudents.alectivo = %s
            AND estudents.codegrad = %s
        GROUP BY 
            calimate.codeestu
        ORDER BY 
            nombret
        """
        cursor.execute(sql, (codearea, alectivo, alectivo, codegrad))
        resultados = cursor.fetchall()

    if periodo == "PER4":
        sql = f"""
        SELECT 
            estudents.codeint, estudents.scodeest, materia.codearea, estudents.codegrad, 
            TRIM(CONCAT(materia.nombre, ' ', materia.valorm, '%')) AS nombrexporje, 
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombret, 
            estudents.lastn2, 
            calimate.*, 
            estudents.alectivo, 
            materia.valorm,  
            {notaparcial1A} AS notaparcial1, 
            {notaparcial2A} AS notaparcial2, 
            {notaparcial3A} AS notaparcial3, 
            {notaparcial4A} AS notaparcial4,
            '' AS notaparcial5, 
            ROUND({notaparcial1A}, 2) AS notafinal, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2}, 2) AS notafinal2, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3}, 2) AS notafinal3, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3} + {notaparcial4A} * {realpp4}, 2) As notafinal4, 
            '' As notafinal5,
            peson4 AS fechact
        FROM 
            calimate
            JOIN estudents ON calimate.codeestu = estudents.scodeest
            JOIN materia ON calimate.codemate = materia.codemate
        WHERE 
            materia.codearea = %s
            AND calimate.alectivo = %s
            AND estudents.alectivo = %s
            AND estudents.codegrad = %s
        GROUP BY 
            calimate.codeestu
        ORDER BY 
            nombret
        """
        cursor.execute(sql, (codearea, alectivo, alectivo, codegrad))
        resultados = cursor.fetchall()

    if periodo == "PER5":
        sql = f"""
        SELECT 
            estudents.codeint, estudents.scodeest, materia.codearea, estudents.codegrad, 
            TRIM(CONCAT(materia.nombre, ' ', materia.valorm, '%')) AS nombrexporje, 
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombret, 
            estudents.lastn2, 
            calimate.*, 
            estudents.alectivo, 
            materia.valorm,  
            {notaparcial1A} AS notaparcial1, 
            {notaparcial2A} AS notaparcial2, 
            {notaparcial3A} AS notaparcial3, 
            {notaparcial4A} AS notaparcial4,
            {notaparcial5A} AS notaparcial5, 
            ROUND({notaparcial1A}, 2) AS notafinal, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2}, 2) AS notafinal2, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3}, 2) AS notafinal3, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3} + {notaparcial4A} * {realpp4}, 2) As notafinal4, 
            ROUND({notaparcial1A} * {realpp1} + {notaparcial2A} * {realpp2} + {notaparcial3A} * {realpp3} + {notaparcial4A} * {realpp4} + {notaparcial5A} * {realpp5}, 2) As notafinal5,
            peson5 AS fechact
        FROM 
            calimate
            JOIN estudents ON calimate.codeestu = estudents.scodeest
            JOIN materia ON calimate.codemate = materia.codemate
        WHERE 
            materia.codearea = %s
            AND calimate.alectivo = %s
            AND estudents.alectivo = %s
            AND estudents.codegrad = %s
        GROUP BY 
            calimate.codeestu
        ORDER BY 
            nombret
        """
        cursor.execute(sql, (codearea, alectivo, alectivo, codegrad))
        resultados = cursor.fetchall()
    #print(f"leyendo calimate solo eso {codearea}, {alectivo}, {codegrad}")
    

    for fila in resultados:
        #print(f"veamos si entro al for :: {periodo}")
        codeestu1 = fila["scodeest"]
        
        codegrad1 = fila["codegrad"]
        
        codearea1 = fila["codearea"]
        

        #per1 = Decimal(fila["notaparcial1"] or 0)
        #per2 = Decimal(fila["notaparcial2"] or 0)
        #per3 = Decimal(fila["notaparcial3"] or 0)
        #per11 = fila["nota1"]
        #per21 = fila["nota2"]
        #per31 = fila["nota3"]
        per11 = Decimal(fila["notaparcial1"] or 0)
        per21 = Decimal(fila["notaparcial2"] or 0)
        per31 = Decimal(fila["notaparcial3"] or 0)
        per41 = Decimal(fila["notaparcial4"] or 0)
        per51 = Decimal(fila["notaparcial5"] or 0)

        ##notaparcial3

        #notafinal = round((per1 * realpp1) , 1)
        #notafinal2 = round((per1 * realpp1) + (per2 * realpp2) , 1)
        #notafinal3 = round((per1 * realpp1) + (per2 * realpp2) + (per3 * realpp3), 1)

        notafinal1 = Decimal(fila["notafinal"] or 0)
        notafinal2 = Decimal(fila["notafinal2"] or 0)
        notafinal3 = Decimal(fila["notafinal3"] or 0)
        notafinal4 = Decimal(fila["notafinal4"] or 0)
        

        #print(f"despues de cargar variables :: {periodo}")
        if periodo == "PER1":
            try:
                

                per11r = per11.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #per11 = str(per11r)
                per11 = f"{per11r:.1f}"
                notafinal1r = notafinal1.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #notafinal1=str(notafinal1r)    
                notafinal1 = f"{notafinal1r:.1f}"

                #aqui se llama la funcion de rangos de calificaciones en observa
                obspe1 = obtener_observacion(per11) ##notta de area suma asignaturas de area

                obsnfinal = obtener_observacion(notafinal1) ##nota de area, suma horiz

                cursor.execute("""
                    UPDATE caliarea 
                    SET per1 = %s, notafinal = %s, obsnfinal = %s, obspe1 =%s
                    WHERE codearea = %s AND codeestu = %s 
                        AND codegrad = %s 
                """, (per11, notafinal1, obsnfinal, obspe1, codearea1, codeestu1, codegrad1))
                #print("Filas afectadas:", cursor.rowcount)
            except Exception as e:
                    print("❌ Error en UPDATE:", e)
        elif periodo == "PER2":
            try:
                per21r = per21.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #per21 = str(per21r)
                per21 = f"{per21r:.1f}"
                notafinal2r = notafinal2.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #notafinal2=str(notafinal2r)
                notafinal2 = f"{notafinal2r:.1f}"

                #aqui se llama la funcion de rangos de calificaciones en observa
                obspe2 = obtener_observacion(per21) ##notta de area suma asignaturas de area

                obsnfinal2 = obtener_observacion(notafinal2)
                
                cursor.execute("""
                        UPDATE caliarea 
                        SET per2 = %s, notafinal2 = %s, obsnfinal2 = %s, obspe2 = %s
                        WHERE codearea = %s AND codeestu = %s 
                            AND codegrad = %s 
                    """, (per21, notafinal2, obsnfinal2, obspe2, codearea1, codeestu1, codegrad1))
                #print("Filas afectadas:", cursor.rowcount)

                
            except Exception as e:
                    print("❌ Error en UPDATE:", e)
                        
        elif periodo == "PER3":
            #print(f"entre en periodo 3")
            try:
                
                per31r = per31.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #per31 = str(per31r)
                per31 = f"{per31r:.1f}"
                #notafinal3_str = str(round(notafinal3, 2))
                #notafinal3r = Decimal(notafinal3.replace(",", ".")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                notafinal3r = notafinal3.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #notafinal3=str(notafinal3r)
                notafinal3 = f"{notafinal3r:.1f}"

                #aqui se llama la funcion de rangos de calificaciones en observa
                obspe3 = obtener_observacion(per31) ##notta de area suma asignaturas de area

                obsnfinal3 = obtener_observacion(notafinal3)
                
                cursor.execute(
                    """
                    UPDATE caliarea
                    SET per3 = %s, notafinal3 = %s, obsnfinal3 = %s, obspe3 = %s
                    WHERE codearea = %s AND codeestu = %s AND codegrad = %s
                    """, (per31, notafinal3, obsnfinal3, obspe3, codearea1, codeestu1, codegrad1))
                
                #print("Filas afectadas:", cursor.rowcount)
            except Exception as e:
                    print("❌ Error en UPDATE:", e)

        elif periodo == "PER4":
            #print(f"entre en periodo 4")
            try:
                
                per41r = per41.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #per41 = str(per41r)
                per41 = f"{per41r:.1f}"
                
                notafinal4r = notafinal4.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                #notafinal4=str(notafinal4r)
                notafinal4 = f"{notafinal4r:.1f}"

                #aqui se llama la funcion de rangos de calificaciones en observa
                obspe4 = obtener_observacion(per41) ##notta de area suma asignaturas de area

                obsnfinal4 = obtener_observacion(notafinal4)
                
                cursor.execute(
                    """
                    UPDATE caliarea
                    SET per4 = %s, notafinal4 = %s, obsnfinal4 = %s, obspe4 = %s
                    WHERE codearea = %s AND codeestu = %s AND codegrad = %s
                    """, (per41, notafinal4, obsnfinal4, obspe4, codearea1, codeestu1, codegrad1))
                
                #print("Filas afectadas:", cursor.rowcount)
            except Exception as e:
                    print("❌ Error en UPDATE:", e)

    #posible aqui
    
    conn.commit()


@app.route("/periodos", methods=["GET"])
def periodos():
    #from main import NIVELESCO  # importar la variable global BACHIL
        
    codemate = request.args.get("codemate")
    #alectivo = request.args.get("alectivo")
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    #scodeemp = current_app.config.get("SCODEEMP")

    #alectivo = ALECTIVO_ACTUAL
    
    nivelesco = request.args.get("nivelesco")
    alectivo = request.args.get("alectivo")
    codegrad = request.args.get("codegrad")
    periodo = request.args.get("periodo")  # Ej: "PER3"
    nivel = request.args.get("nivel")      # Ej: "ALTO"

    codeprof = request.args.get("codeprof")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔹 1. Obtener información del grado (encabezado)
    cursor.execute("SELECT * FROM materia WHERE codemate = %s", (codemate,))
    grado = cursor.fetchone()

    # 🔹 2. Cargar observaciones según NIVELESCO
    cursor.execute("""
        SELECT codeobse, notatt 
        FROM observa
        WHERE nivelesco = %s and scodeemp = '31'
        ORDER BY codeobse
    """, (nivelesco,))
    observaciones = cursor.fetchall()

    # 🔹 3. Construir consulta base
    query = """
        SELECT 
            estudents.codeint,
            estudents.scodeest,
            estudents.names,
            UCASE(estudents.lastn) AS lastn,
            estudents.lastn2,
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombre,
            calimate.*,
            estudents.alectivo
        FROM calimate
        JOIN estudents ON calimate.codeestu = estudents.scodeest
        WHERE 
            calimate.codemate = %s
            AND calimate.alectivo = %s
            AND calimate.codegrad = %s
            AND estudents.status = 'MATRICUL'
    """
    

    # 🔹 7. Ejecutar consulta
    cursor.execute(query, (codemate, alectivo, codegrad))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 8. Renderizar con observaciones para el dropdown
    return render_template(
        "periodos.html",
        grado=grado,
        resultados=resultados,
        periodo=periodo,
        observaciones=observaciones,  # 👈 se pasa al HTML
        nivel_actual=nivel or "",
        nivelesco=nivelesco,
        codeprof=codeprof
    )


@app.template_filter('mostrar_vacio')
def mostrar_vacio(value):
    if value is None or value == 0 or value == 0.0:
        return ''
    return f"{value:.1f}" if isinstance(value, (float, int, Decimal)) else value

@app.route("/actualizar_falta", methods=["POST"])
def actualizar_falta():
    data = request.get_json()
    scodeest = data.get("scodeest")
    codemate = data.get("codemate")
    periodo = data.get("periodo")  # "3" → fp3
    cambio = int(data.get("cambio", 0))  # +1 o -1

    if not all([scodeest, codemate, periodo]):
        return jsonify({"status": "error", "msg": "Datos incompletos"})

    pernum = periodo[-1] # saca el ultimo caracter, en este caso el num 3 de PER3
    campo_fp = f"fp{pernum}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1️⃣ Leer faltas actuales del estudiante
    cursor.execute(
        f"SELECT fp1, fp2, fp3, fp4, faltas FROM calimate WHERE codemate=%s AND codeestu=%s",
        (codemate, scodeest)
    )
    fila = cursor.fetchone()

    if not fila:
        conn.close()
        return jsonify({"status": "error", "msg": "Registro no encontrado"})

    # 2️⃣ Convertir a enteros
    fp1 = int(fila.get("fp1") or 0)
    fp2 = int(fila.get("fp2") or 0)
    fp3 = int(fila.get("fp3") or 0)
    fp4 = int(fila.get("fp4") or 0)

    # 3️⃣ Actualizar el periodo correspondiente
    if campo_fp == "fp1":
        fp1 = max(0, fp1 + cambio)
    elif campo_fp == "fp2":
        fp2 = max(0, fp2 + cambio)
    elif campo_fp == "fp3":
        fp3 = max(0, fp3 + cambio)
    elif campo_fp == "fp4":
        fp4 = max(0, fp4 + cambio)

    # 4️⃣ Recalcular total de faltas
    faltas_total = fp1 + fp2 + fp3 + fp4

    # 5️⃣ Guardar en la BD
    cursor.execute(
        f"""UPDATE calimate
            SET fp1=%s, fp2=%s, fp3=%s, fp4=%s, faltas=%s
            WHERE codemate=%s AND codeestu=%s""",
        (str(fp1), str(fp2), str(fp3), str(fp4), str(faltas_total), codemate, scodeest)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "status": "ok",
        "fp1": fp1,
        "fp2": fp2,
        "fp3": fp3,
        "fp4": fp4,
        "faltas": faltas_total
    })


@app.route("/cargar_formativo", methods=["POST"])
def cargar_formativo():
    data = request.get_json()
    notatt = data.get("notatt")
    scodeemp = data.get("scodeemp")
    codearea = data.get("codearea")

    print(f'aqui el valor numerico de notatt {notatt}')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql = f"""
        SELECT *
        FROM formativo
        WHERE TRIM(scodeemp) = %s
          AND nivelesco = 'BACHIL'
          AND TRIM(codearea) = %s
          AND notatt = %s
        ORDER BY codeobse

    """
    cursor.execute(sql, (scodeemp, codearea, notatt))
    filas = cursor.fetchall()

    cursor.close()
    conn.close()

    if filas:
        return jsonify({"status": "ok", "data": filas})
    else:
        return jsonify(status="error", mensaje="No se encontraron registros")


@app.route("/filtrar_periodos", methods=["POST"])
def filtrar_periodos():
    data = request.get_json()
    codemate = data.get("codemate")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    #scodeemp = current_app.config.get("SCODEEMP")

    #alectivo = ALECTIVO_ACTUAL #data.get("alectivo")
    codegrad = data.get("codegrad")
    codeobse = data.get("codeobse")  # viene del dropdown

    #### periodo = data.get("periodo") aqui se trae periodo desde script

    print(f'codemate es {codemate}')
    print(f'alectivo es {alectivo}')
    print(f'codegrad es {codegrad}')

    print(f'codeobse es {codeobse}')
    # 🔹 Determinar el número de período dinámicamente
    periodo_num = "".join([c for c in PERIODO_ACTUAL if c.isdigit()]) or "1"
    obspe_field = f"obspe{periodo_num}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔹 Construimos la consulta con el campo dinámico
    sql = f"""
        SELECT 
            estudents.codeint,
            estudents.scodeest,
            estudents.names,
            UCASE(estudents.lastn) AS lastn,
            estudents.lastn2,
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombre,
            calimate.*,
            estudents.alectivo
        FROM calimate
        JOIN estudents ON calimate.codeestu = estudents.scodeest
        WHERE 
            calimate.codemate = %s 
            AND calimate.alectivo = %s 
            AND calimate.codegrad = %s
            AND estudents.status = 'MATRICUL'
            AND {obspe_field} = %s
        ORDER BY estudents.lastn
    """

    cursor.execute(sql, (codemate, alectivo, codegrad, codeobse))
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"status": "ok", "data": resultados, "periodo": PERIODO_ACTUAL})

@app.route('/formativo3')
def formativo3():
    #print(f'quiero entrar')
    codeobse = request.args.get('codeobse')
    notatt = request.args.get('notatt')       # Ej: "SUPERIOR"
    codemate = request.args.get("codemate")
    codegrad = request.args.get("codegrad")
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")

    periodo = request.args.get("periodo")
    nivelesco = request.args.get("nivelesco")
    #codeprof = request.args.get("codeprof")

    #print(f'codeprof desde periodos: {codeprof}')
    #alectivo = ALECTIVO_ACTUAL #data.get("alectivo")
    #scodeemp = SCODEEMP
    #nivelesco = NIVELESCO # OJO esto es bachil s
    #periodo=PERIODO_ACTUAL
    
    #obspe_field = "calimate.obspe3"
    #obspe_field = f"calimate.obspe{periodo_num}"

    periodo_num = "".join([c for c in periodo if c.isdigit()]) or "1"
    obspe_field = f"obspe{periodo_num}"

    #print(f'codeobse forma : {codeobse}')
    #print(f'notatt forma : {notatt}')
    #print(f'nivelesco forma : {nivelesco}')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 🔹 0. Cargar observaciones según NIVELESCO
    cursor.execute("""
        SELECT codeobse, notatt 
        FROM observa
        WHERE nivelesco = %s and scodeemp = %s
        ORDER BY codeobse
    """, (nivelesco, scodeemp))
    observaciones = cursor.fetchall()

# 🔹 1. Obtener información del grado (encabezado)
    cursor.execute("SELECT * FROM materia WHERE codemate = %s", (codemate,))
    grado = cursor.fetchone()

    # 📌 Si existe materia, obtenemos su área (codearea)
    codearea = grado.get("codearea") if grado else None

    #print(f'codearea forma : {codearea}')
    

     # SQL con filtrado dinámico
    sql = f"""
        SELECT 
            estudents.codeint,
            estudents.scodeest,
            estudents.names,
            UCASE(estudents.lastn) AS lastn,
            estudents.lastn2,
            CONCAT(UCASE(estudents.lastn), ' ', UCASE(estudents.lastn2), ', ', UCASE(estudents.names)) AS nombre,
            calimate.*,
            estudents.alectivo
        FROM calimate
        JOIN estudents ON calimate.codeestu = estudents.scodeest
        WHERE 
            calimate.codemate = %s 
            AND calimate.alectivo = %s 
            AND calimate.codegrad = %s
            AND estudents.status = 'MATRICUL'
            AND {obspe_field} = %s
        ORDER BY estudents.lastn
    """

    cursor.execute(sql, (codemate, alectivo, codegrad, codeobse))
    resultados = cursor.fetchall()

    # 🔹 Consulta de datos formativos
    cursor.execute("""
        SELECT *
        FROM formativo
        WHERE TRIM(scodeemp) = %s
          AND nivelesco = %s
          AND TRIM(codearea) = %s
          AND notatt = %s
        ORDER BY codeobse
    """, (scodeemp, nivelesco, codearea, notatt))
    filasXX = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'formativo3.html',
        resultados=resultados,
        grado=grado,
        scodeemp=scodeemp,
        filasXX=filasXX,
        notatt=notatt,
        nivelesco=nivelesco,
        periodo=periodo,
        periodo_num=periodo_num,
        observaciones=observaciones
    )

@app.route('/actualizar_formativo', methods=['POST'])
def actualizar_formativo():
    ### viene desde formativo3 desde un script
    data = request.get_json()
    codigosCalm = data.get("codigosCalm", [])
    concepto = data.get("concepto")
    periodo = data.get("periodo")

    periodo_num = "".join([c for c in periodo if c.isdigit()]) or "1"

    if not codigosCalm or not concepto:
        return jsonify({"status": "error", "mensaje": "Datos incompletos."})

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for codecalm in codigosCalm:
            codecalm_int = int(float(codecalm))
            sql = f"""
                UPDATE calimate
                SET rempe{periodo_num} = %s
                WHERE codecalm = %s
            """
            cursor.execute(sql, (concepto, codecalm_int))
        conn.commit()
        return jsonify({"status": "ok", "mensaje": "Formativo actualizado correctamente."})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "mensaje": str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route("/onlyeditnotas/<codemate>")
def onlyeditnotas(codemate):
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    #scodeemp = current_app.config.get("SCODEEMP")

    codeprof = request.args.get("codeprof")

    #scodeemp = SCODEEMP
    #periodo = PERIODO_ACTUAL
    #alectivo = ALECTIVO_ACTUAL
    periodo = None

    # 1️⃣ Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    #DESDE AQUI
    # 2️⃣ Buscar la materia correspondiente
    cursor.execute("SELECT * FROM materia WHERE codemate = %s", (codemate,))
    grado = cursor.fetchone()

    codegrad = grado["codegrad"]
    scodeemp = grado["scodeemp"]

    # 2️⃣ carga el subnivel por el grado
    cursor.execute("""
        SELECT colgrados.codegrad, colgrados.name,  
            colgrados.nivelesco,colgrados.subnivel, materia.codemate
            FROM profesors join materia
                   ON profesors.codeprof=materia.codeprof
                   JOIN colgrados 
                   ON materia.codegrad = colgrados.codegrad
            WHERE (profesors.scodeemp) = %s 
            AND profesors.codeprof = %s 
            AND materia.codemate = %s
                   
    """, (scodeemp, codeprof, codemate))
    nivelxgrado = cursor.fetchone()

    cursor.execute("SELECT * FROM allparam LIMIT 1")
    p = cursor.fetchone()
    
    alectivo = p["alectivo"]
    #scodeemp = p["scodeemp"]
    nivelesco = nivelxgrado["nivelesco"]
    print(f' alectivo para todos: { alectivo }')
    print(f' scodeemp para todos: { scodeemp }')
    print(f' nivelesco por asignatura: { nivelesco } { codemate }')

    if nivelxgrado and nivelxgrado["subnivel"] == "DIURNA":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        #hace otra consulta
    
        if not p:
            return {}

        if p["closedp1"] == "NO":
            periodo = "PER1"
        elif p["closedp2"] == "NO":
            periodo = "PER2"
        elif p["closedp3"] == "NO":
            periodo = "PER3"
        elif p["closedp4"] == "NO":
            periodo = "PER4"
        elif p["closedp5"] == "NO":
            periodo = "PER5"
        else:
            periodo = "PERIODO CERRADO"

        print(f' periodo diurno bachil: { periodo }')
    elif nivelxgrado["subnivel"] == "NOCTUR":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedCI1"] == "NO":
            periodo = "PER1"
        elif p["closedCI2"] == "NO":
            periodo = "PER2"
        elif p["closedCI3"] == "NO":
            periodo = "PER3"
        elif p["closedCI4"] == "NO":
            periodo = "PER4"
        elif p["closedCI5"] == "NO":
            periodo = "PER5"
        else:
            periodo = "PERIODO CERRADO"
        print(f' periodo nocturno bachil: { periodo }')

    elif nivelxgrado["subnivel"] == "RURAL":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedRU1"] == "NO":
            periodo = "PER1"
        elif p["closedRU2"] == "NO":
            periodo = "PER2"
        elif p["closedRU3"] == "NO":
            periodo = "PER3"
        elif p["closedRU4"] == "NO":
            periodo = "PER4"
        elif p["closedRU5"] == "NO":
            periodo = "PER5"
        else:
            periodo = "PERIODO CERRADO"
        print(f' periodo rural bachil: { periodo }')

    elif nivelxgrado["subnivel"] == "SEDEDOS":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedPR1"] == "NO":
            periodo = "PER1"
        elif p["closedPR2"] == "NO":
            periodo = "PER2"
        elif p["closedPR3"] == "NO":
            periodo = "PER3"
        elif p["closedPR4"] == "NO":
            periodo = "PER4"
        elif p["closedPR5"] == "NO":
            periodo = "PER5"
        else:
            periodo = "PERIODO CERRADO" #None
        print(f' periodo primaria bachil: { periodo }')        

    periodo = periodo
    ##hasta aqui

    # 3️⃣ Traer datos de notas
    cursor.execute("""
        SELECT *
        FROM notastxt
        WHERE TRIM(scodeemp) = %s
          AND codegrad = %s
          AND TRIM(codemate) = %s
          AND periodo = %s
          AND alectivo = %s
    """, (scodeemp, codegrad, codemate, periodo, alectivo))
    datanotas = cursor.fetchone()

    #se crea un diccionario para cargar las variables como tbox1label1 hasta tbox30label30
    # estas variables se cargaran en los textbox de la plantilla
    tbox = {}

    if datanotas:
        for i in range(1, 31):
            tbox[f"tbox{i}label{i}"] = datanotas.get(f"label{i}", "")
    else:
        for i in range(1, 31):
            tbox[f"tbox{i}label{i}"] = ""

    #se crea un diccionario para cargar las variables como tbox51valor1 hasta tbox80valor30
    # estas variables se cargaran en los textbox de la plantilla
    tval = {}

    if datanotas:
        for i in range(51, 81):
            raw_value = datanotas.get(f"valor{i - 50}", "")
            # convertir "0" en vacío
            if raw_value == "0" or raw_value is None:
                tval[f"tbox{i}valor{i - 50}"] = ""
            else:
                tval[f"tbox{i}valor{i - 50}"] = raw_value
    else:
        for i in range(51, 81):
            tval[f"tbox{i}valor{i - 50}"] = ""

    #carga los campos fijos
    #se crea un diccionario para cargar las variables como tbox1clos1 hasta tbox30clos30
    # estas variables se cargaran en los checkbox para fijar el valor del porcentaje de la nota de la plantilla
    tfija = {}

    if datanotas:
        for i in range(1, 31):
            tfija[f"tbox{i}fija{i}"] = datanotas.get(f"nfija{i}", "")
    else:
        for i in range(1, 31):
            tfija[f"tbox{i}fija{i}"] = ""

    #aqui se carga el diccionario para bloquear las casillas de notas
    tclo = {}
    if datanotas:
        for i in range(1, 31):
            tclo[f"tbox{i}clon{i}"] = datanotas.get(f"clo{i}", "")
    else:
        for i in range(1, 31):
            tclo[f"tbox{i}clon{i}"] = ""

    #hasta aqui

    tnota = {}

    if datanotas:
        for i in range(1, 31):
            tnota[f"tbox{i}nota{i}"] = datanotas.get(f"not{i}", "")
    else:
        for i in range(1, 31):
            tnota[f"tbox{i}nota{i}"] = ""

    # 4️⃣ Cerrar conexión
    cursor.close()
    conn.close()

    # 5️⃣ Renderizar plantilla con los datos
    return render_template(
        'onlyeditnotas.html',
        grado=grado,
        datanotas=datanotas,
        codemate=codemate,
        periodo=periodo,
        tbox=tbox,
        tval = tval,
        tfija=tfija,
        tclo=tclo,
        tnota=tnota,
        codeprof=codeprof,
        param_name=session.get("param_name"),
        token=session.get("token")
    )

@app.route("/guardar_onlyeditnotas", methods=["POST"])
def guardar_onlyeditnotas():
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    periodo = request.form.get("periodo")
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    #periodo = PERIODO_ACTUAL
    #alectivo = ALECTIVO_ACTUAL

    # 1️⃣ Conexión BD
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    accion = request.form.get("accion")
    prodid = request.form.get("prodid")
    codemate = request.form.get("codemate")
    codeprof = request.form.get("codeprof")


    #print(f'aqui prodid {prodid}')

    # 2️⃣ Obtener el codegrad desde materia
    cursor.execute("SELECT codegrad FROM materia WHERE codemate = %s", (codemate,))
    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        return "Error: materia no encontrada"

    codegrad = row["codegrad"]

    # 3️⃣ Capturar valores enviados por el formulario
    label1 = request.form.get("textbox1", "").strip()
    label2 = request.form.get("TextBox2", "").strip()
    label3 = request.form.get("TextBox3", "").strip()
    label4 = request.form.get("TextBox4", "").strip()
    label5 = request.form.get("TextBox5", "").strip()
    label6 = request.form.get("TextBox6", "").strip()
    label7 = request.form.get("TextBox7", "").strip()
    label8 = request.form.get("TextBox8", "").strip()
    label9 = request.form.get("TextBox9", "").strip()
    label10 = request.form.get("TextBox10", "").strip()
    label11 = request.form.get("TextBox11", "").strip()
    label12 = request.form.get("TextBox12", "").strip()
    label13 = request.form.get("TextBox13", "").strip()
    label14 = request.form.get("TextBox14", "").strip()
    label15 = request.form.get("TextBox15", "").strip()
    label16 = request.form.get("TextBox16", "").strip()
    label17 = request.form.get("TextBox17", "").strip()
    label18 = request.form.get("TextBox18", "").strip()
    label19 = request.form.get("TextBox19", "").strip()
    label20 = request.form.get("TextBox20", "").strip()
    label21 = request.form.get("TextBox21", "").strip()
    label22 = request.form.get("TextBox22", "").strip()
    label23 = request.form.get("TextBox23", "").strip()
    label24 = request.form.get("TextBox24", "").strip()
    label25 = request.form.get("TextBox25", "").strip()
    label26 = request.form.get("TextBox26", "").strip()
    label27 = request.form.get("TextBox27", "").strip()
    label28 = request.form.get("TextBox28", "").strip() ## 28 notas de cada asignatura

    valor1 = request.form.get("textbox51", "").strip()
    valor2 = request.form.get("TextBox52", "").strip()
    valor3 = request.form.get("TextBox53", "").strip()
    valor4 = request.form.get("TextBox54", "").strip()
    valor5 = request.form.get("TextBox55", "").strip()
    valor6 = request.form.get("TextBox56", "").strip()
    valor7 = request.form.get("TextBox57", "").strip()
    valor8 = request.form.get("TextBox58", "").strip()
    valor9 = request.form.get("TextBox59", "").strip()
    valor10 = request.form.get("TextBox60", "").strip()
    valor11 = request.form.get("TextBox61", "").strip()
    valor12 = request.form.get("TextBox62", "").strip()
    valor13 = request.form.get("TextBox63", "").strip()
    valor14 = request.form.get("TextBox64", "").strip()
    valor15 = request.form.get("TextBox65", "").strip()
    valor16 = request.form.get("TextBox66", "").strip()
    valor17 = request.form.get("TextBox67", "").strip()
    valor18 = request.form.get("TextBox68", "").strip()
    valor19 = request.form.get("TextBox69", "").strip()
    valor20 = request.form.get("TextBox70", "").strip()
    valor21 = request.form.get("TextBox71", "").strip()
    valor22 = request.form.get("TextBox72", "").strip()
    valor23 = request.form.get("TextBox73", "").strip()
    valor24 = request.form.get("TextBox74", "").strip()
    valor25 = request.form.get("TextBox75", "").strip()
    valor26 = request.form.get("TextBox76", "").strip()
    valor27 = request.form.get("TextBox77", "").strip()
    valor28 = request.form.get("TextBox78", "").strip()

    not1 = request.form.get("TextBox101", "").strip()
    not2 = request.form.get("TextBox102", "").strip()
    not3 = request.form.get("TextBox103", "").strip()
    not4 = request.form.get("TextBox104", "").strip()
    not5 = request.form.get("TextBox105", "").strip()
    not6 = request.form.get("TextBox106", "").strip()
    not7 = request.form.get("TextBox107", "").strip()
    not8 = request.form.get("TextBox108", "").strip()
    not9 = request.form.get("TextBox109", "").strip()
    not10 = request.form.get("TextBox110", "").strip()
    not11 = request.form.get("TextBox111", "").strip()
    not12 = request.form.get("TextBox112", "").strip()
    not13 = request.form.get("TextBox113", "").strip()
    not14 = request.form.get("TextBox114", "").strip()
    not15 = request.form.get("TextBox115", "").strip()
    not16 = request.form.get("TextBox116", "").strip()
    not17 = request.form.get("TextBox117", "").strip()
    not18 = request.form.get("TextBox118", "").strip()
    not19 = request.form.get("TextBox119", "").strip()
    not20 = request.form.get("TextBox120", "").strip()
    not21 = request.form.get("TextBox121", "").strip()
    not22 = request.form.get("TextBox122", "").strip()
    not23 = request.form.get("TextBox123", "").strip()
    not24 = request.form.get("TextBox124", "").strip()
    not25 = request.form.get("TextBox125", "").strip()
    not26 = request.form.get("TextBox126", "").strip()
    not27 = request.form.get("TextBox127", "").strip()
    not28 = request.form.get("TextBox128", "").strip()

    # el checkbox solo llega si está marcado
    nfija1 = "Y" if request.form.get("CheckBox1") == "1" else ""
    nfija2 = "Y" if request.form.get("CheckBox2") == "1" else ""
    nfija3 = "Y" if request.form.get("CheckBox3") == "1" else ""
    nfija4 = "Y" if request.form.get("CheckBox4") == "1" else ""
    nfija5 = "Y" if request.form.get("CheckBox5") == "1" else ""
    nfija6 = "Y" if request.form.get("CheckBox6") == "1" else ""
    nfija7 = "Y" if request.form.get("CheckBox7") == "1" else ""
    nfija8 = "Y" if request.form.get("CheckBox8") == "1" else ""
    nfija9 = "Y" if request.form.get("CheckBox9") == "1" else ""
    nfija10 = "Y" if request.form.get("CheckBox10") == "1" else ""
    nfija11 = "Y" if request.form.get("CheckBox11") == "1" else ""
    nfija12 = "Y" if request.form.get("CheckBox12") == "1" else ""
    nfija13 = "Y" if request.form.get("CheckBox13") == "1" else ""
    nfija14 = "Y" if request.form.get("CheckBox14") == "1" else ""
    nfija15 = "Y" if request.form.get("CheckBox15") == "1" else ""
    nfija16 = "Y" if request.form.get("CheckBox16") == "1" else ""
    nfija17 = "Y" if request.form.get("CheckBox17") == "1" else ""
    nfija18 = "Y" if request.form.get("CheckBox18") == "1" else ""
    nfija19 = "Y" if request.form.get("CheckBox19") == "1" else ""
    nfija20 = "Y" if request.form.get("CheckBox20") == "1" else ""
    nfija21 = "Y" if request.form.get("CheckBox21") == "1" else ""
    nfija22 = "Y" if request.form.get("CheckBox22") == "1" else ""
    nfija23 = "Y" if request.form.get("CheckBox23") == "1" else ""
    nfija24 = "Y" if request.form.get("CheckBox24") == "1" else ""
    nfija25 = "Y" if request.form.get("CheckBox25") == "1" else ""
    nfija26 = "Y" if request.form.get("CheckBox26") == "1" else ""
    nfija27 = "Y" if request.form.get("CheckBox27") == "1" else ""
    nfija28 = "Y" if request.form.get("CheckBox28") == "1" else ""

    # el checkbox de casilla fija solo llega si está marcado
    clo1 = "Y" if request.form.get("CheckBox51") == "1" else ""
    clo2 = "Y" if request.form.get("CheckBox52") == "1" else ""
    clo3 = "Y" if request.form.get("CheckBox53") == "1" else ""
    clo4 = "Y" if request.form.get("CheckBox54") == "1" else ""
    clo5 = "Y" if request.form.get("CheckBox55") == "1" else ""
    clo6 = "Y" if request.form.get("CheckBox56") == "1" else ""
    clo7 = "Y" if request.form.get("CheckBox57") == "1" else ""
    clo8 = "Y" if request.form.get("CheckBox58") == "1" else ""
    clo9 = "Y" if request.form.get("CheckBox59") == "1" else ""
    clo10 = "Y" if request.form.get("CheckBox60") == "1" else ""
    clo11 = "Y" if request.form.get("CheckBox61") == "1" else ""
    clo12 = "Y" if request.form.get("CheckBox62") == "1" else ""
    clo13 = "Y" if request.form.get("CheckBox63") == "1" else ""
    clo14 = "Y" if request.form.get("CheckBox64") == "1" else ""
    clo15 = "Y" if request.form.get("CheckBox65") == "1" else ""
    clo16 = "Y" if request.form.get("CheckBox66") == "1" else ""
    clo17 = "Y" if request.form.get("CheckBox67") == "1" else ""
    clo18 = "Y" if request.form.get("CheckBox68") == "1" else ""
    clo19 = "Y" if request.form.get("CheckBox69") == "1" else ""
    clo20 = "Y" if request.form.get("CheckBox70") == "1" else ""
    clo21 = "Y" if request.form.get("CheckBox71") == "1" else ""
    clo22 = "Y" if request.form.get("CheckBox72") == "1" else ""
    clo23 = "Y" if request.form.get("CheckBox73") == "1" else ""
    clo24 = "Y" if request.form.get("CheckBox74") == "1" else ""
    clo25 = "Y" if request.form.get("CheckBox75") == "1" else ""
    clo26 = "Y" if request.form.get("CheckBox76") == "1" else ""
    clo27 = "Y" if request.form.get("CheckBox77") == "1" else ""
    clo28 = "Y" if request.form.get("CheckBox78") == "1" else ""

    #print(f'aqui MMMMMMMMMMMMMM label1: {label1}')
    #print(f'aqui MMMMMMMMMMMMMM label2: {label2}')

    # 4️⃣ Verificar si ya existe el registro
    cursor.execute("""
        SELECT * FROM notastxt
        WHERE prodid = %s
          
    """, (prodid,))

    existe = cursor.fetchone()

    # 5️⃣ INSERT si no existe
    if not existe:
        cursor.execute("""
            INSERT INTO notastxt (scodeemp, codegrad, codemate, periodo, alectivo,
                label1,label2, label3, label4, label5, label6, label7, label8, label9, label10, label11, label12, label13, label14, label15, label16, label17, label18, label19, label20, label21, label22, label23, label24, label25, label26, label27, label28, 
                nfija1,nfija2, nfija3, nfija4, nfija5, nfija6, nfija7, nfija8, nfija9, nfija10, nfija11, nfija12, nfija13, nfija14, nfija15, nfija16, nfija17, nfija18, nfija19, nfija20, nfija21, nfija22, nfija23, nfija24, nfija25, nfija26, nfija27, nfija28, 
                valor1,valor2, valor3, valor4, valor5, valor6, valor7, valor8, valor9, valor10, valor11, valor12, valor13, valor14, valor15, valor16, valor17, valor18, valor19, valor20, valor21, valor22, valor23, valor24, valor25, valor26, valor27, valor28, 
                clo1,clo2,clo3,clo4,clo5,clo6,clo7,clo8,clo9,clo10,clo11,clo12,clo13,clo14,clo15,clo16,clo17,clo18,clo19,clo20,clo21,clo22,clo23,clo24,clo25,clo26,clo27,clo28,
                not1, not2, not3, not4, not5, not6, not7, not8, not9, not10, not11, not12, not13, not14, not15, not16, not17, not18, not19, not20, not21, not22, not23, not24, not25, not26, not27, not28)
            VALUES (%s, %s, %s, %s, %s, 
                %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, 
                %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, 
                %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s,
                %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, 
                %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s)
        """, (scodeemp, codegrad, codemate, periodo, alectivo,
              label1,label2, label3, label4, label5, label6, label7, label8, label9, label10, label11, label12, label13, label14, label15, label16, label17, label18, label19, label20, label21, label22, label23, label24, label25, label26, label27, label28, 
              nfija1,nfija2, nfija3, nfija4, nfija5, nfija6, nfija7, nfija8, nfija9, nfija10, nfija11, nfija12, nfija13, nfija14, nfija15, nfija16, nfija17, nfija18, nfija19, nfija20, nfija21, nfija22, nfija23, nfija24, nfija25, nfija26, nfija27, nfija28, 
              valor1,valor2, valor3, valor4, valor5, valor6, valor7, valor8, valor9, valor10, valor11, valor12, valor13, valor14, valor15, valor16, valor17, valor18, valor19, valor20, valor21, valor22, valor23, valor24, valor25, valor26, valor27, valor28, 
              clo1,clo2,clo3,clo4,clo5,clo6,clo7,clo8,clo9,clo10,clo11,clo12,clo13,clo14,clo15,clo16,clo17,clo18,clo19,clo20,clo21,clo22,clo23,clo24,clo25,clo26,clo27,clo28,
              not1,not2, not3, not4, not5, not6, not7, not8, not9, not10, not11, not12, not13, not14, not15, not16, not17, not18, not19, not20, not21, not22, not23, not24, not25, not26, not27, not28))
    else:
        # 6️⃣ UPDATE si ya existe
        cursor.execute("""
            UPDATE notastxt
            SET label1 = %s, label2 = %s, label3 = %s, label4 = %s, label5 = %s, label6 = %s, label7 = %s, label8 = %s, label9 = %s, label10 = %s, label11 = %s, label12 = %s, label13 = %s, label14 = %s, label15 = %s, label16 = %s, label17 = %s, label18 = %s, label19 = %s, label20 = %s, label21 = %s, label22 = %s, label23 = %s, label24 = %s, label25 = %s, label26 = %s, label27 = %s, label28 = %s,
                nfija1 = %s, nfija2 = %s, nfija3 = %s, nfija4 = %s, nfija5 = %s, nfija6 = %s, nfija7 = %s, nfija8 = %s, nfija9 = %s, nfija10 = %s, nfija11 = %s, nfija12 = %s, nfija13 = %s, nfija14 = %s, nfija15 = %s, nfija16 = %s, nfija17 = %s, nfija18 = %s, nfija19 = %s, nfija20 = %s, nfija21 = %s, nfija22 = %s, nfija23 = %s, nfija24 = %s, nfija25 = %s, nfija26 = %s, nfija27 = %s, nfija28 = %s,
                valor1 = %s, valor2 = %s, valor3 = %s, valor4 = %s, valor5 = %s, valor6 = %s, valor7 = %s, valor8 = %s, valor9 = %s, valor10 = %s, valor11 = %s, valor12 = %s, valor13 = %s, valor14 = %s, valor15 = %s, valor16 = %s, valor17 = %s, valor18 = %s, valor19 = %s, valor20 = %s, valor21 = %s, valor22 = %s, valor23 = %s, valor24 = %s, valor25 = %s, valor26 = %s, valor27 = %s, valor28 = %s,
                clo1 = %s,clo2 = %s,clo3 = %s,clo4 = %s,clo5 = %s,clo6 = %s,clo7 = %s,clo8 = %s,clo9 = %s,clo10 = %s,clo11 = %s,clo12 = %s,clo13 = %s,clo14 = %s,clo15 = %s,clo16 = %s,clo17 = %s,clo18 = %s,clo19 = %s,clo20 = %s,clo21 = %s,clo22 = %s,clo23 = %s,clo24 = %s,clo25 = %s,clo26 = %s,clo27 = %s,clo28 = %s,
                not1 = %s, not2 = %s, not3 = %s, not4 = %s, not5 = %s, not6 = %s, not7 = %s, not8 = %s, not9 = %s, not10 = %s, not11 = %s, not12 = %s, not13 = %s, not14 = %s, not15 = %s, not16 = %s, not17 = %s, not18 = %s, not19 = %s, not20 = %s, not21 = %s, not22 = %s, not23 = %s, not24 = %s, not25 = %s, not26 = %s, not27 = %s, not28 = %s 
            WHERE prodid = %s
              
        """, (label1, label2, label3, label4, label5, label6, label7, label8, label9, label10, label11, label12, label13, label14, label15, label16, label17, label18, label19, label20, label21, label22, label23, label24, label25, label26, label27, label28, 
              nfija1, nfija2, nfija3, nfija4, nfija5, nfija6, nfija7, nfija8, nfija9, nfija10, nfija11, nfija12, nfija13, nfija14, nfija15, nfija16, nfija17, nfija18, nfija19, nfija20, nfija21, nfija22, nfija23, nfija24, nfija25, nfija26, nfija27, nfija28, 
              valor1, valor2, valor3, valor4, valor5, valor6, valor7, valor8, valor9, valor10, valor11, valor12, valor13, valor14, valor15, valor16, valor17, valor18, valor19, valor20, valor21, valor22, valor23, valor24, valor25, valor26, valor27, valor28,
              clo1,clo2,clo3,clo4,clo5,clo6,clo7,clo8,clo9,clo10,clo11,clo12,clo13,clo14,clo15,clo16,clo17,clo18,clo19,clo20,clo21,clo22,clo23,clo24,clo25,clo26,clo27,clo28, 
              not1, not2, not3, not4, not5, not6, not7, not8, not9, not10, not11, not12, not13, not14, not15, not16, not17, not18, not19, not20, not21, not22, not23, not24, not25, not26, not27, not28,
              prodid ))

    conn.commit()

    cursor.close()
    conn.close()
    # PENDIENTE CODIGO DE RECUPERACION, casillas 29 y 30, si se activan, esa nota es la que pasa a definitiva
    # 7️⃣ Redirigir de vuelta a la página
    return redirect(url_for("onlyeditnotas", codemate=codemate, codeprof=codeprof, periodo=periodo))

@app.route("/onlylistxalumn2DIR/<codegrad>")
def onlylistxalumn2DIR(codegrad):
    
    alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")

    #periodo = request.args.get("periodo") 
    #periodo = "PER1"
    scodeemp = current_app.config.get("SCODEEMP")

    #scodeemp = SCODEEMP
    #periodo = PERIODO_ACTUAL
    #alectivo = ALECTIVO_ACTUAL

    #print(f'periodo actual desde profe: {periodo}')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    #desde aqui se calcula el periodo 
    #codegrad = grado["codegrad"]
    #scodeemp = grado["scodeemp"]

    # 2️⃣ carga el subnivel por el grado
    cursor.execute("""
        SELECT * from
            colgrados
            where codegrad = %s
                   
    """, (codegrad,))
    cargogrado = cursor.fetchone()

    cursor.execute("SELECT * FROM allparam LIMIT 1")
    p = cursor.fetchone()
    
    alectivo = p["alectivo"]
    #scodeemp = p["scodeemp"]
    nivelesco = cargogrado["nivelesco"]
    print(f' alectivo para todos: { alectivo }')
    print(f' scodeemp para todos: { scodeemp }')
    #print(f' nivelesco por asignatura: { nivelesco } { codemate }')

    if cargogrado and cargogrado["subnivel"] == "DIURNA":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        #hace otra consulta
    
        if not p:
            return {}

        if p["closedp1"] == "NO":
            periodo = "PER1"
        elif p["closedp2"] == "NO":
            periodo = "PER2"
        elif p["closedp3"] == "NO":
            periodo = "PER3"
        elif p["closedp4"] == "NO":
            periodo = "PER4"
        elif p["closedp5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None

        print(f' periodo diurno bachil: { periodo }')
    elif cargogrado["subnivel"] == "NOCTUR":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedCI1"] == "NO":
            periodo = "PER1"
        elif p["closedCI2"] == "NO":
            periodo = "PER2"
        elif p["closedCI3"] == "NO":
            periodo = "PER3"
        elif p["closedCI4"] == "NO":
            periodo = "PER4"
        elif p["closedCI5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo nocturno bachil: { periodo }')

    elif cargogrado["subnivel"] == "RURAL":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedRU1"] == "NO":
            periodo = "PER1"
        elif p["closedRU2"] == "NO":
            periodo = "PER2"
        elif p["closedRU3"] == "NO":
            periodo = "PER3"
        elif p["closedRU4"] == "NO":
            periodo = "PER4"
        elif p["closedRU5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo rural bachil: { periodo }')

    elif cargogrado["subnivel"] == "SEDEDOS":
        #print(f'este es el codeprof, aqui  hay que cargar el periodo: {codeprof}')
        if p["closedPR1"] == "NO":
            periodo = "PER1"
        elif p["closedPR2"] == "NO":
            periodo = "PER2"
        elif p["closedPR3"] == "NO":
            periodo = "PER3"
        elif p["closedPR4"] == "NO":
            periodo = "PER4"
        elif p["closedPR5"] == "NO":
            periodo = "PER5"
        else:
            periodo = None
        print(f' periodo primaria bachil: { periodo }')        

    periodo = periodo
    ##hasta aqui
    #hasta aqui


    #carga el grado especifico del cual es director el profesor
    cursor.execute("""
        SELECT colgrados.*, CONCAT(name, ' :: ', codeinte) as gradox 
        FROM colgrados 
        where trim(scodeemp) = %s AND codegrad = %s
    """, (scodeemp, codegrad))
    dirgrado = cursor.fetchone()

    #carga los estudiantes de un grado especifico
    cursor.execute("""
        SELECT estudents.*, CONCAT(lastn, ' ', lastn2, ', ', names ) as totname 
        FROM estudents 
        where codegrad = %s and trim(scodeemp) = %s and status = 'MATRICUL' and estudents.alectivo = %s 
        order by totname
    """, (codegrad, scodeemp, alectivo))
    estugrado = cursor.fetchall()


    cursor.close()
    conn.close()
    #return render_template("onlylistxalum2DIR.html", dirgrado=dirgrado, periodo=periodo, estugrado=estugrado)
    return render_template("onlylistxalum2DIR.html", dirgrado=dirgrado, estugrado=estugrado, periodo=periodo)

@app.route("/get_notas_estudiante/<codegrad>/<codeestu>")
def get_notas_estudiante(codegrad, codeestu):
    #alectivo = current_app.config.get("ALECTIVO_ACTUAL")
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    scodeemp = current_app.config.get("SCODEEMP")
    #periodo = data.get("periodo")
    periodo = "PER1"

    #print(f'el periodo de notas: {periodo}')
    #scodeemp = SCODEEMP
    #periodo = PERIODO_ACTUAL

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

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
    """, (codegrad, codeestu, scodeemp, periodo))

    notas = cursor.fetchall()

    #carga la grid de notas por area
    cursor.execute("""
    SELECT areasxmate.nombre, caliarea.* 
    from caliarea,areasxmate 
    where areasxmate.codearea = caliarea.codearea and caliarea.codegrad = %s and caliarea.codeestu = %s and trim(caliarea.scodeemp) = %s
    """, (codegrad, codeestu, scodeemp))
    notasxarea = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "notas": notas,
        "notasxarea": notasxarea
    })

@app.route("/consolidado_notas_estudiante")
def consolidado_notas_estudiante():

    codegrad = request.args.get("codegrad")
    codeestu = request.args.get("codeestu")

    print(f'este codegrad viene de main: {codegrad}')
    print(f'este codeestu viene de main: {codeestu}')

    periodo = "PER3"
    #periodo = current_app.config.get("PERIODO_ACTUAL")
    

    return render_template(
        "consolidado_notas_estudiante.html",
        codegrad=codegrad,
        codeestu=codeestu,
        periodo=periodo
    )

def hello():
    return "<h1>Hola mundo</h1>"

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

