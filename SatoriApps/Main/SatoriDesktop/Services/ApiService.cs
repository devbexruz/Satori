using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace SatoriDesktop.Services;

// ── DTOs ──────────────────────────────────────────────────

public record LoginRequest(string Username, string Password);
public record RegisterRequest(string Username, string Password, string FullName);

public record LoginUserData(string Username, string FullName);

// ── API Client ───────────────────────────────────────────

/// <summary>
/// Satori Backend bilan aloqa xizmati.
/// JWT token HttpOnly Cookie orqali boshqariladi.
/// </summary>
public class ApiService
{
    private readonly HttpClient _http;
    private const string BaseUrl = "http://localhost:8080";

    public ApiService()
    {
        var handler = new HttpClientHandler
        {
            UseCookies = true,
            CookieContainer = new System.Net.CookieContainer()
        };
        _http = new HttpClient(handler)
        {
            BaseAddress = new Uri(BaseUrl),
            Timeout = TimeSpan.FromSeconds(15)
        };
        _http.DefaultRequestHeaders.Add("Accept", "application/json");
    }

    // === Auth ===

    public async Task<LoginUserData?> LoginAsync(string username, string password)
    {
        try
        {
            var response = await _http.PostAsJsonAsync("/api/Login", new LoginRequest(username, password));
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<LoginUserData>();
        }
        catch (HttpRequestException ex)
        {
            throw new ApiException($"Login xatosi: {ex.Message}", ex);
        }
    }

    public async Task<bool> RegisterAsync(string username, string password, string fullName)
    {
        try
        {
            var response = await _http.PostAsJsonAsync("/api/Register",
                new RegisterRequest(username, password, fullName));
            return response.IsSuccessStatusCode;
        }
        catch (HttpRequestException ex)
        {
            throw new ApiException($"Ro'yxatdan o'tish xatosi: {ex.Message}", ex);
        }
    }

    // === Health Check ===

    public async Task<bool> IsBackendAliveAsync()
    {
        try
        {
            var response = await _http.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}

// ── Custom Exception ─────────────────────────────────────

public class ApiException : Exception
{
    public ApiException(string message, Exception? inner = null)
        : base(message, inner) { }
}
