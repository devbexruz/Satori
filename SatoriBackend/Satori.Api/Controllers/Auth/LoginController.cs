using Microsoft.AspNetCore.Mvc;
using Satori.Application.Interfaces;
using Satori.Application.DTOs.Auth;

namespace Satori.Api.Controllers.Auth;

[ApiController]
[Route("api/[controller]")]
public class LoginController : ControllerBase
{
    private readonly IAuthService _authService;

    public LoginController(IAuthService authService)
    {
        _authService = authService;
    }

    [HttpPost]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        var response = await _authService.Login(request.Username, request.Password);
        // Response qaytarish 203 status kodi bilan
        // Cookie parametrlarini sozlash
        var cookieOptions = new CookieOptions
        {
            HttpOnly = true,        // JavaScript o'qiy olmaydi (Xavfsiz!)
            Secure = true,          // Faqat HTTPS orqali yuboriladi
            SameSite = SameSiteMode.Strict, // CSRF hujumidan himoya
            Expires = DateTime.UtcNow.AddDays(7) // Muddati
        };

        // Javobga "Set-Cookie" headerini qo'shish
        Response.Cookies.Append("X-Access-Token", response.Token, cookieOptions);
        return Ok(response.UserData);
    }
}
