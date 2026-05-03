using Microsoft.EntityFrameworkCore;
using Satori.Infrastructure.Persistence;
using Scalar.AspNetCore;


var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();


// DbContext ni ro'yxatdan o'tkazish
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        // Bu yerda Npgsql ga vektorlar bilan ishlashni aytamiz
        npgsqlOptions => npgsqlOptions.UseVector()
    ));



// Add services to the container.
builder.Services.AddControllers();


var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

// HTTPS redirect ni Nginx qiladi — API ichida keraksiz
// app.UseHttpsRedirection();

app.UseAuthorization();
app.MapControllers();

app.Run();
