from tkinter import Tk, Toplevel


def center_window(window: Tk) -> None:
    """
    Centers the given window in the center of the screen
    Args:
        window: The window to center
    """
    window.update_idletasks()
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
    x = width / 2 - size[0] / 2
    y = height / 2 - size[1] / 2
    window.geometry("%dx%d+%d+%d" % (size + (x, y)))


def center_popup(popup: Toplevel, parent: Tk) -> None:
    """
    Centers The popup in the center of the parent window
    Args:
        popup: The popup to center
        parent: The parent of the popup
    """
    popup.update()
    x, y, root_width, root_height = get_window_info(parent)
    _, _, width, height = get_window_info(popup)
    width_diff = (root_width - width) / 2
    height_diff = (root_height - height) / 2
    geom = "%dx%d+%d+%d" % (width, height, x+width_diff, y+height_diff)
    popup.geometry(geom)


def get_window_info(window) -> tuple:
    """
    Gives the info about the given window : x_position, y_position, width, height
    Args:
        window: The window from which the info will be retrieved

    Returns: A tuple containing (x_position, y_position, width, height)
    """
    geom = window.geometry()
    temp = geom.split("x")
    width = int(temp[0])
    temp2 = temp[1].split("+")
    height = int(temp2[0])
    x = int(temp2[1])
    y = int(temp2[2])
    return x, y, width, height
