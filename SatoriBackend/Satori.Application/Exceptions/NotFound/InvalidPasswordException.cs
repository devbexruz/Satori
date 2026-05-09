namespace Satori.Application.Exceptions.NotFound;

public class InvalidPasswordException : BaseException
{
	public InvalidPasswordException()
		: base("Invalid password.", 401)
	{
	}
}
