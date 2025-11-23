"""
News scrapers for various blockchain media sources
"""

from .jinse import JinSeScraper
from .odaily import OdailyScraper
from .cointelegraph import CointelegraphScraper
from .coindesk import CoinDeskScraper
from .theblock import TheBlockScraper

__all__ = [
    'JinSeScraper',
    'OdailyScraper',
    'CointelegraphScraper',
    'CoinDeskScraper',
    'TheBlockScraper',
]
