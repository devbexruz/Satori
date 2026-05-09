using Microsoft.EntityFrameworkCore;
using Satori.Application.Interfaces.Repositories;
using Satori.Domain.Entities;
using Satori.Infrastructure.Persistence; // DbContext turgan joy

namespace Satori.Infrastructure.Persistence.Repositories;

public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;

    public UserRepository(AppDbContext context)
    {
        _context = context;
    }
    // Get By Username
    public async Task<User?> GetByUsernameAsync(string username)
    {
        // Bazadan username bo'yicha birinchi uchragan foydalanuvchini topamiz
        return await _context.Users
            .FirstOrDefaultAsync(u => u.Username == username);
    }

    // Add User
    public async Task AddAsync(User user)
    {
        await _context.Users.AddAsync(user);
        await _context.SaveChangesAsync();
    }

    // Get By Id
    public async Task<User?> GetByIdAsync(long id)
    {
        return await _context.Users.FindAsync(id);
    }

    // Get All Users
    public async Task<List<User>> GetAllAsync()
    {
        return await _context.Users.ToListAsync();
    }

    // Save Changes
    public async Task SaveChangesAsync()
    {
        await _context.SaveChangesAsync();
    }
}