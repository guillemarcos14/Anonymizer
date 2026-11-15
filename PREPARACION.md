# Estado de preparación — Anonimizar Windows 0.3.0

Actualizado el 15/11/2026. Código publicado por autorización expresa de Guillem en [guillemarcos14/Anonimizar](https://github.com/guillemarcos14/Anonimizar). Esta copia está versionada y conectada a ese remoto público. El complemento experimental de ChatGPT y la web pública permanecen fuera. El proyecto original no se ha modificado.

## Comprobado localmente

| Área | Resultado y alcance |
|---|---|
| Documentación | Instrucciones actuales separadas del historial; 19 enlaces antiguos retirados de la navegación disponible y conservados como referencias explícitas. Seis instantáneas íntegras y avisos de terceros preservados. |
| Dependencias y modelo | Descarga pública de las 82 dependencias y pip, con URLs y SHA-256 fijados. Instalación nueva sin carpeta auxiliar, `pip check`, versiones, modelo y sustitución sintética superados. |
| Construcción | Instalador generado desde esta copia y su `.venv`, con runtime, modelo, documentación y avisos. Manifiesto por archivo y SHA-256 externo. Las pruebas comprueban el paquete y cada archivo instalado. |
| Instalación y aplicación | Instalación en perfil aislado con rutas largas, migración de historial ficticio conservando la base anterior, página inicial en AppTest, sustitución sintética, guardar/exportar/papelera/restaurar/importar, lanzador C#, identidad HTTP, segunda apertura y cierre correcto. |
| Controles negativos | Kit alterado rechazado antes de crear entorno; payload del instalador alterado rechazado; modo silencioso sin raíz marcada rechazado. Registro y punteros habituales de instalación sin cambios en la prueba. |

Estas comprobaciones se realizaron en este ordenador. No acreditan una instalación externa representativa, revisión visual en navegador, detección total, auditoría integral de red o equivalencia binaria con el instalador anterior. La integración habitual de Aplicaciones instaladas y los diálogos nativos no se han ejecutado. El ciclo de desinstalación y reinstalación sí se ha probado en un perfil y una clave de registro exclusivos, con datos ficticios y testigos.

## Antes de publicar

1. Decidir los términos de las aportaciones propias para GitHub. No se ha elegido licencia nueva ni se amplían permisos de terceros por esta preparación.
2. Resolver los permisos de recursos visuales documentados en [assets/PROCEDENCIA-ENTRADA.md](assets/PROCEDENCIA-ENTRADA.md), o sustituir los afectados.
3. Validar en otro entorno Windows la integración habitual de Aplicaciones instaladas y los diálogos de instalación/desinstalación; decidir la distribución pública del ejecutable. El instalador local no está firmado y no se ha comprobado su aceptación por SmartScreen o antivirus externos.
4. Completar las verificaciones de interfaz, calidad y privacidad según el alcance que se quiera ofrecer. Repetir la revisión de secretos antes de un primer envío.

## Procesos disponibles en la copia

[INSTALACION.md](INSTALACION.md) describe la adquisición pública y la instalación desde un kit local verificado. Se mantienen las 82 versiones de ejecución. `htbuilder` 0.9.0 se construye desde la fuente oficial con hash, porque el wheel histórico no está publicado en PyPI. Pip 26.0.1 se fija aparte y setuptools 84.2.1 se obtiene del mismo kit. Los bloqueos históricos permanecen íntegros.

[INSTALADOR.md](INSTALADOR.md) describe la construcción y prueba aislada del ejecutable. Se añadió un modo de prueba que requiere una raíz marcada y evita la inscripción real en el registro. Una extracción inicial falló por el límite de rutas largas de .NET; esa candidata y su extracción se conservan. La corrección del instalador permite repetir la instalación en rutas de más de 260 caracteres sin cambiar el registro del sistema.

El código de ejecución del motor y la aplicación conserva sus bytes. Los cambios técnicos afectan a la adquisición de dependencias, comprobaciones y empaquetado; los cambios documentales separan lo vigente de lo histórico. El archivo histórico está en [avisos/historico-producto/README.md](avisos/historico-producto/README.md). Las atribuciones y condiciones se mantienen en [LICENCIAS.md](LICENCIAS.md) y [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md).

## Artefactos y evidencias

El instalador, SHA-256, `build.json` y el intermedio `payload.zip` están en `dist-local/`, excluido de Git. Las descargas de `wheelhouse/` y el entorno `.venv` también están excluidos. No se incluyen bases de usuarios, credenciales, OAuth, archivos de trabajo ni evidencias en el paquete.

Las comprobaciones actuales guardan resultados y registros bajo `verificacion-local/instalacion/` y `verificacion-local/instalador/ejecucion-*`, excluidos de Git. Cada prueba del instalador conserva sus datos ficticios y resultados. Los informes iniciales de selección, limpieza e integridad se conservan en la carpeta auxiliar hermana `Anonimizar-GitHub-preparacion`; los procesos nuevos no la necesitan. La comprobación inicial del original verificó 34.016 archivos sin cambios; no se ha escrito en ese árbol durante esta preparación.

Los resultados verifican los artefactos concretos identificados por sus hashes. Los informes anteriores no se convierten en validación de cambios posteriores: tras una nueva construcción debe ejecutarse de nuevo la prueba del instalador.

## Desinstalación aislada y reinstalación — 15/11/2026

Se incorpora un alcance común entre instalador y desinstalador, con marcador de propiedad para cada versión y clave exclusiva de prueba. El desinstalador comprueba el motor, rechaza enlaces/uniones, conserva carpetas ajenas y espera fuera del programa mediante un auxiliar que produce un resultado final verificable. No se elimina ninguna carpeta de datos ni se ejecuta el borrado mediante PowerShell.

El ciclo comprobado cubre cancelación, motor activo, unión de directorios, registro incoherente con resultado de fallo, retirada de programa/accesos/clave propia y reinstalación. Historial, papelera, ajustes y exportación conservan sus bytes; seis archivos y dos claves testigo permanecen intactos. Los accesos se han leído mediante COM y sus destinos/iconos, junto con los valores de la clave de prueba, son correctos. Los punteros y claves habituales no cambiaron.

Las evidencias se conservan en `verificacion-local/desinstalador/ejecucion-*`. La prueba usa decisiones explícitas en lugar de pulsar los diálogos nativos. No acredita la inscripción habitual de Windows, un ordenador diferente ni una revisión general de seguridad frente a todos los cambios concurrentes o atacantes locales. Los archivos anteriores y el original permanecen preservados; no hay publicación ni licencia nueva.

## Publicación del código — 15/11/2026

Guillem ha elegido expresamente un repositorio público y visible en su perfil. Se publica el código revisado, conservando avisos y condiciones. Las referencias anteriores a no publicar describen las fases previas de preparación. Esta autorización no elige una licencia global ni resuelve automáticamente permisos de recursos visuales. Los datos, credenciales, entornos, evidencias locales e instaladores permanecen fuera del repositorio Git. El instalador probado sigue disponible localmente; no se ha creado una release de descarga.
