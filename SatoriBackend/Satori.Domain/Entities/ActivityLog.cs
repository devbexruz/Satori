namespace Satori.Domain.Entities;

/// <summary>
/// Satori ekotizimidagi barcha ilovalardan keladigan
/// faoliyat loglari — markazlashgan telemetriya.
///
/// ItachiAssist, SatoriDesktop va boshqa SatoriApps
/// bu jadvalga o'z loglarini yozadi.
/// </summary>
public class ActivityLog
{
    public long Id { get; set; }

    /// <summary>Qaysi ilovadan: "itachi-assist", "satori-desktop"</summary>
    public string AppSlug { get; set; } = string.Empty;

    /// <summary>Sessiya UUID — bir ishga tushish = bir sessiya</summary>
    public string SessionId { get; set; } = string.Empty;

    /// <summary>Daraja: INFO, ACTION, WARNING, ERROR</summary>
    public string LogLevel { get; set; } = "INFO";

    /// <summary>Kategoriya: OS_WINDOW, IDE_CODE, VOICE_CMD, SYSTEM</summary>
    public string Category { get; set; } = string.Empty;

    /// <summary>Moslashuvchan JSONB payload — turli ma'lumotlar</summary>
    public string Payload { get; set; } = "{}";

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    // Navigation
    public long? UserId { get; set; }
    public User? User { get; set; }
}
