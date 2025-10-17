import concurrent.futures
import sys
from pathlib import Path
import random

# Extensions to recognize
MEDIA_EXTS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v'}
SUBTITLE_EXTS = {'.srt', '.sub', '.ass', '.vtt'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tbn'}
NFO_EXT = '.nfo'

BAR_WIDTH = 20

# Color schemes dictionary with 'header' added
# Color schemes dictionary with 'header' added and new schemes
COLOR_SCHEMES = {
    'default': {
        'good': '\033[32m',    # Green
        'fair': '\033[33m',    # Yellow
        'poor': '\033[31m',    # Red
        'reset': '\033[0m',
        'header': '\033[1;37m',  # White (Bold)
    },
    'monochrome': {
        'good': '\033[37m',    # White
        'fair': '\033[90m',    # Bright Black (Gray)
        'poor': '\033[30m',    # Black
        'reset': '\033[0m',
        'header': '\033[1;30m',  # Gray (Bold)
    },
    'blueish': {
        'good': '\033[34m',    # Blue
        'fair': '\033[36m',    # Cyan
        'poor': '\033[35m',    # Magenta
        'reset': '\033[0m',
        'header': '\033[1;34m',  # Bright Blue (Bold)
    },
    'highcontrast': {
        'good': '\033[92m',    # Bright Green
        'fair': '\033[93m',    # Bright Yellow
        'poor': '\033[91m',    # Bright Red
        'reset': '\033[0m',
        'header': '\033[1;37m',  # White (Bold)
    },
    'pastel': {
        'good': '\033[38;5;82m',    # Pastel Green
        'fair': '\033[38;5;220m',   # Pastel Yellow
        'poor': '\033[38;5;196m',   # Pastel Red
        'reset': '\033[0m',
        'header': '\033[38;5;81m',  # Pastel Blue (Bold)
    },
    'vintage': {
        'good': '\033[38;5;154m',    # Vintage Green
        'fair': '\033[38;5;226m',    # Vintage Yellow
        'poor': '\033[38;5;124m',    # Vintage Red
        'reset': '\033[0m',
        'header': '\033[38;5;102m',  # Vintage Cyan (Bold)
    },
    'retro': {
        'good': '\033[38;5;47m',     # Retro Green
        'fair': '\033[38;5;214m',    # Retro Yellow
        'poor': '\033[38;5;196m',    # Retro Red
        'reset': '\033[0m',
        'header': '\033[38;5;51m',   # Retro Blue (Bold)
    },
    'fire': {
        'good': '\033[38;5;202m',    # Fire Orange
        'fair': '\033[38;5;214m',    # Fire Yellow
        'poor': '\033[38;5;124m',    # Fire Red
        'reset': '\033[0m',
        'header': '\033[38;5;202m',  # Fire Red (Bold)
    },
    'neon': {
        'good': '\033[38;5;81m',     # Neon Green
        'fair': '\033[38;5;13m',     # Neon Pink
        'poor': '\033[38;5;9m',      # Neon Red
        'reset': '\033[0m',
        'header': '\033[38;5;51m',   # Neon Cyan (Bold)
    },
    'tropical': {
        'good': '\033[38;5;34m',     # Tropical Green
        'fair': '\033[38;5;226m',    # Tropical Yellow
        'poor': '\033[38;5;196m',    # Tropical Red
        'reset': '\033[0m',
        'header': '\033[38;5;51m',   # Tropical Blue (Bold)
    },
    'earthy': {
        'good': '\033[38;5;59m',     # Earthy Green
        'fair': '\033[38;5;130m',    # Earthy Yellow
        'poor': '\033[38;5;88m',     # Earthy Red
        'reset': '\033[0m',
        'header': '\033[38;5;28m',   # Earthy Brown (Bold)
    },
    'sunset': {
        'good': '\033[38;5;214m',    # Sunset Orange
        'fair': '\033[38;5;220m',    # Sunset Yellow
        'poor': '\033[38;5;124m',    # Sunset Red
        'reset': '\033[0m',
        'header': '\033[38;5;208m',  # Sunset Purple (Bold)
    },
    'aqua': {
        'good': '\033[38;5;48m',     # Aqua Green
        'fair': '\033[38;5;33m',     # Aqua Blue
        'poor': '\033[38;5;129m',    # Aqua Red
        'reset': '\033[0m',
        'header': '\033[38;5;39m',   # Aqua Cyan (Bold)
    },
    'forest': {
        'good': '\033[38;5;22m',     # Forest Green
        'fair': '\033[38;5;148m',    # Forest Yellow
        'poor': '\033[38;5;130m',    # Forest Red
        'reset': '\033[0m',
        'header': '\033[38;5;28m',   # Forest Brown (Bold)
    },
    'ocean': {
        'good': '\033[38;5;32m',     # Ocean Green
        'fair': '\033[38;5;67m',     # Ocean Blue
        'poor': '\033[38;5;196m',    # Ocean Red
        'reset': '\033[0m',
        'header': '\033[38;5;33m',   # Ocean Cyan (Bold)
    },
    'rose': {
        'good': '\033[38;5;210m',    # Rose Pink
        'fair': '\033[38;5;13m',     # Rose Red
        'poor': '\033[38;5;88m',     # Rose Dark Red
        'reset': '\033[0m',
        'header': '\033[38;5;201m',  # Rose Violet (Bold)
    },
    'emerald': {
        'good': '\033[38;5;46m',     # Emerald Green
        'fair': '\033[38;5;40m',     # Emerald Light Green
        'poor': '\033[38;5;9m',      # Emerald Red
        'reset': '\033[0m',
        'header': '\033[38;5;40m',   # Emerald Green (Bold)
    },
}

def clean_and_validate_path(path_str: str):
    """
    Clean up and validate a user-provided path string.

    Removes enclosing quotes and whitespace, normalizes path,
    checks if path exists and is a directory.

    Returns:
        Path object if valid,
        None if invalid (and prints error message).
    """
    if not isinstance(path_str, str):
        print(f"Error: Path must be a string, got {type(path_str)}")
        return None

    cleaned = path_str.strip().strip('\'"')

    try:
        p = Path(cleaned).expanduser().resolve()
    except Exception as e:
        print(f"Error: Cannot resolve path '{cleaned}': {e}")
        return None

    if not p.exists():
        print(f"Error: Path does not exist: '{p}'")
        return None

    if not p.is_dir():
        print(f"Error: Path is not a directory: '{p}'")
        return None

    return p

def color_for_percentage(pct: float, colors: dict) -> str:
    if pct >= 90:
        return colors['good']
    elif pct >= 70:
        return colors['fair']
    else:
        return colors['poor']

def bar_graph(pct: float, colors: dict) -> str:
    filled_len = int(pct / 100 * BAR_WIDTH)
    bar = '#' * filled_len + '-' * (BAR_WIDTH - filled_len)
    color = color_for_percentage(pct, colors)
    return f'{color}[{bar}]{colors["reset"]}'

def scan_library(path: Path, colors: dict):
    media_files = [f for f in path.rglob('*') if f.suffix.lower() in MEDIA_EXTS]

    total = len(media_files)
    if total == 0:
        return {
            'path': str(path),
            'total': 0,
            'nfo': 0,
            'subs': 0,
            'images': 0,
        }

    nfo_count = 0
    subs_count = 0
    images_count = 0

    common_images = {
        'folder.jpg', 'folder.png', 'poster.jpg', 'poster.png', 'cover.jpg', 'cover.png',
        'fanart.jpg', 'fanart.png', 'banner.jpg', 'banner.png', 'thumb.jpg', 'thumb.png'
    }

    for media in media_files:
        base = media.with_suffix('')

        # .nfo check
        if base.with_suffix(NFO_EXT).exists():
            nfo_count += 1

        folder = media.parent
        folder_files = {f.name.lower() for f in folder.iterdir() if f.is_file()}

        # Subtitle check - any subtitle file in the same folder
        if any(f.suffix.lower() in SUBTITLE_EXTS for f in folder.iterdir() if f.is_file()):
            subs_count += 1

        # Image check - common image filenames in folder (case-insensitive)
        if any(img_name in folder_files for img_name in common_images):
            images_count += 1

    pct_nfo = (nfo_count / total) * 100
    pct_subs = (subs_count / total) * 100
    pct_images = (images_count / total) * 100

    avg = (pct_nfo + pct_subs + pct_images) / 3
    if avg >= 85:
        status = (colors['good'], 'GOOD', 'Most items are complete')
    elif avg >= 70:
        status = (colors['fair'], 'FAIR', 'Some missing metadata')
    else:
        status = (colors['poor'], 'POOR', 'Many items incomplete')

    return {
        'path': str(path),
        'total': total,
        'nfo': (nfo_count, pct_nfo),
        'subs': (subs_count, pct_subs),
        'images': (images_count, pct_images),
        'status': status,
    }

def print_report(report, colors: dict):
    path = report['path']
    total = report['total']

    header = f'Library: {path} ({total} items)'
    print(header)
    print('-' * len(header))
    if total == 0:
        print('  No media files found.\n')
        return

    nfo_count, pct_nfo = report['nfo']
    subs_count, pct_subs = report['subs']
    images_count, pct_images = report['images']

    print(f'NFO Files       {bar_graph(pct_nfo, colors)} {nfo_count} / {total} ({pct_nfo:.1f}%)')
    print(f'Subtitle Files  {bar_graph(pct_subs, colors)} {subs_count} / {total} ({pct_subs:.1f}%)')
    print(f'Image Files     {bar_graph(pct_images, colors)} {images_count} / {total} ({pct_images:.1f}%)')

    color, status_label, status_msg = report['status']
    print(f'Status: {color}{status_label}{colors["reset"]} - {status_msg}\n')

def print_header(colors: dict) -> None:
    media_report_ascii = r"""
     __  __          _ _         ____                       _   
    |  \/  | ___  __| (_) __ _  |  _ \ ___ _ __   ___  _ __| |_ 
    | |\/| |/ _ \/ _` | |/ _` | | |_) / _ \ '_ \ / _ \| '__| __|
    | |  | |  __/ (_| | | (_| | |  _ <  __/ |_) | (_) | |  | |_ 
    |_|  |_|\___|\__,_|_|\__,_| |_| \_\___| .__/ \___/|_|   \__|
                                          |_|                    
    """
    header_text = "=== Media Report ==="
    print(colors['header'] + media_report_ascii + colors['reset'])
    print()

def main(paths, color_scheme_name: str = 'default'):
    if color_scheme_name == 'random':
        color_scheme_name = random.choice(list(COLOR_SCHEMES.keys()))

    colors = COLOR_SCHEMES.get(color_scheme_name, COLOR_SCHEMES['default'])

    # print header
    print_header(colors)

    valid_paths = []
    for p in paths:
        validated = clean_and_validate_path(p)
        if validated:
            valid_paths.append(validated)
        else:
            print(f"Skipping invalid path: {p}")

    if not valid_paths:
        print("No valid paths to scan. Exiting.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(valid_paths))) as executor:
        futures = {executor.submit(scan_library, path, colors): path for path in valid_paths}

        for future in concurrent.futures.as_completed(futures):
            report = future.result()
            print_report(report, colors)

def print_usage():
    print("Usage: python media_report.py [--color-scheme=<scheme>] <library_path1> [<library_path2> ...]")
    print("\nColor schemes available:")
    for scheme in COLOR_SCHEMES:
        print(f"  {scheme}")
    print("Use --color-scheme=random to pick a random scheme.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # Parse --color-scheme parameter if exists
    arg_paths = []
    color_scheme_arg = 'default'
    for arg in sys.argv[1:]:
        if arg.startswith('--color-scheme='):
            color_scheme_arg = arg.split('=', 1)[1].lower()
        else:
            arg_paths.append(arg)

    if not arg_paths:
        print("Error: No library paths provided.")
        print_usage()
        sys.exit(1)

    main(arg_paths, color_scheme_arg)
