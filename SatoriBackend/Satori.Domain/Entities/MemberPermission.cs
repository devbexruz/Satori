namespace Satori.Domain.Entities;

// -- MEMBER PERMISSION ---
public class MemberPermission
{
    public long Id { get; set; }
    
    public long MemberId { get; set; }
    public FamilyMember Member { get; set; } = null!;

    public long FamilyId { get; set; }
    public Family Family { get; set; } = null!;

    public long PermissionId { get; set; } // Rasmda permestion_id
    public Permission Permission { get; set; } = null!;

    public bool IsAccess { get; set; } // boolean
}