from tools import *
from bdd import *

# Initialiser ncurses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.endwin()

# Initialiser les couleurs
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

# Initialiser les variables de la fenêtre
height, width = stdscr.getmaxyx()
height = height - 1
width = width - 1

# Initialiser les fenêtres
menu = curses.newwin(10, width, 0, 0)

def choix_combo_list():
    root = tk.Tk()
    root.withdraw()
    # file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    file_path = "D:/OneDrive/développement/GITHUB/fidelite/combo-list/test.txt"

    if not file_path:
        exit()

    with open(file_path, "r") as f:
        combo_list = f.read().splitlines()

    # enlever les lignes vides
    combo_list = [x for x in combo_list if x]

    # enlever les doublons
    combo_list = list(dict.fromkeys(combo_list))

    # enlever les lignes qui ne sont pas des combos
    combo_list = [x for x in combo_list if ":" in x]

    #enlever les espaces
    combo_list = [x.replace(" ", "") for x in combo_list]

    # créer une liste de dictionnaire avec les combos 
    combo_list = [{"email": x.split(":")[0], "password": x.split(":")[1]} for x in combo_list]
    return combo_list

def choix_compte():
    menu.addstr(0, 0, "Choix du compte", curses.color_pair(4))
    menu.addstr(1, 0, "1 - Utiliser un fichier de combo", curses.color_pair(4))
    menu.addstr(2, 0, "2 - Vérifier les comptes qui n'ont pas pu être vérifié", curses.color_pair(4))
    menu.addstr(3, 0, "3 - Vérifier les comptes fonctionnels", curses.color_pair(4))
    menu.refresh()
    while True:
        key = menu.getkey()
        if key == "1":
            curses.endwin()
            return choix_combo_list(), False
        elif key == "2":
            curses.endwin()
            return get_compte_non_verifie(), True
        elif key == "3":
            curses.endwin()
            return get_compte_valide(), True