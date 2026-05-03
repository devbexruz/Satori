namespace Satori.Domain.Entities;

// -- PERMISSIONS --

public class Permission
{
    public long Id { get; set; }
    public string Code { get; set; } = string.Empty; // varchar

    public ICollection<MemberPermission> MemberPermissions { get; set; } = new List<MemberPermission>();
}
