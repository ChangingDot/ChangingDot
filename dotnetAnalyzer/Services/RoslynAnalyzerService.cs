using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.MSBuild;
using DotnetAnalyzer;

namespace RoslynAnalyzer;


public class CompileError
{
    public string ErrorText { get; set; }
    public string ProjectName { get; set; }
    public string FilePath { get; set; }
    public List<int> Position { get; set; }

    public CompileError(string errorText, string projectName, string filePath, List<int> position)
    {
        ErrorText = errorText;
        ProjectName = projectName;
        FilePath = filePath;
        Position = position;
    }

    public override string ToString()
    {
        return $"Error: {ErrorText}\nFile: {FilePath}\nPosition: {string.Join(", ", Position)}";
    }
}
class RoslynAnalyzerService : FeedbackServer.FeedbackServerBase
{
    MSBuildWorkspace workspace;
    public RoslynAnalyzerService()
    {
        workspace = MSBuildWorkspace.Create();
    }

    public async Task<bool> HasSyntaxErrors(string solutionPath)
    {
        RestoreService.Restore(solutionPath);
        var solution = await workspace.OpenSolutionAsync(solutionPath);

        if (workspace.Diagnostics.Any())
        {
            Console.WriteLine("Diagnostics while loading the solution:");
            foreach (var diag in workspace.Diagnostics)
            {
                Console.WriteLine($"  {diag.Kind}: {diag.Message}");
            }
        }
        bool hasSyntaxErrors = false;

        foreach (var project in solution.Projects)
        {


            foreach (var document in project.Documents)
            {
                var syntaxTree = await document.GetSyntaxTreeAsync();
                var syntaxErrors = syntaxTree!.GetRoot().GetDiagnostics().ToList();
                if (syntaxErrors.Count != 0) hasSyntaxErrors = true;
            }
        }
        return hasSyntaxErrors;
    }

    public async Task<List<CompileError>> AnalyzeSolution(string solutionPath)
    {
        RestoreService.Restore(solutionPath);
        var solution = await workspace.OpenSolutionAsync(solutionPath);

        if (workspace.Diagnostics.Any())
        {
            Console.WriteLine("Diagnostics while loading the solution:");
            foreach (var diag in workspace.Diagnostics)
            {
                Console.WriteLine($"  {diag.Kind}: {diag.Message}");
            }
        }

        List<CompileError> allCompileError = [];

        foreach (var project in solution.Projects)
        {
            var compilation = await project.GetCompilationAsync();

            var compilationOptions = new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary);

            var diagnostics = compilation?.GetDiagnostics().Where(diagnostic =>
                diagnostic.IsWarningAsError || diagnostic.Severity == DiagnosticSeverity.Error);

            if (diagnostics == null) return allCompileError;

            diagnostics = diagnostics.Where(d => !(d.Location.SourceTree?.FilePath ?? "").Contains("/obj/"));


            List<CompileError> compileErrors = diagnostics.Select(diag =>
            {
                var lineSpan = diag.Location.GetLineSpan().StartLinePosition;
                var endLineSpan = diag.Location.GetLineSpan().EndLinePosition;
                var filePath = diag.Location?.SourceTree?.FilePath ?? project.FilePath ?? "";
                // Add one to go from index to line_number
                return new CompileError(diag.GetMessage(), project.Name, filePath, [lineSpan.Line + 1, lineSpan.Character + 1, endLineSpan.Line + 1, endLineSpan.Character + 1]);
            }).ToList();

            allCompileError = allCompileError.Concat(compileErrors).ToList();

        }
        return allCompileError;

    }
}