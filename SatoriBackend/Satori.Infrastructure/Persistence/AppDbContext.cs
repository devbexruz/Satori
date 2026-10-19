using Microsoft.EntityFrameworkCore;
using Satori.Domain.Entities;

namespace Satori.Infrastructure.Persistence;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    // Jadvallar (Tables)
    public DbSet<User> Users => Set<User>();
    public DbSet<Device> Devices => Set<Device>();
    public DbSet<LogData> LogDatas => Set<LogData>();
    public DbSet<InsightData> InsightDatas => Set<InsightData>();
    public DbSet<Source> Sources => Set<Source>();
    public DbSet<Activity> Activities => Set<Activity>();
    public DbSet<Family> Families => Set<Family>();
    public DbSet<FamilyMember> FamilyMembers => Set<FamilyMember>();
    public DbSet<Permission> Permissions => Set<Permission>();
    public DbSet<MemberPermission> MemberPermissions => Set<MemberPermission>();

    // === Satori AI ===
    public DbSet<ActivityLog> ActivityLogs => Set<ActivityLog>();
    public DbSet<AiMemory> AiMemories => Set<AiMemory>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // PostgreSQL pgvector kengaytmasi
        modelBuilder.HasPostgresExtension("vector");

        // --- LogData ---
        modelBuilder.Entity<LogData>(entity =>
        {
            entity.Property(e => e.Embedding)
                .HasColumnType("vector(768)");
            entity.Property(e => e.Metadata)
                .HasColumnType("jsonb");
        });

        // --- InsightData ---
        modelBuilder.Entity<InsightData>(entity =>
        {
            entity.Property(e => e.VectorSummary)
                .HasColumnType("vector(768)");
            entity.Property(e => e.AnalysisData)
                .HasColumnType("jsonb");
        });

        // === Satori AI Tables ===

        // --- ActivityLog ---
        modelBuilder.Entity<ActivityLog>(entity =>
        {
            entity.ToTable("satori_activity_logs");
            entity.HasIndex(e => e.CreatedAt);
            entity.HasIndex(e => e.AppSlug);
            entity.HasIndex(e => e.Category);

            // Payload JSONB formatida
            entity.Property(e => e.Payload)
                .HasColumnType("jsonb")
                .HasDefaultValue("{}");

            // UserId ixtiyoriy (anonymous log ham bo'lishi mumkin)
            entity.HasOne(e => e.User)
                .WithMany(u => u.ActivityLogs)
                .HasForeignKey(e => e.UserId)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.SetNull);
        });

        // --- AiMemory ---
        modelBuilder.Entity<AiMemory>(entity =>
        {
            entity.ToTable("satori_ai_memories");
            entity.HasIndex(e => e.UserId);
            entity.HasIndex(e => e.MemoryType);
            entity.HasIndex(e => e.CreatedAt);

            // 768 dim embedding (text-embedding-004)
            entity.Property(e => e.Embedding)
                .HasColumnType("vector(768)");

            // UserId majburiy
            entity.HasOne(e => e.User)
                .WithMany(u => u.AiMemories)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}