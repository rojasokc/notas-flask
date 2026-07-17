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
        "NIVELESCO": "BACHIL",
        # Porcentajes de los períodos
        "PORC_PER1": float(p["valporper1"] or 0) / 100,
        "PORC_PER2": float(p["valporper2"] or 0) / 100,
        "PORC_PER3": float(p["valporper3"] or 0) / 100,
        "PORC_PER4": float(p["valporper4"] or 0) / 100,
        "PORC_PER5": float(p["valporper5"] or 0) / 100,

    }

def init_config(app):
    params = cargar_parametros()

    app.config["ALECTIVO_ACTUAL"] = params.get("ALECTIVO_ACTUAL")
    #app.config["PERIODO_ACTUAL"] = params.get("PERIODO_ACTUAL")
    app.config["SCODEEMP"] = params.get("SCODEEMP")
    app.config["NIVELESCO"] = params.get("NIVELESCO")
    app.config["VALPORPER1"] = params.get("PORC_PER1")
    app.config["VALPORPER2"] = params.get("PORC_PER2")
    app.config["VALPORPER3"] = params.get("PORC_PER3")
    app.config["VALPORPER4"] = params.get("PORC_PER4")
    app.config["VALPORPER5"] = params.get("PORC_PER5")

def reload_config(app):
    params = cargar_parametros()

    app.config["ALECTIVO_ACTUAL"] = params.get("ALECTIVO_ACTUAL")
    #app.config["PERIODO_ACTUAL"] = params.get("PERIODO_ACTUAL")
    app.config["SCODEEMP"] = params.get("SCODEEMP")
    app.config["NIVELESCO"] = params.get("NIVELESCO")
    pp = params.get("PERIODO_ACTUAL")
    app.config["VALPORPER1"] = params.get("PORC_PER1")
    app.config["VALPORPER2"] = params.get("PORC_PER2")
    app.config["VALPORPER3"] = params.get("PORC_PER3")
    app.config["VALPORPER4"] = params.get("PORC_PER4")
    app.config["VALPORPER5"] = params.get("PORC_PER5")
    #print(f'verificando reload parametros: {pp}')