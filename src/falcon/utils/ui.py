from tqdm import tqdm
import time

def show_progress_bar_type1(text, speed):
    """
    Shows a progress bar with style 1.
    """
    for i in tqdm(range(100),
                  desc=f"{text}",
                  unit="w",
                  unit_scale=True,
                  ncols=100,
                  colour='white',
                  bar_format="{l_bar}{bar}|"
                  ):
        time.sleep(speed)

def show_progress_bar_type2(text, speed):
    """
    Shows a progress bar with style 2.
    """
    for i in tqdm(range(100),
                  desc=f"{text}",
                  unit="w",
                  unit_scale=True,
                  ncols=100,
                  colour='white',
                  bar_format="{l_bar}{bar}|"
                  ):
        time.sleep(speed)
