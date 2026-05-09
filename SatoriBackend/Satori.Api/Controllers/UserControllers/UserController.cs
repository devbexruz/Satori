
using Satori.Application.Exceptions.NotFound;
using Satori.Application.Interfaces.Repositories;
using Microsoft.AspNetCore.Mvc;
using Satori.Application.Attributes;
using Satori.Domain.Entities;

namespace Satori.Api.Controllers.UserControllers
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
        public async Task<IActionResult> GetProfile([FromCurrentUser] User user)
        {
            if (user == null){
                throw new UnauthorizedException();
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