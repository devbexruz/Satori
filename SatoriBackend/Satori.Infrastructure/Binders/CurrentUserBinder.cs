using Microsoft.AspNetCore.Mvc.ModelBinding;
using Satori.Application.Interfaces.Repositories; // Repository interfeysi uchun
using Satori.Domain.Entities;
using System.Security.Claims;

public class CurrentUserBinder : IModelBinder
{
    private readonly IUserRepository _userRepository; // Sizning repository

    public CurrentUserBinder(IUserRepository userRepository)
    {
        _userRepository = userRepository;
    }

    public async Task BindModelAsync(ModelBindingContext bindingContext)
    {
        // Token validatsiyadan o'tgach, User.Identity ichida ID bo'ladi
        var userIdClaim = bindingContext.HttpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (userIdClaim == null || !long.TryParse(userIdClaim, out var userId))
        {
            bindingContext.Result = ModelBindingResult.Failed();
            return;
        }

        var user = await _userRepository.GetByIdAsync(userId);
        bindingContext.Result = ModelBindingResult.Success(user);
    }
}