namespace Satori.Domain.Entities;

// -- FAMILY MEMBER ---

public class FamilyMember
{
    public long Id { get; set; }
    
    public long FamilyId { get; set; }
    public Family Family { get; set; } = null!;

    public long UserId { get; set; }
    public User User { get; set; } = null!;

    public string Role { get; set; } = string.Empty; // text

    public ICollection<MemberPermission> Permissions { get; set; } = new List<MemberPermission>();
}
