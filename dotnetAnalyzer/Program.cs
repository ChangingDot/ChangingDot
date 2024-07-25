using DotnetAnalyzer.Services;
using Microsoft.Build.Locator;

MSBuildLocator.RegisterDefaults();

var builder = WebApplication.CreateBuilder(args);

// Configure Kestrel server options
builder.WebHost.ConfigureKestrel(options =>
{
    // Example: Set the max receive message size to 50 MB
    options.Limits.MaxRequestBodySize = 50 * 1024 * 1024;
});

builder.WebHost.UseUrls("http://localhost:5177");

// Add services to the container.
builder.Services.AddGrpc(options =>
{
    // Set the maximum receive message size for gRPC
    // Example: 50 MB
    options.MaxReceiveMessageSize = 50 * 1024 * 1024; // 50 MB
});

var app = builder.Build();

// Configure the HTTP request pipeline.
app.MapGrpcService<GrpcService>();
app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
