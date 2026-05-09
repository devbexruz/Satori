namespace Satori.Application.Exceptions.AlreadyExists;

public class UserAlreadyExistsException : BaseException
{
	public UserAlreadyExistsException()
		: base("User with this email already exists.", 409)
	{
	}
}
