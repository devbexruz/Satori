namespace Satori.Application.DTOs.Auth;

public record LoginResponse(LoginUserData UserData, string Token);
