import mysql.connector

def conectar():

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Carlos@123",
        database="db_biometrico"
    )

    return conexion