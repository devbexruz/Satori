using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;
using Pgvector;

#nullable disable

namespace Satori.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddSatoriAiTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "satori_activity_logs",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    AppSlug = table.Column<string>(type: "text", nullable: false),
                    SessionId = table.Column<string>(type: "text", nullable: false),
                    LogLevel = table.Column<string>(type: "text", nullable: false),
                    Category = table.Column<string>(type: "text", nullable: false),
                    Payload = table.Column<string>(type: "jsonb", nullable: false, defaultValue: "{}"),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    UserId = table.Column<long>(type: "bigint", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_satori_activity_logs", x => x.Id);
                    table.ForeignKey(
                        name: "FK_satori_activity_logs_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.SetNull);
                });

            migrationBuilder.CreateTable(
                name: "satori_ai_memories",
                columns: table => new
                {
                    Id = table.Column<long>(type: "bigint", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    Content = table.Column<string>(type: "text", nullable: false),
                    MemoryType = table.Column<string>(type: "text", nullable: false),
                    AppSlug = table.Column<string>(type: "text", nullable: false),
                    Embedding = table.Column<Vector>(type: "vector(768)", nullable: true),
                    Importance = table.Column<float>(type: "real", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    ExpiresAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    UserId = table.Column<long>(type: "bigint", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_satori_ai_memories", x => x.Id);
                    table.ForeignKey(
                        name: "FK_satori_ai_memories_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_satori_activity_logs_AppSlug",
                table: "satori_activity_logs",
                column: "AppSlug");

            migrationBuilder.CreateIndex(
                name: "IX_satori_activity_logs_Category",
                table: "satori_activity_logs",
                column: "Category");

            migrationBuilder.CreateIndex(
                name: "IX_satori_activity_logs_CreatedAt",
                table: "satori_activity_logs",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_satori_activity_logs_UserId",
                table: "satori_activity_logs",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_satori_ai_memories_CreatedAt",
                table: "satori_ai_memories",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_satori_ai_memories_MemoryType",
                table: "satori_ai_memories",
                column: "MemoryType");

            migrationBuilder.CreateIndex(
                name: "IX_satori_ai_memories_UserId",
                table: "satori_ai_memories",
                column: "UserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "satori_activity_logs");

            migrationBuilder.DropTable(
                name: "satori_ai_memories");
        }
    }
}
