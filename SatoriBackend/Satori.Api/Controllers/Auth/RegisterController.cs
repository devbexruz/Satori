using Microsoft.AspNetCore.Mvc;
using Satori.Application.Interfaces;
using Satori.Application.DTOs.Auth;

namespace Satori.Api.Controllers.Auth;

[ApiController]
[Route("api/[controller]")]
public class RegisterController : ControllerBase
{
    private readonly IAuthService _authService;

    public RegisterController(IAuthService authService)
    {
        _authService = authService;
    }

    [HttpPost]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        var response = await _authService.Register(request.Username, request.Password, request.FullName);
        return Ok(response);
    }

}