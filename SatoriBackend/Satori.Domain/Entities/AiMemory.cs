using Pgvector;

namespace Satori.Domain.Entities;

/// <summary>
/// Itachi AI agentining xotira qatlami.
/// RAG (Retrieval-Augmented Generation) uchun
/// foydalanuvchi bilan suhbat tarixi va muhim faktlar.
///
/// Vector embedding pgvector orqali saqlanadi —
/// semantik qidiruv imkoni beradi.
/// </summary>
public class AiMemory
{
    public long Id { get; set; }

    /// <summary>Foydalanuvchi kiritgan matn yoki hodisa xulosa</summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>Xotira turi: CONVERSATION, FACT, SUMMARY, PREFERENCE</summary>
    public string MemoryType { get; set; } = "CONVERSATION";

    /// <summary>
    /// Qaysi ilovadan: "itachi-assist", "satori-desktop"
    /// </summary>
    public string AppSlug { get; set; } = "itachi-assist";

    /// <summary>
    /// text-embedding-004 (768 dim) — semantik qidiruv uchun.
    /// Null bo'lishi mumkin (embedding hali hisoblanmagan).
    /// </summary>
    public Vector? Embedding { get; set; }

    /// <summary>Xotira ahamiyati — vaqt o'tishi bilan pasayadi</summary>
    public float Importance { get; set; } = 1.0f;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? ExpiresAt { get; set; }  // Null = abadiy

    // Navigation
    public long UserId { get; set; }
    public User User { get; set; } = null!;
}
