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
/// Itachi avatari (ko'zlar saffoligi/yonishi), chat paneli va input ni boshqaradi.
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
        PositionToBottomRight();

        Opened += (_, _) =>
        {
            MakeWindowStickyOnAllWorkspaces();
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

    public void TriggerWakeAnimation()
    {
        ItachiAvatar?.TriggerWakeAnimation();
    }

    public void SetEyeState(string mode, double spinSpeed, string glow)
    {
        ItachiAvatar?.SetMode(mode, spinSpeed, glow);
    }

    public void SetEyesOpacity(double percent)
    {
        ItachiAvatar?.SetEyesOpacity(percent);
        if (OpacityLabel != null)
        {
            OpacityLabel.Text = $"{Math.Round(percent)}%";
        }
        if (EyeOpacitySlider != null)
        {
            EyeOpacitySlider.Value = percent;
        }
    }

    public void SetAudioAmplitude(double value)
    {
        ItachiAvatar?.SetAmplitude(value);
    }

    // -------------------------------------------------------
    // Dinamik oyna o'lchami: Tinch holatda faqat Avatar (200x200),
    // Chat yoki Input ochilganda (340x480) kengayadi.
    // -------------------------------------------------------

    private bool _isExpanded = false;

    public void SetExpandedState(bool expanded)
    {
        if (_isExpanded == expanded) return;
        _isExpanded = expanded;

        double targetW = expanded ? 340 : 200;
        double targetH = expanded ? 480 : 200;

        int dw = (int)(targetW - Width);
        int dh = (int)(targetH - Height);

        // Oyna tepaga va chapga kengayadi / torayadi (avatar joyi o'zgarmaydi)
        Position = new PixelPoint(Position.X - dw, Position.Y - dh);
        Width = targetW;
        Height = targetH;
    }

    public void CheckAndCollapse()
    {
        bool hasChat = ChatPanel is not null && ChatPanel.IsVisible;
        bool hasInput = InputPanel is not null && InputPanel.IsVisible;

        if (!hasChat && !hasInput)
        {
            SetExpandedState(false);
        }
    }

    public void ShowChatReply(string text, bool typingEffect)
    {
        SetExpandedState(true);
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

        _ = HideChatAfterAsync(20_000);
    }

    public void ShowThinking(bool visible)
    {
        if (visible)
        {
            SetExpandedState(true);
            if (ChatPanel is not null) ChatPanel.IsVisible = true;
            if (ThinkingPanel is not null) ThinkingPanel.IsVisible = true;
            if (ChatText is not null) ChatText.IsVisible = false;
            ItachiAvatar?.SetMode("THINKING");
        }
        else
        {
            if (ThinkingPanel is not null) ThinkingPanel.IsVisible = false;
            CheckAndCollapse();
            ItachiAvatar?.SetMode("IDLE");
        }
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
            await Task.Delay(22, CancellationToken.None);
        }
    }

    private async Task HideChatAfterAsync(int delayMs)
    {
        await Task.Delay(delayMs);
        Dispatcher.UIThread.Post(() =>
        {
            if (ChatPanel is not null) ChatPanel.IsVisible = false;
            CheckAndCollapse();
        });
    }

    // -------------------------------------------------------
    // Foydalanuvchi hodisalari
    // -------------------------------------------------------

    // -------------------------------------------------------
    // Oynani sudrab ko'chirish (Drag & Drop) va Barcha Ish stollarida (Sticky) ko'rsatish
    // -------------------------------------------------------

    private PixelPoint _dragStartPointerScreen;
    private PixelPoint _dragStartWindowPos;
    private bool _isDragging = false;
    private bool _hasDragged = false;

    private void Avatar_PointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
        {
            _dragStartPointerScreen = this.PointToScreen(e.GetPosition(this));
            _dragStartWindowPos = Position;
            _isDragging = true;
            _hasDragged = false;
        }
    }

    private void Avatar_PointerMoved(object? sender, PointerEventArgs e)
    {
        if (_isDragging)
        {
            var currentScreen = this.PointToScreen(e.GetPosition(this));
            int dx = currentScreen.X - _dragStartPointerScreen.X;
            int dy = currentScreen.Y - _dragStartPointerScreen.Y;

            if (Math.Abs(dx) > 3 || Math.Abs(dy) > 3)
            {
                _hasDragged = true;
                Position = new PixelPoint(
                    _dragStartWindowPos.X + dx,
                    _dragStartWindowPos.Y + dy
                );
            }
        }
    }

    private void Avatar_PointerReleased(object? sender, PointerReleasedEventArgs e)
    {
        if (_isDragging)
        {
            _isDragging = false;
            if (!_hasDragged)
            {
                // Sichqoncha surilmagan bo'lsa (oddiy Click) — Input panelini ochish/yopish
                ToggleInputPanel();
            }
        }
    }

    private void DragHandle_PointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
        {
            BeginMoveDrag(e);
        }
    }

    private void ToggleInputPanel()
    {
        _inputVisible = !_inputVisible;
        if (InputPanel is not null) InputPanel.IsVisible = _inputVisible;

        if (_inputVisible)
        {
            SetExpandedState(true);
            InputBox?.Focus();
            ItachiAvatar?.SetMode("ACTIVE");
        }
        else
        {
            CheckAndCollapse();
            ItachiAvatar?.SetMode("IDLE");
        }

        PipeListener.SendEvent("EYE_CLICKED", new { button = "LEFT" });
    }

    private void MakeWindowStickyOnAllWorkspaces()
    {
        // Linux GNOME/Mutter da oynani barcha virtual ish stollarida (workspaces) ko'rinadigan qilish
        if (System.OperatingSystem.IsLinux())
        {
            Task.Run(async () =>
            {
                await Task.Delay(400); // Oyna to'liq render bo'lishini kutish
                try
                {
                    var psi = new System.Diagnostics.ProcessStartInfo
                    {
                        FileName = "/bin/bash",
                        Arguments = "-c \"for w in $(xdotool search --name 'ItachiAssist' 2>/dev/null); do xprop -id $w -f _NET_WM_STATE 32a -set _NET_WM_STATE '_NET_WM_STATE_STICKY,_NET_WM_STATE_ABOVE' 2>/dev/null; xdotool set_desktop_for_window $w 4294967295 2>/dev/null; done\"",
                        CreateNoWindow = true,
                        UseShellExecute = false
                    };
                    using var proc = System.Diagnostics.Process.Start(psi);
                    proc?.WaitForExit(1000);
                }
                catch { }
            });
        }
    }

    private void EyeOpacitySlider_ValueChanged(object? sender, Avalonia.Controls.Primitives.RangeBaseValueChangedEventArgs e)
    {
        double val = e.NewValue;
        if (OpacityLabel != null)
        {
            OpacityLabel.Text = $"{Math.Round(val)}%";
        }
        ItachiAvatar?.SetEyesOpacity(val);
    }

    private void AutoBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        ItachiAvatar?.ResetToAutoMode();
        if (OpacityLabel != null)
        {
            OpacityLabel.Text = "Auto";
        }
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
            CheckAndCollapse();
            ItachiAvatar?.SetMode("IDLE");
        }
    }

    private void MicBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        ItachiAvatar?.TriggerWakeAnimation();
        PipeListener.SendEvent("MIC_BUTTON_TOGGLED");
    }

    private void SendBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        SubmitInput();
    }

    private void ScreenBtn_Click(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        string text = InputBox?.Text?.Trim() ?? "Ekrandagi narsani tahlil qil";
        if (InputBox is not null) InputBox.Text = "";
        _inputVisible = false;
        if (InputPanel is not null) InputPanel.IsVisible = false;

        ItachiAvatar?.SetMode("THINKING");

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

        ItachiAvatar?.SetMode("THINKING");

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
