namespace Satori.Api.Middlewares;
using System.Security.Claims;
using Satori.Application.Interfaces; // IJwtProvider uchun
using Microsoft.AspNetCore.Http;


public class JwtMiddleware
{
    private readonly RequestDelegate _next;
        
    public JwtMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task Invoke(HttpContext context, IJwtProvider jwtProvider)
    {
        // 1. Header'dan "Authorization" qismini olamiz
        // Ko'rinishi: "Bearer eyJhbGci..."
        
        var token = context.Request.Cookies["X-Access-Token"];
        Console.WriteLine($"Extracted Token: {token}"); // Log token for debugging

        if (token != null)
        {
            // 2. Tokenni tekshiramiz va ichidagi ma'lumotlarni (Claims) chiqaramiz
            AttachUserToContext(context, token, jwtProvider);
        }

        // 3. Keyingi middleware-ga o'tkazamiz
        await _next(context);
    }
    private void AttachUserToContext(HttpContext context, string token, IJwtProvider jwtProvider)
    {
        try
        {
            // 1. Tokenni ValidateToken orqali tekshiramiz
            var principal = jwtProvider.ValidateToken(token);

            if (principal != null)
            {
                // 2. Principal ichidan NameIdentifier (ID) claim'ini qidiramiz
                var userIdClaim = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value;

                if (userIdClaim != null)
                {
                    // 3. Faqat ID ning o'zini context'ga yozamiz
                    context.Items["UserId"] = userIdClaim;
                    
                    // 4. .NET standart Authentication'ni ham qondirish uchun User obyektini biriktiramiz
                    context.User = principal;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Middleware Error: {ex.Message}");
        }
    }
}
