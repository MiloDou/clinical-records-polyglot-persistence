# Frontend: estructura y puntos de integración

## Alcance implementado

El cliente permite recorrer una portada editorial, abrir la mesa clínica, cambiar la institución visible y navegar por operaciones comunes y especializadas. Presenta búsquedas, formularios y estados vacíos. No hay autenticación, API ni conexión a una base de datos. El selector de institución solo cambia el contexto visual local y **no representa identidad, autorización ni enrutamiento real**.

La búsqueda queda deshabilitada sin servidor. Los formularios de demostración muestran sus campos con un aviso visible para usar únicamente datos inventados; su validación es del navegador y no transmite ni guarda valores. Al probarla, conserva lo escrito en la pantalla. No se incluyen pacientes ficticios ni persistencia en almacenamiento local.

## Cómo está conectado

```text
index.html
  └─ src/main.tsx  carga React, tipografías y estilos globales
       └─ src/App.tsx  controla la vista, institución, sección y avisos de interfaz
            └─ src/domain/institutions.ts  crea el espacio de trabajo y define módulos
                 └─ src/styles.css  tokens, composición editorial y adaptación responsive
```

- Vite sirve la aplicación y compila el directorio `dist/`.
- React conserva en memoria el estado de vista, institución, sección y formularios abiertos.
- `createInstitutionWorkspace(id)` es el punto Factory Method: a partir de una institución construye el menú especializado, usando una navegación compartida. La franja de botones de institución es solo un selector de presentación local.
- Los campos de los formularios se describen en `src/App.tsx`; el catálogo de operaciones y sus estados vacíos vive en `src/domain/institutions.ts`. El registro pediátrico incluye a la persona tutora y resultados de laboratorio permiten agregar parámetros variables.
- `showUnavailable()` concentra la respuesta temporal para las acciones que necesitarán servidor.
- Los íconos pertenecen a Lucide. Las fuentes Inter y Karantina se empaquetan localmente mediante Fontsource.
- La ilustración de portada está en `public/images/salud-comunitaria.png`; su prompt y uso están documentados en el archivo `.prompt.json` adyacente.

## Módulos visibles

| Módulo | Institución |
|---|---|
| Búsqueda, pacientes, historial, citas, consultas, diagnósticos, tratamientos, recetas y archivo | Todas |
| Procedimientos | Clínica Odontológica |
| Órdenes de examen y resultados con parámetros variables | Laboratorio Clínico |
| Crecimiento y vacunación | Centro Médico Pediátrico |

Hospital General, Clínica Odontológica, Laboratorio Clínico y Centro Médico Pediátrico se presentan como una sola familia de interfaz. La elección final de motores no debe filtrarse al cliente.

## Puntos sensibles

1. **`src/domain/institutions.ts`:** los identificadores tipados y el catálogo `institutions` conectan selector local, fábrica y menú. Al agregar o renombrar una institución, actualice todas esas fuentes juntas. No asigne motores aquí.
2. **`createInstitutionWorkspace`:** mantiene un lenguaje común y agrega solo las operaciones propias de cada institución. Evite duplicar la navegación o incorporar condiciones por motor.
3. **`src/App.tsx`:** es composición y estado de interfaz, no una capa de autorización. La selección local nunca debe utilizarse para decidir acceso a expedientes.
4. **`showUnavailable`:** es un aviso temporal para acciones que no guardan. Al conectar una API, sustitúyalo por llamadas a un cliente adaptador con estados de carga, error y éxito verdaderos; no presente éxito hasta tener evidencia de persistencia.
5. **Formularios:** actualmente solo recorren campos y validación HTML local. La advertencia de demostración debe permanecer antes de campos sensibles; no agregue `localStorage`, datos de ejemplo que parezcan reales, analítica con campos clínicos ni trazas que capturen datos.
6. **`src/styles.css`:** concentra la composición y tokens visuales. Mantenga legibles las pantallas clínicas aunque ajuste la portada política o la gráfica editorial.
7. **`public/images/salud-comunitaria.png`:** es una imagen generada, no una fotografía documental. Mantenga junto a ella el sidecar de procedencia cuando la reemplace o genere otros rasteres.

## Integración futura con el servidor

La siguiente etapa debe añadir un cliente HTTP/adaptador bajo una frontera tipada. El cliente autentica mediante el mecanismo acordado y envía operaciones de negocio a la API. El servidor valida la identidad, deriva la institución de las credenciales confiables, ejecuta las reglas comunes y dirige la persistencia al motor asignado a esa institución.

```text
Interfaz → puerto/API cliente → servidor y casos de uso → puerto de repositorio
                                               ├─ adaptador PostgreSQL
                                               ├─ adaptador MySQL
                                               ├─ adaptador MongoDB
                                               └─ adaptador Firebase
```

La interfaz no debe abrir conexiones directas a motores ni elegir adaptadores. La asignación de motor todavía está pendiente de la documentación del proyecto. Operaciones de registrar consulta, agregar diagnóstico y recetar medicamento deben compartir reglas de negocio en el servidor, aunque sus adaptadores guarden datos con modelos diferentes.

## Decisiones KISS

- No se añadió un router, gestor global de estado, framework de componentes o biblioteca de formularios: la aplicación tiene una sola superficie y el estado transitorio cabe en React.
- La fábrica es una función de dominio pequeña y tipada, sin jerarquías de clases. Devuelve la configuración que la navegación necesita.
- Los componentes están concentrados en `App.tsx` porque solo se usan en esta superficie; sepárelos cuando exista una segunda vista que realmente comparta el componente.
- La compilación TypeScript está en modo estricto y marca imports o variables sin uso.
