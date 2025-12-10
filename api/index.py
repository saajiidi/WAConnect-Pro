import os
import sys

# Add the parent directory to sys.path to allow imports from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# This is the key part for Vercel
# It creates a WSGI handler that Vercel can use
handler = app.wsgi_app
