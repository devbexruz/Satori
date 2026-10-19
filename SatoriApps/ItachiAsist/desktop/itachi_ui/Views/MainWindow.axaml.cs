using System;
using System.Threading;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Threading;
using ItachiUI.Controls;

namespace ItachiUI.Views;

/// <summary>
/// MainWindow — Shaffof overlay asosiy oynasi.
/// 
/// Python itachi_core dan buyruqlar qabul qilib,
/// Sharingan animatsiyasi, chat paneli va input ni boshqaradi.
/// </summary>
public partial class MainWindow : Window
{
    private PipeListener? _pipeListener;
    private bool _inputVisible = false;
    private CancellationTokenSource? _typingCts;

    public MainWindow()
    {
        InitializeComponent();
        SetupWindow();
        StartPipeListener();
    }

    private void InitializeComponent()
    {
        Avalonia.Markup.Xaml.AvaloniaXamlLoader.Load(this);
    }

    // -------------------------------------------------------
    // Oyna sozlash
    // -------------------------------------------------------

    private void SetupWindow()
    {
        // Ekranning o'ng pastki burchagi
        PositionToBottomRight();

        // Oyna ochilganda Python ga xabar berish
        Opened += (_, _) =>
        {
            PipeListener.SendEvent("UI_READY");
        };
    }

    private void PositionToBottomRight()
    {
        var screen = Screens.Primary;
        if (screen is null) return;

        double screenW = screen.WorkingArea.Width;
        double screenH = screen.WorkingArea.Height;

        Position = new PixelPoint(
            (int)(screenW - Width - 20),
            (int)(screenH - Height - 20)
        );
    }

    private void StartPipeListener()
    {
        _pipeListener = new PipeListener(this);
        _pipeListener.Start();
    }

    // -------------------------------------------------------
    // Python buyruqlarini bajarish (PipeListener chaqiradi)
    // -------------------------------------------------------

    public void SetEyeState(string mode, double spinSpeed, string glow)
    {
        Sharingan?.SetMode(mode, spinSpeed, glow);
    }

    public void SetAudioAmplitude(double value)
    {
        Sharingan?.SetAmplitude(value);
    }

    public void ShowChatReply(string text, bool typingEffect)
    {
        // Chat panelini ko'rsatish
        if (ChatPanel is not null) ChatPanel.IsVisible = true;
        if (ThinkingPanel is not null) ThinkingPanel.IsVisible = false;

        if (typingEffect)
        {
            _ = TypeTextAsync(text);
        }
        else
        {
            if (ChatText is not null)
            {
                ChatText.Text = text;
                ChatText.IsVisible = true;
            }
        }

        // 30 soniyadan keyin chat panelini yashirish
        _ = HideChatAfterAsync(30_000);
    }

    public void ShowThinking(bool visible)
    {
        if (ChatPanel is not null) ChatPanel.IsVisible = visible;
        if (ThinkingPanel is not null) ThinkingPanel.IsVisible = visible;
        if (ChatText is not null && visible) ChatText.IsVisible = false;
    }

    // -------------------------------------------------------
    // Typing animatsiyasi
    // -------------------------------------------------------

    private async Task TypeTextAsync(string text)
    {
        _typingCts?.Cancel();
        _typingCts = new CancellationTokenSource();
        var token = _typingCts.Token;

        if (ChatText is null) return;
        ChatText.Text = "";
        ChatText.IsVisible = true;

        foreach (char ch in text)
        {
            if (token.IsCancellationRequested) break;
            ChatText.Text += ch;
            await Task.Delay(22, CancellationToken.None);  // ~45 belgi/soniya
        }
    }

    private async Task HideChatAfterAsync(int delayMs)
    {
        await Task.Delay(delayMs);
        Dispatcher.UIThread.Post(() =>
        {
            if (ChatPanel is not null) ChatPanel.IsVisible = false;
        });
    }

    // -------------------------------------------------------
    // Foydalanuvchi hodisalari
    // -------------------------------------------------------

    private void Sharingan_Clicked(object? sender, PointerPressedEventArgs e)
    {
        // Ko'zga bosish → input panelini ko'rsatish/yashirish
        _inputVisible = !_inputVisible;
        if (InputPanel is not null) InputPanel.IsVisible = _inputVisible;

        if (_inputVisible)
        {
            InputBox?.Focus();
        }

        PipeListener.SendEvent("EYE_CLICKED", new { button = "LEFT" });
    }

    private void InputBox_KeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Key == Key.Return || e.Key == Key.Enter)
        {
            SubmitInput();
        }
        else if (e.Key == Key.Escape)
        {
            _inputVisible = false;
            if (InputPanel is not null) InputPanel.IsVisible = false;
        }
    }

    private void SendBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        SubmitInput();
    }

    private void ScreenBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        // Ekranga qarab yuborish (include_screen: true)
        string text = InputBox?.Text?.Trim() ?? "Ekrandagi narsani tahlil qil";
        if (InputBox is not null) InputBox.Text = "";
        _inputVisible = false;
        if (InputPanel is not null) InputPanel.IsVisible = false;

        PipeListener.SendEvent("USER_TEXT_SUBMIT", new
        {
            text,
            include_screen = true
        });
    }

    private void SubmitInput()
    {
        string text = InputBox?.Text?.Trim() ?? "";
        if (string.IsNullOrEmpty(text)) return;

        if (InputBox is not null) InputBox.Text = "";
        _inputVisible = false;
        if (InputPanel is not null) InputPanel.IsVisible = false;

        // Python ga yuborish
        PipeListener.SendEvent("USER_TEXT_SUBMIT", new
        {
            text,
            include_screen = false
        });
    }

    // -------------------------------------------------------
    // Oyna yopilish
    // -------------------------------------------------------

    protected override void OnClosing(WindowClosingEventArgs e)
    {
        _pipeListener?.Stop();
        base.OnClosing(e);
    }
}
