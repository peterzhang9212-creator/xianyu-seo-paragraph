from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_OUTPUT_SUFFIX = "_水印"
FONT_KEYWORDS = (
    "yahei",
    "simhei",
    "simsun",
    "pingfang",
    "heiti",
    "noto",
    "sourcehan",
    "wqy",
    "wenquanyi",
    "cjk",
    "unicode",
)
FONT_SEARCH_ROOTS = (
    Path(r"C:\Windows\Fonts"),
    Path("/System/Library/Fonts"),
    Path("/Library/Fonts"),
    Path("/usr/share/fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local/share/fonts",
)
JPEG_QUALITY_CANDIDATES = (85, 75, 68)
WEBP_QUALITY_CANDIDATES = (80, 70, 65)
SIZE_RATIO_LIMIT = 1.5
ABSOLUTE_SIZE_LIMIT_BYTES = 300 * 1024


@dataclass(frozen=True)
class WatermarkSettings:
    font_size: int
    spacing_scale: float
    opacity: int


@dataclass(frozen=True)
class WatermarkLayout:
    step_x: int
    step_y: int
    row_offset: int
    canvas_width: int
    canvas_height: int


@dataclass(frozen=True)
class ProcessSummary:
    total_count: int
    success_count: int
    skip_count: int
    output_root: Path
    oversized_files: list[Path]


def build_output_root(root: str | Path, output_suffix: str = DEFAULT_OUTPUT_SUFFIX) -> Path:
    root = Path(root)
    return root.parent / f"{root.name}{output_suffix}"


def collect_image_files(root: str | Path) -> list[Path]:
    root = Path(root)
    files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS]
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def suggest_watermark_settings(image_size: tuple[int, int]) -> WatermarkSettings:
    short_side = min(image_size)
    font_size = max(18, min(72, int(short_side * 0.055)))
    spacing_scale = max(0.85, min(1.35, round(short_side / 1600, 2)))
    opacity = 72
    return WatermarkSettings(font_size=font_size, spacing_scale=spacing_scale, opacity=opacity)


@lru_cache(maxsize=1)
def _discover_font_paths() -> list[Path]:
    discovered: list[Path] = []
    for root in FONT_SEARCH_ROOTS:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in {".ttf", ".ttc", ".otf", ".otc"}:
                    name = path.name.lower()
                    if any(keyword in name for keyword in FONT_KEYWORDS):
                        discovered.append(path)
        except OSError:
            continue
    return discovered


@lru_cache(maxsize=16)
def choose_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simkai.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf",
    ]

    for candidate in font_candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue

    for path in _discover_font_paths():
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue

    return ImageFont.load_default()


def _text_bounds(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> tuple[int, int]:
    canvas = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def calculate_watermark_layout(
    image_size: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    spacing_scale: float,
) -> WatermarkLayout:
    width, height = image_size
    text_width, text_height = _text_bounds(text, font)
    base_step_x = max(int(text_width * 1.45), max(120, width // 5))
    base_step_y = max(int(text_height * 2.1), max(90, height // 5))
    step_x = max(1, int(base_step_x * spacing_scale))
    step_y = max(1, int(base_step_y * spacing_scale))
    row_offset = step_x // 2
    canvas_side = max(width, height) * 3
    return WatermarkLayout(
        step_x=step_x,
        step_y=step_y,
        row_offset=row_offset,
        canvas_width=canvas_side,
        canvas_height=canvas_side,
    )


def _build_watermark_layer(
    image_size: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    spacing_scale: float,
    opacity: int,
) -> Image.Image:
    layout = calculate_watermark_layout(image_size, text, font, spacing_scale)
    canvas = Image.new("RGBA", (layout.canvas_width, layout.canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    fill = (210, 210, 210, opacity)

    for row_index, y in enumerate(range(layout.step_y // 2, layout.canvas_height, layout.step_y)):
        x_start = layout.step_x // 2
        if row_index % 2 == 1:
            x_start += layout.row_offset
        for x in range(x_start, layout.canvas_width, layout.step_x):
            draw.text((x, y), text, font=font, fill=fill)

    width, height = image_size
    rotated = canvas.rotate(45, resample=Image.BICUBIC, expand=True)
    left = max((rotated.width - width) // 2, 0)
    top = max((rotated.height - height) // 2, 0)
    return rotated.crop((left, top, left + width, top + height))


@lru_cache(maxsize=32)
def _get_cached_watermark_layer(
    image_size: tuple[int, int],
    watermark_text: str,
    font_size: int,
    spacing_scale: float,
    opacity: int,
) -> Image.Image:
    font = choose_font(font_size)
    return _build_watermark_layer(image_size, watermark_text, font, spacing_scale, opacity)


def apply_watermark_to_image(
    image: Image.Image,
    watermark_text: str,
    font_size: int,
    spacing_scale: float,
    opacity: int,
) -> Image.Image:
    base = image.convert("RGBA")
    watermark = _get_cached_watermark_layer(base.size, watermark_text, font_size, spacing_scale, opacity)
    return Image.alpha_composite(base, watermark)


def _target_output_size(source_size: int) -> int:
    ratio_limit = int(source_size * SIZE_RATIO_LIMIT)
    return min(ratio_limit, ABSOLUTE_SIZE_LIMIT_BYTES)


def _save_best_effort(
    image: Image.Image,
    output_path: Path,
    image_format: str,
    candidate_kwargs: list[dict[str, object]],
    source_size: int,
) -> int:
    target_size = _target_output_size(source_size)
    best_payload = b""

    for save_kwargs in candidate_kwargs:
        buffer = BytesIO()
        image.save(buffer, format=image_format, **save_kwargs)
        payload = buffer.getvalue()

        if not best_payload or len(payload) < len(best_payload):
            best_payload = payload

        if len(payload) <= target_size:
            best_payload = payload
            break

    output_path.write_bytes(best_payload)
    return len(best_payload)


def _save_image(
    image: Image.Image,
    source_format: str | None,
    source_suffix: str,
    output_path: Path,
    source_size: int,
) -> int:
    source_format = (source_format or source_suffix.lstrip(".")).upper()

    if source_format in {"JPG", "JPEG"}:
        image = image.convert("RGB")
        return _save_best_effort(
            image=image,
            output_path=output_path,
            image_format="JPEG",
            candidate_kwargs=[{"quality": quality, "optimize": True, "progressive": True} for quality in JPEG_QUALITY_CANDIDATES],
            source_size=source_size,
        )

    if source_format == "WEBP":
        return _save_best_effort(
            image=image,
            output_path=output_path,
            image_format="WEBP",
            candidate_kwargs=[{"quality": quality, "method": 6} for quality in WEBP_QUALITY_CANDIDATES],
            source_size=source_size,
        )

    if source_format == "PNG":
        image.save(output_path, format="PNG", optimize=True, compress_level=6)
        return output_path.stat().st_size

    image.save(output_path, format=source_format)
    return output_path.stat().st_size


def is_oversized(source_size: int, output_size: int) -> bool:
    return output_size > _target_output_size(source_size)


def process_directory(
    root: str | Path,
    watermark_text: str,
    font_size: int,
    spacing_scale: float,
    opacity: int,
    output_suffix: str = DEFAULT_OUTPUT_SUFFIX,
    logger=print,
) -> ProcessSummary:
    root = Path(root)
    output_root = build_output_root(root, output_suffix=output_suffix)
    output_root.mkdir(parents=True, exist_ok=True)

    image_files = collect_image_files(root)
    success_count = 0
    skip_count = 0
    oversized_files: list[Path] = []

    logger(f"开始处理目录: {root}")
    logger(f"共发现 {len(image_files)} 张图片")

    for index, source_path in enumerate(image_files, start=1):
        logger(f"正在处理 [{index}/{len(image_files)}]: {source_path}")
        try:
            with Image.open(source_path) as source_image:
                source_image.load()
                result_image = apply_watermark_to_image(
                    image=source_image,
                    watermark_text=watermark_text,
                    font_size=font_size,
                    spacing_scale=spacing_scale,
                    opacity=opacity,
                )

                relative_path = source_path.relative_to(root)
                output_path = output_root / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_size = _save_image(
                    image=result_image,
                    source_format=source_image.format,
                    source_suffix=source_path.suffix,
                    output_path=output_path,
                    source_size=source_path.stat().st_size,
                )

            success_count += 1
            if is_oversized(source_path.stat().st_size, output_size):
                oversized_files.append(output_path)
                logger(f"已输出但超限: {output_path} ({output_size} bytes)")
            else:
                logger(f"处理完成: {output_path}")
        except Exception as exc:
            skip_count += 1
            logger(f"跳过文件: {source_path}，原因: {exc}")

    logger(
        f"全部处理完成，成功 {success_count} 张，跳过 {skip_count} 张，超限 {len(oversized_files)} 张，输出目录: {output_root}"
    )
    return ProcessSummary(
        total_count=len(image_files),
        success_count=success_count,
        skip_count=skip_count,
        output_root=output_root,
        oversized_files=oversized_files,
    )
