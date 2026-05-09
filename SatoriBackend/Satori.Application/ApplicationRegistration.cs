using Microsoft.Extensions.DependencyInjection;
using Satori.Application.Interfaces;
using Satori.Application.Services;

public static class ApplicationRegistration
{
	public static IServiceCollection AddApplication(this IServiceCollection services)
	{
		services.AddScoped<IAuthService, AuthService>();
		return services;
	}
}
