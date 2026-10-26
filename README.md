# Plataforma de historiales clínicos con persistencia poliglota

## Descripción

Proyecto académico del curso **Bases de Datos II** orientado al diseño de una plataforma para administrar historiales clínicos en una red de instituciones médicas independientes. El proyecto compara la implementación de reglas de negocio comunes sobre distintos motores de bases de datos, manteniendo una experiencia uniforme para sus usuarios.

La solución se plantea con una arquitectura hexagonal. La lógica del dominio debe mantenerse desacoplada de los motores de persistencia, y las operaciones deben dirigirse al motor correspondiente a la institución del usuario autenticado.

## Alcance del proyecto

El alcance final contempla cuatro instituciones: hospital general, clínica odontológica, laboratorio clínico y centro médico pediátrico. La consigna establece que cada institución utilice un motor distinto, sin repetirlo. Las alternativas definidas para el proyecto son PostgreSQL, MySQL, MongoDB y Firebase; la asignación y su justificación deben quedar documentadas.

La entrega académica presentada como base de este repositorio desarrolla los modelos del **Hospital General** y del **Centro Médico Pediátrico**. Incluye entidades, atributos, operaciones previstas, clasificación de información y diagramas. La documentación asigna PostgreSQL al Hospital General por sus requisitos de integridad referencial y transacciones. La cobertura de las otras dos instituciones y la asignación completa de motores forman parte del trabajo pendiente.

## Objetivos

- Diseñar y mantener historiales clínicos para las instituciones incluidas en el proyecto.
- Registrar pacientes, consultas, diagnósticos y tratamientos de acuerdo con las reglas de cada institución.
- Comparar modelos relacionales y documentales y justificar la ubicación de los datos.
- Aplicar transacciones, consistencia, control de acceso y protección de información clínica según el motor utilizado.
- Enrutar las operaciones a la persistencia de la institución correspondiente sin duplicar la lógica de negocio.

## Estado

El material de referencia corresponde a la fase de análisis y modelado. Este repositorio aún no contiene una aplicación ejecutable ni adaptadores de base de datos. La descripción distingue lo presentado en la entrega base de las capacidades previstas para el proyecto completo.

## Trabajo pendiente

1. Completar los modelos de la clínica odontológica y el laboratorio clínico.
2. Revisar los modelos a partir de la retroalimentación recibida y definir la asignación final de los cuatro motores.
3. Implementar la aplicación cliente-servidor y los adaptadores de persistencia bajo la arquitectura hexagonal.
4. Implementar operaciones equivalentes entre instituciones y motores.
5. Documentar consistencia, decisiones de modelado, seguridad, autorización y configuración de cada motor.

## Información y seguridad

Los modelos clasifican la información en pública, confidencial y restringida. Los datos de identidad y contacto requieren acceso controlado; los historiales, consultas, diagnósticos, tratamientos y registros pediátricos son información clínica restringida. La implementación deberá aplicar permisos acordes con el rol del usuario y evitar almacenar credenciales o datos clínicos reales en el repositorio.

## Motores considerados

- PostgreSQL
- MySQL
- MongoDB
- Firebase

La asignación definitiva debe cubrir una institución por motor y justificarse en la documentación comparativa del proyecto.
