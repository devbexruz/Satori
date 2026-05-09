using Satori.Application.Exceptions;
using Satori.Application.Exceptions.Auth;
using Satori.Application.Exceptions.NotFound;
using Satori.Application.Exceptions.AlreadyExists;
using Satori.Application.Interfaces.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace Satori.Api.Controllers.User
{
    [ApiController]
    [Route("api/[controller]")]
    public class UserController : ControllerBase
    {
        private readonly IUserRepository _userRepository;
        public UserController(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        [HttpGet("profile")]
        public async Task<IActionResult> GetProfile()
        {
            var userId = HttpContext.Items["UserId"] as string;
            if (userId == null){
                throw new UnauthorizedException();
            }

            var user = await _userRepository.GetByIdAsync(long.Parse(userId));
            if (user == null){
                throw new UserNotFoundedException();
            }

            return Ok(new
            {
                user.Id,
                user.Username,
                user.FullName
            });
        }
    }
}