using Microsoft.Extensions.DependencyInjection;
using Satori.Infrastructure.Services;
using Satori.Infrastructure.Persistence.Repositories;
using Satori.Infrastructure.Persistence;
using Satori.Application.Interfaces;
using Satori.Application.Interfaces.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;

public static class InfrastructureRegistration
{
    // Infrastructure qatlami: "Menda mana bu narsalar bor, asosiysiga qo'shib qo'y"
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration) 
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("ConnectionStrings:DefaultConnection topilmadi.");

        
        
        // DbContext ni ro'yxatdan o'tkazish
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(connectionString));
        AddServices(services);
        AddRepositories(services);
        return services; // Konteynerning o'zini qaytaradi
    }

    public static void AddServices(IServiceCollection services)
    {
        // Bu yerda barcha xizmatlarni ro'yxatdan o'tkazish mumkin
        services.AddScoped<IJwtProvider, JwtProvider>();
        services.AddScoped<IPasswordHasher, PasswordHasher>();
    }
    public static void AddRepositories(IServiceCollection services)
    {
        // Repositories bu yerda ro'yxatdan o'tkaziladi
        services.AddScoped<IUserRepository, UserRepository>();
    }
}