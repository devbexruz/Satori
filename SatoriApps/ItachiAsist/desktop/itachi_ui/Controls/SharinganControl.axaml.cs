using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Threading;

namespace ItachiUI.Controls;

// ═══════════════════════════════════════════════════════════════════
// SharinganCanvas — Avalonia DrawingContext orqali GPU rendering
// Qo'shimcha NuGet paket SHART EMAS
// ═══════════════════════════════════════════════════════════════════

/// <summary>
/// Sharingan ko'zini chizuvchi asosiy Control.
/// Avalonia ning o'z DrawingContext API sidan foydalanadi.
/// </summary>
public class SharinganCanvas : Control
{
    private string _mode = "IDLE_3TOMOE";
    private double _spinSpeed = 1.0;
    private Color _glowColor = Color.FromArgb(170, 255, 0, 0);
    private double _audioAmplitude = 0.0;
    private double _rotationAngle = 0;
    private DispatcherTimer? _timer;

    public SharinganCanvas()
    {
        Width = 160;
        Height = 160;
        StartAnimation();
    }

    private void StartAnimation()
    {
        _timer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(16)  // 60 FPS
        };
        _timer.Tick += (_, _) =>
        {
            _rotationAngle = (_rotationAngle + _spinSpeed * 2.0) % 360;
            InvalidateVisual();  // Qayta chizish
        };
        _timer.Start();
    }

    // ───────────────────────────────────────────────────────────────
    // Asosiy chizish metodi
    // ───────────────────────────────────────────────────────────────

    public override void Render(DrawingContext ctx)
    {
        double w = Bounds.Width;
        double h = Bounds.Height;
        double cx = w / 2;
        double cy = h / 2;
        double radius = Math.Min(cx, cy) * 0.88;

        if (_mode == "MANGEKYOU")
            DrawMangekyou(ctx, cx, cy, radius);
        else
            DrawThreeTomoe(ctx, cx, cy, radius);
    }

    // ───────────────────────────────────────────────────────────────
    // 3-Tomoe Sharingan
    // ───────────────────────────────────────────────────────────────

    private void DrawThreeTomoe(DrawingContext ctx, double cx, double cy, double r)
    {
        // 1. Tashqi neon glow halqa
        double glowR = r * (1.05 + _audioAmplitude * 0.20);
        byte glowAlpha = (byte)(90 + _audioAmplitude * 130);
        var glowBrush = new RadialGradientBrush
        {
            GradientOrigin = new RelativePoint(0.5, 0.5, RelativeUnit.Relative),
            Center = new RelativePoint(0.5, 0.5, RelativeUnit.Relative),
            RadiusX = new RelativeScalar(0.5, RelativeUnit.Relative),
            RadiusY = new RelativeScalar(0.5, RelativeUnit.Relative),
            GradientStops =
            {
                new GradientStop(Color.FromArgb(glowAlpha, _glowColor.R, _glowColor.G, _glowColor.B), 0),
                new GradientStop(Color.FromArgb(0, _glowColor.R, _glowColor.G, _glowColor.B), 1.0)
            }
        };
        ctx.DrawEllipse(glowBrush, null,
            new Point(cx, cy), glowR, glowR);

        // 2. Qora tashqi doira
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(15, 10, 10)), null,
            new Point(cx, cy), r, r);

        // 3. Qizil asosiy doira
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(210, 18, 18)), null,
            new Point(cx, cy), r * 0.88, r * 0.88);

        // 4. 3 ta Tomoe (aylanib turadi)
        for (int i = 0; i < 3; i++)
        {
            double angle = DegToRad(_rotationAngle + i * 120.0);
            DrawTomoe(ctx, cx, cy, r * 0.56, angle);
        }

        // 5. Markaziy qora doira
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(12, 6, 6)), null,
            new Point(cx, cy), r * 0.30, r * 0.30);

        // 6. Markaziy qizil nuqta (pupil)
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(230, 30, 30)), null,
            new Point(cx, cy), r * 0.10, r * 0.10);

        // 7. Tashqi chegara halqasi
        double borderWidth = r * 0.05;
        var borderPen = new Pen(
            new SolidColorBrush(_glowColor), borderWidth);
        ctx.DrawEllipse(null, borderPen,
            new Point(cx, cy), r * 0.93, r * 0.93);
    }

    private void DrawTomoe(DrawingContext ctx, double cx, double cy,
                           double orbitR, double angleRad)
    {
        // Tomoe markazi
        double tx = cx + Math.Sin(angleRad) * orbitR;
        double ty = cy - Math.Cos(angleRad) * orbitR;
        double r = orbitR * 0.24;

        // Tomoe tanasi — qizil ellips
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(200, 15, 15)), null,
            new Point(tx, ty), r, r * 1.35);

        // Tomoe ichidagi qora nuqta
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(10, 4, 4)), null,
            new Point(tx, ty - r * 0.15), r * 0.40, r * 0.40);
    }

    // ───────────────────────────────────────────────────────────────
    // Mangekyou Sharingan
    // ───────────────────────────────────────────────────────────────

    private void DrawMangekyou(DrawingContext ctx, double cx, double cy, double r)
    {
        // 1. Kuchli qizil glow
        double glowR = r * (1.15 + _audioAmplitude * 0.30);
        byte glowAlpha = (byte)(130 + _audioAmplitude * 110);
        var glowBrush = new RadialGradientBrush
        {
            GradientOrigin = new RelativePoint(0.5, 0.5, RelativeUnit.Relative),
            Center = new RelativePoint(0.5, 0.5, RelativeUnit.Relative),
            RadiusX = new RelativeScalar(0.5, RelativeUnit.Relative),
            RadiusY = new RelativeScalar(0.5, RelativeUnit.Relative),
            GradientStops =
            {
                new GradientStop(Color.FromArgb(glowAlpha, 255, 20, 0), 0),
                new GradientStop(Color.FromArgb(0, 255, 20, 0), 1.0)
            }
        };
        ctx.DrawEllipse(glowBrush, null, new Point(cx, cy), glowR, glowR);

        // 2. Asosiy qizil doira
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(175, 8, 8)), null,
            new Point(cx, cy), r * 0.90, r * 0.90);

        // 3. Mangekyou pattern — 3 ta petal (aylanadi)
        DrawMangekyouPetals(ctx, cx, cy, r);

        // 4. Markaziy qora doira
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(5, 0, 0)), null,
            new Point(cx, cy), r * 0.26, r * 0.26);

        // 5. Markaziy yorqin nuqta
        ctx.DrawEllipse(
            new SolidColorBrush(Color.FromRgb(255, 60, 0)), null,
            new Point(cx, cy), r * 0.09, r * 0.09);
    }

    private void DrawMangekyouPetals(DrawingContext ctx, double cx, double cy, double r)
    {
        // 3 ta qora petal — aylanma simmetriya
        for (int i = 0; i < 3; i++)
        {
            double baseAngle = _rotationAngle * 0.7 + i * 120.0;
            DrawPetal(ctx, cx, cy, r, baseAngle);
        }
    }

    private void DrawPetal(DrawingContext ctx, double cx, double cy,
                           double r, double angleDeg)
    {
        // PathGeometry bilan petal chizish
        double a1 = DegToRad(angleDeg - 30);
        double a2 = DegToRad(angleDeg + 30);
        double pr = r * 0.72;

        var geom = new PathGeometry();
        var fig = new PathFigure { StartPoint = new Point(cx, cy), IsClosed = true };

        // Markazdan chap burchakka
        double x1 = cx + Math.Sin(a1) * pr * 0.4;
        double y1 = cy - Math.Cos(a1) * pr * 0.4;

        // Petal uchi
        double petalAngle = DegToRad(angleDeg);
        double xTip = cx + Math.Sin(petalAngle) * pr;
        double yTip = cy - Math.Cos(petalAngle) * pr;

        // Markazdan o'ng burchakka
        double x2 = cx + Math.Sin(a2) * pr * 0.4;
        double y2 = cy - Math.Cos(a2) * pr * 0.4;

        fig.Segments = new PathSegments
        {
            new LineSegment { Point = new Point(x1, y1) },
            new QuadraticBezierSegment
            {
                Point1 = new Point(xTip, yTip),
                Point2 = new Point(xTip, yTip)
            },
            new LineSegment { Point = new Point(x2, y2) },
        };

        geom.Figures = new PathFigures { fig };

        ctx.DrawGeometry(
            new SolidColorBrush(Color.FromRgb(8, 3, 3)),
            null,
            geom);
    }

    // ───────────────────────────────────────────────────────────────
    // Tashqi nazorat metodlari
    // ───────────────────────────────────────────────────────────────

    public void SetMode(string mode, double spinSpeed, string glowHex)
    {
        _mode = mode;
        _spinSpeed = spinSpeed;
        _glowColor = ParseColor(glowHex);
    }

    public void SetAmplitude(double value)
    {
        _audioAmplitude = Math.Clamp(value, 0.0, 1.0);
    }

    private static Color ParseColor(string hex)
    {
        hex = hex.TrimStart('#');
        try
        {
            return hex.Length switch
            {
                8 => Color.FromArgb(
                    Convert.ToByte(hex[0..2], 16),
                    Convert.ToByte(hex[2..4], 16),
                    Convert.ToByte(hex[4..6], 16),
                    Convert.ToByte(hex[6..8], 16)),
                6 => Color.FromRgb(
                    Convert.ToByte(hex[0..2], 16),
                    Convert.ToByte(hex[2..4], 16),
                    Convert.ToByte(hex[4..6], 16)),
                _ => Color.FromArgb(170, 255, 0, 0)
            };
        }
        catch { return Color.FromArgb(170, 255, 0, 0); }
    }

    private static double DegToRad(double deg) => deg * Math.PI / 180.0;
}

// ═══════════════════════════════════════════════════════════════════
// SharinganControl (UserControl wrapper) — AXAML bilan birgalikda
// ═══════════════════════════════════════════════════════════════════

public partial class SharinganControl : UserControl
{
    private SharinganCanvas? _canvas;

    public SharinganControl()
    {
        Avalonia.Markup.Xaml.AvaloniaXamlLoader.Load(this);

        // Canvas ni code-behind da Grid ga qo'shish
        _canvas = new SharinganCanvas { Width = 160, Height = 160 };
        var grid = this.Find<Avalonia.Controls.Grid>("RootGrid");
        grid?.Children.Add(_canvas);
    }

    public void SetMode(string mode, double spinSpeed, string glow)
        => _canvas?.SetMode(mode, spinSpeed, glow);

    public void SetAmplitude(double value)
        => _canvas?.SetAmplitude(value);
}
