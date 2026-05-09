using System;
using Avalonia.Controls;

namespace SatoriDesktop.Views
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }
    }

    // LogEntry modeli shu faylda yoki alohida faylda bo‘lishi mumkin
    public class LogEntry
    {
        public DateTime Time { get; set; }
        public string Message { get; set; }

        public LogEntry(string message)
        {
            Time = DateTime.Now;
            Message = message;
        }
    }
}