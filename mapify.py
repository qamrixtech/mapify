#!/usr/bin/env python3
"""
Mapify - Ethical SEO Sitemap Generator
Respects robots.txt while creating comprehensive sitemaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()