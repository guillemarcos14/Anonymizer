# Condiciones y límites — preparación de Anonimizar 0.3.0

Esta es una reorganización documental de las condiciones existentes, sin nueva licencia, contrato, aceptación por participantes ni autorización de entrega o de documentos reales. La copia Windows sigue en preparación local, sin publicación. Se conservan íntegros el [documento anterior](avisos/historico-producto/CONDICIONES-ENTREGA-antes-de-limpieza.txt) y el [borrador doc-05-08](avisos/historico-producto/BORRADOR-CONDICIONES-PRUEBA-doc-05-08.txt), con sus condiciones y excepciones.

## Funcionamiento vigente y datos

La aplicación actual es Windows local, sin registro ni cuentas externas. El servidor escucha en `127.0.0.1`; el navegador muestra la interfaz. El límite provisional es de 10.000 caracteres y la revisión humana sigue siendo obligatoria. La salida puede conservar datos identificativos; compartirla es decisión del usuario.

El historial está activado por defecto y puede guardar original, configuración del documento y revisión. Los datos y ajustes están en `%LOCALAPPDATA%\Anonimizar`, fuera del programa, sin cifrado local propio. Desactivar el historial no borra los documentos ya guardados. El borrador no se guarda en disco por la aplicación. La afirmación histórica de que no existía persistencia de documentos no describe la versión 0.3.0. Ver [LOCAL.md](LOCAL.md) para recuperación, papelera y cierre.

Se conserva la promesa acordada: **«La aplicación procesa localmente y no envía automáticamente tus documentos a servicios externos».** Las estadísticas de uso de Streamlit están desactivadas. La primera ejecución sin caché de `tldextract` puede consultar URLs fijas de una lista pública de dominios; según la revisión de código documentada, esa consulta no incluye el documento y existe una copia incluida para funcionamiento sin red. Esto no acredita ausencia universal de tráfico: navegador, extensiones, dependencias y otros procesos tienen comportamiento propio.

Vaciar o cerrar no garantiza borrar RAM, paginación, portapapeles, descargas, historial o copias del sistema. No habilitar `ALLOW_CONFIG_EDIT`, servidor externo ni registros debug. No se garantiza saneamiento universal de errores de bibliotecas. Las vistas de detección y exportaciones técnicas pueden contener originales; revisar qué se comparte.

## Alcance comprobado y límites

La evaluación histórica de la revisión MIT integrada se limitaba a `EMAIL_ADDRESS`, `PHONE_NUMBER`, `IBAN_CODE`, `ES_NIF` de persona física y `ES_NIE`, con `replace` y umbral 0,35. Excluía PERSON automático y no validaba LOCATION o domicilios completos. Se conserva ese límite: no trasladar sus resultados a otros tipos, umbrales o versiones.

La copia de GitHub ha superado una instalación offline y `pip check`, una prueba sintética de sustitución de correo y teléfono con conservación del importe, ejecución inicial sin excepciones en AppTest y comprobaciones HTTP de identidad y HTML. Esto no equivale a una nueva evaluación general de precisión, comprensión humana o privacidad de red. Posteriormente se reconstruyó y probó el instalador local en un perfil aislado con datos ficticios; ver [INSTALADOR.md](INSTALADOR.md). Posteriormente se comprobó también el ciclo aislado de desinstalación y reinstalación, conservando datos ficticios y testigos. Siguen sin validarse otro ordenador, la integración habitual de Aplicaciones instaladas, sus diálogos nativos y la apariencia en navegador.

La existencia de seis modos y controles de configuración no acredita su calidad en todos los casos. El modelo multilingüe no constituye validación de otros idiomas. No se promete detección total, anonimización irreversible, certificación RGPD, aval de terceros ni aptitud universal para expedientes reales.

## Decisiones conservadas de la prueba interna

Estas decisiones proceden de la prueba documentada en noviembre de 2026. Se conservan como condiciones y antecedentes de esa prueba; no se convierten automáticamente en una licencia pública de GitHub:

1. Guillem Arcos González organiza a título personal; el correo designado es guillemarcos23@gmail.com. Soporte manual de instalación, uso e incidencias con ejemplos ficticios, sin plazo de respuesta garantizado. La preparación no prueba la recepción del correo ni crea cuentas.
2. Participación y salida voluntarias, producto gratuito hasta nuevo aviso, sin cobro, permanencia ni conversión automática a pago. Cualquier oferta futura requiere decisión y aceptación separadas. No existe entrega o aceptación por participantes acreditada en esta preparación.
3. La política aprobada permite la prueba interna gratuita sobre aportaciones licenciables, respetando permisos de terceros y facultades legales. Las restricciones requieren derechos suficientes y no acreditan exclusividad ni garantizan impedir copia o reventa. No hay concesión abierta nueva por esta limpieza.
4. D1 conserva el compromiso separado propuesto de no redistribuir incrementos locales durante **12 meses desde aceptación válida por ambas partes**, con exclusiones de terceros y facultades legales, sin renovación automática. No empieza por una aprobación interna, no es un plazo de gratuidad ni se aplica globalmente a este repositorio. El alcance, anexo y texto íntegro siguen en el borrador doc-05-08 conservado.
5. La política de contactos de la prueba limita la recogida a datos profesionales mínimos, durante la actividad y hasta 90 días tras su cierre. No autoriza recoger expedientes ni supone borrado automático del historial local del producto. La participación, salida, conservación y demás condiciones completas permanecen en el borrador histórico.

No solicitar expedientes por correo. Comunicar versión, plataforma, pasos y error con ejemplos ficticios. Cualquier acceso imprescindible a contenido real exige acordar previamente alcance y condiciones.

## Antes de una distribución pública

Quedan pendientes los términos de las aportaciones propias para GitHub, los permisos de determinados recursos visuales y la instalación externa representativa con su integración y desinstalación. Las atribuciones de [LICENCIAS.md](LICENCIAS.md) se mantienen. La documentación de terceros no concede por sí sola derechos adicionales sobre la adaptación.

El [estado de preparación](PREPARACION.md) distingue las comprobaciones realizadas de los pendientes. El [índice histórico](avisos/historico-producto/README.md) conserva las referencias internas ausentes sin presentarlas como enlaces disponibles ni controles completados.
