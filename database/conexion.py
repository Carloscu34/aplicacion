import mysql.connector

def conectar():

    conexion = mysql.connector.connect(
        host="biometrico-mysql.hpr-0f2570c4.svc",
	port=3306,
        user="hpr-0f2570c4-biometrico",
        password="QrIfHB6yDdvN2XaB",
        database="hpr-0f2570c4-biometrico"
    )

    return conexion
