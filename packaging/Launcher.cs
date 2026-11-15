using System;
using System.IO;
using System.Diagnostics;
using System.Windows.Forms;

class Launcher {
    [STAThread]
    static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            string python = Path.Combine(root, "runtime", "pythonw.exe");
            string script = Path.Combine(root, "app", "anonimizar_launcher.py");
            ProcessStartInfo start = new ProcessStartInfo(python, "\"" + script + "\" " + String.Join(" ", args));
            start.WorkingDirectory = Path.Combine(root, "app");
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.EnvironmentVariables.Remove("PYTHONHOME");
            start.EnvironmentVariables.Remove("PYTHONPATH");
            start.EnvironmentVariables["PYTHONNOUSERSITE"] = "1";
            using (Process process = Process.Start(start)) {
                process.WaitForExit();
                return process.ExitCode;
            }
        } catch {
            MessageBox.Show("No se pudo abrir Anonimizar. Vuelve a ejecutar el instalador; tus documentos se conservan por separado.", "Anonimizar");
            return 1;
        }
    }
}
