# Anonimizar 0.3.0 para Windows

Aplicación local para revisar y sustituir datos identificativos en texto en español mediante Presidio. El navegador muestra la interfaz y el motor escucha en `127.0.0.1`. No requiere cuenta. Límite provisional: 10.000 caracteres. Toda salida requiere revisión humana: puede contener omisiones y falsos positivos.

**Estado: código publicado en [GitHub](https://github.com/guillemarcos14/Anonimizar).** Esta copia contiene la aplicación Windows. El complemento experimental de ChatGPT y la web pública quedan fuera. La licencia de las aportaciones propias, los permisos de algunos recursos visuales siguen pendientes; ver [PREPARACION.md](PREPARACION.md).

## Instalar en Windows

**[Descargar Anonimizar 0.3.0 para Windows x64](https://github.com/guillemarcos14/Anonimizar/releases/download/v0.3.0/Anonimizar-Setup-0.3.0-win-x64.exe)** · [SHA-256](https://github.com/guillemarcos14/Anonimizar/releases/download/v0.3.0/Anonimizar-Setup-0.3.0-win-x64.exe.sha256) · [Notas de la versión](https://github.com/guillemarcos14/Anonimizar/releases/tag/v0.3.0)

1. Descarga y ejecuta el instalador en Windows x64. Requiere .NET Framework 4.6.2 o posterior.
2. Confirma la instalación para tu usuario. Incluye Python, motor y modelo; no necesitas instalarlos por separado.
3. Abre **Anonimizar** desde el escritorio o Inicio, pega texto y revisa siempre el resultado antes de compartirlo.

Es una **versión preliminar**, probada con datos ficticios en un equipo Windows. El instalador no tiene firma de editor; Windows puede mostrar una advertencia. Las pruebas en otro equipo y los diálogos e integración habitual de Windows siguen pendientes. Consulta las notas de la versión para el hash y el alcance de las comprobaciones.

## Instalar para desarrollar

Se requiere Windows x64 y [CPython 3.13.7 x64](https://www.python.org/downloads/release/python-3137/). Los scripts obtienen el conjunto fijado y el modelo desde PyPI y la publicación oficial de Explosion, sin usar el proyecto original ni la carpeta auxiliar.

En PowerShell, desde esta carpeta:

```powershell
.\descargar-dependencias.ps1 -Python 'C:\ruta\Python313\python.exe'
.\instalar.ps1 -Python 'C:\ruta\Python313\python.exe'
.\iniciar.ps1
```

La descarga necesita Internet y verifica los hashes de las 82 dependencias y de pip. La instalación posterior usa solo el kit local, fija versiones y rechaza un entorno existente. Conserva las versiones de 0.3.0; `htbuilder` se construye desde su fuente oficial verificada, porque el wheel local anterior no está publicado en PyPI. No se promete un instalador idéntico byte a byte.

Consultar [INSTALACION.md](INSTALACION.md) para requisitos, hashes, uso sin red, diagnóstico y diferencia entre el bloqueo público y el histórico. Los paquetes en `wheelhouse/`, el entorno `.venv` y las evidencias locales quedan fuera de Git.

Para detener el motor, usar **Configuración → Cerrar Anonimizar y detener el motor**. Cerrar solo la pestaña deja el motor activo. El instalador se distribuye por separado en la release enlazada arriba y no se guarda en el historial Git.

## Uso, datos y límites

Pegar texto, enviar, revisar y copiar o descargar el resultado. El historial está activado por defecto y conserva original y revisión en `%LOCALAPPDATA%\Anonimizar`; puede desactivarse en Configuración. Desactivarlo no elimina documentos anteriores. No hay cifrado local propio ni bloqueo de acceso dentro del mismo usuario de Windows.

Ver [LOCAL.md](LOCAL.md) para historial, recuperación, cierre y construcción. No se promete detección completa, anonimización irreversible ni ausencia universal de conexiones externas. Las condiciones y el alcance de las pruebas están en [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md).

## Construir el instalador

Con el entorno `.venv` instalado en esta carpeta:

```powershell
.\.venv\Scripts\python.exe packaging\build_local.py
```

Se requiere también el compilador .NET Framework de Windows. La construcción genera `dist-local/Anonimizar-Setup-0.3.0-win-x64.exe` e incluye runtime y dependencias locales. Los archivos generados quedan fuera de Git. La construcción y comprobación local se documentan en [INSTALADOR.md](INSTALADOR.md). La prueba en otro ordenador sigue pendiente.

## Documentación y atribuciones

| Documento | Contenido |
|---|---|
| [INSTALACION.md](INSTALACION.md) | Descarga pública verificada, instalación offline y diagnóstico |
| [LOCAL.md](LOCAL.md) | Funcionamiento actual de Windows 0.3.0 |
| [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md) | Condiciones conservadas, privacidad y límites de validación |
| [LICENCIAS.md](LICENCIAS.md) | Atribuciones, textos de terceros y permisos pendientes |
| [PREPARACION.md](PREPARACION.md) | Comprobaciones y trabajo pendiente antes de publicar |
| [Archivo histórico](avisos/historico-producto/README.md) | Documentos previos íntegros y referencias internas no incluidas |

Los avisos y textos de terceros permanecen en `avisos/`. No se añade una licencia global ni se amplían permisos de redistribución por preparar esta copia.
