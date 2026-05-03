namespace Satori.Domain.Entities;

// --- FAMILY ---

public class Family
{
    public long Id { get; set; }
    public long UserId { get; set; } // Owner of the family
    public User User { get; set; } = null!;

    public ICollection<FamilyMember> Members { get; set; } = new List<FamilyMember>();
    public ICollection<MemberPermission> MemberPermissions { get; set; } = new List<MemberPermission>();
}