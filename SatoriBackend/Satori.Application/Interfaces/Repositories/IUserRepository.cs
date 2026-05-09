using System.Collections.Generic;
using System.Threading.Tasks;
using Satori.Domain.Entities;

namespace Satori.Application.Interfaces.Repositories;

public interface IUserRepository
{
	public Task<User?> GetByUsernameAsync(string username);

	public Task AddAsync(User user);

	public Task<User?> GetByIdAsync(long id);

	public Task<List<User>> GetAllAsync();

	public Task SaveChangesAsync();
}
