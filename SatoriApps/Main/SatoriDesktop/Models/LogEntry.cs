namespace SatoriDesktop.Models;

// Log turlari
public enum LogLevel { Info, Warning, Error, Success }

public class LogEntry
{
    public string Time { get; set; }
    public string Message { get; set; }
    public LogLevel Level { get; set; }
    
    // Log darajasiga qarab yon panel (Border) rangini belgilash
    public string IndicatorColor => Level switch
    {
        LogLevel.Info => "#3B82F6",    // Ko'k
        LogLevel.Warning => "#F59E0B", // Sariq
        LogLevel.Error => "#EF4444",   // Qizil
        LogLevel.Success => "#10B981", // Yashil
        _ => "#888888"
    };
}