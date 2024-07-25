using Grpc.Core;
using RoslynAnalyzer;


namespace DotnetAnalyzer.Services;

public class GrpcService : FeedbackServer.FeedbackServerBase
{
    RoslynAnalyzerService roslynAnalyzerService;

    public GrpcService()
    {
        roslynAnalyzerService = new RoslynAnalyzerService();
    }

    public override async Task<GetCompileErrorsReply> GetCompileErrors(GetCompileErrorsRequest request, ServerCallContext context)
    {
        List<CompileError> compileErrors = await roslynAnalyzerService.AnalyzeSolution(request.FilePath);

        var reply = new GetCompileErrorsReply();
        foreach (var error in compileErrors)
        {
            var compileError = new Error
            {
                ErrorText = error.ErrorText,
                ProjectName = error.ProjectName,
                FilePath = error.FilePath,
            };
            compileError.Position.AddRange(error.Position);
            reply.Errors.Add(compileError);
        }

        return await Task.FromResult(reply);
    }
    public override async Task<HasSyntaxErrorsReply> HasSyntaxErrors(HasSyntaxErrorsRequest request, ServerCallContext context)
    {
        bool hasSyntaxErrors = await roslynAnalyzerService.HasSyntaxErrors(request.FilePath);

        return new HasSyntaxErrorsReply
        {
            HasSyntaxErrors = hasSyntaxErrors
        };
    }
}


