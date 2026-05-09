namespace Satori.Application.Exceptions.Auth;

public class UserNotFoundedException : BaseException
{
	public UserNotFoundedException()
		: base("User not found.", 404)
	{
	}
}
