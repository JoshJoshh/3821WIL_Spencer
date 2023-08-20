white = "#FFFFFF"
gray = "#EDF2F4"
light_red = "#C02424"
red = "#980f0f"
dark_red = "#6e0703"
dark_gray = "#474747"
black = "#000000"


from customtkinter import *

class SquareButton(CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=red, hover_color=light_red, corner_radius=0)

class RoundButton(CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=red, hover_color=light_red, corner_radius=25)

class SquareCheckbox(CTkCheckBox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=red, hover_color=light_red, corner_radius=0)
