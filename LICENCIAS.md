# Licencias y atribuciones — Anonimizar 0.3.0

Este documento organiza los avisos existentes; no concede una licencia nueva, no acredita permisos adicionales y no sustituye los textos íntegros de cada componente. El nombre histórico `presidio-es-mit` no significa que el producto completo tenga una licencia MIT global. La preparación local no autoriza publicación ni distribución.

## Componentes y textos conservados

El manifiesto identifica 82 paquetes fijados, incluido `xx_ent_wiki_sm` 3.8.0. Los wheels se conservan en un kit local externo al repositorio. Los hashes están en [requirements-win-py313.lock](requirements-win-py313.lock) y [wheelhouse-sha256.json](wheelhouse-sha256.json). El modelo anterior `es_core_news_md` no se incluye en esta revisión. La siguiente tabla conserva las declaraciones y obligaciones del registro previo; esta limpieza documental no es una nueva auditoría jurídica.

| Componente / material | Condiciones declaradas y cumplimiento preparado |
|---|---|
| Demo upstream y Presidio2.2.366 | MIT. Declaración propia del Space en `avisos/DEMO-UPSTREAM-README.md`, revisión9fb5e22d76bdd3b06e2a956ae62003ca9973920d. TextosMIT/copyright originales conservados; origen y cambios en `avisos/ORIGEN-Y-CAMBIOS.json`. No se inventa titular de las aportaciones ni aval de los autores. |
| xx_ent_wiki_sm3.8.0 | MIT, copyright2021ExplosionAI GmbH. Modelo sin modificar; LICENSE y metadatos reales en `avisos/xx-ent-wiki-sm`. MIT permite uso/modificación/redistribución/venta conservando copyright, permiso y exenciones. No exige publicar fuente de la aplicación propia. |
| WikiNER, fuente del modelo | CC BY4.0. Autores: Joel Nothman, Nicky Ringland, Will Radford, Tara Murphy, James R Curran. Procedencia: https://figshare.com/articles/Learning_multilingual_named_entity_recognition_from_Wikipedia/5462500 . Texto y atribución completos en `avisos/xx-ent-wiki-sm/LICENSES_SOURCES`. Sin modificaciones al modelo ni a ese material por esta integración. Conservar autoría, procedencia, licencia y exenciones; indicar cambios si se producen. No hay condiciónShareAlike, pero no se pueden restringir los derechosCCBY del material cubierto. |
| Streamlit1.66.1, bibliotecas e interfaz incorporadas | Apache2 y terceros en NOTICES oficial completo, incluidas fuentesOFL, iconos y KaTeXMIT. Otros wheels conservan MIT/BSD/ISC/PSF/MIT-CMU/Zlib y términos particulares según sus textos. No recortar avisos por no usar una función de la interfaz. |
| MPL y excepciones | Conservar condiciones por archivo de certifi, tqdm, partes de setuptools y la listaPublicSuffixList incluida en tldextract, con fuente legible local indicada abajo. NumPy incluye avisosOpenBLAS/LAPACK y runtimeGCC con GPL+excepción3.1: preservar excepción, no describir esta revisión como libre de toda licenciaGPL oMPL. |

## Dónde consultar los textos y las fuentes

`avisos/inventario.json` identifica82paquetes y metadatos locales; `avisos/AVISOS-TERCEROS.txt` contiene136textos completos. Cada texto existe también en `avisos/textos-completos`, con SHA256 en `avisos/indice-textos.json`. Los avisos originales por paquete permanecen en `avisos/<paquete>`. El índice puede conservar referencias a la evidencia interna para explicar procedencia; no es necesario acceder a esas rutas para leer los textos locales completos.

Las formas legibles incluidas en los wheels se instalan en `.venv/Lib/site-packages`. ArchivosMPL cubiertos y fuentes están identificados en `avisos/FUENTES-MPL.json`: el kit incorpora copias legibles sin modificar de certifi/tqdm y componentesMPL de setuptools, junto con sus avisos. No son solo enlaces a una rama cambiante. Se proporcionan bajo sus condicionesMPL/MIT correspondientes, sin restricciones adicionales sobre esas fuentes. No se han modificado esos paquetes. Las demás licencias permisivas no exigen genéricamente acompañar todos los archivos fuente; se conservan sus avisos y las condiciones particulares aplicables.

## Artefactos públicos de instalación

El proceso actual usa [dependencias-publicas.json](dependencias-publicas.json) y [requirements-publicas-win-py313.lock](requirements-publicas-win-py313.lock). Se conservan las 82 versiones del producto. Para `htbuilder` 0.9.0 se obtiene la fuente oficial de PyPI con hash fijado y se construye localmente; el wheel histórico permanece identificado en los manifiestos anteriores, sin declararlo disponible públicamente. No se cambia su licencia Apache 2 ni se retiran sus avisos. El registro original `avisos/ORIGEN-Y-CAMBIOS.json` describe la integración anterior, no una huella de esta nueva construcción.

Pip 26.0.1 se fija como herramienta de instalación separada y no añade una dependencia de ejecución a la lista de 82. La adquisición no reconstruye ni redistribuye un instalador; las atribuciones de pip incluidas en su distribución deben conservarse si posteriormente se empaqueta. Ver [INSTALACION.md](INSTALACION.md).

## Tipografías, imágenes y recursos visuales

Inter Variable sin modificar: copyright © 2016 The Inter Project Authors, SIL Open Font License 1.1. El archivo está en [assets/fonts/InterVariable.woff2](assets/fonts/InterVariable.woff2); el texto íntegro y la procedencia están en [avisos/inter/LICENSE.txt](avisos/inter/LICENSE.txt) y [avisos/inter/procedencia.json](avisos/inter/procedencia.json).

Instrument Serif Regular se conserva con su [SIL Open Font License 1.1](assets/fonts/InstrumentSerif-OFL.txt), sin modificar. La procedencia registrada es [Google Fonts — Instrument Serif](https://github.com/google/fonts/tree/main/ofl/instrumentserif). Su conservación no implica que sea la fuente activa de la interfaz actual.

Camera Plain, los fondos y otros recursos extraídos de referencias de Lovable conservan su procedencia en [assets/PROCEDENCIA-ENTRADA.md](assets/PROCEDENCIA-ENTRADA.md) y [assets/PROCEDENCIA-REGISTRO.md](assets/PROCEDENCIA-REGISTRO.md). Esos registros no acreditan permisos de redistribución. No se atribuyen a esos recursos las licencias del motor o del modelo.

Las adaptaciones visuales y el icono añadido mediante IA no acreditan exclusividad, disponibilidad registral ni aval de los autores de las referencias. Los antecedentes completos se conservan en el [archivo histórico](avisos/historico-producto/README.md).

## Aportaciones propias y condiciones

No se ha escogido una licencia abierta global para las aportaciones propias. Se conservan las decisiones previas de prueba interna gratuita, los límites sobre material con derechos suficientes y las excepciones de terceros. Su contexto y el compromiso propuesto de 12 meses se documentan en [CONDICIONES-ENTREGA.md](CONDICIONES-ENTREGA.md) y en los originales históricos íntegros.

Esta preparación no acredita titularidad exclusiva de material generado mediante IA ni convierte en propios los componentes upstream o el modelo. No se adopta GPL para el conjunto ni se eliminan las condiciones GPL con excepciones, MPL u otras presentes en componentes concretos. No imponer restricciones globales que supriman permisos de terceros.

## Historial y trazabilidad

El [registro anterior íntegro](avisos/historico-producto/LICENCIAS-antes-de-limpieza.txt) conserva revisiones visuales, decisiones y redacción original. El [índice histórico](avisos/historico-producto/README.md) identifica las referencias internas no incluidas. Los documentos de terceros y sus índices originales en `avisos/` permanecen intactos; sus rutas de procedencia histórica no son instrucciones de instalación de esta copia.
