CREATE TABLE usuarios (
    id_usuarios INT AUTO_INCREMENT PRIMARY KEY, 
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contraseña VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE mascotas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuarios INT,
    nombre VARCHAR(100),
    tipo VARCHAR(100),
    estado VARCHAR(100),
    descripcion TEXT,
    foto BLOB,
    zona VARCHAR(255),
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    comentario TEXT,
    FOREIGN KEY (id_usuarios) REFERENCES usuarios(id_usuarios) ON DELETE CASCADE
);


INSERT INTO usuarios (nombre, apellido, correo, contraseña) 
VALUES 
('Delfina', 'Videla', 'dvidela@gmail.com', 'contraseña123'),
('Victoria', 'Grumelli', 'vgrumelli@gmail.com', 'contraseña456'),
('Matias', 'Prestti', 'mprestti@gmail.com', 'contraseña789');

INSERT INTO mascotas (id_usuarios, nombre, tipo, estado, descripcion, zona, comentario)
VALUES 
(1, 'Luna', 'Gato', 'Perdida', 'Gato gris con ojos verdes.', 'Barrio Norte', 'Vi a Luna cerca de la plaza.'),
(2, 'Tomi', 'Perro', 'Perdida', 'Perro labrador de color amarillo.', 'Villa Urquiza', NULL), 
(3, 'Cheems', 'Perro', 'Encontrada', 'Perro encontrado cerca de la estación.', 'Palermo', 'Cheems estaba cerca de plaza Italia.');




