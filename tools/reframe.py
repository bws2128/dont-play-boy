import pathlib
from PIL import Image, ImageDraw, ImageFilter

proj = pathlib.Path.home() / "Developer" / "dont-play-boy"
src = Image.open(proj / "images" / "headshot-original.jpg").convert("RGB")

# --- canvas: wide cinematic 16:9 so cover-fill on a widescreen barely zooms ---
CW, CH = 2560, 1440
INK = (10, 7, 8)

canvas = Image.new("RGB", (CW, CH), INK)

# subtle red glow behind the subject (brand warmth), centered a touch above middle
glow = Image.new("L", (CW, CH), 0)
gd = ImageDraw.Draw(glow)
gx, gy = CW // 2, int(CH * 0.42)
for i, (rad, val) in enumerate([(1150, 70), (820, 90), (520, 95)]):
    gd.ellipse([gx - rad, gy - int(rad * 0.82), gx + rad, gy + int(rad * 0.82)], fill=val)
glow = glow.filter(ImageFilter.GaussianBlur(220))
red = Image.new("RGB", (CW, CH), (120, 18, 26))  # deep brand red
canvas = Image.composite(red, canvas, glow)

# --- place the figure: smaller + set back, with headroom ---
FIG_H = 1010                       # figure height on the 1440 canvas (~70%) => "further back"
scale = FIG_H / src.height
fig_w = int(src.width * scale)
fig = src.resize((fig_w, FIG_H), Image.LANCZOS)

fx = (CW - fig_w) // 2             # centered horizontally
fy = 150                           # top: headroom above his head

# feather mask so the photo edges dissolve into the dark (no hard rectangle seam)
mask = Image.new("L", (fig_w, FIG_H), 0)
md = ImageDraw.Draw(mask)
inset = 2
md.rounded_rectangle([inset, inset, fig_w - inset, FIG_H - inset], radius=90, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(70))   # soft vignette edge

canvas.paste(fig, (fx, fy), mask)

# gentle global vignette to seat him in the frame
vig = Image.new("L", (CW, CH), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-CW * 0.15, -CH * 0.15, CW * 1.15, CH * 1.15], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(260))
dark = Image.new("RGB", (CW, CH), INK)
canvas = Image.composite(canvas, dark, vig)

out = proj / "images" / "headshot.jpg"
canvas.save(out, "JPEG", quality=86, optimize=True, progressive=True)
print("saved", out, canvas.size, out.stat().st_size, "bytes")
print("figure box: x", fx, "->", fx + fig_w, " y", fy, "->", fy + FIG_H,
      " center%", round((fx + fig_w / 2) / CW * 100, 1), round((fy + FIG_H / 2) / CH * 100, 1))
