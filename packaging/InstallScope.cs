using System;
using System.IO;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.Net;
using System.Diagnostics;

class InstallScope {
    public string TestRoot, TestId, DataRoot, ProgramRoot, DataDirectory, Desktop, Menu, RegistryPath;
    public bool IsTest { get { return TestRoot != null; } }
    public static string Full(string path) { return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar); }
    public static bool Same(string a, string b) { return String.Equals(Full(a), Full(b), StringComparison.OrdinalIgnoreCase); }
    public static void NoReparse(string path) {
        DirectoryInfo current = new DirectoryInfo(Path.GetFullPath(path));
        while (current != null) {
            try { if ((File.GetAttributes(current.FullName) & FileAttributes.ReparsePoint) != 0) throw new IOException("No se permite borrar mediante enlaces o uniones: " + current.FullName); }
            catch (FileNotFoundException) { } catch (DirectoryNotFoundException) { }
            current = current.Parent;
        }
    }
    public static void CheckTree(string root) {
        NoReparse(root);
        var pending = new Stack<string>(); pending.Push(root);
        while (pending.Count != 0) {
            foreach (string path in Directory.EnumerateFileSystemEntries(pending.Pop())) {
                FileAttributes attributes = File.GetAttributes(path);
                if ((attributes & FileAttributes.ReparsePoint) != 0) throw new IOException("Se conserva la instalacion: contiene un enlace o union.");
                if ((attributes & FileAttributes.Directory) != 0) pending.Push(path);
            }
        }
    }
    public static InstallScope Create(string testRoot, bool createId) {
        var scope = new InstallScope();
        if (testRoot != null) {
            if (!Path.IsPathRooted(testRoot)) throw new ArgumentException("La raiz de prueba debe ser absoluta.");
            scope.TestRoot = Full(testRoot); NoReparse(scope.TestRoot);
            string marker = Path.Combine(scope.TestRoot, ".anonimizar-installer-test");
            if (!File.Exists(marker) || File.ReadAllText(marker).Trim() != "Anonimizar isolated installer test 0.3.0") throw new ArgumentException("Falta el marcador de prueba.");
            string idFile = Path.Combine(scope.TestRoot, ".test-id");
            if (!File.Exists(idFile) && createId) File.WriteAllText(idFile, Guid.NewGuid().ToString("N"));
            if (!File.Exists(idFile)) throw new ArgumentException("Falta el identificador del perfil de prueba.");
            Guid id; scope.TestId = File.ReadAllText(idFile).Trim();
            if (!Guid.TryParseExact(scope.TestId, "N", out id)) throw new ArgumentException("Identificador de prueba invalido.");
        }
        scope.DataRoot = scope.TestRoot ?? Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        scope.ProgramRoot = Full(Path.Combine(scope.DataRoot, "Programs", "Anonimizar"));
        scope.DataDirectory = Full(Path.Combine(scope.DataRoot, "Anonimizar"));
        scope.Desktop = scope.IsTest ? Path.Combine(scope.TestRoot, "Desktop") : Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
        scope.Menu = scope.IsTest ? Path.Combine(scope.TestRoot, "StartMenu", "Anonimizar") : Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "Anonimizar");
        scope.RegistryPath = scope.IsTest ? @"Software\Anonimizar\InstallerTests\" + scope.TestId + @"\Uninstall\Anonimizar" : @"Software\Microsoft\Windows\CurrentVersion\Uninstall\Anonimizar";
        return scope;
    }
    public Dictionary<string, object> Ownership() {
        return new Dictionary<string, object> { {"product", "Anonimizar"}, {"programRoot", ProgramRoot}, {"testId", TestId ?? ""}, {"testRoot", TestRoot ?? ""} };
    }
    public bool Owns(string directory) {
        directory = Full(directory);
        if (!Same(Path.GetDirectoryName(directory), ProgramRoot) || !Path.GetFileName(directory).StartsWith("app-", StringComparison.Ordinal)) return false;
        string marker = Path.Combine(directory, ".anonimizar-installation.json");
        if (!File.Exists(marker) || !File.Exists(Path.Combine(directory, "installed.ok"))) return false;
        var value = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(marker));
        return Convert.ToString(value["product"]) == "Anonimizar" && Same(Convert.ToString(value["programRoot"]), ProgramRoot) && Convert.ToString(value["testId"]) == (TestId ?? "") && Convert.ToString(value["testRoot"]) == (TestRoot ?? "");
    }
    public void CheckEngineStopped() {
        foreach (string name in new string[] { "Anonimizar", "Anonimous" }) {
            string file = Path.Combine(DataRoot, name, "runtime.json");
            if (!File.Exists(file)) continue;
            var state = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(file));
            int port = Convert.ToInt32(state["port"]);
            if (port < 1 || port > 65535) throw new InvalidDataException("Estado del motor invalido; no se borra nada.");
            bool alive = false;
            try {
                var request = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:" + port + (name == "Anonimous" ? "/anonimous/identity" : "/anonimizar/identity"));
                request.Proxy = null; request.Timeout = 1000;
                using (var response = request.GetResponse()) using (var reader = new StreamReader(response.GetResponseStream())) {
                    var identity = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(reader.ReadToEnd());
                    alive = Convert.ToString(identity["instance"]) == Convert.ToString(state["token"]);
                }
            } catch (WebException) { }
            if (alive) throw new InvalidOperationException("Cierra el motor desde Configuracion antes de desinstalar; no se borra nada.");
            if (state.ContainsKey("pid")) {
                try { using (Process process = Process.GetProcessById(Convert.ToInt32(state["pid"]))) if (!process.HasExited) throw new InvalidOperationException("No se puede confirmar que el motor este detenido; no se borra nada."); }
                catch (ArgumentException) { }
            }
        }
    }
}
