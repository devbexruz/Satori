namespace Satori.Domain.Entities;
using Pgvector;

// --- LOGGING & INSIGHTS ---

public class LogData
{
    public long Id { get; set; }
    public DateTime CreatedAt { get; set; }
    public long UserId { get; set; }
    public User User { get; set; } = null!;

    public long DeviceId { get; set; }
    public Device Device { get; set; } = null!;

    public int SourceCode { get; set; }
    public Source Source { get; set; } = null!;

    public long ActivityTypeId { get; set; }
    public Activity ActivityType { get; set; } = null!;

    public short? FocusScore { get; set; } // smallint uchun short
    public string Content { get; set; } = string.Empty;
    
    // JSONB ustun uchun string yechimi yoki JsonDocument (string ishlashga osonroq)
    public string? Metadata { get; set; } 
    
    // pgvector uchun float massiv
    public Vector? Embedding { get; set; }
}