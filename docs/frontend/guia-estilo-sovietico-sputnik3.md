# Guía de dirección visual: Sputnik 3

**Proyecto:** Plataforma de historiales clínicos con persistencia poliglota

**Uso:** Referencia para diseñar el frontend
**Estado:** Dirección visual; no constituye una implementación ni un sistema de diseño cerrado

## 1. Propósito

Definir una identidad visual para la plataforma clínica inspirada en el diseño editorial soviético, la gráfica de propaganda histórica y la imaginación tecnológica de la era espacial. La metáfora de **Sputnik 3** aporta una sensación de instrumentación, observación, telemetría y exploración técnica.

La interfaz sigue siendo una herramienta sanitaria contemporánea. Debe comunicar orden, cuidado, precisión y confianza. La referencia histórica orienta la composición y el lenguaje gráfico; no expresa una posición política ni presenta un sistema político como modelo para la atención médica.

## 2. Lectura de las referencias proporcionadas

### Ensayos y textos políticos

- **Vittorio Strada, “Socialismo y comunismo” (1991):** ensayo crítico que diferencia conceptos y examina sus usos históricos, incluida la experiencia soviética. Para el diseño aporta una actitud de análisis y distancia crítica. La interfaz no debe convertir una doctrina en verdad institucional, usar consignas ni representar la historia como un relato único e inevitable.
- **Marta Harnecker, _Socialismo y comunismo_ (Akal, 1979):** exposición didáctica organizada en introducción, partes temáticas, resumen y cuestionario. Su estructura inspira jerarquías claras, módulos que avanzan por etapas, esquemas explicativos y vocabulario consistente. No se trasladan sus afirmaciones políticas al contenido de la aplicación.
- **Karl Marx y Friedrich Engels, _Manifiesto comunista_ (edición digital consultada, 2000):** texto de intervención pública, organizado en secciones y escrito con una voz enfática. Para la composición sirve como referencia de títulos contundentes y lectura editorial por bloques. Se excluyen el tono de confrontación, los llamados políticos y las frases ideológicas de la interfaz clínica.

Estos textos cumplen funciones distintas: Strada ofrece una lectura crítica, Harnecker una presentación pedagógica de una tradición teórica y Marx y Engels un manifiesto político. Se usan como contexto cultural para interpretar el material visual, no como una fuente de requisitos funcionales o clínicos.

### Referencias visuales

- La captura de **USSR × Design** emplea fondo oscuro, encabezado mínimo, tipografía roja enorme, etiquetas laterales pequeñas y una imagen espacial parcialmente cubierta por el titular. Inspira portadas y encabezados editoriales, no las pantallas de trabajo con expedientes.
- La tarjeta de color reduce el lenguaje a **negro, rojo y blanco**. Ese contraste es la base; se amplía con un marfil cálido para que las pantallas clínicas no sean completamente oscuras.
- El retrato ilustrado de Lenin usa una figura central, haces radiales, tonos rojos y dorados, azul verdoso y textura impresa. Inspira ilustraciones de portada o separadores históricos. No se propone usar retratos políticos en la interfaz cotidiana.
- La pantalla de catálogo combina una superficie marfil, un panel rojo angular, imágenes circulares y un elemento seleccionado dominante. Inspira carruseles o selectores de contenido, con formas simplificadas y controles claramente funcionales.
- Los ejemplos de presentaciones históricas combinan papel envejecido, carbón, rojo, fotografía de archivo, tipografía condensada, anotaciones y collages. Inspiran una capa editorial o de archivo, aplicada con moderación.
- La imagen negra sin contenido legible no aporta un patrón visual utilizable y queda fuera de la dirección de arte.

## 3. Principios de diseño

1. **La información clínica manda.** La decoración nunca debe competir con nombres, identificadores, alertas, resultados o acciones.
2. **Instrumento antes que escenografía.** La plataforma debe sentirse como un sistema técnico bien organizado, no como un afiche en cada pantalla.
3. **Editorial en los puntos de entrada.** La escala tipográfica y los recursos de cartel se reservan para inicio de sesión, bienvenida, selección institucional y páginas vacías.
4. **Archivo con trazabilidad.** Fechas, estados, procedencia y secuencia temporal deben ser fáciles de distinguir, como registros de una bitácora.
5. **Cuidado colectivo y privacidad.** La atención relaciona a pacientes y equipos, pero cada dato clínico debe mostrarse solo con el acceso apropiado.
6. **Neutralidad política.** Se toma prestado un lenguaje gráfico histórico; no se usan consignas, símbolos partidarios ni exaltación de líderes como parte de la marca clínica.
7. **Coherencia entre motores.** La presentación no debe cambiar según PostgreSQL, MySQL, MongoDB o Firebase esté activo.

## 4. Paleta propuesta

Los valores siguientes traducen las referencias a una interfaz legible. Deben verificarse sobre los componentes reales antes de considerarse definitivos.

| Token | Color | Uso |
|---|---|---|
| `--ink` | `#171717` | Texto principal, navegación y superficies oscuras |
| `--graphite` | `#292626` | Paneles oscuros secundarios y barras |
| `--signal-red` | `#E31837` | Acciones principales, selección y acentos gráficos |
| `--deep-red` | `#A81029` | Rojo oscuro para elementos que llevan texto claro |
| `--paper` | `#F1E6C8` | Fondo cálido de áreas editoriales y paneles |
| `--surface` | `#FAF9F5` | Fondo de trabajo y formularios |
| `--white` | `#FFFFFF` | Tarjetas, campos y texto sobre superficies oscuras |
| `--muted` | `#77716C` | Texto secundario, bordes y metadatos |
| `--signal-amber` | `#D79A27` | Avisos y marcas de archivo, con etiqueta textual |
| `--signal-teal` | `#236B69` | Acento tecnológico ocasional; no sustituye estados semánticos |

### Reglas de color

- Mantener las pantallas de trabajo principalmente en `--surface` o `--paper`; reservar grandes áreas negras para portada, navegación o momentos de transición.
- Usar `--signal-red` con intención y en áreas pequeñas. No teñir de rojo todo lo importante: errores, urgencias y acciones destructivas deben tener significado diferenciado.
- No usar color como única indicación de estado. Acompañar cada estado con texto, icono o forma.
- Usar texto claro sobre `--deep-red` o `--ink`; validar el contraste de cada combinación. No colocar texto pequeño sobre rojo brillante ni sobre fondos con textura.
- El ámbar y el teal son acentos secundarios; no deben crear una segunda identidad visual dominante.

## 5. Tipografía y composición

### Tipografía

- **Titulares de campaña:** sans serif pesada, geométrica y preferiblemente condensada, con mayúsculas y escala grande. Usarla solo en títulos cortos.
- **Interfaz y lectura clínica:** sans serif de alta legibilidad, con formas abiertas y tamaños cómodos. Priorizar legibilidad sobre el parecido histórico.
- **Datos técnicos:** monoespaciada para códigos, números de expediente, marcas de tiempo o etiquetas de telemetría; nunca para párrafos largos.
- Evitar tipos decorativos o stencil en campos, instrucciones, diagnósticos y botones.

### Retícula

- Usar una retícula modular estable, alineaciones rectas y márgenes consistentes.
- Agrupar por paciente, episodio, consulta o tarea. Separar grupos con espacio y líneas finas antes de recurrir a paneles ornamentales.
- Permitir asimetría en portadas y separadores; mantener simetría funcional en formularios, tablas y datos comparables.
- Reservar texto vertical, numeración editorial y microetiquetas para navegación secundaria o material de portada.

## 6. Componentes de interfaz

- **Barra superior:** compacta, con nombre de la institución, usuario activo y acciones globales. Una línea fina puede evocar las reglas horizontales de los carteles.
- **Navegación lateral:** carbón o negro, con iconos sencillos, etiquetas textuales y selección roja claramente visible.
- **Búsqueda de paciente:** control prominente, amplio y de alto contraste; permitir búsquedas por los datos definidos por el sistema.
- **Resumen del paciente:** identidad y estado primero; separar datos de contacto de la información clínica restringida.
- **Historial:** línea temporal sobria con fechas, tipo de evento y profesional responsable. La ornamentación radial no debe interferir con la lectura cronológica.
- **Tablas y resultados:** superficies claras, columnas alineadas, encabezados persistentes cuando ayuden y acciones visibles sin depender de hover.
- **Formularios:** etiquetas explícitas, campos con espacio suficiente, errores junto al campo y confirmación visible después de guardar.
- **Estados:** texto y símbolos además del color. Distinguir información, aviso, error y urgencia clínica mediante patrones consistentes.
- **Vacíos y carga:** pueden usar motivos orbitales o de telemetría ligeros, acompañados por una explicación útil y una acción siguiente.

## 7. Recursos gráficos

Se permiten órbitas, arcos, coordenadas, marcas de calibración, cuadrículas, números de serie, sellos y diagramas esquemáticos de instrumentos. Deben funcionar como anotaciones y nunca como ruido detrás de los datos.

Las fotografías de archivo, collages y figuras históricas se reservan para páginas editoriales opcionales. Para su uso se debe verificar autoría, licencia y contexto. Las imágenes de referencia proporcionadas son moodboard; no se deben copiar al producto sin revisar derechos y pertinencia.

El cirílico puede aparecer como detalle ornamental en una pieza editorial si el equipo decide usarlo, pero no debe reemplazar etiquetas, controles ni contenido en español. Los símbolos de partido, consignas, retratos de dirigentes y emblemas soviéticos no se incorporan a los controles clínicos ni a la identidad funcional del sistema.

## 8. Movimiento y adaptación

- Usar movimiento breve y discreto: una órbita lenta, un pulso de carga o una transición de panel.
- Evitar parpadeos, barridos que cubran texto y animaciones que retrasen la atención a una alerta.
- Respetar la preferencia del sistema por movimiento reducido.
- En móvil, retirar adornos y microtexto antes de reducir el tamaño de los campos o de los datos clínicos.

## 9. Accesibilidad y seguridad visual

- Mantener lectura clara en pantalla, impresión y escala de grises.
- Dar foco visible a la navegación por teclado y mantener un orden de tabulación predecible.
- No comunicar resultados, riesgos ni estados únicamente mediante rojo, ámbar o teal.
- Evitar texturas detrás de párrafos, tablas o formularios.
- No mostrar datos sensibles en portadas, vistas previas o espacios editoriales.
- Mantener consistencia visual cuando cambie el motor de base de datos; el usuario no debe tener que interpretar detalles técnicos de persistencia.

## 10. Qué hacer y qué evitar

### Hacer

- Usar titulares grandes en entradas editoriales y títulos compactos en pantallas de trabajo.
- Combinar negro, rojo y marfil con superficies claras y amplias para leer expedientes.
- Aplicar numeración, diagramas y etiquetas como herramientas de orientación.
- Dar jerarquía a paciente, fecha, evento y responsable.
- Mantener una voz clínica respetuosa, directa y sin consignas.

### Evitar

- Convertir cada pantalla en un cartel político o en un collage.
- Usar rojo para todos los botones, advertencias y datos destacados.
- Simular paneles de telemetría que no aporten información útil.
- Usar tipografía condensada en texto largo o datos pequeños.
- Incorporar imágenes de líderes, propaganda o textos políticos como contenido clínico.
- Sugerir que la interfaz representa una tecnología histórica real de Sputnik 3; es una inspiración contemporánea.

## 11. Resumen de dirección

**Archivo editorial soviético + instrumentación espacial retro + aplicación clínica contemporánea.** La identidad debe ser reconocible en sus títulos, color y geometría; la operación clínica debe permanecer tranquila, comprensible, privada y consistente.

## 12. Referencias consultadas

### Textos proporcionados

- Strada, Vittorio. “Socialismo y comunismo”. _El Socialismo del Futuro_, n.º 4, 1991, pp. 65–70. Archivo proporcionado: `6_1_vittorio-strada_socialismo-y-comunismo-_nc2ba-4_1991_editado.pdf`.
- Harnecker, Marta, con colaboración de Gabriela Uribe. _Socialismo y comunismo_. Akal Editor, edición revisada, 1979. Archivo proporcionado: `88350.pdf`.
- Marx, Karl y Friedrich Engels. _Manifiesto comunista_. Edición digital de elaleph.com, 2000. Archivo proporcionado: `marx-manifiesto-comunista.pdf`.

### Imágenes proporcionadas

- Capturas de USSR × Design y una tarjeta de paleta negro-rojo-blanco.
- Ilustración de Lenin con haces radiales y acentos cálidos.
- Referencia de catálogo rojo y marfil con selección central geométrica.
- Tres láminas editoriales sobre arte, publicidad y moda soviéticas.
- Una imagen negra sin contenido visual legible, excluida como referencia activa.
