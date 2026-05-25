from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from database.conexion import conectar
import base64
import cv2
import qrcode
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)
CARPETA_FOTOS = 'static/fotos'

app.config['CARPETA_FOTOS'] = CARPETA_FOTOS
detector_facial = cv2.CascadeClassifier(
    'modelo/haarcascade_frontalface_default.xml'
)
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

    sedes.nombre_sede

    FROM personas

    INNER JOIN tipos_persona
    ON personas.id_tipo = tipos_persona.id_tipo

    INNER JOIN carreras
    ON personas.id_carrera = carreras.id_carrera

    INNER JOIN sedes
    ON personas.id_sede = sedes.id_sede

    """)

    personas = cursor.fetchall()

    cursor.execute("SELECT * FROM tipos_persona")
    tipos = cursor.fetchall()

    cursor.execute("SELECT * FROM carreras")
    carreras = cursor.fetchall()

    cursor.execute("SELECT * FROM sedes")
    sedes = cursor.fetchall()



    conexion.close()

    mensaje = request.args.get('mensaje')

    return render_template(
        'index.html',
        personas=personas,
        tipos=tipos,
        carreras=carreras,
        sedes=sedes,
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
    id_sede = request.form['id_sede']
   

    imagen_base64 = foto_capturada.split(",")[1]

    imagen_bytes = base64.b64decode(imagen_base64)

    nombre_foto = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    ) + ".png"

    ruta_foto = os.path.join(
        app.config['CARPETA_FOTOS'],
        nombre_foto
    )

    with open(ruta_foto, "wb") as archivo:
        archivo.write(imagen_bytes)

    imagen = cv2.imread(ruta_foto)

    gris = cv2.cvtColor(
        imagen,
        cv2.COLOR_BGR2GRAY
    )

    rostros = detector_facial.detectMultiScale(
    gris,
    scaleFactor=1.3,
    minNeighbors=8,
    minSize=(100, 100)
)

    if len(rostros) == 0:

        os.remove(ruta_foto)

        return redirect(
            url_for(
                'inicio',
                mensaje='No se detectó un rostro'
            )
        )

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
        id_sede
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
    id_sede
)

    cursor.execute(sql, valores)
    
    cursor.execute(
        "SELECT nombre_carrera FROM carreras WHERE id_carrera = %s",
        (id_carrera,)
    )
    nombre_carrera = cursor.fetchone()[0]

    cursor.execute(
            "SELECT nombre FROM tipos_persona WHERE id_tipo = %s",
        (id_tipo,)
        )

    nombre_tipo = cursor.fetchone()[0]

    conexion.commit()
    qr = qrcode.make(carnet)

    ruta_qr = os.path.join(
    'static/qr',
    carnet + '.png'
)

    qr.save(ruta_qr)
    pdf = FPDF(
    orientation='L',
    unit='mm',
    format=('A4')
)

    pdf.add_page()

    pdf.image(
    'static/logo/logo_umg.png',
    x=3,
    y=3,
    w=20
)

    pdf.set_font(
    'Arial',
    'B',
    10
)

    pdf.set_xy(25, 5)

    pdf.cell(
    50,
    5,
    'UNIVERSIDAD MARIANO GALVEZ'
)

    pdf.set_font(
    'Arial',
    '',
    8
)


    pdf.image(
    ruta_foto,
    x=5,
    y=28,
    w=25,
    h=30
)

    pdf.set_font(
    'Arial',
    'B',
    9
)
    pdf.set_xy(35, 20)
    pdf.cell(
    40,
    5,
    '2026'
    )
    pdf.set_xy(35, 25)

    pdf.cell(
    40,
    5,
    f'{nombres} {apellidos}'
)

    pdf.set_font(
    'Arial',
    '',
    8
)

    pdf.set_xy(35, 32)

    pdf.cell(
    40,
    5,
    f'Carnet: {carnet}'
)

    pdf.image(
    ruta_qr,
    x=65,
    y=22,
    w=18
)

    
    pdf.set_xy(35, 42)

    pdf.cell(
        40,
        5,
        f'Tipo: {nombre_tipo}'
    )
    pdf.set_xy(35, 37)

    pdf.cell(
        40,
        5,
        f'Carrera: {nombre_carrera}'
    )

    ruta_pdf = os.path.join(
        'static/carnets',
        carnet + '.pdf'
    )

    pdf.output(ruta_pdf)

    conexion.close()

    return redirect(
        url_for(
            'inicio',
            mensaje='Persona registrada correctamente'
        )
    )
    url_for(
            'inicio',
            mensaje='Persona registrada correctamente'
        )

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
        id_sede
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
        id_sede
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
    app.run(host="0.0.0.0", port=5000, debug=False)
