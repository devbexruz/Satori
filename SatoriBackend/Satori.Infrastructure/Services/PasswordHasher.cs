using Satori.Infrastructure.Interfaces;

namespace Satori.Infrastructure.Services;

public class PasswordHasher : IPasswordHasher
{
    public string HashPassword(string password) 
        => BCrypt.Net.BCrypt.HashPassword(password);

    public bool VerifyPassword(string password, string hash) 
        => BCrypt.Net.BCrypt.Verify(password, hash);
}