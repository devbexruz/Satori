using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using Satori.Domain.Entities; // User modeli uchun
using Satori.Application.Interfaces;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace Satori.Infrastructure.Services;

public class JwtProvider : IJwtProvider
{
    private readonly IConfiguration _configuration;
    private readonly SigningCredentials _creds;
    private readonly double _expiryMinutes = 60;

    public JwtProvider(IConfiguration configuration)
    {
        _configuration = configuration;
        
        // Constructor ichida kalitni bir marta yaratib olamiz
        var keyMatni = _configuration["Jwt:Key"];
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(keyMatni!));

        _creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        // Expiry vaqtini ham configuration orqali olish mumkin, hozirda 60 daqiqa qilib qo'ydim
        _expiryMinutes = Convert.ToDouble(_configuration["Jwt:ExpireMinutes"]);
    }

    public string Generate(User user)
    {
        // 1. Token ichidagi "ma'lumotlar paketi" (Claims)
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new(ClaimTypes.Name, user.Username),
        };

        // 2. Token parametrlarini yig'ish
        var token = new JwtSecurityToken(
            issuer: _configuration["Jwt:Issuer"],
            audience: _configuration["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_expiryMinutes),
            signingCredentials: _creds
        );

        // 5. Tokenni string (matn) ko'rinishiga o'tkazish
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
    public ClaimsPrincipal? ValidateToken(string token)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.UTF8.GetBytes(_configuration["Jwt:Key"]!);

        try
        {
            var principal = tokenHandler.ValidateToken(token, new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidIssuer = _configuration["Jwt:Issuer"],
                ValidateAudience = true,
                ValidAudience = _configuration["Jwt:Audience"],
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero // Tokenning muddati o'tganini aniq tekshirish uchun
            }, out SecurityToken validatedToken);

            return principal;
        }
        catch
        {
            // Token xato bo'lsa yoki validatsiya o'tmasa, null qaytaramiz
            return null;
        }
    }
}
