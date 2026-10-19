using Avalonia;
using System;

namespace ItachiUI;

/// <summary>
/// ItachiUI — C# Avalonia "Puppet" dastur.
/// Python itachi_core tomonidan subprocess sifatida ishga tushiriladi.
/// stdin orqali buyruqlar qabul qiladi, stdout orqali hodisalar yuboradi.
/// </summary>
internal class Program
{
    // Dastur ishga tushirilganda birinchi chaqiriladigan metod.
    // Avalonia platformasini initsializatsiya qilish uchun
    // [STAThread] kerak (Windows da).
    [STAThread]
    public static void Main(string[] args)
    {
        BuildAvaloniaApp()
            .StartWithClassicDesktopLifetime(args);
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
}
