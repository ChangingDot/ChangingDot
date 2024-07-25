using System.Diagnostics;

namespace RoslynAnalyzer;

public static class RestoreService
{
    public static void Restore(string solutionPath)
    {
        ProcessStartInfo psiRestore = new ProcessStartInfo
        {
            FileName = "dotnet",
            Arguments = $"restore {solutionPath}",
            RedirectStandardOutput = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        Process processRestore = Process.Start(psiRestore)!;
        processRestore.WaitForExit();
    }
}
