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

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // 1. PostgreSQL ga "pgvector" kengaytmasini o'rnatishni buyuramiz
        modelBuilder.HasPostgresExtension("vector");

        // --- LogData jadvali sozlamalari ---
        modelBuilder.Entity<LogData>(entity =>
        {
            // Vector ustunini Gemini 004 modeliga moslab (768 o'lcham) belgilaymiz
            entity.Property(e => e.Embedding)
                .HasColumnType("vector(768)");

            // Metadata ustunini JSONB formatiga o'tkazamiz
            entity.Property(e => e.Metadata)
                .HasColumnType("jsonb");
        });

        // --- InsightData jadvali sozlamalari ---
        modelBuilder.Entity<InsightData>(entity =>
        {
            entity.Property(e => e.VectorSummary)
                .HasColumnType("vector(768)");

            entity.Property(e => e.AnalysisData)
                .HasColumnType("jsonb");
        });

        // (EF Core ko'p bog'liqliklarni o'zi topib oladi, shuning uchun boshqa FK'larni yozish shart emas)
    }
}