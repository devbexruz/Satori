using Satori.Application.Exceptions;
namespace Satori.Api.Middlewares;

public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;

    public ExceptionHandlingMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context); // Dastur ishlashda davom etadi
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private static Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        // Standart status kodi
        int statusCode = 500;
        
        // Standart xabar
        // string message = "Serverda ichki xato yuz berdi.";

        // Response'ni JSON formatida qaytarish uchun tayyorlaymiz
        context.Response.ContentType = "application/json";

        // Status kodini o'rnatamiz, bu kod xatolik turiga qarab o'zgaradi (401, 404, 409 va h.k.)
        context.Response.StatusCode = statusCode;

        // Agar xato bizning BaseException dan meros olgan bo'lsa
        if (exception is BaseException baseException)
        {
            statusCode = baseException.StatusCode; // Biz bergan 401, 404 va h.k.

            // Status kodini o'rnatamiz
            context.Response.StatusCode = statusCode;

            // BaseException ichida GetResponse metodini chaqiramiz
            var response = baseException.GetResponse();
            return context.Response.WriteAsJsonAsync(response);
        }
        throw exception; // Agar xato BaseException dan meros olmagan bo'lsa, uni tashlab yuboramiz va standart 500 xatoni qaytaramiz

        // Agar xato BaseException dan meros olmagan bo'lsa, standart 500 va umumiy xabarni qaytarish
        // return context.Response.WriteAsJsonAsync(new { detail = message });
    }
}
