namespace Satori.Domain.Entities;

using Pgvector;
using Satori.Domain.Enums;

// --- INSIGHT DATA ---

public class InsightData
{
    public long Id { get; set; }
    public DateTime CreatedAt { get; set; }
    public long UserId { get; set; }
    public User User { get; set; } = null!;

    public PeriodType PeriodType { get; set; }
    public DateTime TargetDate { get; set; } // date
    
    public string? AnalysisData { get; set; } // jsonb
    public short? OverallScore { get; set; }  // smallint
    
    public Vector? VectorSummary { get; set; } // pgvector
    
    public string? PrimaryFocus { get; set; } // varchar(100)
}
