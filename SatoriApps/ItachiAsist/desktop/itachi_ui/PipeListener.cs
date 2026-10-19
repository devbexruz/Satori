using System;
using System.IO;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Avalonia.Threading;
using ItachiUI.Views;

namespace ItachiUI;

/// <summary>
/// Python itachi_core bilan stdin/stdout NDJSON protokoli orqali aloqa.
/// 
/// PROTOKOL:
///   stdin  ← Python yuborgan buyruqlar (JSON + '\n')
///   stdout → Python ga yuboradigan hodisalar (JSON + '\n')
/// 
/// Buyruq strukturasi:
///   {"cmd": "EYE_STATE", "mode": "MANGEKYOU", "spin_speed": 6.5}
///   {"cmd": "CHAT_REPLY", "text": "Salom", "typing_effect": true}
///   {"cmd": "AUDIO_AMP", "value": 0.78}
///   {"cmd": "WINDOW", "action": "SHOW", "position": "BOTTOM_RIGHT"}
/// </summary>
public class PipeListener
{
    private readonly MainWindow _window;
    private CancellationTokenSource? _cts;
    private Thread? _readThread;

    public PipeListener(MainWindow window)
    {
        _window = window;
    }

    /// <summary>
    /// stdin o'qishni fon threadida boshlash.
    /// </summary>
    public void Start()
    {
        _cts = new CancellationTokenSource();
        _readThread = new Thread(ReadLoop)
        {
            IsBackground = true,
            Name = "PipeListener"
        };
        _readThread.Start();
    }

    public void Stop()
    {
        _cts?.Cancel();
    }

    // -------------------------------------------------------
    // Python → C#: stdin o'qish
    // -------------------------------------------------------

    private void ReadLoop()
    {
        using var reader = new StreamReader(Console.OpenStandardInput());

        while (!_cts!.Token.IsCancellationRequested)
        {
            try
            {
                string? line = reader.ReadLine();
                if (line is null) break;   // stdin yopildi
                line = line.Trim();
                if (string.IsNullOrEmpty(line)) continue;

                ProcessCommand(line);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                Console.Error.WriteLine($"[PipeListener] O'qish xatosi: {ex.Message}");
            }
        }
    }

    private void ProcessCommand(string json)
    {
        try
        {
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;
            string cmd = root.GetProperty("cmd").GetString() ?? "";

            // UI threadida ishlash (Avalonia talabi)
            Dispatcher.UIThread.Post(() =>
            {
                switch (cmd)
                {
                    case "WINDOW":
                        HandleWindowCmd(root);
                        break;
                    case "EYE_STATE":
                        HandleEyeStateCmd(root);
                        break;
                    case "AUDIO_AMP":
                        HandleAudioAmpCmd(root);
                        break;
                    case "CHAT_REPLY":
                        HandleChatReplyCmd(root);
                        break;
                    case "CHAT_THINKING":
                        HandleChatThinkingCmd(root);
                        break;
                    case "SHUTDOWN":
                        _window.Close();
                        break;
                    default:
                        Console.Error.WriteLine($"[PipeListener] Noma'lum buyruq: {cmd}");
                        break;
                }
            });
        }
        catch (JsonException ex)
        {
            Console.Error.WriteLine($"[PipeListener] JSON xatosi: {ex.Message} | Input: {json}");
        }
    }

    private void HandleWindowCmd(JsonElement root)
    {
        string action = root.TryGetProperty("action", out var a) ? a.GetString() ?? "" : "";
        switch (action)
        {
            case "SHOW":
                _window.Show();
                break;
            case "HIDE":
                _window.Hide();
                break;
        }
    }

    private void HandleEyeStateCmd(JsonElement root)
    {
        string mode = root.TryGetProperty("mode", out var m) ? m.GetString() ?? "IDLE_3TOMOE" : "IDLE_3TOMOE";
        double speed = root.TryGetProperty("spin_speed", out var s) ? s.GetDouble() : 1.0;
        string glow = root.TryGetProperty("glow", out var g) ? g.GetString() ?? "#AAFF0000" : "#AAFF0000";

        _window.SetEyeState(mode, speed, glow);
    }

    private void HandleAudioAmpCmd(JsonElement root)
    {
        double value = root.TryGetProperty("value", out var v) ? v.GetDouble() : 0.0;
        _window.SetAudioAmplitude(value);
    }

    private void HandleChatReplyCmd(JsonElement root)
    {
        string text = root.TryGetProperty("text", out var t) ? t.GetString() ?? "" : "";
        bool typing = root.TryGetProperty("typing_effect", out var te) && te.GetBoolean();
        _window.ShowChatReply(text, typing);
    }

    private void HandleChatThinkingCmd(JsonElement root)
    {
        bool visible = root.TryGetProperty("visible", out var v) && v.GetBoolean();
        _window.ShowThinking(visible);
    }

    // -------------------------------------------------------
    // C# → Python: stdout ga hodisa yuborish
    // -------------------------------------------------------

    public static void SendEvent(string eventName, object? data = null)
    {
        var payload = new
        {
            @event = eventName,
            timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            data
        };
        string json = JsonSerializer.Serialize(payload);
        Console.WriteLine(json);
        Console.Out.Flush();
    }
}
