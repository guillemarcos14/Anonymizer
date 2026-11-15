# Anonimizar local 0.3.0 — Windows x64

Guía del funcionamiento actual. Esta copia está en preparación y todavía no se distribuye desde GitHub. Para requisitos y el proceso completo de descarga pública e instalación offline, consultar [INSTALACION.md](INSTALACION.md).

## Abrir y cerrar

Con `.venv` instalada en esta carpeta, ejecutar `./iniciar.ps1` desde PowerShell. El lanzador abre el navegador; no se requiere cuenta. Una segunda apertura reutiliza el motor existente. Si el puerto habitual está ocupado, el lanzador busca otro puerto local sin detener procesos ajenos.

Para detener el motor, usar **Configuración → Cerrar Anonimizar y detener el motor**. Cerrar solo la pestaña deja el motor disponible para volver a abrirlo. El servidor escucha en `127.0.0.1`: el navegador es la ventana, no un servicio alojado.

El instalador generado crea accesos en escritorio e Inicio e incluye Python y modelo; su uso no requiere instalar Python por separado. Ese instalador no forma parte del repositorio. La construcción y la prueba local se describen en [INSTALADOR.md](INSTALADOR.md); la instalación externa representativa sigue pendiente.

## Texto y revisión

Pegar hasta 10.000 caracteres, enviar, revisar y copiar o descargar el resultado. Revisar tanto omisiones como sustituciones incorrectas, nombres, atribuciones y detalles indirectos que permitan identificar a alguien. No se garantiza detección completa ni anonimización irreversible. La disponibilidad de una opción no implica que tenga validación general; ver [condiciones y alcance](CONDICIONES-ENTREGA.md).

## Historial y privacidad

- El historial está activado por defecto, salvo preferencia explícita guardada. Se desactiva en Configuración. Desactivarlo impide guardar nuevos resultados automáticamente, pero no elimina los anteriores.
- Historial y ajustes viven en `%LOCALAPPDATA%\Anonimizar`, fuera del programa. Un documento guardado conserva original, configuración del documento y revisión. Los ajustes generales excluyen textos, listas libres y claves de cifrado. El borrador no se guarda en disco por la aplicación.
- El producto no cifra el historial ni ofrece bloqueo propio. El acceso al mismo usuario de Windows permite acceder a los datos. No hay sincronización ni autenticación externa; las estadísticas de uso de Streamlit están desactivadas.
- Configuración permite exportar/importar JSON, enviar documentos a la papelera, restaurarlos y vaciarla con confirmación. Borrar del historial no borra exportaciones o copias anteriores, ni garantiza borrado forense.
- Vaciar o cerrar no elimina necesariamente RAM, paginación, portapapeles, descargas o copias del sistema. Las limitaciones de red y tratamiento están en [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md).

## Compatibilidad y recuperación

Las bases antiguas por cuenta no se incluyen en esta copia. Si existen en una instalación anterior, Configuración permite copiar expresamente una colección; repetir la operación no la duplica. Antes de copiar se crea una instantánea en `recovery/legacy-documents.sqlite3`. Esa instantánea puede contener otras colecciones: es una copia de recuperación, no el historial activo. Los originales anteriores se conservan.

El código mantiene la compatibilidad con el nombre anterior del producto. Esos identificadores no representan cuentas externas activas ni recursos que deban incluirse en Git.

## Actualización, desinstalación y errores

Cerrar el motor y ejecutar el siguiente instalador cuando exista una distribución autorizada. El instalador usa un directorio versionado dentro de `%LOCALAPPDATA%\Programs\Anonimizar`; actualiza los accesos y conserva los datos por separado. Las versiones anteriores se mantienen para recuperación y pueden abrirse con el motor detenido. No hay canal público ni descarga automática de actualizaciones.

La desinstalación habitual se ofrece desde Configuración de Windows → Aplicaciones y requiere confirmación. Verifica que el motor esté detenido y conserva los datos del usuario. Esa integración habitual y sus diálogos aún necesitan validación separada; el ciclo aislado está documentado en [INSTALADOR.md](INSTALADOR.md). Solo se retiran versiones identificadas como propias; los archivos ajenos y versiones antiguas sin marcador se conservan. No borrar la carpeta de datos sin exportar antes lo que se quiera conservar.

Si falla el arranque, el lanzador muestra el error y la ruta del registro en `logs`. El lanzador no añade texto de documentos a sus mensajes, pero no se garantiza saneamiento universal de todos los errores de dependencias. Comunicar versión, plataforma, pasos y error con ejemplos ficticios, sin expedientes.

## Construcción y documentación

`instalar.ps1` prepara el entorno de desarrollo; no es el instalador del usuario final. `iniciar.ps1` usa `.venv`. `packaging/build_local.py` construye el instalador offline desde ese entorno y CPython 3.13.7. El manifiesto y SHA-256 se generan en `dist-local/build.json`. El ejecutable no está firmado con certificado de editor. Consultar los comandos y requisitos en [README.md](README.md).

Las atribuciones y condiciones están en [LICENCIAS.md](LICENCIAS.md) y [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md). La [guía anterior íntegra](avisos/historico-producto/LOCAL-antes-de-limpieza.txt) se conserva como referencia histórica, sin sustituir este estado.
