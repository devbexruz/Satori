namespace Satori.Domain.Entities;

// --- ACTIVITY ---

public class Activity
{
    public long Id { get; set; }
    public string Name { get; set; } = string.Empty; // Rasmda bigint edi, string qildim

    public ICollection<LogData> Logs { get; set; } = new List<LogData>();
}
