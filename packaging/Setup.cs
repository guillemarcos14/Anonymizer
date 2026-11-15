using System;
using System.IO;
using System.IO.Compression;
using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Windows.Forms;
using Microsoft.Win32;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using System.Net;

class Setup {
    const string Version = "__VERSION__";
    const string Hash = "__HASH__";
    // Previous identifiers are used only to preserve existing installations.
    const string LegacyProduct = "Anonimous";
    static string TestRoot;
    static InstallScope Scope;
    static bool IsTest { get { return TestRoot != null; } }
    static string DataRoot { get { return TestRoot ?? Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData); } }
    static string DesktopRoot { get { return IsTest ? Path.Combine(TestRoot, "Desktop") : Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory); } }
    static string MenuRoot { get { return IsTest ? Path.Combine(TestRoot, "StartMenu") : Environment.GetFolderPath(Environment.SpecialFolder.Programs); } }

    static void ConfigureTest(string[] args, bool quiet) {
        int index = Array.IndexOf(args, "--test-root");
        if (index < 0) {
            if (quiet) throw new ArgumentException("--quiet-test requiere --test-root; no se permite una prueba silenciosa sobre la instalacion habitual.");
            return;
        }
        if (!quiet || index + 1 >= args.Length || !Path.IsPathRooted(args[index + 1])) throw new ArgumentException("La prueba requiere --quiet-test y una ruta absoluta explicita.");
        string candidate = Path.GetFullPath(args[index + 1]).TrimEnd(Path.DirectorySeparatorChar);
        string marker = Path.Combine(candidate, ".anonimizar-installer-test");
        if (!Directory.Exists(candidate) || !File.Exists(marker) || File.ReadAllText(marker).Trim() != "Anonimizar isolated installer test 0.3.0") throw new ArgumentException("Falta el marcador de directorio aislado de prueba; no se ha instalado nada.");
        TestRoot = candidate;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool CreateHardLink(string target, string existing, IntPtr reserved);
    [DllImport("shell32.dll")]
    static extern void SHChangeNotify(uint eventId, uint flags, IntPtr a, IntPtr b);

    static string Digest(Stream input) {
        using (SHA256 sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "").ToLowerInvariant();
    }

    static List<string> PreviousInstallations() {
        var result = new List<string>();
        foreach (string name in new string[] {"Anonimizar", LegacyProduct}) {
            string root = Path.GetFullPath(Path.Combine(DataRoot, "Programs", name));
            string pointer = Path.Combine(root, "current.txt");
            if (!File.Exists(pointer)) continue;
            string candidate = Path.GetFullPath(File.ReadAllText(pointer).Trim());
            if (candidate.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && File.Exists(Path.Combine(candidate, "installed.ok"))) result.Add(candidate);
        }
        return result;
    }

    static bool ReuseRuntime(ZipArchiveEntry entry, string target, List<string> previous, Dictionary<string, string> manifest) {
        if (!entry.FullName.StartsWith("runtime/", StringComparison.Ordinal)) return false;
        string expected;
        if (!manifest.TryGetValue(entry.FullName, out expected)) return false;
        foreach (string root in previous) {
            string existing = Path.Combine(root, entry.FullName);
            if (!File.Exists(existing) || new FileInfo(existing).Length != entry.Length) continue;
            using (FileStream input = File.OpenRead(existing)) if (Digest(input) != expected) continue;
            if (CreateHardLink(target, existing, IntPtr.Zero)) return true;
        }
        return false;
    }

    static void CheckEngineStopped() {
        foreach (string name in new string[] {"Anonimizar", LegacyProduct}) {
            string runtime = Path.Combine(DataRoot, name, "runtime.json");
            if (!File.Exists(runtime)) continue;
            try {
                var state = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(runtime));
                int port = Convert.ToInt32(state["port"]);
                if (port < 1 || port > 65535) continue;
                string route = name == LegacyProduct ? "/anonimous/identity" : "/anonimizar/identity";
                var request = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:" + port + route);
                request.Proxy = null; request.Timeout = 1000;
                using (var response = request.GetResponse())
                using (var reader = new StreamReader(response.GetResponseStream())) {
                    var identity = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(reader.ReadToEnd());
                    if (Convert.ToString(identity["instance"]) == Convert.ToString(state["token"])) throw new InvalidOperationException("Cierra el motor desde Configuración de la aplicación y vuelve a ejecutar el instalador. Tus documentos y ajustes se conservarán.");
                }
            } catch (WebException) { } catch (ArgumentException) { } catch (KeyNotFoundException) { } catch (FormatException) { }
        }
    }

    static void MigrateData(string destination) {
        var start = new ProcessStartInfo(Path.Combine(destination, "runtime", "python.exe"), "-I \"" + Path.Combine(destination, "app", "product_upgrade.py") + "\"");
        start.UseShellExecute = false; start.CreateNoWindow = true;
        start.EnvironmentVariables.Remove("PYTHONHOME"); start.EnvironmentVariables.Remove("PYTHONPATH");
        if (IsTest) start.EnvironmentVariables["LOCALAPPDATA"] = DataRoot;
        using (Process migration = Process.Start(start)) {
            migration.WaitForExit();
            if (migration.ExitCode != 0) throw new InvalidOperationException("No se pudieron conservar los datos anteriores. No se han eliminado los originales.");
        }
    }

    static void ArchivePreviousShortcuts() {
        string backup = Path.Combine(DataRoot, "Anonimizar", "upgrade-backup");
        string oldDesktop = Path.Combine(DesktopRoot, LegacyProduct + ".lnk");
        string oldMenu = Path.Combine(MenuRoot, LegacyProduct);
        if (File.Exists(oldDesktop) || Directory.Exists(oldMenu)) Directory.CreateDirectory(backup);
        string suffix = DateTime.UtcNow.ToString("yyyyMMddHHmmssfff");
        if (File.Exists(oldDesktop)) File.Move(oldDesktop, Path.Combine(backup, "previous-desktop-" + suffix + ".lnk"));
        if (Directory.Exists(oldMenu)) Directory.Move(oldMenu, Path.Combine(backup, "previous-menu-" + suffix));
        if (!IsTest) using (RegistryKey old = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\" + LegacyProduct, true)) {
            if (old != null) old.SetValue("SystemComponent", 1, RegistryValueKind.DWord);
        }
    }

    static void Shortcut(string path, string target) {
        Type shellType = Type.GetTypeFromProgID("WScript.Shell");
        object shell = Activator.CreateInstance(shellType);
        object link = shellType.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] {path});
        Type type = link.GetType();
        type.InvokeMember("TargetPath", BindingFlags.SetProperty, null, link, new object[] {target});
        type.InvokeMember("WorkingDirectory", BindingFlags.SetProperty, null, link, new object[] {Path.GetDirectoryName(target)});
        type.InvokeMember("Description", BindingFlags.SetProperty, null, link, new object[] {"Anonimización local de texto"});
        type.InvokeMember("IconLocation", BindingFlags.SetProperty, null, link, new object[] {Path.Combine(Path.GetDirectoryName(target), "app", "assets", "anonimizar-app.ico") + ",0"});
        type.InvokeMember("Save", BindingFlags.InvokeMethod, null, link, null);
    }

    [STAThread]
    static int Main(string[] args) {
        AppContext.SetSwitch("Switch.System.IO.UseLegacyPathHandling", false);
        AppContext.SetSwitch("Switch.System.IO.BlockLongPaths", false);
        bool quiet = Array.IndexOf(args, "--quiet-test") >= 0;
        try {
            ConfigureTest(args, quiet);
            Scope = InstallScope.Create(TestRoot,true);
            InstallScope.NoReparse(Scope.ProgramRoot);
            InstallScope.NoReparse(Scope.Desktop);
            InstallScope.NoReparse(Scope.Menu);
            string programs = Path.Combine(DataRoot, "Programs", "Anonimizar");
            string destination = Path.Combine(programs, "app-" + Version + "-" + Hash.Substring(0, 8));
            if (!quiet && MessageBox.Show("Instalar Anonimizar " + Version + " para este usuario de Windows.\n\nIncluye el motor y el modelo. No requiere cuenta ni conexión.\nLos datos se guardan por separado y no se borran al actualizar.\n\n¿Continuar?", "Anonimizar", MessageBoxButtons.YesNo, MessageBoxIcon.Information) != DialogResult.Yes) return 0;
            CheckEngineStopped();
            List<string> previous = PreviousInstallations();
            Directory.CreateDirectory(programs);
            using (Stream payload = Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip")) {
                using (SHA256 sha = SHA256.Create()) {
                    string digest = BitConverter.ToString(sha.ComputeHash(payload)).Replace("-", "").ToLowerInvariant();
                    if (digest != Hash) throw new InvalidDataException("El instalador no supera la verificación de integridad.");
                }
                payload.Position = 0;
                {
                    // A failed extraction is retained; a fresh directory prevents overwriting it.
                    if (Directory.Exists(destination)) destination += "-" + DateTime.UtcNow.ToString("yyyyMMddHHmmssfff");
                    Directory.CreateDirectory(destination);
                    using (ZipArchive archive = new ZipArchive(payload, ZipArchiveMode.Read)) {
                        var json = new JavaScriptSerializer(); json.MaxJsonLength = Int32.MaxValue;
                        Dictionary<string, string> manifest;
                        using (var reader = new StreamReader(archive.GetEntry("manifest.json").Open())) manifest = json.Deserialize<Dictionary<string, string>>(reader.ReadToEnd());
                        foreach (ZipArchiveEntry entry in archive.Entries) {
                            string target = Path.GetFullPath(Path.Combine(destination, entry.FullName));
                            if (!target.StartsWith(Path.GetFullPath(destination) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Ruta de instalación no válida.");
                            Directory.CreateDirectory(Path.GetDirectoryName(target));
                            if (ReuseRuntime(entry, target, previous, manifest)) continue;
                            if (new DriveInfo(Path.GetPathRoot(target)).AvailableFreeSpace < entry.Length + 16L * 1024 * 1024) throw new IOException("No hay espacio suficiente para completar la instalación. Libera espacio y vuelve a ejecutar el instalador; se conservan la versión y los datos anteriores.");
                            using (Stream input = entry.Open())
                            using (FileStream output = File.Create(target)) input.CopyTo(output);
                        }
                    }
                    File.WriteAllText(Path.Combine(destination, ".anonimizar-installation.json"), new JavaScriptSerializer().Serialize(Scope.Ownership()));
                    File.WriteAllText(Path.Combine(destination, "installed.ok"), Hash);
                }
            }
            MigrateData(destination);
            string launcher = Path.Combine(destination, "Anonimizar.exe");
            string menu = Path.Combine(MenuRoot, "Anonimizar");
            Directory.CreateDirectory(menu);
            Shortcut(Path.Combine(menu, "Anonimizar.lnk"), launcher);
            if (IsTest) Directory.CreateDirectory(DesktopRoot);
            Shortcut(Path.Combine(DesktopRoot, "Anonimizar.lnk"), launcher);
            using (RegistryKey key = Registry.CurrentUser.CreateSubKey(Scope.RegistryPath)) {
                key.SetValue("DisplayName", "Anonimizar (local)");
                key.SetValue("DisplayVersion", Version);
                key.SetValue("DisplayIcon", Path.Combine(destination, "app", "assets", "anonimizar-app.ico"));
                key.SetValue("InstallLocation", destination);
                key.SetValue("UninstallString", "\"" + Path.Combine(destination, "Desinstalar.exe") + "\"");
                key.SetValue("NoModify", 1);
                key.SetValue("NoRepair", 1);
            }
            if (IsTest) File.WriteAllText(Path.Combine(TestRoot, "registration-test.json"), new JavaScriptSerializer().Serialize(new Dictionary<string, object> {
                {"DisplayName", "Anonimizar (local)"}, {"DisplayVersion", Version}, {"InstallLocation", destination}, {"UninstallString", Path.Combine(destination, "Desinstalar.exe")}, {"NormalRegistrationModified", false}, {"TestRegistryModified", true}, {"RegistryPath", Scope.RegistryPath}
            }));
            ArchivePreviousShortcuts();
            File.WriteAllText(Path.Combine(programs, "current.txt"), destination);
            if (!IsTest) SHChangeNotify(0x08000000, 0, IntPtr.Zero, IntPtr.Zero);
            if (!quiet) {
                MessageBox.Show("Anonimizar está instalado. Ábrelo desde el escritorio o el menú Inicio.\n\nSi estabas usando una versión anterior, ciérrala desde Configuración antes de abrir esta.", "Anonimizar");
            }
            return 0;
        } catch (Exception error) {
            if (!quiet) MessageBox.Show("No se pudo completar la instalación: " + error.Message + "\nLos documentos existentes no se han eliminado.", "Anonimizar", MessageBoxButtons.OK, MessageBoxIcon.Error);
            else Console.Error.WriteLine(error.Message);
            return 1;
        }
    }
}
