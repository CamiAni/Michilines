from flask import Flask, jsonify, request, abort
import pymysql
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Configuración de la base de datos
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3307)),
    "user": os.getenv("DB_USER", "powpatrol"),
    "password": os.getenv("DB_PASSWORD", "Powpatrol1."),
    "database": os.getenv("DB_NAME", "pawbase")
}

def get_db_connection():
    return pymysql.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

# Initialize Flask app
app = Flask(__name__)

# --- Rutas para Mascotas ---
@app.route('/mascotas', methods=['GET'])
def obtener_mascotas():
    query = "SELECT * FROM mascotas;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            resultado = cursor.fetchall()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener mascotas: {str(e)}'}), 500
    finally:
        connection.close()

@app.route('/mascotas', methods=['POST'])
def agregar_mascota():
    nueva_mascota = request.get_json()
    query = """INSERT INTO mascotas (id_usuarios, nombre, tipo, estado, descripcion, zona, comentario)
               VALUES (%s, %s, %s, %s, %s, %s, %s);"""
    values = (
        nueva_mascota['id_usuarios'], nueva_mascota['nombre'], nueva_mascota['tipo'],
        nueva_mascota['estado'], nueva_mascota['descripcion'], nueva_mascota['zona'],
        nueva_mascota.get('comentario', None)
    )
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            connection.commit()
        return jsonify({'message': 'Mascota agregada exitosamente'}), 201
    except Exception as e:
        return jsonify({'message': f'Error al agregar mascota: {str(e)}'}), 500
    finally:
        connection.close()

@app.route('/mascotas/<int:id>', methods=['PATCH'])
def modificar_mascota(id):
    modificar_mascota = request.get_json()
    campos = ', '.join([f"{key} = %s" for key in modificar_mascota])
    valores = tuple(modificar_mascota.values())
    query = f"UPDATE mascotas SET {campos} WHERE id = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, valores + (id,))
            connection.commit()
        return jsonify({'message': 'Mascota modificada exitosamente'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al modificar mascota: {str(e)}'}), 500
    finally:
        connection.close()

@app.route('/mascotas/<int:id>', methods=['DELETE'])
def borrar_mascota(id):
    query = "DELETE FROM mascotas WHERE id = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (id,))
            if cursor.rowcount == 0:
                abort(404, description="Mascota no encontrada")
            connection.commit()
        return jsonify({'message': 'Mascota eliminada exitosamente'}), 200
    except Exception as e:
        abort(500, description=f'Error al eliminar mascota: {str(e)}')
    finally:
        connection.close()

# --- Rutas para Comentarios ---
@app.route('/comentarios', methods=['POST'])
def agregar_comentario():
    nuevo_comentario = request.get_json()
    query = """INSERT INTO comentarios (id_mascota, id_usuario, texto)
               VALUES (%s, %s, %s);"""
    values = (
        nuevo_comentario['id_mascota'], nuevo_comentario['id_usuario'], nuevo_comentario['texto']
    )
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            connection.commit()
        return jsonify({'message': 'Comentario agregado exitosamente'}), 201
    except Exception as e:
        return jsonify({'message': f'Error al agregar comentario: {str(e)}'}), 500
    finally:
        connection.close()

@app.route('/comentarios/<int:id>', methods=['DELETE'])
def borrar_comentario(id):
    query = "DELETE FROM comentarios WHERE id = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (id,))
            if cursor.rowcount == 0:
                abort(404, description="Comentario no encontrado")
            connection.commit()
        return jsonify({'message': 'Comentario eliminado exitosamente'}), 200
    except Exception as e:
        abort(500, description=f'Error al eliminar comentario: {str(e)}')
    finally:
        connection.close()

# --- Rutas para Usuarios ---
@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    campos_requeridos = ['nombre', 'apellido', 'correo', 'contraseña']
    
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"message": "Faltan datos obligatorios"}), 400

    hashed_password = generate_password_hash(data['contraseña'])
    query = """
        INSERT INTO usuarios (nombre, apellido, correo, contraseña)
        VALUES (%s, %s, %s, %s)
    """
    values = (data['nombre'], data['apellido'], data['correo'], hashed_password)

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (data['correo'],))
            if cursor.fetchone():
                return jsonify({"message": "El correo ya está registrado"}), 400
            cursor.execute(query, values)
            connection.commit()
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    except Exception as e:
        return jsonify({'message': f'Error al registrar usuario: {str(e)}'}), 500
    finally:
        connection.close()

@app.route('/usuarios/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')

    if not correo or not contraseña:
        return jsonify({"message": "Correo y contraseña son obligatorios"}), 400

    query = "SELECT * FROM usuarios WHERE correo = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()
        if usuario and check_password_hash(usuario['contraseña'], contraseña):
            return jsonify({"message": "Inicio de sesión exitoso", "usuario": usuario}), 200
        else:
            return jsonify({"message": "Credenciales incorrectas"}), 401
    except Exception as e:
        return jsonify({'message': f'Error al iniciar sesión: {str(e)}'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)