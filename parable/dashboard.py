from nicegui import ui, app

from matplotlib import pyplot as plt
import numpy as np

import parable.auth as auth
from parable.theme import frame

competitor_data = {
    []
}

@auth.page('/dashboard')
def dashboard():
    with frame('Dashboard'):
        with ui.pyplot(figsize=(10,10), close=False):
            pass
