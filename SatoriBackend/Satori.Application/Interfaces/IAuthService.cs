using System.Threading.Tasks;
using Satori.Application.DTOs.Auth;

namespace Satori.Application.Interfaces;

public interface IAuthService
{
	public Task<LoginResponse> Login(string username, string password);

	public Task<RegisterResponse> Register(string username, string password, string fullName);
}
