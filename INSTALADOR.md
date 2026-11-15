# Construir y comprobar el instalador local

El instalador Windows 0.3.0 se construye desde esta copia y su `.venv`, preparada mediante [INSTALACION.md](INSTALACION.md). No utiliza el entorno ni el instalador del proyecto original. La construcción es local: no firma, sube ni publica archivos.

## Construcción

Desde PowerShell en el repositorio:

```powershell
.\.venv\Scripts\python.exe -B packaging\build_local.py
```

Se requieren Windows x64, CPython 3.13.7 y la `.venv` de esta carpeta con las versiones fijadas, además del compilador .NET Framework de Windows. El empaquetador comprueba versiones antes de construir. El instalador usa .NET Framework con soporte de rutas largas (4.6.2 o posterior); el comportamiento se verifica en este ordenador, sin acreditar otros equipos o versiones de Windows.

La carpeta `dist-local/`, excluida de Git, contiene:

| Archivo | Contenido |
|---|---|
| `Anonimizar-Setup-0.3.0-win-x64.exe` | Instalador local con payload incrustado |
| `Anonimizar-Setup-0.3.0-win-x64.exe.sha256` | SHA-256 del ejecutable generado |
| `build.json` | Versión, hash del instalador y del payload, número de archivos |
| `payload.zip` | Intermedio de construcción con manifiesto SHA-256 por archivo |
| `Anonimizar.exe`, `Desinstalar.exe` | Lanzador y desinstalador incluidos en el payload |

No se promete igualdad binaria con el instalador anterior. Los hashes detectan diferencias respecto de este artefacto, pero no sustituyen la firma de un editor. Este ejecutable local no está firmado; la aceptación por SmartScreen y antivirus en otros equipos no se ha comprobado.

## Contenido del paquete

Incluye código de la aplicación, modelo y dependencias instaladas, runtime Python independiente, configuración local, recursos visuales, documentación y avisos íntegros. Se incluyen también scripts y manifiestos de procedencia para conservar los enlaces documentales. Los comandos de desarrollo de README/INSTALACION corresponden al repositorio, no a la carpeta instalada: esta última utiliza `runtime/`, sin `.venv`.

Se excluyen `.data`, bases de documentos/cuentas, OAuth, credenciales, wheels, cachés de Python, registros de prueba, carpetas de trabajo y el complemento experimental. La revisión de contenido verifica todas las entradas del manifiesto y los enlaces Markdown locales del paquete. Los certificados públicos de confianza de las dependencias y sus avisos se conservan; no son credenciales de usuario.

## Prueba aislada y repetible

```powershell
.\.venv\Scripts\python.exe -B tools\verificar_instalador.py
```

El script crea un directorio nuevo bajo `verificacion-local/instalador/ejecucion-*`, conserva las evidencias y ejecuta el mismo instalador con `--quiet-test --test-root RUTA_ABSOLUTA`. El directorio lleva un marcador explícito; el instalador rechaza el modo silencioso sin esa raíz marcada. No se deben usar esos argumentos para una instalación habitual.

En ese modo, los programas, datos ficticios, accesos de escritorio y menú se crean dentro del perfil de prueba. La inscripción habitual en Aplicaciones instaladas y las notificaciones del escritorio se omiten. Se escribe y comprueba una clave real exclusiva bajo `HKCU\Software\Anonimizar\InstallerTests\<id>\Uninstall\Anonimizar`, más una ficha JSON que distingue esa clave de la inscripción habitual. La migración lee únicamente los datos ficticios de ese perfil. El script compara los punteros y claves de desinstalación habituales antes y después.

La prueba cubre integridad del payload y archivos instalados, migración de un historial ficticio conservando la base anterior, modelo y sustitución sintética, página inicial en AppTest, guardado/exportación/papelera/restauración/importación, lanzador C#, identidad HTTP, segunda apertura y cierre. También comprueba rechazo de un payload alterado. Cada ejecución crea evidencias nuevas y no elimina las anteriores.

La inscripción habitual en Aplicaciones instaladas y los diálogos nativos de confirmación no se ejecutan en estas pruebas. El desinstalador sí se ejecuta dentro del alcance aislado, con decisiones de prueba explícitas. Tampoco se acredita revisión visual en navegador, instalación en otro ordenador ni auditoría completa de red o del detector. Los resultados y pendientes están en [PREPARACION.md](PREPARACION.md).

## Ciclo de desinstalación y reinstalación

```powershell
.\.venv\Scripts\python.exe -B tools\verificar_desinstalacion.py
```

Esta prueba comienza verificando el instalador actual, después siembra historial, papelera, ajustes y una exportación ficticios. Cancela una desinstalación, comprueba el bloqueo con el motor activo y prueba rechazo de una unión de directorios y de una inscripción que apunta a otro lugar. Compara archivos y claves testigo antes y después. Finalmente desinstala y reinstala el mismo artefacto y verifica que los datos protegidos conservan sus hashes y que el modelo sigue funcionando.

El desinstalador identifica las versiones mediante `.anonimizar-installation.json` e `installed.ok`. Solo retira carpetas de versión que pertenecen al alcance calculado, el puntero correspondiente, accesos cuyo destino coincide y su clave exacta de registro. Conserva directorios ajenos aunque estén dentro de la carpeta de programas y deja el menú si contiene otros archivos. Las versiones antiguas sin marcador de propiedad no se eliminan automáticamente.

El proceso inicial confirma la decisión y comprueba el motor. Copia un auxiliar a `Anonimizar/uninstall-work/<id>` dentro de la carpeta de datos; ese auxiliar espera a que termine el proceso inicial y realiza el borrado fuera de la carpeta del programa. No usa una cadena de borrado en PowerShell. Las rutas absolutas se verifican antes del borrado y se rechazan enlaces/uniones en las carpetas propias.

El código de salida del proceso inicial indica si la solicitud pudo iniciarse; **no acredita que haya terminado el borrado**. El resultado definitivo queda en `result.json` del directorio del auxiliar, con estado `pending`, `completed` o `failed`, mensaje y rutas retiradas. Las comprobaciones esperan un estado final, y un fallo no se registra como éxito. En el uso habitual el auxiliar muestra el resultado; en la prueba se consulta el JSON.

Los documentos, papelera, ajustes, exportaciones, copias de recuperación y registros quedan fuera de las carpetas retiradas. El auxiliar y sus informes se conservan junto a los datos como evidencia. El modo aislado requiere raíz marcada, identificador de prueba y exactamente una decisión `--confirm-test` o `--cancel-test`; esas decisiones automáticas no se aceptan en el modo habitual.

La prueba usa seis archivos testigo, incluidos uno dentro de la carpeta de programas y otro en el menú, y dos claves testigo vecinas. Se han comprobado los valores de destino, directorio de trabajo e icono de los accesos y los valores de la clave de prueba. Esto no equivale a probar la lista habitual de Aplicaciones instaladas ni los diálogos nativos: esos controles siguen pendientes en un entorno Windows separado.

## Corrección encontrada durante la comprobación

La primera extracción de prueba falló al superar 260 caracteres en la ruta aislada. Se conserva esa candidata y su extracción fallida en las evidencias locales. El instalador incorpora un manifiesto Windows `longPathAware` y activa el manejo de rutas largas de .NET en su proceso, sin cambiar el registro del sistema. Referencias: [normalización de rutas de .NET](https://learn.microsoft.com/en-us/dotnet/framework/migration-guide/mitigation-path-normalization) y [límites de rutas de Windows](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation).

Las atribuciones y condiciones de [LICENCIAS.md](LICENCIAS.md) y [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md) permanecen. La construcción y las pruebas locales no resuelven permisos de redistribución de recursos ni conceden una licencia nueva.
