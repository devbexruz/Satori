using System;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Markup.Xaml;
using Avalonia.Threading;

namespace ItachiUI.Controls;

/// <summary>
/// ItachiAvatarControl — Itachi portreti va uning Sharingan ko'zlari.
/// 
/// QOIDALAR:
/// - Boshlang'ich holat (Idle): Itachi 50% (0.50), Ko'zlar 0% (0.00 - to'liq shaffof).
/// - Uyg'onish (Wake Word / Click):
///     1. Ko'zlar 0 dan 100% gacha Ease-Out formulasi bilan yorishadi.
///     2. Keyin ko'zlar 80% gacha Ease-In formulasi bilan barqarorlashadi.
///     3. Itachining asosiy qismi 50% dan 80% gacha ko'tariladi.
/// - Asosiy qism (Itachi tanasi) HECH QACHON 80% (0.80) dan oshmaydi!
/// </summary>
public partial class ItachiAvatarControl : UserControl
{
    private Image? _baseItachiImage;
    private Image? _eyesOverlayImage;
    private Border? _auraGlow;
    private Border? _eyeFlare;
    private Grid? _rootGrid;

    // Asosiy qism va ko'zlar shaffofligi (0.0 - 1.0)
    // Standart holat: Itachi 50%, Ko'zlar 0% (to'liq shaffof)
    private double _currentBaseOpacity = 0.50;  // Default 50%
    private double _targetBaseOpacity = 0.50;   // Default 50%

    private double _currentEyesOpacity = 0.00;  // Default 0%
    private double _targetEyesOpacity = 0.00;   // Default 0%

    private double _manualEyesOpacity = -1.0;   // Foydalanuvchi qo'lda belgilagan bo'lsa (0.0 - 1.0)

    // Qat'iy chegara — Itachi tanasi hech qachon 80% dan oshmaydi!
    private const double MaxBaseOpacity = 0.80;

    // Uyg'onish animatsiyasi (Wake Animation: Ease-Out 0->100%, keyin Ease-In 100->80%)
    private bool _isWakeAnimating = false;
    private double _wakeTimer = 0.0;
    private const double WakeBurstDuration = 0.40;   // 0.4s: 0% -> 100% Ease-Out
    private const double WakeSettleDuration = 0.60;  // 0.6s: 100% -> 80% Ease-In
    private double _wakeActiveHoldTimer = 0.0;       // Necha soniya 80% da faol turishi

    // Rejimlar
    private string _mode = "IDLE";
    private double _audioAmplitude = 0.0;
    private double _pulsePhase = 0.0;
    private bool _isPointerOver = false;

    private readonly DispatcherTimer _animTimer;

    public ItachiAvatarControl()
    {
        InitializeComponent();

        _baseItachiImage = this.FindControl<Image>("BaseItachiImage");
        _eyesOverlayImage = this.FindControl<Image>("EyesOverlayImage");
        _auraGlow = this.FindControl<Border>("AuraGlow");
        _eyeFlare = this.FindControl<Border>("EyeFlare");
        _rootGrid = this.FindControl<Grid>("RootGrid");

        if (_rootGrid != null)
        {
            _rootGrid.PointerEntered += OnPointerEntered;
            _rootGrid.PointerExited += OnPointerExited;
        }

        // Boshlang'ich holat: Itachi 50%, Ko'zlar 0%
        ApplyVisualOpacity(_currentEyesOpacity, _currentBaseOpacity);

        // 60 FPS silliq animatsiya taymeri (~16ms)
        _animTimer = new DispatcherTimer(
            TimeSpan.FromMilliseconds(16),
            DispatcherPriority.Render,
            OnAnimTick);
        _animTimer.Start();
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    // ───────────────────────────────────────────────────────────────
    // Uyg'onish Animatsiyasi: Ease-Out (0->100%) + Ease-In (100->80%)
    // ───────────────────────────────────────────────────────────────

    /// <summary>
    /// "Itachi" yoki "Hey Itachi" eshitilganda chaqiriladi.
    /// Ko'zlar 0 dan 100% gacha Ease-Out formulasi bilan chaqnaydi,
    /// so'ngra 80% gacha Ease-In formulasi bilan o'rnashadi.
    /// Asosiy qism 50% dan 80% gacha ko'tariladi (max 80%).
    /// </summary>
    public void TriggerWakeAnimation()
    {
        _manualEyesOpacity = -1.0;
        _isWakeAnimating = true;
        _wakeTimer = 0.0;
        _wakeActiveHoldTimer = 7.0; // 7 soniya faol uyg'oq turadi
        _mode = "ACTIVE";
    }

    // ───────────────────────────────────────────────────────────────
    // Qo'lda Saffolikni O'rnatish (Slayder yoki API)
    // ───────────────────────────────────────────────────────────────

    public void SetEyesOpacity(double percent, bool instant = false)
    {
        double eyesClamped = Math.Clamp(percent / 100.0, 0.0, 1.0);
        _manualEyesOpacity = eyesClamped;
        _targetEyesOpacity = eyesClamped;
        _isWakeAnimating = false; // Qo'lda boshqarilganda animatsiyani to'xtatish

        _targetBaseOpacity = CalculateBaseOpacity(eyesClamped);

        if (instant)
        {
            _currentEyesOpacity = _targetEyesOpacity;
            _currentBaseOpacity = _targetBaseOpacity;
            ApplyVisualOpacity(_currentEyesOpacity, _currentBaseOpacity);
        }
    }

    public void ResetToAutoMode()
    {
        _manualEyesOpacity = -1.0;
        _isWakeAnimating = false;
        UpdateTargetsFromState();
    }

    // ───────────────────────────────────────────────────────────────
    // Rejim va Audio boshqaruvi
    // ───────────────────────────────────────────────────────────────

    public void SetMode(string mode, double spinSpeed = 1.0, string glowHex = "#AAFF0000")
    {
        _mode = mode.ToUpperInvariant();
        if (_mode == "ACTIVE" || _mode == "MANGEKYOU" || _mode == "WAKE")
        {
            TriggerWakeAnimation();
            return;
        }

        if (_manualEyesOpacity < 0 && !_isWakeAnimating)
        {
            UpdateTargetsFromState();
        }
    }

    public void SetAmplitude(double value)
    {
        _audioAmplitude = Math.Clamp(value, 0.0, 1.0);
        if (_manualEyesOpacity < 0 && !_isWakeAnimating)
        {
            UpdateTargetsFromState();
        }
    }

    private static double CalculateBaseOpacity(double eyesOpacity)
    {
        // eyes = 0.00 -> base = 0.50 (50% shaffoflik)
        // eyes >= 0.80 -> base = 0.80 (80% shaffoflik)
        // Har doim 0.50 dan 0.80 gacha! Hech qachon 0.80 dan oshmaydi.
        double ratio = Math.Clamp(eyesOpacity / 0.80, 0.0, 1.0);
        double baseCalculated = 0.50 + ratio * (MaxBaseOpacity - 0.50);
        return Math.Clamp(baseCalculated, 0.50, MaxBaseOpacity);
    }

    private void UpdateTargetsFromState()
    {
        if (_manualEyesOpacity >= 0)
        {
            _targetEyesOpacity = _manualEyesOpacity;
            _targetBaseOpacity = CalculateBaseOpacity(_manualEyesOpacity);
            return;
        }

        // Hover holatida ko'zlar 100%, asosiy qism 80%
        if (_isPointerOver)
        {
            _targetEyesOpacity = 1.00;
            _targetBaseOpacity = MaxBaseOpacity;
            return;
        }

        switch (_mode)
        {
            case "ACTIVE":
                _targetEyesOpacity = 0.80;
                _targetBaseOpacity = MaxBaseOpacity;
                break;

            case "THINKING":
                _targetEyesOpacity = 0.65 + 0.35 * Math.Abs(Math.Sin(_pulsePhase * 2.5));
                _targetBaseOpacity = CalculateBaseOpacity(_targetEyesOpacity);
                break;

            case "SPEAKING":
                _targetEyesOpacity = 0.60 + _audioAmplitude * 0.40;
                _targetBaseOpacity = CalculateBaseOpacity(_targetEyesOpacity);
                break;

            case "IDLE":
            default:
                // Standart tinch holat: Itachi 50%, Ko'zlar 0% (to'liq shaffof)
                _targetEyesOpacity = 0.00;
                _targetBaseOpacity = 0.50;
                break;
        }
    }

    // ───────────────────────────────────────────────────────────────
    // Animatsiya Takti (60 FPS)
    // ───────────────────────────────────────────────────────────────

    private void OnAnimTick(object? sender, EventArgs e)
    {
        _pulsePhase += 0.05;
        if (_pulsePhase > Math.PI * 2.0) _pulsePhase -= Math.PI * 2.0;

        // 1. Agar Wake Animation (Uyg'onish) ishlayotgan bo'lsa
        if (_isWakeAnimating)
        {
            ProcessWakeAnimationStep(0.016); // ~16ms delta
        }
        else
        {
            if (_manualEyesOpacity < 0)
            {
                UpdateTargetsFromState();
            }

            // Silliq o'tish (Smooth Lerp)
            double lerpSpeed = 0.18;
            _currentEyesOpacity += (_targetEyesOpacity - _currentEyesOpacity) * lerpSpeed;
            _currentBaseOpacity += (_targetBaseOpacity - _currentBaseOpacity) * lerpSpeed;
            _currentBaseOpacity = Math.Min(_currentBaseOpacity, MaxBaseOpacity);
        }

        ApplyVisualOpacity(_currentEyesOpacity, _currentBaseOpacity);
    }

    private void ProcessWakeAnimationStep(double dt)
    {
        _wakeTimer += dt;

        // Faza 1: 0 dan 100% gacha Ease-Out (0.0 -> 0.40s)
        if (_wakeTimer <= WakeBurstDuration)
        {
            double u = _wakeTimer / WakeBurstDuration;
            // Ease-Out Cubic: 1 - (1 - u)^3
            double easeOut = 1.0 - Math.Pow(1.0 - u, 3.0);

            _currentEyesOpacity = easeOut * 1.0; // 0.0 -> 1.00 (0 -> 100%)
            _currentBaseOpacity = 0.50 + 0.30 * easeOut; // 0.50 -> 0.80 (50% -> 80%)
        }
        // Faza 2: 100% dan 80% gacha Ease-In (0.40s -> 1.00s)
        else if (_wakeTimer <= (WakeBurstDuration + WakeSettleDuration))
        {
            double v = (_wakeTimer - WakeBurstDuration) / WakeSettleDuration;
            // Ease-In Quad: v^2
            double easeIn = Math.Pow(v, 2.0);

            _currentEyesOpacity = 1.0 - (1.0 - 0.80) * easeIn; // 1.0 -> 0.80 (100% -> 80%)
            _currentBaseOpacity = MaxBaseOpacity; // 0.80 da mustahkam
        }
        // Faza 3: 80% da faol turish va so'ngra tinch holatga qaytish
        else
        {
            _currentEyesOpacity = 0.80;
            _currentBaseOpacity = MaxBaseOpacity;

            _wakeActiveHoldTimer -= dt;
            if (_wakeActiveHoldTimer <= 0.0)
            {
                // Tinch holatga qaytish
                _isWakeAnimating = false;
                _mode = "IDLE";
                _targetEyesOpacity = 0.00;
                _targetBaseOpacity = 0.50;
            }
        }

        _currentBaseOpacity = Math.Min(_currentBaseOpacity, MaxBaseOpacity);
    }

    private void ApplyVisualOpacity(double eyesOpacity, double baseOpacity)
    {
        baseOpacity = Math.Clamp(baseOpacity, 0.0, MaxBaseOpacity);
        eyesOpacity = Math.Clamp(eyesOpacity, 0.0, 1.0);

        // 1. Asosiy qism (Itachi tanasi) — Tinch holatda 50%, Max 80%
        if (_baseItachiImage != null)
        {
            _baseItachiImage.Opacity = baseOpacity;
        }

        // 2. Ko'zlar qatlami — Tinch holatda 0% (to'liq shaffof), Uyg'onganda 100% -> 80%
        if (_eyesOverlayImage != null)
        {
            _eyesOverlayImage.Opacity = eyesOpacity;
        }

        // 3. Orqa fon qizil aurası (ko'zlar 40% dan yuqoriga yonganda kuchayadi)
        if (_auraGlow != null)
        {
            double aura = Math.Max(0.0, (eyesOpacity - 0.30) / 0.70);
            _auraGlow.Opacity = aura * 0.85;
        }

        // 4. Yuqori porlash nuri (ko'zlar 70% dan yuqori bo'lganda chaqnaydi)
        if (_eyeFlare != null)
        {
            double flare = Math.Max(0.0, (eyesOpacity - 0.70) / 0.30);
            _eyeFlare.Opacity = flare * 0.75;
        }
    }

    // ───────────────────────────────────────────────────────────────
    // Sichqoncha hodisalari (Hover = Ko'zlar 100%, Asosiy qism 80%)
    // ───────────────────────────────────────────────────────────────

    private void OnPointerEntered(object? sender, PointerEventArgs e)
    {
        _isPointerOver = true;
    }

    private void OnPointerExited(object? sender, PointerEventArgs e)
    {
        _isPointerOver = false;
    }
}
