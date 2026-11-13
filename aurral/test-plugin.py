import sys
from unittest import TestCase

sys.path.insert(0, "/usr/local/bin/yt-dlp")

from yt_dlp import YoutubeDL
from yt_dlp.extractor.youtube.pot._registry import _pot_providers

check = TestCase()
with YoutubeDL({"quiet": True, "cachedir": False}):
    providers = {provider.PROVIDER_NAME for provider in _pot_providers.value.values()}
    check.assertIn("bgutil:http", providers)

    from yt_dlp_plugins.extractor.getpot_bgutil import __version__

    check.assertEqual(__version__, sys.argv[1])

print(f"yt-dlp loads bgutil HTTP provider {__version__} from its default plugin directories")
