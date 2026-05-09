using System;
using System.Collections.ObjectModel;
using SatoriDesktop.Models;

namespace SatoriDesktop.ViewModels;

public class MainWindowViewModel
{
    public ObservableCollection<LogEntry> Logs { get; set; } = new();
    public UserProfile CurrentUser { get; set; }

    public MainWindowViewModel()
    {
        // Profil ma'lumotlari
        CurrentUser = new UserProfile
        {
            Name = "Bexruz",
            Role = "System Administrator",
            Email = "admin@satori.dev",
            Status = "Online (Secured)",
            AvatarInitials = "BX"
        };

        // Boshlang'ich loglar
        Logs.Add(new LogEntry { Time = "08:00:00", Message = "Satori Engine muvaffaqiyatli ishga tushdi.", Level = LogLevel.Success });
        Logs.Add(new LogEntry { Time = "08:05:12", Message = "Tizim resurslari tekshirilmoqda...", Level = LogLevel.Info });
        Logs.Add(new LogEntry { Time = "08:15:44", Message = "Ruxsatsiz kirish urinishi aniqlandi (IP: 192.168.1.45)", Level = LogLevel.Error });
        Logs.Add(new LogEntry { Time = "08:20:10", Message = "Xotira sarfi 85% dan oshdi.", Level = LogLevel.Warning });
    }
}