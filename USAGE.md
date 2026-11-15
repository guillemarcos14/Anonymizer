**English** | [Español](LOCAL.md)

# Using Anonimizar 0.3.0 — Windows x64

Usage guide for pre-release 0.3.0, available through [GitHub Releases](https://github.com/guillemarcos14/local-text-anonymizer/releases/tag/v0.3.0). The app interface and text-processing workflow are in Spanish. For requirements and the complete source-installation process, see [INSTALLATION.md](INSTALLATION.md).

## Open and close the app

If you used the installer, open **Anonimizar** from the desktop or Start menu. If you run from source, execute `./iniciar.ps1` in PowerShell with `.venv` installed in the repository directory. The launcher opens your browser; no app account is required. Opening it again reuses the existing engine. If the usual port is occupied, the launcher looks for another local port without stopping unrelated processes.

To stop the engine, use **Configuración → Cerrar Anonimizar y detener el motor** in the Spanish interface. Closing the browser tab alone leaves the engine available for reopening. The server listens on `127.0.0.1`: the browser is the app's window, not a hosted service.

The installer creates desktop and Start menu shortcuts and includes Python and the model; you do not need to install Python separately to use it. It is distributed as a release asset, outside Git history. Build details and local tests are documented in [INSTALADOR.md (Spanish)](INSTALADOR.md); installation on a representative external computer still needs validation.

## Text and review

Paste up to 10,000 characters, submit, review, and copy or download the result. Check omissions as well as incorrect substitutions, names, attribution and indirect details that could identify someone. Complete detection and irreversible anonymization are not guaranteed. An available option does not imply general validation; see [conditions and scope (Spanish)](CONDICIONES-ENTREGA.md).

## History and privacy

- History is enabled by default unless an explicit preference has been saved. Disable it in **Configuración**. Doing so prevents automatic saving of new results but does not remove earlier documents.
- History and settings live in `%LOCALAPPDATA%\Anonimizar`, outside the program directory. A saved document keeps the original, document settings and review. General preferences exclude text, free-form lists and encryption keys. The app does not save the working draft to disk.
- The product does not encrypt history or provide its own access lock. Access to the same Windows user account allows access to the data. There is no synchronization or external authentication; Streamlit usage statistics are disabled.
- **Configuración** lets you export/import JSON, move documents to the trash, restore them and empty the trash with confirmation. Removing something from history does not remove exports or earlier backups and does not guarantee forensic erasure.
- Clearing or closing does not necessarily remove content from RAM, paging, the clipboard, downloads or system backups. Network and processing limitations are documented in [CONDICIONES-ENTREGA.md (Spanish)](CONDICIONES-ENTREGA.md).

## Compatibility and recovery

Old per-account databases are not included in this copy. If they exist in an earlier installation, **Configuración** allows an explicitly selected collection to be copied; repeating the operation does not duplicate it. Before copying, a snapshot is created at `recovery/legacy-documents.sqlite3`. That snapshot may contain other collections: it is a recovery copy, not active history. Earlier originals are preserved.

The code keeps compatibility with the product's previous name. These identifiers do not represent active external accounts or resources that should be committed to Git.

## Updates, uninstallation and errors

To update, stop the engine and run the installer from a new release when one is available. The installer uses a versioned directory under `%LOCALAPPDATA%\Programs\Anonimizar`; it updates shortcuts while keeping data separate. Earlier versions are retained for recovery and can be opened with the engine stopped. Updates are downloaded manually from Releases; the app does not download them automatically.

Standard uninstallation is offered through Windows **Settings → Apps** and requires confirmation. It checks that the engine is stopped and preserves user data. This standard integration and its native dialogs still need separate validation; the isolated cycle is documented in [INSTALADOR.md (Spanish)](INSTALADOR.md). Only versions identified as belonging to the installation are removed; unrelated files and older versions without an ownership marker are preserved. Do not delete the data directory without first exporting anything you want to keep.

If startup fails, the launcher shows an error and the diagnostic log location under `logs`. The launcher does not add document text to its messages, but there is no universal guarantee that every dependency error is sanitized. Report the version, platform, steps and error using fictional examples, without real case files.

## Build and documentation

`instalar.ps1` prepares the development environment; it is not the end-user installer. `iniciar.ps1` uses `.venv`. `packaging/build_local.py` builds the offline installer from that environment and CPython 3.13.7. The manifest and SHA-256 are generated in `dist-local/build.json`. The executable has no publisher certificate signature. See [README.md](README.md) for commands and requirements.

Attributions and conditions are preserved in [LICENCIAS.md (Spanish)](LICENCIAS.md) and [CONDICIONES-ENTREGA.md (Spanish)](CONDICIONES-ENTREGA.md). The [complete earlier Spanish guide](avisos/historico-producto/LOCAL-antes-de-limpieza.txt) is kept as a historical reference; it does not replace the current guidance.
