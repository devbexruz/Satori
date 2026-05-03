# 1-BOSQICH: Build
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Barcha loyihalarni alohida nusxalash (Restore keshini saqlash uchun)
COPY ["Satori.Api/Satori.Api.csproj", "Satori.Api/"]
COPY ["Satori.Infrastructure/Satori.Infrastructure.csproj", "Satori.Infrastructure/"]
COPY ["Satori.Domain/Satori.Domain.csproj", "Satori.Domain/"]
COPY ["Satori.Application/Satori.Application.csproj", "Satori.Application/"]

RUN dotnet restore "Satori.Api/Satori.Api.csproj"

# Qolgan barcha kodlarni nusxalash
COPY . .
WORKDIR "/src/Satori.Api"
RUN dotnet publish "Satori.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

# 2-BOSQICH: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

ENV DOTNET_GCHeapHardLimit=200000000 
EXPOSE 8080
ENTRYPOINT ["dotnet", "Satori.Api.dll"]