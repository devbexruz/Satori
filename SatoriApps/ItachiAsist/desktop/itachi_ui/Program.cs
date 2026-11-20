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
    private static System.Threading.Mutex? _singleInstanceMutex;

    [STAThread]
    public static void Main(string[] args)
    {
        try
        {
            _singleInstanceMutex = new System.Threading.Mutex(true, "ItachiUI_SingleInstance_UniqueLock", out bool createdNew);
            if (!createdNew)
            {
                Console.Error.WriteLine("[ItachiUI] Boshqa UI oynasi allaqachon ishlamoqda. Ikkinchi nusxa to'xtatildi.");
                return;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[ItachiUI] Mutex tekshirishda ogohlantirish: {ex.Message}");
        }

        BuildAvaloniaApp()
            .StartWithClassicDesktopLifetime(args);
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
}
