# Revisión UX/UI y QA del frontend

Fecha de revisión: 25 de octubre de 2026

## Alcance

Se revisó la maqueta frontend en `frontend`: portada de declaración pública, navegación clínica, cambio local de institución, estados sin servidor y formularios de demostración. La fase solicitada no incluye API, autenticación, reglas de dominio en servidor ni persistencia, por lo que no se presentan esos flujos como operativos.

## Revisión UX/UI

En la revisión independiente, el detector `impeccable detect` se ejecutó sobre `src/App.tsx`, `src/domain/institutions.ts` e `index.html` y devolvió cero hallazgos automáticos. La revisión heurística independiente encontró riesgos de claridad y uso que se corrigieron en esta rama:

| Hallazgo | Prioridad | Ajuste aplicado |
|---|---|---|
| La búsqueda parecía funcionar sin API y borraba el criterio escrito. | Alta | Búsqueda y botón deshabilitados; estado de servidor pendiente explicado junto al control. |
| Formularios con datos sensibles podían inducir a ingresar información real y limpiar lo escrito. | Alta | Aviso visible antes de los campos, uso de datos inventados, envío etiquetado como validación local y conservación de valores en pantalla. |
| Tres controles distintos cambiaban la institución y las pestañas tenían semántica ARIA incompleta. | Media | Se conserva una sola franja de botones con `aria-pressed`; el pie muestra las instituciones como texto. |
| Identidad de mesa y sesión podía sugerir autenticación existente. | Media | Encabezado cambiado a `CLIENTE / MAQUETA`; el selector se declara local. |
| Etiquetas pequeñas y ausencia de salto al contenido. | Media | Tipografía de navegación y campos aumentada; añadido enlace accesible para saltar al contenido. |

La interfaz conserva la navegación a operaciones generales y específicas por institución. El manifiesto político y su ilustración editorial son la entrada; la mesa de trabajo mantiene la composición aprobada como segundo referente.

## QA ejecutado

- `npm run build`: correcto (TypeScript y compilación de producción Vite).
- `npm install`: revisión del árbol de dependencias sin vulnerabilidades reportadas en el momento de instalación.
- Recorrido manual con navegador integrado: entrada desde la portada; cambio de institución; navegación a laboratorio y pediatría; apertura de formularios y agregado de filas de parámetros.
- Tras los cambios se verificó de nuevo el flujo de laboratorio: se ingresaron valores marcados como ficticios, se ejecutó la validación y los valores permanecieron en pantalla. El aviso confirmó que no se enviaron ni guardaron.
- Captura visual de escritorio revisada con la portada completa y su declaración política, CTA e imagen editorial.
- En una pasada previa a los últimos cambios se comprobó ausencia de desbordamiento horizontal en las dimensiones disponibles del navegador, tanto en escritorio como en móvil. La medición móvil correspondió a 349 px de ancho de ventana interior.
- El prototipo mostró el estado de API desconectada en los flujos revisados.

## Límites de la evidencia

- El entorno disponible no expuso una consola del navegador para la última revisión; el estado de errores de consola queda sin confirmar.
- La evaluación del agente independiente no pudo medir móvil ni inyectar el overlay de inspección; su captura de escritorio no permite concluir desbordamiento.
- No se ejecutó `impeccable audit`: el comando no está disponible en la instalación local. Se usaron el detector automático y una revisión heurística independiente.
- La comprobación anterior de tamaños ocurrió antes de los últimos cambios de aviso y accesibilidad. Se recomienda una pasada final en dispositivos reales cuando se integre en un entorno con navegador medible.
- El comando local `impeccable` no estaba disponible para repetir el detector luego de aplicar los ajustes; el resultado de cero hallazgos pertenece a la revisión independiente previa a los cambios.
- No se verificaron conexiones HTTP, autenticación, persistencia, aislamiento entre instituciones ni reglas clínicas porque aún no existe backend.

## Pendientes de QA para la integración

1. Probar búsqueda y formularios contra una API real con cuentas de prueba y datos sintéticos.
2. Validar permisos y aislamiento institucional desde el servidor; el selector actual es solo visual.
3. Revisar teclado, lector de pantalla, zoom y tamaños móviles con herramientas de inspección completas.
4. Verificar flujos de carga, error, reintento y confirmación tras conectar persistencia.
