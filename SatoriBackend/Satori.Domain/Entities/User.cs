namespace Satori.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Satori.Domain.Enums;

// --- USER ---
[Index(nameof(Username), IsUnique = true)]
public class User
{
    public long Id { get; set; }
    public string FullName { get; set; } = string.Empty;
    public UserRole Role { get; set; }
    public string Username { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string AccessToken { get; set; } = string.Empty;

    // Navigation properties
    public ICollection<LogData> Logs { get; set; } = new List<LogData>();
    public ICollection<InsightData> Insights { get; set; } = new List<InsightData>();
    public ICollection<Device> Devices { get; set; } = new List<Device>();
    public ICollection<FamilyMember> FamilyMemberships { get; set; } = new List<FamilyMember>();
    public Family? OwnedFamily { get; set; } // Agar foydalanuvchi bitta oila yarata olsa
}
