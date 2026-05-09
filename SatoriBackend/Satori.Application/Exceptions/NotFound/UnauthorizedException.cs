namespace Satori.Application.Exceptions.NotFound;

public class UnauthorizedException : BaseException
{
	public UnauthorizedException()
		: base("Unauthorized.", 401)
	{
	}
}
