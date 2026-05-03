using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Satori.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class CreatedAtfieldaddtoInsightDataandLogDatatabales : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "CreatedAt",
                table: "LogDatas",
                type: "timestamp with time zone",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));

            migrationBuilder.AddColumn<DateTime>(
                name: "CreatedAt",
                table: "InsightDatas",
                type: "timestamp with time zone",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified));
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "CreatedAt",
                table: "LogDatas");

            migrationBuilder.DropColumn(
                name: "CreatedAt",
                table: "InsightDatas");
        }
    }
}
