using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;
using Microsoft.Win32;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.Reflection;
using System.Security.Cryptography;

class Uninstall {
    static JavaScriptSerializer Json = new JavaScriptSerializer();
    static string Digest(string path) { using (var stream = File.OpenRead(path)) using (SHA256 hash = SHA256.Create()) return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant(); }
    static string Arg(string[] args, string name) { int i = Array.IndexOf(args, name); if (i < 0) return null; if (i + 1 >= args.Length) throw new ArgumentException("Falta valor para " + name); return args[i + 1]; }
    static void Result(string path, string status, string message, List<string> deleted) {
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        File.WriteAllText(path, Json.Serialize(new Dictionary<string, object> { {"status",status}, {"message",message}, {"deleted",deleted}, {"completedUtc",DateTime.UtcNow.ToString("o")} }));
    }
    static bool OwnedShortcut(string file, List<string> versions) {
        if (!File.Exists(file)) return false;
        Type type = Type.GetTypeFromProgID("WScript.Shell"); object shell = Activator.CreateInstance(type);
        object link = type.InvokeMember("CreateShortcut", BindingFlags.InvokeMethod, null, shell, new object[] {file});
        string target = Convert.ToString(link.GetType().InvokeMember("TargetPath", BindingFlags.GetProperty, null, link, null));
        foreach (string version in versions) if (InstallScope.Same(target, Path.Combine(version,"Anonimizar.exe"))) return true;
        return false;
    }
    static int Worker(string requestPath) {
        string own = InstallScope.Full(AppDomain.CurrentDomain.BaseDirectory);
        requestPath = Path.GetFullPath(requestPath);
        if (!InstallScope.Same(Path.GetDirectoryName(requestPath), own)) return 1;
        var request = Json.Deserialize<Dictionary<string, object>>(File.ReadAllText(requestPath));
        string testRoot = Convert.ToString(request["testRoot"]); if (testRoot == "") testRoot = null;
        InstallScope scope = InstallScope.Create(testRoot, false);
        string id = Convert.ToString(request["id"]); Guid transaction;
        if (!Guid.TryParseExact(id,"N",out transaction) || !InstallScope.Same(own,Path.Combine(scope.DataDirectory,"uninstall-work",id))) return 1;
        string result = Path.Combine(own,"result.json"); var deleted = new List<string>();
        bool quiet = Convert.ToBoolean(request["quiet"]);
        try {
            if (Digest(Assembly.GetExecutingAssembly().Location) != Convert.ToString(request["workerSha256"])) throw new InvalidDataException("El auxiliar no supera la verificacion.");
            try {
                using (Process parent = Process.GetProcessById(Convert.ToInt32(request["parentPid"]))) {
                    if (parent.StartTime.ToUniversalTime().Ticks == Convert.ToInt64(request["parentStartedTicks"]) && !parent.WaitForExit(30000)) throw new IOException("El desinstalador inicial no ha terminado.");
                }
            } catch (ArgumentException) { }
            scope.CheckEngineStopped(); InstallScope.NoReparse(scope.ProgramRoot);
            var versions = new List<string>();
            foreach (string path in Directory.EnumerateDirectories(scope.ProgramRoot)) if (scope.Owns(path)) { InstallScope.CheckTree(path); versions.Add(path); }
            if (versions.Count == 0) throw new InvalidDataException("No se identifican carpetas propias para retirar.");
            string installation = Convert.ToString(request["installation"]);
            if (!scope.Owns(installation) || !versions.Exists(v => InstallScope.Same(v,installation))) throw new InvalidDataException("La instalacion de origen no pertenece al alcance esperado.");
            using (RegistryKey key = Registry.CurrentUser.OpenSubKey(scope.RegistryPath)) {
                if (key == null || !versions.Exists(v => InstallScope.Same(v,Convert.ToString(key.GetValue("InstallLocation"))))) throw new InvalidDataException("La clave de instalacion no corresponde a estas carpetas; no se borra nada.");
            }
            string desktop = Path.Combine(scope.Desktop,"Anonimizar.lnk"), menu = Path.Combine(scope.Menu,"Anonimizar.lnk");
            InstallScope.NoReparse(desktop); InstallScope.NoReparse(menu);
            bool removeDesktop = OwnedShortcut(desktop,versions), removeMenu = OwnedShortcut(menu,versions);
            string pointer = Path.Combine(scope.ProgramRoot,"current.txt"); InstallScope.NoReparse(pointer);
            bool removePointer = File.Exists(pointer) && versions.Exists(v => InstallScope.Same(v,File.ReadAllText(pointer).Trim()));
            // Recheck the exact absolute targets immediately before recursive deletion.
            foreach (string version in versions) {
                if (!scope.Owns(version)) throw new InvalidDataException("Cambio el propietario de la carpeta.");
                InstallScope.CheckTree(version); Directory.Delete(version,true); deleted.Add(version);
            }
            if (removeDesktop) { File.Delete(desktop); deleted.Add(desktop); }
            if (removeMenu) { File.Delete(menu); deleted.Add(menu); }
            if (removePointer) { File.Delete(pointer); deleted.Add(pointer); }
            if (Directory.Exists(scope.Menu) && Directory.GetFileSystemEntries(scope.Menu).Length == 0) Directory.Delete(scope.Menu);
            if (Directory.Exists(scope.ProgramRoot) && Directory.GetFileSystemEntries(scope.ProgramRoot).Length == 0) Directory.Delete(scope.ProgramRoot);
            Registry.CurrentUser.DeleteSubKeyTree(scope.RegistryPath,false); deleted.Add("HKCU\\" + scope.RegistryPath);
            Result(result,"completed","Programa retirado; documentos, papelera, ajustes, exportaciones y evidencias conservados.",deleted);
            if (!quiet) MessageBox.Show("Anonimizar se ha desinstalado. Tus documentos y ajustes se conservan.","Anonimizar");
            return 0;
        } catch (Exception error) {
            Result(result,"failed",error.Message,deleted);
            if (!quiet) MessageBox.Show("No se completo la desinstalacion: " + error.Message + "\nRegistro: " + result,"Anonimizar",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        }
    }
    [STAThread]
    static int Main(string[] args) {
        AppContext.SetSwitch("Switch.System.IO.UseLegacyPathHandling",false);
        AppContext.SetSwitch("Switch.System.IO.BlockLongPaths",false);
        bool quiet = Array.IndexOf(args,"--quiet-test") >= 0;
        try {
            string worker = Arg(args,"--worker"); if (worker != null) return Worker(worker);
            string testRoot = Arg(args,"--test-root");
            if (quiet != (testRoot != null)) throw new ArgumentException("La prueba requiere --quiet-test y --test-root explicitos.");
            if (!quiet && (Array.IndexOf(args,"--confirm-test") >= 0 || Array.IndexOf(args,"--cancel-test") >= 0)) throw new ArgumentException("Las decisiones de prueba no se admiten en la desinstalacion habitual.");
            InstallScope scope = InstallScope.Create(testRoot,false);
            string installation = InstallScope.Full(AppDomain.CurrentDomain.BaseDirectory);
            if (!scope.Owns(installation)) throw new InvalidDataException("Este ejecutable no pertenece a una instalacion del alcance indicado.");
            InstallScope.CheckTree(installation);
            if (quiet) {
                bool confirm = Array.IndexOf(args,"--confirm-test") >= 0, cancel = Array.IndexOf(args,"--cancel-test") >= 0;
                if (confirm == cancel) throw new ArgumentException("Indica exactamente una decision de prueba: confirmar o cancelar.");
                if (cancel) { Console.WriteLine("cancelled"); return 0; }
            } else if (MessageBox.Show("¿Desinstalar Anonimizar?\n\nLos documentos, papelera y ajustes se conservaran.\nCierra el motor antes de continuar.","Anonimizar",MessageBoxButtons.YesNo,MessageBoxIcon.Question) != DialogResult.Yes) return 0;
            scope.CheckEngineStopped();
            string id = Guid.NewGuid().ToString("N"), work = Path.Combine(scope.DataDirectory,"uninstall-work",id);
            InstallScope.NoReparse(work); Directory.CreateDirectory(work);
            string copy = Path.Combine(work,"DesinstalarWorker.exe"); File.Copy(Assembly.GetExecutingAssembly().Location,copy,false);
            string requestPath = Path.Combine(work,"request.json"), resultPath = Path.Combine(work,"result.json");
            using (Process self = Process.GetCurrentProcess()) File.WriteAllText(requestPath,Json.Serialize(new Dictionary<string,object> {
                {"id",id}, {"testRoot",scope.TestRoot ?? ""}, {"installation",installation}, {"quiet",quiet}, {"parentPid",self.Id}, {"parentStartedTicks",self.StartTime.ToUniversalTime().Ticks}, {"workerSha256",Digest(copy)}
            }));
            Result(resultPath,"pending","Auxiliar iniciado; consultar el resultado final.",new List<string>());
            var start = new ProcessStartInfo(copy,"--worker \"" + requestPath + "\""); start.UseShellExecute=false; start.CreateNoWindow=true; start.WorkingDirectory=work;
            Process.Start(start); Console.WriteLine(resultPath); return 0;
        } catch (Exception error) {
            if (quiet) Console.Error.WriteLine(error.Message); else MessageBox.Show("No se ha iniciado la desinstalacion: " + error.Message,"Anonimizar",MessageBoxButtons.OK,MessageBoxIcon.Error);
            return 1;
        }
    }
}
