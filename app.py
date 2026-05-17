from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from database.conexion import conectar
import base64
from datetime import datetime

app = Flask(__name__)
CARPETA_FOTOS = 'static/fotos'

app.config['CARPETA_FOTOS'] = CARPETA_FOTOS
@app.route('/')
def inicio():

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""

    SELECT

    personas.id_persona,
    personas.carnet,
    personas.nombres,
    personas.apellidos,
    personas.telefono,
    personas.correo,
    personas.fotografia,

    tipos_persona.nombre,

    carreras.nombre_carrera,

    secciones.seccion

    FROM personas

    INNER JOIN tipos_persona
    ON personas.id_tipo = tipos_persona.id_tipo

    INNER JOIN carreras
    ON personas.id_carrera = carreras.id_carrera

    INNER JOIN secciones
    ON personas.id_seccion = secciones.id_seccion

    """)

    personas = cursor.fetchall()

    cursor.execute("SELECT * FROM tipos_persona")
    tipos = cursor.fetchall()

    cursor.execute("SELECT * FROM carreras")
    carreras = cursor.fetchall()

    cursor.execute("SELECT * FROM secciones")
    secciones = cursor.fetchall()

    conexion.close()

    mensaje = request.args.get('mensaje')

    return render_template(
        'index.html',
        personas=personas,
        tipos=tipos,
        carreras=carreras,
        secciones=secciones,
        mensaje=mensaje
    )
@app.route('/guardar', methods=['POST'])
def guardar():

    carnet = request.form['carnet']
    nombres = request.form['nombres']
    apellidos = request.form['apellidos']
    telefono = request.form['telefono']
    correo = request.form['correo']
    foto_capturada = request.form['foto_capturada']

    id_tipo = request.form['id_tipo']
    id_carrera = request.form['id_carrera']
    id_seccion = request.form['id_seccion']

    imagen_base64 = foto_capturada.split(",")[1]
    imagen_bytes = base64.b64decode(imagen_base64)

    nombre_foto = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"

    ruta_foto = os.path.join(
        app.config['CARPETA_FOTOS'],
        nombre_foto
    )

    with open(ruta_foto, "wb") as archivo:
        archivo.write(imagen_bytes)

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO personas
    (
        carnet,
        nombres,
        apellidos,
        telefono,
        correo,
        fotografia,
        id_tipo,
        id_carrera,
        id_seccion
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        carnet,
        nombres,
        apellidos,
        telefono,
        correo,
        ruta_foto,
        id_tipo,
        id_carrera,
        id_seccion
    )

    cursor.execute(sql, valores)
    conexion.commit()
    conexion.close()

    return redirect(
        url_for(
            'inicio',
            mensaje='Persona registrada correctamente'
        )
    )


if __name__ == '__main__':
    app.run(debug=True)