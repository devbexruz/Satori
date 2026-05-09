
using Satori.Application.Binders;
using Microsoft.AspNetCore.Mvc;

namespace Satori.Application.Attributes;

[AttributeUsage(AttributeTargets.Parameter)]
public class FromCurrentUserAttribute : ModelBinderAttribute
{
    public FromCurrentUserAttribute()
    {
        // BinderType ni biz yaratgan klassga yo'naltiramiz
        BinderType = typeof(CurrentUserBinder);
    }
}