using System.Threading.Tasks;
using Satori.Application.DTOs.Auth;
using Satori.Application.Exceptions.AlreadyExists;
using Satori.Application.Exceptions.Auth;
using Satori.Application.Exceptions.NotFound;
using Satori.Application.Interfaces;
using Satori.Application.Interfaces.Repositories;
using Satori.Domain.Entities;

namespace Satori.Application.Services;

public class AuthService : IAuthService
{
	private readonly IPasswordHasher _passwordHasher;

	private readonly IUserRepository _userRepository;

	private readonly IJwtProvider _jwtProvider;

	public AuthService(IPasswordHasher passwordHasher, IUserRepository userRepository, IJwtProvider jwtProvider)
	{
		_passwordHasher = passwordHasher;
		_userRepository = userRepository;
		_jwtProvider = jwtProvider;
	}

	public async Task<LoginResponse> Login(string username, string password)
	{
		User? user = await _userRepository.GetByUsernameAsync(username);
		if (user == null)
		{
			throw new UserNotFoundedException();
		}
		if (!_passwordHasher.VerifyPassword(password, user.PasswordHash))
		{
			throw new InvalidPasswordException();
		}
		string token = _jwtProvider.Generate(user);
		return new LoginResponse(new LoginUserData(user.Username, user.FullName), token);
	}

	public async Task<RegisterResponse> Register(string username, string password, string fullName)
	{
		if (await _userRepository.GetByUsernameAsync(username) != null)
		{
			throw new UserAlreadyExistsException();
		}
		string passwordHash = _passwordHasher.HashPassword(password);
		User newUser = new User
		{
			Username = username,
			PasswordHash = passwordHash,
			FullName = fullName
		};
		await _userRepository.AddAsync(newUser);
		await _userRepository.SaveChangesAsync();
		return new RegisterResponse(newUser.Username, newUser.FullName);
	}
}
