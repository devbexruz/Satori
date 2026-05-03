namespace Satori.Domain.Entities;

// --- DEVICE ---
public class Device
{
    public long Id { get; set; }
    public long UserId { get; set; }
    public User User { get; set; } = null!;

    // Rasmda bigint edi, lekin nom odatda string bo'ladi
    public string Name { get; set; } = string.Empty; 
    public string SecretKey { get; set; } = string.Empty;
    
    // Mac address ham odatda string (yoki maxsus format) bo'ladi
    public string MacAddress { get; set; } = string.Empty; 

    public ICollection<LogData> Logs { get; set; } = new List<LogData>();
}
