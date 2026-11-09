-- Esquema operativo de Pediatría para MySQL 8.
CREATE DATABASE IF NOT EXISTS pediatria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pediatria_db;

CREATE TABLE IF NOT EXISTS paciente (
  id_paciente INT AUTO_INCREMENT PRIMARY KEY,
  nombre_paciente VARCHAR(100) NOT NULL,
  dpi_cui VARCHAR(20) NOT NULL UNIQUE,
  fecha_nacimiento DATE NOT NULL,
  genero VARCHAR(15),
  telefono_paciente VARCHAR(20),
  tutor_nombre VARCHAR(100),
  tutor_telefono VARCHAR(20),
  fecha_registro DATE DEFAULT (CURRENT_DATE),
  estado VARCHAR(15) DEFAULT 'activo'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS consulta_pediatrica (
  id_consulta INT AUTO_INCREMENT PRIMARY KEY,
  id_paciente INT NOT NULL,
  fecha_consulta DATETIME NOT NULL,
  nombre_medico VARCHAR(100),
  motivo VARCHAR(300),
  observaciones TEXT,
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cita_pediatrica (
  id_cita INT AUTO_INCREMENT PRIMARY KEY,
  id_paciente INT NOT NULL,
  fecha DATETIME NOT NULL,
  servicio VARCHAR(200) NOT NULL,
  notas TEXT,
  estado VARCHAR(15) NOT NULL DEFAULT 'programada',
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS diagnostico (
  id_diagnostico INT AUTO_INCREMENT PRIMARY KEY,
  id_consulta INT NOT NULL,
  codigo_cie10 VARCHAR(10),
  descripcion VARCHAR(300) NOT NULL,
  FOREIGN KEY (id_consulta) REFERENCES consulta_pediatrica(id_consulta)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS receta (
  id_receta INT AUTO_INCREMENT PRIMARY KEY,
  id_consulta INT NOT NULL,
  medicamento VARCHAR(100) NOT NULL,
  dosis VARCHAR(50),
  frecuencia VARCHAR(50),
  duracion_dias INT,
  FOREIGN KEY (id_consulta) REFERENCES consulta_pediatrica(id_consulta)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tratamiento_pediatrico (
  id_tratamiento INT AUTO_INCREMENT PRIMARY KEY,
  id_diagnostico INT NOT NULL,
  descripcion VARCHAR(300) NOT NULL,
  indicaciones TEXT,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE,
  FOREIGN KEY (id_diagnostico) REFERENCES diagnostico(id_diagnostico)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS control_crecimiento (
  id_control INT AUTO_INCREMENT PRIMARY KEY,
  id_paciente INT NOT NULL,
  fecha_control DATE NOT NULL,
  peso_kg DECIMAL(5,2),
  talla_cm DECIMAL(5,2),
  perimetro_cefalico_cm DECIMAL(5,2),
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS vacuna_aplicada (
  id_vacuna INT AUTO_INCREMENT PRIMARY KEY,
  id_paciente INT NOT NULL,
  nombre_vacuna VARCHAR(100) NOT NULL,
  fecha_aplicacion DATE NOT NULL,
  dosis VARCHAR(50),
  lote VARCHAR(50),
  FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
) ENGINE=InnoDB;
