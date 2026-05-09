using System.Security.Claims;
using Satori.Domain.Entities;

namespace Satori.Application.Interfaces;

public interface IJwtProvider
{
	public ClaimsPrincipal? ValidateToken(string token);

	public string Generate(User user);
}
