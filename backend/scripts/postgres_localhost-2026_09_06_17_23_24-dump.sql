--
-- PostgreSQL database dump
--

\restrict htD2KPRAao2d59Au22rJAVLBly4RCu1NKv8GNnL2O4baagcI3VasbM4U1FYKXcQ

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: hospital; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA hospital;


ALTER SCHEMA hospital OWNER TO postgres;

--
-- Name: laboratorio; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA laboratorio;


ALTER SCHEMA laboratorio OWNER TO postgres;

--
-- Name: odontologia; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA odontologia;


ALTER SCHEMA odontologia OWNER TO postgres;

--
-- Name: pediatria; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pediatria;


ALTER SCHEMA pediatria OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: catalogo_cie10; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.catalogo_cie10 (
    codigo_cie10 character varying(10) NOT NULL,
    descripcion_estandar character varying(300) NOT NULL
);


ALTER TABLE hospital.catalogo_cie10 OWNER TO postgres;

--
-- Name: cita; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.cita (
    id_cita integer NOT NULL,
    id_paciente integer NOT NULL,
    id_medico integer NOT NULL,
    fecha_hora timestamp without time zone NOT NULL,
    estado_cita character varying(20) DEFAULT 'programada'::character varying NOT NULL,
    motivo_consulta character varying(200),
    CONSTRAINT cita_estado_cita_check CHECK (((estado_cita)::text = ANY ((ARRAY['programada'::character varying, 'atendida'::character varying, 'cancelada'::character varying, 'no asistio'::character varying])::text[])))
);


ALTER TABLE hospital.cita OWNER TO postgres;

--
-- Name: cita_id_cita_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.cita_id_cita_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.cita_id_cita_seq OWNER TO postgres;

--
-- Name: cita_id_cita_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.cita_id_cita_seq OWNED BY hospital.cita.id_cita;


--
-- Name: consulta; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.consulta (
    id_consulta integer NOT NULL,
    id_cita integer,
    id_paciente integer NOT NULL,
    id_medico integer NOT NULL,
    fecha_consulta timestamp without time zone NOT NULL,
    motivo_consulta character varying(300)
);


ALTER TABLE hospital.consulta OWNER TO postgres;

--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.consulta_id_consulta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.consulta_id_consulta_seq OWNER TO postgres;

--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.consulta_id_consulta_seq OWNED BY hospital.consulta.id_consulta;


--
-- Name: diagnostico; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.diagnostico (
    id_diagnostico integer NOT NULL,
    id_consulta integer NOT NULL,
    codigo_cie10 character varying(10) NOT NULL,
    observacion_medico text,
    fecha_diagnostico date DEFAULT CURRENT_DATE NOT NULL
);


ALTER TABLE hospital.diagnostico OWNER TO postgres;

--
-- Name: diagnostico_id_diagnostico_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.diagnostico_id_diagnostico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.diagnostico_id_diagnostico_seq OWNER TO postgres;

--
-- Name: diagnostico_id_diagnostico_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.diagnostico_id_diagnostico_seq OWNED BY hospital.diagnostico.id_diagnostico;


--
-- Name: especialidad; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.especialidad (
    id_especialidad integer NOT NULL,
    nombre_especialidad character varying(80) NOT NULL
);


ALTER TABLE hospital.especialidad OWNER TO postgres;

--
-- Name: especialidad_id_especialidad_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.especialidad_id_especialidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.especialidad_id_especialidad_seq OWNER TO postgres;

--
-- Name: especialidad_id_especialidad_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.especialidad_id_especialidad_seq OWNED BY hospital.especialidad.id_especialidad;


--
-- Name: medicamento; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.medicamento (
    id_medicamento integer NOT NULL,
    nombre_medicamento character varying(100) NOT NULL,
    presentacion_medicamento character varying(50),
    concentracion_medicamento character varying(50)
);


ALTER TABLE hospital.medicamento OWNER TO postgres;

--
-- Name: medicamento_id_medicamento_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.medicamento_id_medicamento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.medicamento_id_medicamento_seq OWNER TO postgres;

--
-- Name: medicamento_id_medicamento_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.medicamento_id_medicamento_seq OWNED BY hospital.medicamento.id_medicamento;


--
-- Name: medico; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.medico (
    id_medico integer NOT NULL,
    nombre_medico character varying(100) NOT NULL,
    no_colegiado character varying(20) NOT NULL,
    id_especialidad integer NOT NULL,
    telefono_medico integer,
    email_medico character varying(20)
);


ALTER TABLE hospital.medico OWNER TO postgres;

--
-- Name: medico_id_medico_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.medico_id_medico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.medico_id_medico_seq OWNER TO postgres;

--
-- Name: medico_id_medico_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.medico_id_medico_seq OWNED BY hospital.medico.id_medico;


--
-- Name: paciente; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.paciente (
    id_paciente integer NOT NULL,
    nombre_paciente character varying(100) NOT NULL,
    dpi_cui character varying(20) NOT NULL,
    fecha_nacimiento date NOT NULL,
    genero character varying(15),
    direccion_paciente character varying(100),
    telefono_paciente integer,
    email_paciente character varying(20),
    tipo_sangre character varying(10),
    contacto_emergencia_nombre character varying(100),
    contacto_emergencia_telefono character varying(20),
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    estado_paciente character varying(15) DEFAULT 'activo'::character varying NOT NULL,
    CONSTRAINT paciente_estado_paciente_check CHECK (((estado_paciente)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'archivado'::character varying])::text[])))
);


ALTER TABLE hospital.paciente OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.paciente_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.paciente_id_paciente_seq OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.paciente_id_paciente_seq OWNED BY hospital.paciente.id_paciente;


--
-- Name: receta; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.receta (
    id_receta integer NOT NULL,
    id_tratamiento integer NOT NULL,
    id_medicamento integer NOT NULL,
    dosis_medicamento character varying(20),
    frecuencia_medicamento character varying(20),
    duracion_dias_medicamento integer
);


ALTER TABLE hospital.receta OWNER TO postgres;

--
-- Name: receta_id_receta_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.receta_id_receta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.receta_id_receta_seq OWNER TO postgres;

--
-- Name: receta_id_receta_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.receta_id_receta_seq OWNED BY hospital.receta.id_receta;


--
-- Name: tratamiento; Type: TABLE; Schema: hospital; Owner: postgres
--

CREATE TABLE hospital.tratamiento (
    id_tratamiento integer NOT NULL,
    id_diagnostico integer NOT NULL,
    descripcion_tratamiento character varying(300),
    indicaciones_tratamiento character varying(300),
    fecha_inicio date,
    fecha_fin date
);


ALTER TABLE hospital.tratamiento OWNER TO postgres;

--
-- Name: tratamiento_id_tratamiento_seq; Type: SEQUENCE; Schema: hospital; Owner: postgres
--

CREATE SEQUENCE hospital.tratamiento_id_tratamiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE hospital.tratamiento_id_tratamiento_seq OWNER TO postgres;

--
-- Name: tratamiento_id_tratamiento_seq; Type: SEQUENCE OWNED BY; Schema: hospital; Owner: postgres
--

ALTER SEQUENCE hospital.tratamiento_id_tratamiento_seq OWNED BY hospital.tratamiento.id_tratamiento;


--
-- Name: examen; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.examen (
    id_examen integer NOT NULL,
    id_orden integer NOT NULL,
    id_tipo_examen integer NOT NULL,
    id_tecnico integer NOT NULL,
    fecha_toma_examen timestamp without time zone,
    fecha_resultado_examen timestamp without time zone,
    estado_examen character varying(30) DEFAULT 'pendiente'::character varying NOT NULL
);


ALTER TABLE laboratorio.examen OWNER TO postgres;

--
-- Name: examen_id_examen_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.examen_id_examen_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.examen_id_examen_seq OWNER TO postgres;

--
-- Name: examen_id_examen_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.examen_id_examen_seq OWNED BY laboratorio.examen.id_examen;


--
-- Name: medico_referente; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.medico_referente (
    id_medico_ref integer NOT NULL,
    nombre character varying(100) NOT NULL,
    no_colegiado_medico_ref character varying(20) NOT NULL,
    institucion_origen character varying(100),
    telefono_medico_ref integer
);


ALTER TABLE laboratorio.medico_referente OWNER TO postgres;

--
-- Name: medico_referente_id_medico_ref_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.medico_referente_id_medico_ref_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.medico_referente_id_medico_ref_seq OWNER TO postgres;

--
-- Name: medico_referente_id_medico_ref_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.medico_referente_id_medico_ref_seq OWNED BY laboratorio.medico_referente.id_medico_ref;


--
-- Name: orden_examen; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.orden_examen (
    id_orden integer NOT NULL,
    id_paciente integer NOT NULL,
    id_medico_ref integer NOT NULL,
    fecha_orden date DEFAULT CURRENT_DATE NOT NULL,
    estado character varying(20) DEFAULT 'pendiente'::character varying NOT NULL
);


ALTER TABLE laboratorio.orden_examen OWNER TO postgres;

--
-- Name: orden_examen_id_orden_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.orden_examen_id_orden_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.orden_examen_id_orden_seq OWNER TO postgres;

--
-- Name: orden_examen_id_orden_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.orden_examen_id_orden_seq OWNED BY laboratorio.orden_examen.id_orden;


--
-- Name: paciente; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.paciente (
    id_paciente integer NOT NULL,
    nombre_paciente character varying(100) NOT NULL,
    dpi_cui character varying(20) NOT NULL,
    fecha_nacimiento date NOT NULL,
    telefono_paciente integer,
    fecha_registro_paciente date DEFAULT CURRENT_DATE NOT NULL
);


ALTER TABLE laboratorio.paciente OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.paciente_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.paciente_id_paciente_seq OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.paciente_id_paciente_seq OWNED BY laboratorio.paciente.id_paciente;


--
-- Name: parametro_examen; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.parametro_examen (
    id_parametro integer NOT NULL,
    id_tipo_examen integer NOT NULL,
    nombre_parametro character varying(30) NOT NULL,
    unidad_medida character varying(30),
    valor_ref_min numeric(10,2),
    valor_ref_max numeric(10,2),
    orden integer
);


ALTER TABLE laboratorio.parametro_examen OWNER TO postgres;

--
-- Name: parametro_examen_id_parametro_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.parametro_examen_id_parametro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.parametro_examen_id_parametro_seq OWNER TO postgres;

--
-- Name: parametro_examen_id_parametro_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.parametro_examen_id_parametro_seq OWNED BY laboratorio.parametro_examen.id_parametro;


--
-- Name: resultado_parametro; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.resultado_parametro (
    id_resultado integer NOT NULL,
    id_examen integer NOT NULL,
    id_parametro integer NOT NULL,
    valor_resultado_parametro character varying(50),
    observacion_resultado_parametro text,
    alerta_resultado_parametro boolean DEFAULT false NOT NULL
);


ALTER TABLE laboratorio.resultado_parametro OWNER TO postgres;

--
-- Name: resultado_parametro_id_resultado_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.resultado_parametro_id_resultado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.resultado_parametro_id_resultado_seq OWNER TO postgres;

--
-- Name: resultado_parametro_id_resultado_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.resultado_parametro_id_resultado_seq OWNED BY laboratorio.resultado_parametro.id_resultado;


--
-- Name: tecnico; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.tecnico (
    id_tecnico integer NOT NULL,
    nombre_tecnico character varying(100) NOT NULL,
    no_colegiado_tecnico character varying(20)
);


ALTER TABLE laboratorio.tecnico OWNER TO postgres;

--
-- Name: tecnico_id_tecnico_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.tecnico_id_tecnico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.tecnico_id_tecnico_seq OWNER TO postgres;

--
-- Name: tecnico_id_tecnico_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.tecnico_id_tecnico_seq OWNED BY laboratorio.tecnico.id_tecnico;


--
-- Name: tipo_examen; Type: TABLE; Schema: laboratorio; Owner: postgres
--

CREATE TABLE laboratorio.tipo_examen (
    id_tipo_examen integer NOT NULL,
    nombre_tipo_examen character varying(30) NOT NULL,
    descripcion_tipo_examen character varying(300),
    tiempo_entrega_horas integer
);


ALTER TABLE laboratorio.tipo_examen OWNER TO postgres;

--
-- Name: tipo_examen_id_tipo_examen_seq; Type: SEQUENCE; Schema: laboratorio; Owner: postgres
--

CREATE SEQUENCE laboratorio.tipo_examen_id_tipo_examen_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE laboratorio.tipo_examen_id_tipo_examen_seq OWNER TO postgres;

--
-- Name: tipo_examen_id_tipo_examen_seq; Type: SEQUENCE OWNED BY; Schema: laboratorio; Owner: postgres
--

ALTER SEQUENCE laboratorio.tipo_examen_id_tipo_examen_seq OWNED BY laboratorio.tipo_examen.id_tipo_examen;


--
-- Name: atencion; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.atencion (
    id_atencion integer NOT NULL,
    id_cita integer NOT NULL,
    fecha_atencion timestamp without time zone NOT NULL,
    observaciones_atencion character varying(400)
);


ALTER TABLE odontologia.atencion OWNER TO postgres;

--
-- Name: atencion_id_atencion_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.atencion_id_atencion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.atencion_id_atencion_seq OWNER TO postgres;

--
-- Name: atencion_id_atencion_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.atencion_id_atencion_seq OWNED BY odontologia.atencion.id_atencion;


--
-- Name: cita; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.cita (
    id_cita integer NOT NULL,
    id_paciente integer NOT NULL,
    id_odontologo integer NOT NULL,
    id_secretaria integer NOT NULL,
    fecha_hora timestamp without time zone NOT NULL,
    estado_cita character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    motivo_consulta_cita character varying(300)
);


ALTER TABLE odontologia.cita OWNER TO postgres;

--
-- Name: cita_id_cita_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.cita_id_cita_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.cita_id_cita_seq OWNER TO postgres;

--
-- Name: cita_id_cita_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.cita_id_cita_seq OWNED BY odontologia.cita.id_cita;


--
-- Name: diagnostico_dental; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.diagnostico_dental (
    id_diagnostico integer NOT NULL,
    id_atencion integer NOT NULL,
    id_pieza integer NOT NULL,
    descripcion_diagnostico_dental character varying(300),
    severidad_diagnostico_dental character varying(50)
);


ALTER TABLE odontologia.diagnostico_dental OWNER TO postgres;

--
-- Name: diagnostico_dental_id_diagnostico_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.diagnostico_dental_id_diagnostico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.diagnostico_dental_id_diagnostico_seq OWNER TO postgres;

--
-- Name: diagnostico_dental_id_diagnostico_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.diagnostico_dental_id_diagnostico_seq OWNED BY odontologia.diagnostico_dental.id_diagnostico;


--
-- Name: odontologo; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.odontologo (
    id_odontologo integer NOT NULL,
    nombre_odontologo character varying(100) NOT NULL,
    no_colegiado character varying(20) NOT NULL,
    telefono_odontologo integer,
    email_odontologo character varying(20)
);


ALTER TABLE odontologia.odontologo OWNER TO postgres;

--
-- Name: odontologo_id_odontologo_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.odontologo_id_odontologo_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.odontologo_id_odontologo_seq OWNER TO postgres;

--
-- Name: odontologo_id_odontologo_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.odontologo_id_odontologo_seq OWNED BY odontologia.odontologo.id_odontologo;


--
-- Name: paciente; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.paciente (
    id_paciente integer NOT NULL,
    nombre_paciente character varying(100) NOT NULL,
    dpi_cui character varying(20) NOT NULL,
    fecha_nacimiento date NOT NULL,
    telefono_paciente integer,
    direccion_paciente character varying(100),
    email_paciente character varying(20),
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    estado_paciente character varying(15) DEFAULT 'activo'::character varying NOT NULL,
    CONSTRAINT paciente_estado_paciente_check CHECK (((estado_paciente)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'archivado'::character varying])::text[])))
);


ALTER TABLE odontologia.paciente OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.paciente_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.paciente_id_paciente_seq OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.paciente_id_paciente_seq OWNED BY odontologia.paciente.id_paciente;


--
-- Name: pieza_dental; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.pieza_dental (
    id_pieza integer NOT NULL,
    nombre character varying(80) NOT NULL
);


ALTER TABLE odontologia.pieza_dental OWNER TO postgres;

--
-- Name: pieza_dental_id_pieza_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.pieza_dental_id_pieza_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.pieza_dental_id_pieza_seq OWNER TO postgres;

--
-- Name: pieza_dental_id_pieza_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.pieza_dental_id_pieza_seq OWNED BY odontologia.pieza_dental.id_pieza;


--
-- Name: procedimiento; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.procedimiento (
    id_procedimiento integer NOT NULL,
    nombre_procedimiento character varying(100) NOT NULL,
    descripcion_estandar character varying(300),
    costo_base_procedimiento numeric(10,2),
    duracion_estimada_min integer
);


ALTER TABLE odontologia.procedimiento OWNER TO postgres;

--
-- Name: procedimiento_id_procedimiento_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.procedimiento_id_procedimiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.procedimiento_id_procedimiento_seq OWNER TO postgres;

--
-- Name: procedimiento_id_procedimiento_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.procedimiento_id_procedimiento_seq OWNED BY odontologia.procedimiento.id_procedimiento;


--
-- Name: secretaria; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.secretaria (
    id_secretaria integer NOT NULL,
    nombre_secretaria character varying(100) NOT NULL,
    usuario_secretaria character varying(20) NOT NULL,
    telefono_secretaria integer,
    email_secretaria character varying(20)
);


ALTER TABLE odontologia.secretaria OWNER TO postgres;

--
-- Name: secretaria_id_secretaria_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.secretaria_id_secretaria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.secretaria_id_secretaria_seq OWNER TO postgres;

--
-- Name: secretaria_id_secretaria_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.secretaria_id_secretaria_seq OWNED BY odontologia.secretaria.id_secretaria;


--
-- Name: tratamiento_dental; Type: TABLE; Schema: odontologia; Owner: postgres
--

CREATE TABLE odontologia.tratamiento_dental (
    id_tratamiento integer NOT NULL,
    id_diagnostico integer NOT NULL,
    id_procedimiento integer NOT NULL,
    fecha_tratamiento_dental date,
    estado_tratamiento_dental character varying(20),
    costo_tratamiento_dental numeric(10,2)
);


ALTER TABLE odontologia.tratamiento_dental OWNER TO postgres;

--
-- Name: tratamiento_dental_id_tratamiento_seq; Type: SEQUENCE; Schema: odontologia; Owner: postgres
--

CREATE SEQUENCE odontologia.tratamiento_dental_id_tratamiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE odontologia.tratamiento_dental_id_tratamiento_seq OWNER TO postgres;

--
-- Name: tratamiento_dental_id_tratamiento_seq; Type: SEQUENCE OWNED BY; Schema: odontologia; Owner: postgres
--

ALTER SEQUENCE odontologia.tratamiento_dental_id_tratamiento_seq OWNED BY odontologia.tratamiento_dental.id_tratamiento;


--
-- Name: consulta; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.consulta (
    id_consulta integer NOT NULL,
    id_paciente integer NOT NULL,
    id_pediatra integer NOT NULL,
    fecha_consulta timestamp without time zone NOT NULL,
    motivo_consulta character varying(300),
    notas_consulta text
);


ALTER TABLE pediatria.consulta OWNER TO postgres;

--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.consulta_id_consulta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.consulta_id_consulta_seq OWNER TO postgres;

--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.consulta_id_consulta_seq OWNED BY pediatria.consulta.id_consulta;


--
-- Name: control_crecimiento; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.control_crecimiento (
    id_control integer NOT NULL,
    id_consulta integer NOT NULL,
    peso numeric(6,2),
    talla numeric(6,2),
    perimetro_cefalico numeric(6,2),
    percentil numeric(6,2),
    fecha_control date NOT NULL
);


ALTER TABLE pediatria.control_crecimiento OWNER TO postgres;

--
-- Name: control_crecimiento_id_control_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.control_crecimiento_id_control_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.control_crecimiento_id_control_seq OWNER TO postgres;

--
-- Name: control_crecimiento_id_control_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.control_crecimiento_id_control_seq OWNED BY pediatria.control_crecimiento.id_control;


--
-- Name: paciente; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.paciente (
    id_paciente integer NOT NULL,
    nombre_paciente character varying(100) NOT NULL,
    fecha_nacimiento_paciente date NOT NULL,
    genero_paciente character varying(20),
    tipo_sangre_paciente character varying(20),
    fecha_registro date DEFAULT CURRENT_DATE NOT NULL,
    estado_paciente character varying(30) DEFAULT 'activo'::character varying NOT NULL,
    CONSTRAINT paciente_estado_paciente_check CHECK (((estado_paciente)::text = ANY ((ARRAY['activo'::character varying, 'inactivo'::character varying, 'archivado'::character varying])::text[])))
);


ALTER TABLE pediatria.paciente OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.paciente_id_paciente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.paciente_id_paciente_seq OWNER TO postgres;

--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.paciente_id_paciente_seq OWNED BY pediatria.paciente.id_paciente;


--
-- Name: paciente_tutor; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.paciente_tutor (
    id_paciente integer NOT NULL,
    id_tutor integer NOT NULL,
    parentesco character varying(50),
    es_principal boolean DEFAULT false NOT NULL
);


ALTER TABLE pediatria.paciente_tutor OWNER TO postgres;

--
-- Name: pediatra; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.pediatra (
    id_pediatra integer NOT NULL,
    nombre_pediatra character varying(100) NOT NULL,
    no_colegiado character varying(20) NOT NULL,
    telefono_pediatra integer
);


ALTER TABLE pediatria.pediatra OWNER TO postgres;

--
-- Name: pediatra_id_pediatra_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.pediatra_id_pediatra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.pediatra_id_pediatra_seq OWNER TO postgres;

--
-- Name: pediatra_id_pediatra_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.pediatra_id_pediatra_seq OWNED BY pediatria.pediatra.id_pediatra;


--
-- Name: tutor; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.tutor (
    id_tutor integer NOT NULL,
    nombre_tutor character varying(100) NOT NULL,
    dpi_cui character varying(20) NOT NULL,
    telefono integer,
    direccion character varying(100),
    email character varying(20)
);


ALTER TABLE pediatria.tutor OWNER TO postgres;

--
-- Name: tutor_id_tutor_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.tutor_id_tutor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.tutor_id_tutor_seq OWNER TO postgres;

--
-- Name: tutor_id_tutor_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.tutor_id_tutor_seq OWNED BY pediatria.tutor.id_tutor;


--
-- Name: vacuna; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.vacuna (
    id_vacuna integer NOT NULL,
    nombre_vacuna character varying(30) NOT NULL,
    fabricante_vacuna character varying(30),
    dosis_totales integer,
    edad_recomendada_meses integer
);


ALTER TABLE pediatria.vacuna OWNER TO postgres;

--
-- Name: vacuna_aplicada; Type: TABLE; Schema: pediatria; Owner: postgres
--

CREATE TABLE pediatria.vacuna_aplicada (
    id_aplicacion integer NOT NULL,
    id_paciente integer NOT NULL,
    id_vacuna integer NOT NULL,
    id_pediatra integer NOT NULL,
    numero_dosis integer NOT NULL,
    fecha_aplicacion date NOT NULL,
    lote_vacuna character varying(30),
    proxima_dosis_fecha date
);


ALTER TABLE pediatria.vacuna_aplicada OWNER TO postgres;

--
-- Name: vacuna_aplicada_id_aplicacion_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.vacuna_aplicada_id_aplicacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.vacuna_aplicada_id_aplicacion_seq OWNER TO postgres;

--
-- Name: vacuna_aplicada_id_aplicacion_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.vacuna_aplicada_id_aplicacion_seq OWNED BY pediatria.vacuna_aplicada.id_aplicacion;


--
-- Name: vacuna_id_vacuna_seq; Type: SEQUENCE; Schema: pediatria; Owner: postgres
--

CREATE SEQUENCE pediatria.vacuna_id_vacuna_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE pediatria.vacuna_id_vacuna_seq OWNER TO postgres;

--
-- Name: vacuna_id_vacuna_seq; Type: SEQUENCE OWNED BY; Schema: pediatria; Owner: postgres
--

ALTER SEQUENCE pediatria.vacuna_id_vacuna_seq OWNED BY pediatria.vacuna.id_vacuna;


--
-- Name: cita id_cita; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.cita ALTER COLUMN id_cita SET DEFAULT nextval('hospital.cita_id_cita_seq'::regclass);


--
-- Name: consulta id_consulta; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.consulta ALTER COLUMN id_consulta SET DEFAULT nextval('hospital.consulta_id_consulta_seq'::regclass);


--
-- Name: diagnostico id_diagnostico; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.diagnostico ALTER COLUMN id_diagnostico SET DEFAULT nextval('hospital.diagnostico_id_diagnostico_seq'::regclass);


--
-- Name: especialidad id_especialidad; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.especialidad ALTER COLUMN id_especialidad SET DEFAULT nextval('hospital.especialidad_id_especialidad_seq'::regclass);


--
-- Name: medicamento id_medicamento; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.medicamento ALTER COLUMN id_medicamento SET DEFAULT nextval('hospital.medicamento_id_medicamento_seq'::regclass);


--
-- Name: medico id_medico; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.medico ALTER COLUMN id_medico SET DEFAULT nextval('hospital.medico_id_medico_seq'::regclass);


--
-- Name: paciente id_paciente; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.paciente ALTER COLUMN id_paciente SET DEFAULT nextval('hospital.paciente_id_paciente_seq'::regclass);


--
-- Name: receta id_receta; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.receta ALTER COLUMN id_receta SET DEFAULT nextval('hospital.receta_id_receta_seq'::regclass);


--
-- Name: tratamiento id_tratamiento; Type: DEFAULT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.tratamiento ALTER COLUMN id_tratamiento SET DEFAULT nextval('hospital.tratamiento_id_tratamiento_seq'::regclass);


--
-- Name: examen id_examen; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.examen ALTER COLUMN id_examen SET DEFAULT nextval('laboratorio.examen_id_examen_seq'::regclass);


--
-- Name: medico_referente id_medico_ref; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.medico_referente ALTER COLUMN id_medico_ref SET DEFAULT nextval('laboratorio.medico_referente_id_medico_ref_seq'::regclass);


--
-- Name: orden_examen id_orden; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.orden_examen ALTER COLUMN id_orden SET DEFAULT nextval('laboratorio.orden_examen_id_orden_seq'::regclass);


--
-- Name: paciente id_paciente; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.paciente ALTER COLUMN id_paciente SET DEFAULT nextval('laboratorio.paciente_id_paciente_seq'::regclass);


--
-- Name: parametro_examen id_parametro; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.parametro_examen ALTER COLUMN id_parametro SET DEFAULT nextval('laboratorio.parametro_examen_id_parametro_seq'::regclass);


--
-- Name: resultado_parametro id_resultado; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.resultado_parametro ALTER COLUMN id_resultado SET DEFAULT nextval('laboratorio.resultado_parametro_id_resultado_seq'::regclass);


--
-- Name: tecnico id_tecnico; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.tecnico ALTER COLUMN id_tecnico SET DEFAULT nextval('laboratorio.tecnico_id_tecnico_seq'::regclass);


--
-- Name: tipo_examen id_tipo_examen; Type: DEFAULT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.tipo_examen ALTER COLUMN id_tipo_examen SET DEFAULT nextval('laboratorio.tipo_examen_id_tipo_examen_seq'::regclass);


--
-- Name: atencion id_atencion; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.atencion ALTER COLUMN id_atencion SET DEFAULT nextval('odontologia.atencion_id_atencion_seq'::regclass);


--
-- Name: cita id_cita; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.cita ALTER COLUMN id_cita SET DEFAULT nextval('odontologia.cita_id_cita_seq'::regclass);


--
-- Name: diagnostico_dental id_diagnostico; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.diagnostico_dental ALTER COLUMN id_diagnostico SET DEFAULT nextval('odontologia.diagnostico_dental_id_diagnostico_seq'::regclass);


--
-- Name: odontologo id_odontologo; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.odontologo ALTER COLUMN id_odontologo SET DEFAULT nextval('odontologia.odontologo_id_odontologo_seq'::regclass);


--
-- Name: paciente id_paciente; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.paciente ALTER COLUMN id_paciente SET DEFAULT nextval('odontologia.paciente_id_paciente_seq'::regclass);


--
-- Name: pieza_dental id_pieza; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.pieza_dental ALTER COLUMN id_pieza SET DEFAULT nextval('odontologia.pieza_dental_id_pieza_seq'::regclass);


--
-- Name: procedimiento id_procedimiento; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.procedimiento ALTER COLUMN id_procedimiento SET DEFAULT nextval('odontologia.procedimiento_id_procedimiento_seq'::regclass);


--
-- Name: secretaria id_secretaria; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.secretaria ALTER COLUMN id_secretaria SET DEFAULT nextval('odontologia.secretaria_id_secretaria_seq'::regclass);


--
-- Name: tratamiento_dental id_tratamiento; Type: DEFAULT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.tratamiento_dental ALTER COLUMN id_tratamiento SET DEFAULT nextval('odontologia.tratamiento_dental_id_tratamiento_seq'::regclass);


--
-- Name: consulta id_consulta; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.consulta ALTER COLUMN id_consulta SET DEFAULT nextval('pediatria.consulta_id_consulta_seq'::regclass);


--
-- Name: control_crecimiento id_control; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.control_crecimiento ALTER COLUMN id_control SET DEFAULT nextval('pediatria.control_crecimiento_id_control_seq'::regclass);


--
-- Name: paciente id_paciente; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.paciente ALTER COLUMN id_paciente SET DEFAULT nextval('pediatria.paciente_id_paciente_seq'::regclass);


--
-- Name: pediatra id_pediatra; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.pediatra ALTER COLUMN id_pediatra SET DEFAULT nextval('pediatria.pediatra_id_pediatra_seq'::regclass);


--
-- Name: tutor id_tutor; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.tutor ALTER COLUMN id_tutor SET DEFAULT nextval('pediatria.tutor_id_tutor_seq'::regclass);


--
-- Name: vacuna id_vacuna; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna ALTER COLUMN id_vacuna SET DEFAULT nextval('pediatria.vacuna_id_vacuna_seq'::regclass);


--
-- Name: vacuna_aplicada id_aplicacion; Type: DEFAULT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna_aplicada ALTER COLUMN id_aplicacion SET DEFAULT nextval('pediatria.vacuna_aplicada_id_aplicacion_seq'::regclass);


--
-- Data for Name: catalogo_cie10; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.catalogo_cie10 (codigo_cie10, descripcion_estandar) FROM stdin;
\.


--
-- Data for Name: cita; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.cita (id_cita, id_paciente, id_medico, fecha_hora, estado_cita, motivo_consulta) FROM stdin;
\.


--
-- Data for Name: consulta; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.consulta (id_consulta, id_cita, id_paciente, id_medico, fecha_consulta, motivo_consulta) FROM stdin;
\.


--
-- Data for Name: diagnostico; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.diagnostico (id_diagnostico, id_consulta, codigo_cie10, observacion_medico, fecha_diagnostico) FROM stdin;
\.


--
-- Data for Name: especialidad; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.especialidad (id_especialidad, nombre_especialidad) FROM stdin;
\.


--
-- Data for Name: medicamento; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.medicamento (id_medicamento, nombre_medicamento, presentacion_medicamento, concentracion_medicamento) FROM stdin;
\.


--
-- Data for Name: medico; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.medico (id_medico, nombre_medico, no_colegiado, id_especialidad, telefono_medico, email_medico) FROM stdin;
\.


--
-- Data for Name: paciente; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.paciente (id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento, genero, direccion_paciente, telefono_paciente, email_paciente, tipo_sangre, contacto_emergencia_nombre, contacto_emergencia_telefono, fecha_registro, estado_paciente) FROM stdin;
\.


--
-- Data for Name: receta; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.receta (id_receta, id_tratamiento, id_medicamento, dosis_medicamento, frecuencia_medicamento, duracion_dias_medicamento) FROM stdin;
\.


--
-- Data for Name: tratamiento; Type: TABLE DATA; Schema: hospital; Owner: postgres
--

COPY hospital.tratamiento (id_tratamiento, id_diagnostico, descripcion_tratamiento, indicaciones_tratamiento, fecha_inicio, fecha_fin) FROM stdin;
\.


--
-- Data for Name: examen; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.examen (id_examen, id_orden, id_tipo_examen, id_tecnico, fecha_toma_examen, fecha_resultado_examen, estado_examen) FROM stdin;
\.


--
-- Data for Name: medico_referente; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.medico_referente (id_medico_ref, nombre, no_colegiado_medico_ref, institucion_origen, telefono_medico_ref) FROM stdin;
\.


--
-- Data for Name: orden_examen; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.orden_examen (id_orden, id_paciente, id_medico_ref, fecha_orden, estado) FROM stdin;
\.


--
-- Data for Name: paciente; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.paciente (id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento, telefono_paciente, fecha_registro_paciente) FROM stdin;
\.


--
-- Data for Name: parametro_examen; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.parametro_examen (id_parametro, id_tipo_examen, nombre_parametro, unidad_medida, valor_ref_min, valor_ref_max, orden) FROM stdin;
\.


--
-- Data for Name: resultado_parametro; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.resultado_parametro (id_resultado, id_examen, id_parametro, valor_resultado_parametro, observacion_resultado_parametro, alerta_resultado_parametro) FROM stdin;
\.


--
-- Data for Name: tecnico; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.tecnico (id_tecnico, nombre_tecnico, no_colegiado_tecnico) FROM stdin;
\.


--
-- Data for Name: tipo_examen; Type: TABLE DATA; Schema: laboratorio; Owner: postgres
--

COPY laboratorio.tipo_examen (id_tipo_examen, nombre_tipo_examen, descripcion_tipo_examen, tiempo_entrega_horas) FROM stdin;
\.


--
-- Data for Name: atencion; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.atencion (id_atencion, id_cita, fecha_atencion, observaciones_atencion) FROM stdin;
\.


--
-- Data for Name: cita; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.cita (id_cita, id_paciente, id_odontologo, id_secretaria, fecha_hora, estado_cita, motivo_consulta_cita) FROM stdin;
\.


--
-- Data for Name: diagnostico_dental; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.diagnostico_dental (id_diagnostico, id_atencion, id_pieza, descripcion_diagnostico_dental, severidad_diagnostico_dental) FROM stdin;
\.


--
-- Data for Name: odontologo; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.odontologo (id_odontologo, nombre_odontologo, no_colegiado, telefono_odontologo, email_odontologo) FROM stdin;
\.


--
-- Data for Name: paciente; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.paciente (id_paciente, nombre_paciente, dpi_cui, fecha_nacimiento, telefono_paciente, direccion_paciente, email_paciente, fecha_registro, estado_paciente) FROM stdin;
\.


--
-- Data for Name: pieza_dental; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.pieza_dental (id_pieza, nombre) FROM stdin;
\.


--
-- Data for Name: procedimiento; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.procedimiento (id_procedimiento, nombre_procedimiento, descripcion_estandar, costo_base_procedimiento, duracion_estimada_min) FROM stdin;
\.


--
-- Data for Name: secretaria; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.secretaria (id_secretaria, nombre_secretaria, usuario_secretaria, telefono_secretaria, email_secretaria) FROM stdin;
\.


--
-- Data for Name: tratamiento_dental; Type: TABLE DATA; Schema: odontologia; Owner: postgres
--

COPY odontologia.tratamiento_dental (id_tratamiento, id_diagnostico, id_procedimiento, fecha_tratamiento_dental, estado_tratamiento_dental, costo_tratamiento_dental) FROM stdin;
\.


--
-- Data for Name: consulta; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.consulta (id_consulta, id_paciente, id_pediatra, fecha_consulta, motivo_consulta, notas_consulta) FROM stdin;
\.


--
-- Data for Name: control_crecimiento; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.control_crecimiento (id_control, id_consulta, peso, talla, perimetro_cefalico, percentil, fecha_control) FROM stdin;
\.


--
-- Data for Name: paciente; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.paciente (id_paciente, nombre_paciente, fecha_nacimiento_paciente, genero_paciente, tipo_sangre_paciente, fecha_registro, estado_paciente) FROM stdin;
\.


--
-- Data for Name: paciente_tutor; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.paciente_tutor (id_paciente, id_tutor, parentesco, es_principal) FROM stdin;
\.


--
-- Data for Name: pediatra; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.pediatra (id_pediatra, nombre_pediatra, no_colegiado, telefono_pediatra) FROM stdin;
\.


--
-- Data for Name: tutor; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.tutor (id_tutor, nombre_tutor, dpi_cui, telefono, direccion, email) FROM stdin;
\.


--
-- Data for Name: vacuna; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.vacuna (id_vacuna, nombre_vacuna, fabricante_vacuna, dosis_totales, edad_recomendada_meses) FROM stdin;
\.


--
-- Data for Name: vacuna_aplicada; Type: TABLE DATA; Schema: pediatria; Owner: postgres
--

COPY pediatria.vacuna_aplicada (id_aplicacion, id_paciente, id_vacuna, id_pediatra, numero_dosis, fecha_aplicacion, lote_vacuna, proxima_dosis_fecha) FROM stdin;
\.


--
-- Name: cita_id_cita_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.cita_id_cita_seq', 1, false);


--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.consulta_id_consulta_seq', 1, false);


--
-- Name: diagnostico_id_diagnostico_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.diagnostico_id_diagnostico_seq', 1, false);


--
-- Name: especialidad_id_especialidad_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.especialidad_id_especialidad_seq', 1, false);


--
-- Name: medicamento_id_medicamento_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.medicamento_id_medicamento_seq', 1, false);


--
-- Name: medico_id_medico_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.medico_id_medico_seq', 1, false);


--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.paciente_id_paciente_seq', 1, false);


--
-- Name: receta_id_receta_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.receta_id_receta_seq', 1, false);


--
-- Name: tratamiento_id_tratamiento_seq; Type: SEQUENCE SET; Schema: hospital; Owner: postgres
--

SELECT pg_catalog.setval('hospital.tratamiento_id_tratamiento_seq', 1, false);


--
-- Name: examen_id_examen_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.examen_id_examen_seq', 1, false);


--
-- Name: medico_referente_id_medico_ref_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.medico_referente_id_medico_ref_seq', 1, false);


--
-- Name: orden_examen_id_orden_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.orden_examen_id_orden_seq', 1, false);


--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.paciente_id_paciente_seq', 1, false);


--
-- Name: parametro_examen_id_parametro_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.parametro_examen_id_parametro_seq', 1, false);


--
-- Name: resultado_parametro_id_resultado_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.resultado_parametro_id_resultado_seq', 1, false);


--
-- Name: tecnico_id_tecnico_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.tecnico_id_tecnico_seq', 1, false);


--
-- Name: tipo_examen_id_tipo_examen_seq; Type: SEQUENCE SET; Schema: laboratorio; Owner: postgres
--

SELECT pg_catalog.setval('laboratorio.tipo_examen_id_tipo_examen_seq', 1, false);


--
-- Name: atencion_id_atencion_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.atencion_id_atencion_seq', 1, false);


--
-- Name: cita_id_cita_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.cita_id_cita_seq', 1, false);


--
-- Name: diagnostico_dental_id_diagnostico_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.diagnostico_dental_id_diagnostico_seq', 1, false);


--
-- Name: odontologo_id_odontologo_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.odontologo_id_odontologo_seq', 1, false);


--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.paciente_id_paciente_seq', 1, false);


--
-- Name: pieza_dental_id_pieza_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.pieza_dental_id_pieza_seq', 1, false);


--
-- Name: procedimiento_id_procedimiento_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.procedimiento_id_procedimiento_seq', 1, false);


--
-- Name: secretaria_id_secretaria_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.secretaria_id_secretaria_seq', 1, false);


--
-- Name: tratamiento_dental_id_tratamiento_seq; Type: SEQUENCE SET; Schema: odontologia; Owner: postgres
--

SELECT pg_catalog.setval('odontologia.tratamiento_dental_id_tratamiento_seq', 1, false);


--
-- Name: consulta_id_consulta_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.consulta_id_consulta_seq', 1, false);


--
-- Name: control_crecimiento_id_control_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.control_crecimiento_id_control_seq', 1, false);


--
-- Name: paciente_id_paciente_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.paciente_id_paciente_seq', 1, false);


--
-- Name: pediatra_id_pediatra_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.pediatra_id_pediatra_seq', 1, false);


--
-- Name: tutor_id_tutor_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.tutor_id_tutor_seq', 1, false);


--
-- Name: vacuna_aplicada_id_aplicacion_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.vacuna_aplicada_id_aplicacion_seq', 1, false);


--
-- Name: vacuna_id_vacuna_seq; Type: SEQUENCE SET; Schema: pediatria; Owner: postgres
--

SELECT pg_catalog.setval('pediatria.vacuna_id_vacuna_seq', 1, false);


--
-- Name: catalogo_cie10 catalogo_cie10_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.catalogo_cie10
    ADD CONSTRAINT catalogo_cie10_pkey PRIMARY KEY (codigo_cie10);


--
-- Name: cita cita_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.cita
    ADD CONSTRAINT cita_pkey PRIMARY KEY (id_cita);


--
-- Name: consulta consulta_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.consulta
    ADD CONSTRAINT consulta_pkey PRIMARY KEY (id_consulta);


--
-- Name: diagnostico diagnostico_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.diagnostico
    ADD CONSTRAINT diagnostico_pkey PRIMARY KEY (id_diagnostico);


--
-- Name: especialidad especialidad_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.especialidad
    ADD CONSTRAINT especialidad_pkey PRIMARY KEY (id_especialidad);


--
-- Name: medicamento medicamento_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.medicamento
    ADD CONSTRAINT medicamento_pkey PRIMARY KEY (id_medicamento);


--
-- Name: medico medico_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.medico
    ADD CONSTRAINT medico_pkey PRIMARY KEY (id_medico);


--
-- Name: paciente paciente_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id_paciente);


--
-- Name: receta receta_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.receta
    ADD CONSTRAINT receta_pkey PRIMARY KEY (id_receta);


--
-- Name: tratamiento tratamiento_pkey; Type: CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.tratamiento
    ADD CONSTRAINT tratamiento_pkey PRIMARY KEY (id_tratamiento);


--
-- Name: examen examen_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.examen
    ADD CONSTRAINT examen_pkey PRIMARY KEY (id_examen);


--
-- Name: medico_referente medico_referente_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.medico_referente
    ADD CONSTRAINT medico_referente_pkey PRIMARY KEY (id_medico_ref);


--
-- Name: orden_examen orden_examen_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.orden_examen
    ADD CONSTRAINT orden_examen_pkey PRIMARY KEY (id_orden);


--
-- Name: paciente paciente_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id_paciente);


--
-- Name: parametro_examen parametro_examen_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.parametro_examen
    ADD CONSTRAINT parametro_examen_pkey PRIMARY KEY (id_parametro);


--
-- Name: resultado_parametro resultado_parametro_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.resultado_parametro
    ADD CONSTRAINT resultado_parametro_pkey PRIMARY KEY (id_resultado);


--
-- Name: tecnico tecnico_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.tecnico
    ADD CONSTRAINT tecnico_pkey PRIMARY KEY (id_tecnico);


--
-- Name: tipo_examen tipo_examen_pkey; Type: CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.tipo_examen
    ADD CONSTRAINT tipo_examen_pkey PRIMARY KEY (id_tipo_examen);


--
-- Name: atencion atencion_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.atencion
    ADD CONSTRAINT atencion_pkey PRIMARY KEY (id_atencion);


--
-- Name: cita cita_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.cita
    ADD CONSTRAINT cita_pkey PRIMARY KEY (id_cita);


--
-- Name: diagnostico_dental diagnostico_dental_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.diagnostico_dental
    ADD CONSTRAINT diagnostico_dental_pkey PRIMARY KEY (id_diagnostico);


--
-- Name: odontologo odontologo_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.odontologo
    ADD CONSTRAINT odontologo_pkey PRIMARY KEY (id_odontologo);


--
-- Name: paciente paciente_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id_paciente);


--
-- Name: pieza_dental pieza_dental_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.pieza_dental
    ADD CONSTRAINT pieza_dental_pkey PRIMARY KEY (id_pieza);


--
-- Name: procedimiento procedimiento_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.procedimiento
    ADD CONSTRAINT procedimiento_pkey PRIMARY KEY (id_procedimiento);


--
-- Name: secretaria secretaria_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.secretaria
    ADD CONSTRAINT secretaria_pkey PRIMARY KEY (id_secretaria);


--
-- Name: secretaria secretaria_usuario_secretaria_key; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.secretaria
    ADD CONSTRAINT secretaria_usuario_secretaria_key UNIQUE (usuario_secretaria);


--
-- Name: tratamiento_dental tratamiento_dental_pkey; Type: CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.tratamiento_dental
    ADD CONSTRAINT tratamiento_dental_pkey PRIMARY KEY (id_tratamiento);


--
-- Name: consulta consulta_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.consulta
    ADD CONSTRAINT consulta_pkey PRIMARY KEY (id_consulta);


--
-- Name: control_crecimiento control_crecimiento_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.control_crecimiento
    ADD CONSTRAINT control_crecimiento_pkey PRIMARY KEY (id_control);


--
-- Name: paciente paciente_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.paciente
    ADD CONSTRAINT paciente_pkey PRIMARY KEY (id_paciente);


--
-- Name: paciente_tutor paciente_tutor_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.paciente_tutor
    ADD CONSTRAINT paciente_tutor_pkey PRIMARY KEY (id_paciente, id_tutor);


--
-- Name: pediatra pediatra_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.pediatra
    ADD CONSTRAINT pediatra_pkey PRIMARY KEY (id_pediatra);


--
-- Name: tutor tutor_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.tutor
    ADD CONSTRAINT tutor_pkey PRIMARY KEY (id_tutor);


--
-- Name: vacuna_aplicada vacuna_aplicada_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna_aplicada
    ADD CONSTRAINT vacuna_aplicada_pkey PRIMARY KEY (id_aplicacion);


--
-- Name: vacuna vacuna_pkey; Type: CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna
    ADD CONSTRAINT vacuna_pkey PRIMARY KEY (id_vacuna);


--
-- Name: cita fk_cita_medico; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.cita
    ADD CONSTRAINT fk_cita_medico FOREIGN KEY (id_medico) REFERENCES hospital.medico(id_medico);


--
-- Name: cita fk_cita_paciente; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.cita
    ADD CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES hospital.paciente(id_paciente);


--
-- Name: consulta fk_consulta_cita; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.consulta
    ADD CONSTRAINT fk_consulta_cita FOREIGN KEY (id_cita) REFERENCES hospital.cita(id_cita);


--
-- Name: consulta fk_consulta_medico; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.consulta
    ADD CONSTRAINT fk_consulta_medico FOREIGN KEY (id_medico) REFERENCES hospital.medico(id_medico);


--
-- Name: consulta fk_consulta_paciente; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.consulta
    ADD CONSTRAINT fk_consulta_paciente FOREIGN KEY (id_paciente) REFERENCES hospital.paciente(id_paciente);


--
-- Name: diagnostico fk_diagnostico_cie10; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.diagnostico
    ADD CONSTRAINT fk_diagnostico_cie10 FOREIGN KEY (codigo_cie10) REFERENCES hospital.catalogo_cie10(codigo_cie10);


--
-- Name: diagnostico fk_diagnostico_consulta; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.diagnostico
    ADD CONSTRAINT fk_diagnostico_consulta FOREIGN KEY (id_consulta) REFERENCES hospital.consulta(id_consulta);


--
-- Name: medico fk_medico_especialidad; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.medico
    ADD CONSTRAINT fk_medico_especialidad FOREIGN KEY (id_especialidad) REFERENCES hospital.especialidad(id_especialidad);


--
-- Name: receta fk_receta_medicamento; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.receta
    ADD CONSTRAINT fk_receta_medicamento FOREIGN KEY (id_medicamento) REFERENCES hospital.medicamento(id_medicamento);


--
-- Name: receta fk_receta_tratamiento; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.receta
    ADD CONSTRAINT fk_receta_tratamiento FOREIGN KEY (id_tratamiento) REFERENCES hospital.tratamiento(id_tratamiento);


--
-- Name: tratamiento fk_tratamiento_diagnostico; Type: FK CONSTRAINT; Schema: hospital; Owner: postgres
--

ALTER TABLE ONLY hospital.tratamiento
    ADD CONSTRAINT fk_tratamiento_diagnostico FOREIGN KEY (id_diagnostico) REFERENCES hospital.diagnostico(id_diagnostico);


--
-- Name: examen fk_examen_orden; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.examen
    ADD CONSTRAINT fk_examen_orden FOREIGN KEY (id_orden) REFERENCES laboratorio.orden_examen(id_orden);


--
-- Name: examen fk_examen_tecnico; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.examen
    ADD CONSTRAINT fk_examen_tecnico FOREIGN KEY (id_tecnico) REFERENCES laboratorio.tecnico(id_tecnico);


--
-- Name: examen fk_examen_tipoexamen; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.examen
    ADD CONSTRAINT fk_examen_tipoexamen FOREIGN KEY (id_tipo_examen) REFERENCES laboratorio.tipo_examen(id_tipo_examen);


--
-- Name: orden_examen fk_orden_medicoref; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.orden_examen
    ADD CONSTRAINT fk_orden_medicoref FOREIGN KEY (id_medico_ref) REFERENCES laboratorio.medico_referente(id_medico_ref);


--
-- Name: orden_examen fk_orden_paciente; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.orden_examen
    ADD CONSTRAINT fk_orden_paciente FOREIGN KEY (id_paciente) REFERENCES laboratorio.paciente(id_paciente);


--
-- Name: parametro_examen fk_parametro_tipoexamen; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.parametro_examen
    ADD CONSTRAINT fk_parametro_tipoexamen FOREIGN KEY (id_tipo_examen) REFERENCES laboratorio.tipo_examen(id_tipo_examen);


--
-- Name: resultado_parametro fk_resultado_examen; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.resultado_parametro
    ADD CONSTRAINT fk_resultado_examen FOREIGN KEY (id_examen) REFERENCES laboratorio.examen(id_examen);


--
-- Name: resultado_parametro fk_resultado_parametro; Type: FK CONSTRAINT; Schema: laboratorio; Owner: postgres
--

ALTER TABLE ONLY laboratorio.resultado_parametro
    ADD CONSTRAINT fk_resultado_parametro FOREIGN KEY (id_parametro) REFERENCES laboratorio.parametro_examen(id_parametro);


--
-- Name: atencion fk_atencion_cita; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.atencion
    ADD CONSTRAINT fk_atencion_cita FOREIGN KEY (id_cita) REFERENCES odontologia.cita(id_cita);


--
-- Name: cita fk_cita_odontologo; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.cita
    ADD CONSTRAINT fk_cita_odontologo FOREIGN KEY (id_odontologo) REFERENCES odontologia.odontologo(id_odontologo);


--
-- Name: cita fk_cita_paciente; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.cita
    ADD CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES odontologia.paciente(id_paciente);


--
-- Name: cita fk_cita_secretaria; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.cita
    ADD CONSTRAINT fk_cita_secretaria FOREIGN KEY (id_secretaria) REFERENCES odontologia.secretaria(id_secretaria);


--
-- Name: diagnostico_dental fk_diagdental_atencion; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.diagnostico_dental
    ADD CONSTRAINT fk_diagdental_atencion FOREIGN KEY (id_atencion) REFERENCES odontologia.atencion(id_atencion);


--
-- Name: diagnostico_dental fk_diagdental_pieza; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.diagnostico_dental
    ADD CONSTRAINT fk_diagdental_pieza FOREIGN KEY (id_pieza) REFERENCES odontologia.pieza_dental(id_pieza);


--
-- Name: tratamiento_dental fk_tratdental_diagnostico; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.tratamiento_dental
    ADD CONSTRAINT fk_tratdental_diagnostico FOREIGN KEY (id_diagnostico) REFERENCES odontologia.diagnostico_dental(id_diagnostico);


--
-- Name: tratamiento_dental fk_tratdental_procedimiento; Type: FK CONSTRAINT; Schema: odontologia; Owner: postgres
--

ALTER TABLE ONLY odontologia.tratamiento_dental
    ADD CONSTRAINT fk_tratdental_procedimiento FOREIGN KEY (id_procedimiento) REFERENCES odontologia.procedimiento(id_procedimiento);


--
-- Name: consulta fk_consulta_paciente; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.consulta
    ADD CONSTRAINT fk_consulta_paciente FOREIGN KEY (id_paciente) REFERENCES pediatria.paciente(id_paciente);


--
-- Name: consulta fk_consulta_pediatra; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.consulta
    ADD CONSTRAINT fk_consulta_pediatra FOREIGN KEY (id_pediatra) REFERENCES pediatria.pediatra(id_pediatra);


--
-- Name: control_crecimiento fk_control_consulta; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.control_crecimiento
    ADD CONSTRAINT fk_control_consulta FOREIGN KEY (id_consulta) REFERENCES pediatria.consulta(id_consulta);


--
-- Name: paciente_tutor fk_pactutor_paciente; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.paciente_tutor
    ADD CONSTRAINT fk_pactutor_paciente FOREIGN KEY (id_paciente) REFERENCES pediatria.paciente(id_paciente);


--
-- Name: paciente_tutor fk_pactutor_tutor; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.paciente_tutor
    ADD CONSTRAINT fk_pactutor_tutor FOREIGN KEY (id_tutor) REFERENCES pediatria.tutor(id_tutor);


--
-- Name: vacuna_aplicada fk_vacapl_paciente; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna_aplicada
    ADD CONSTRAINT fk_vacapl_paciente FOREIGN KEY (id_paciente) REFERENCES pediatria.paciente(id_paciente);


--
-- Name: vacuna_aplicada fk_vacapl_pediatra; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna_aplicada
    ADD CONSTRAINT fk_vacapl_pediatra FOREIGN KEY (id_pediatra) REFERENCES pediatria.pediatra(id_pediatra);


--
-- Name: vacuna_aplicada fk_vacapl_vacuna; Type: FK CONSTRAINT; Schema: pediatria; Owner: postgres
--

ALTER TABLE ONLY pediatria.vacuna_aplicada
    ADD CONSTRAINT fk_vacapl_vacuna FOREIGN KEY (id_vacuna) REFERENCES pediatria.vacuna(id_vacuna);


--
-- PostgreSQL database dump complete
--

\unrestrict htD2KPRAao2d59Au22rJAVLBly4RCu1NKv8GNnL2O4baagcI3VasbM4U1FYKXcQ

