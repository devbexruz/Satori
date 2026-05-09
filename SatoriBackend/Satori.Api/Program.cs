using Scalar.AspNetCore;
using Satori.Api.Middlewares;


var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();


// Add application services to the container.
builder.Services.AddApplication();

// Add infrastructure services to the container.
builder.Services.AddInfrastructure(builder.Configuration);

// Add controllers (API endpoints) to the container.
builder.Services.AddControllers();

// Build the application.
var app = builder.Build();

// Add middlewares to the application.
app.UseMiddleware<JwtMiddleware>();
app.UseMiddleware<ExceptionHandlingMiddleware>();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    // OpenAPI Documentation
    app.MapOpenApi();

    // Scalar API Reference
    app.MapScalarApiReference();
}

// app.UseHttpsRedirection();

// app.UseAuthorization();

// Map controller routes (API endpoints).
app.MapControllers();

Console.WriteLine("Satori API is running...\n");
Console.WriteLine("Open: http://localhost:8080/Scalar to view API documentation.\n");

// Run the application.
app.Run();

