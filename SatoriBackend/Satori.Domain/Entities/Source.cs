namespace Satori.Domain.Entities;

// --- SOURCE ---

public class Source
{
    public long Id { get; set; }
    public int Code { get; set; }
    public string Name { get; set; } = string.Empty;

    public ICollection<LogData> Logs { get; set; } = new List<LogData>();
}

