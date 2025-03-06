from nicegui import ui, app

from matplotlib import pyplot as plt
import numpy as np

from . import auth
from .theme import frame

competitor_data = {}

@auth.admin_page('/dashboard')
def dashboard():
    with frame('Dashboard'):
        with ui.pyplot(figsize=(10,10), close=False):
            pass
