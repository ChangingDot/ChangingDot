# Use the official Microsoft .NET 8 SDK image as the build environment.
FROM mcr.microsoft.com/dotnet/sdk:8.0
WORKDIR /app

# Copy the project files and build our release
COPY ./protos ./protos
COPY ./dotnetAnalyzer ./dotnetAnalyzer
RUN cd dotnetAnalyzer && dotnet restore
RUN cd dotnetAnalyzer && dotnet publish -c Release -o out

ENTRYPOINT ["dotnet", "./dotnetAnalyzer/out/DotnetAnalyzer.dll"]
