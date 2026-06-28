from db import get_db_connection
#ALECTIVO_ACTUAL = "2020"
#PERIODO_ACTUAL  = "PER1"
#SCODEEMP        = "31"
#NIVELESCO       = "BACHIL"

# Variables globales (se llenarán abajo)
#ALECTIVO_ACTUAL = None
#PERIODO_ACTUAL = None
#SCODEEMP = "31"
#NIVELESCO = "BACHIL"


#def cargar_configuracion():
#    global ALECTIVO_ACTUAL, PERIODO_ACTUAL, SCODEEMP, NIVELESCO

#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)

#    cursor.execute("SELECT * FROM allparam LIMIT 1")
#    p = cursor.fetchone()

#    if not p:
#        return

#    ALECTIVO_ACTUAL = p["alectivo"]
#    #SCODEEMP = p.get("scodeemp")
#    #NIVELESCO = p.get("nivelesco")

#    if p["closedp1"] == "NO":
#        PERIODO_ACTUAL = "PER1"
#    elif p["closedp2"] == "NO":
#        PERIODO_ACTUAL = "PER2"
#    elif p["closedp3"] == "NO":
#        PERIODO_ACTUAL = "PER3"
#    elif p["closedp4"] == "NO":
#        PERIODO_ACTUAL = "PER4"
#    elif p["closedp5"] == "NO":
#        PERIODO_ACTUAL = "PER5"
#    else:
#        PERIODO_ACTUAL = None

#    cursor.close()
#    conn.close()


# 🔥 IMPORTANTE: se ejecuta automáticamente al importar
#cargar_configuracion()

#from flask import g

#class ConfigVar:
#    def __init__(self, key):
#        self.key = key

#    def __str__(self):
#        return str(self.get())

#    def __repr__(self):
#        return str(self.get())

#    def __eq__(self, other):
#        return self.get() == other

#    def __ne__(self, other):
#        return self.get() != other

#    def get(self):
#        try:
#            return g.config.get(self.key)
#        except:
#            return None  # fallback si no hay request


# 🔥 Variables "globales dinámicas"
#ALECTIVO_ACTUAL = ConfigVar("ALECTIVO_ACTUAL")
#PERIODO_ACTUAL = ConfigVar("PERIODO_ACTUAL")
#SCODEEMP = ConfigVar("SCODEEMP")
#NIVELESCO = ConfigVar("NIVELESCO")

#SCODEEMP        = "31"
#NIVELESCO       = "BACHIL"
