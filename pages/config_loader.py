from db import get_db_connection

def cargar_parametros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM allparam LIMIT 1")
    p = cursor.fetchone()

    cursor.close()
    conn.close()

    if not p:
        return {}

    #if p["closedp1"] == "NO":
    #    periodo = "PER1"
    #elif p["closedp2"] == "NO":
    #    periodo = "PER2"
    #elif p["closedp3"] == "NO":
    #    periodo = "PER3"
    #elif p["closedp4"] == "NO":
    #    periodo = "PER4"
    #elif p["closedp5"] == "NO":
    #    periodo = "PER5"
    #else:
    #    periodo = None

    #print(f'verificando cargar parametros: {periodo}')
    return {
        "ALECTIVO_ACTUAL": p["alectivo"],
        #"PERIODO_ACTUAL": periodo,
        "SCODEEMP": p["scodeemp"],
        "NIVELESCO": "BACHIL"
    }

def init_config(app):
    params = cargar_parametros()

    app.config["ALECTIVO_ACTUAL"] = params.get("ALECTIVO_ACTUAL")
    #app.config["PERIODO_ACTUAL"] = params.get("PERIODO_ACTUAL")
    app.config["SCODEEMP"] = params.get("SCODEEMP")
    app.config["NIVELESCO"] = params.get("NIVELESCO")

def reload_config(app):
    params = cargar_parametros()

    app.config["ALECTIVO_ACTUAL"] = params.get("ALECTIVO_ACTUAL")
    #app.config["PERIODO_ACTUAL"] = params.get("PERIODO_ACTUAL")
    app.config["SCODEEMP"] = params.get("SCODEEMP")
    app.config["NIVELESCO"] = params.get("NIVELESCO")
    pp = params.get("PERIODO_ACTUAL")
    print(f'verificando reload parametros: {pp}')