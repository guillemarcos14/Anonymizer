"""Conserva delimitadores externos sin cambiar la detección ni su puntuación."""
from presidio_analyzer.predefined_recognizers import PhoneRecognizer


class PhoneRecognizerWithBoundaries(PhoneRecognizer):
    """Mismo reconocedor; ajusta solo aperturas sin pareja dentro del hallazgo."""

    def _get_recognizer_result(self, match, text, region, nlp_artifacts):
        result = super()._get_recognizer_result(match, text, region, nlp_artifacts)
        original_start = result.start
        # phonenumbers puede incluir «(» del envoltorio y excluir «)».
        # Un prefijo interno como «(955)» conserva su pareja y no se recorta.
        pairs = {'(': ')', '[': ']', '（': '）', '［': '］'}
        while result.start < result.end and text[result.start] in pairs:
            fragment = text[result.start:result.end]
            opening = fragment[0]
            if fragment.count(opening) <= fragment.count(pairs[opening]):
                break
            result.start += 1
        if result.start != original_start:
            result.analysis_explanation.textual_explanation += (
                '; external unmatched opening delimiter preserved'
            )
        return result
