from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection   # ajusta el import según tu proyecto
from datetime import date
from datetime import datetime

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

def chckNOTASxMatriinsCRITA(cursor, codeestu, codegrad, codemate):
    # lógica aquí
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    
    #periodo = PERIODO_ACTUAL
    alectivo = ALECTIVO_ACTUAL

    cursor.execute("""
        SELECT * FROM calinotas 
            where codeestu = %s 
            and codegrad = %s 
            and codemate = %s 
            and alectivo = %s 
            and scodeemp = %s
    """, (codeestu, codegrad, codemate, alectivo, scodeemp1))
    chcknotasxmatrinscrita = cursor.fetchall()             
    #cursor.close()
    #conn.close()

    return chcknotasxmatrinscrita

def savematri(cursor, codeestu, codegrad, codemate,keymate):
    # lógica aquí
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    periodo = PERIODO_ACTUAL
    alectivo = ALECTIVO_ACTUAL

    fechmatri = date.today()
    peson1 = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    peson2 = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    peson3 = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    peson4 = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    peson5 = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    sql_insert = """
        INSERT INTO calimate (codeestu, codegrad, codemate,alectivo,scodeemp,fechmatri,keymate, peson1,peson2,peson3,peson4,peson5)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)
    """
    params = (codeestu, codegrad, codemate, alectivo, scodeemp1,fechmatri,keymate, peson1,peson2,peson3,peson4,peson5)
    cursor.execute(sql_insert, params)
    #conn.commit()

    #cursor.close()
    #conn.close()

    return True

def savenotasxmatri(cursor, codeestu, codegrad, codemate):
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")


    scodeemp1 = SCODEEMP

    alectivo = ALECTIVO_ACTUAL

    sql_insert = """
        INSERT INTO calinotas (codeestu, codegrad, codemate, alectivo, scodeemp, periodo) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    for i in range(1, 6):  # 1 a 5
        periodo = f"PER{i}"

        params = (codeestu, codegrad, codemate, alectivo, scodeemp1, periodo)
        cursor.execute(sql_insert, params)

    return True

def savepuntajesxmatri(cursor,codeestu, codegrad, codemate):
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")


    scodeemp1 = SCODEEMP  # o como lo estés manejando
    periodo = PERIODO_ACTUAL
    alectivo = ALECTIVO_ACTUAL

    sql_insert = """
        INSERT INTO estustat (codeestu, codegrad, codemate,alectivo,scodeemp) 
        values ( %s, %s, %s, %s, %s)
    """
    params = (codeestu, codegrad, codemate, alectivo, scodeemp1)                                                                           
    cursor.execute(sql_insert, params)
    #conn.commit()

    #cursor.close()
    #conn.close()

    return True

def savenotasxarea(cursor,codeestu, codegrad, codemate, codearea, nombret):
    #conn = get_db_connection()
    #cursor = conn.cursor(dictionary=True)
    ALECTIVO_ACTUAL = current_app.config.get("ALECTIVO_ACTUAL")
    PERIODO_ACTUAL = current_app.config.get("PERIODO_ACTUAL")
    SCODEEMP = current_app.config.get("SCODEEMP")

    scodeemp1 = SCODEEMP  # o como lo estés manejando
    periodo = PERIODO_ACTUAL
    alectivo = ALECTIVO_ACTUAL

    sql_insert = """
        insert INTO caliarea (codeestu, codegrad, codemate, alectivo,scodeemp,nombret,codearea) 
        values ( %s, %s, %s, %s, %s, %s, %s)

    """
    params = (codeestu, codegrad, codemate, alectivo, scodeemp1,nombret,codearea)                                                                           
    cursor.execute(sql_insert, params)
    #conn.commit()

    #cursor.close()
    #conn.close()

    return True