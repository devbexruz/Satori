using Microsoft.AspNetCore.Mvc.ModelBinding;
using Satori.Application.Interfaces.Repositories;
using System.Security.Claims;

namespace Satori.Application.Binders;

public class CurrentUserBinder : IModelBinder
{
    private readonly IUserRepository _userRepository;

    public CurrentUserBinder(IUserRepository userRepository)
    {
        _userRepository = userRepository;
    }

    public async Task BindModelAsync(ModelBindingContext bindingContext)
    {
        // 1. JWT dan UserId ni o'qiymiz
        var userIdClaim = bindingContext.HttpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        // UserId ni o'qishda xatolik bo'lsa, binding muvaffaqiyatsiz bo'ladi
        if (string.IsNullOrEmpty(userIdClaim) || !long.TryParse(userIdClaim, out var userId))
        {
            bindingContext.Result = ModelBindingResult.Failed();
            return;
        }

        // 2. Bazadan foydalanuvchini yuklaymiz
        var user = await _userRepository.GetByIdAsync(userId);

        // Agar user topilsa, model binding muvaffaqiyatli bo'ladi, aks holda muvaffaqiyatsiz bo'ladi
        if (user != null)
        {
            bindingContext.Result = ModelBindingResult.Success(user);
        }
        else
        {
            bindingContext.Result = ModelBindingResult.Failed();
        }
    }
}