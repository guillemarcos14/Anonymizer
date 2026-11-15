"""Integrity checks for the public dependency acquisition process."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dependencias', ROOT / 'tools/dependencias.py')
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='anonimizar-kit-test-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.content = b'synthetic dependency bytes'
        self.entry = {'filename': 'synthetic-1.0-py3-none-any.whl',
                      'sha256': hashlib.sha256(self.content).hexdigest(),
                      'url': 'https://example.invalid/never-requested'}
        (self.folder / self.entry['filename']).write_bytes(self.content)

    def test_corruption_is_rejected(self):
        deps.verify(self.folder, [self.entry])
        (self.folder / self.entry['filename']).write_bytes(b'altered')
        with self.assertRaisesRegex(ValueError, 'SHA-256 incorrecto'):
            deps.verify(self.folder, [self.entry])

    def test_unapproved_file_is_rejected(self):
        (self.folder / 'unapproved.whl').write_bytes(b'unapproved')
        with self.assertRaisesRegex(ValueError, 'ajenos al manifiesto'):
            deps.verify(self.folder, [self.entry])

    def test_invalid_existing_file_is_not_replaced_or_downloaded(self):
        path = self.folder / self.entry['filename']
        path.write_bytes(b'keep for diagnosis')
        with patch.object(deps.urllib.request, 'urlopen') as network:
            with self.assertRaisesRegex(ValueError, 'No se sobrescribe'):
                deps.download(self.folder, [self.entry])
            network.assert_not_called()
        self.assertEqual(path.read_bytes(), b'keep for diagnosis')


if __name__ == '__main__':
    unittest.main()
