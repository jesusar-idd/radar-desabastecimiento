# Data inventory

## AEMPS / CIMA

### Fuente
CIMA REST API v1.23 de la Agencia Española de Medicamentos y
Productos Sanitarios (AEMPS).

### Problemas de suministro

Endpoints principales:

- `GET psuministro?{condiciones}`
  - Devuelve los problemas de suministro actuales.
- `GET psuministro/:codNacional`
  - Devuelve los problemas de suministro asociados a un Código Nacional.

### Campos
- `cn`: Código Nacional
- `nombre`: nombre de la presentación
- `fini`: fecha de inicio del problema
- `ffin`: fecha prevista de fin; para problemas no activos,
  corresponde a la fecha en la que se solucionó
- `observ`: observaciones
- `activo`: indica si el problema continúa activo

### Fechas

Los campos `fini` y `ffin` se proporcionan mediante timestamps
Unix Epoch/POSIX. `ffin` puede no estar informado cuando el problema
continúa activo.

### tipoProblemaSuministro
Código categórico asociado al problema de suministro.

Los códigos 1–9 están documentados en la documentación específica de
CIMA/AEMPS sobre problemas de suministro. En los datos actuales de la API
también aparecen los códigos 10, 11 y 12, pero no se ha localizado en la
documentación REST consultada una tabla oficial que defina explícitamente
estos tres códigos.

| Código | Significado |
|---:|---|
| 1 | Consultar Nota Informativa |
| 2 | Suministro sólo a hospitales |
| 3 | El médico prescriptor deberá determinar la posibilidad de utilizar otros tratamientos comercializados |
| 4 | Desabastecimiento temporal |
| 5 | Existe/n otro/s medicamento/s con el mismo principio activo y para la misma vía de administración |
| 6 | Existe/n otro/s medicamento/s con los mismos principios activos y para la misma vía de administración |
| 7 | Se puede solicitar como medicamento extranjero |
| 8 | Se recomienda restringir su prescripción reservándolo para casos en que no exista una alternativa apropiada |
| 9 | El titular de autorización de comercialización está realizando una distribución controlada al existir unidades limitadas |
| 10 | Comercialización excepcional autorizada por AEMPS* |
| 11 | Existen tratamientos alternativos no sujetos a prescripción* |
| 12 | Distribución controlada a hospitales por el titular* |

\* Para los códigos 10–12, estas descripciones se han observado en el
campo `observ` de los registros actuales de la API, pero no se ha localizado
una definición oficial explícita en la documentación consultada.

### Formato
- Respuesta: JSON
- Codificación: UTF-8
- Fechas: Unix Epoch (POSIX), GMT+2:00

### Histórico
El endpoint general devuelve los problemas de suministro actuales.
La consulta por Código Nacional puede devolver problemas que ya han
sido solucionados.

Pendiente de comprobar mediante pruebas de consulta qué cobertura
histórica podemos obtener de forma sistemática.

### Registro de cambios

La API también dispone de `registroCambios`, que permite consultar
medicamentos dados de alta, baja o modificados desde una fecha.
Entre los tipos de cambio se encuentra `psum`, relacionado con
problemas de suministro.

### Presentaciones

Endpoint validado:

GET /presentacion/:codNacional

Permite obtener información detallada de una presentación a partir
de su Código Nacional.

Campos relevantes identificados:

| Campo | Descripción | Uso previsto |
|---|---|---|
| cn | Código Nacional | Clave de unión |
| nregistro | Número de registro | Identificador CIMA |
| nombre | Nombre de la presentación | Identificación |
| pactivos | Principios activos | Identificación |
| labtitular | Laboratorio titular | Caracterización |
| cpresc | Condiciones de prescripción | Caracterización |
| comerc | Indica si está comercializada | Caracterización |
| receta | Indica si requiere receta | Caracterización |
| generico | Indica si es genérico | Caracterización |
| biosimilar | Indica si es biosimilar | Caracterización |
| psum | Indica si tiene problemas de suministro abiertos | Validación |
| principiosActivos | Lista de principios activos | Tabla relacionada |
| atcs | Lista de códigos ATC | Tabla relacionada |

### Observación sobre estructuras anidadas

La respuesta contiene estructuras de tipo lista, como `principiosActivos`
y `atcs`. Estas estructuras no se tratarán inicialmente como columnas
simples, sino como entidades relacionadas en el proceso de transformación.

## ISCIII

## Ministerio de Sanidad

## Open-Meteo