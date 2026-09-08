
import sys
import tomllib
from pathlib import Path


    
    
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QWidget,
    QHBoxLayout,
    QLabel,
)


# ============================================================
# Configuration
# ============================================================

APP_DIR = Path(__file__).parent
DISHES_DIR = APP_DIR / "plat"


# ============================================================
# used for text normalization
import unicodedata
def normalize(text):
    text = text.lower()

    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    

# ============================================================
# Gestion des plats
# ============================================================

def load_dishes():
    #Charge tous les fichiers TOML du dossier des plats

    plats = []

    for file in DISHES_DIR.glob("*.toml"):
        try:
            with open(file, "rb") as f:
                data = tomllib.load(f)

            # On garde également le chemin du fichier
            data["_file"] = file

            plats.append(data)

        except Exception as e:
            print(f"Impossible de charger {file}: {e}")

    return plats


#verifie la recherche

def search_dishes(dishes, search):
    search = normalize(search)

    # retourne tous les plats si la recherche est vide
    if not search:
        return dishes
    
    
    results = []

    for dish in dishes:

        if search in normalize(dish["name"]):
            results.append(dish)
            continue
        
        if "\\tags:" in search:
            sub_search = search.replace("\\tags:","")
            if any(sub_search in normalize(ingredient)
                for ingredient in dish["tags"]):
                results.append(dish)
                continue
            
        if "\\ingredients:" in search:
            sub_search = search.replace("\\ingredients:","")
            if any(sub_search in normalize(tag)
                for tag in dish["ingredients"]):
                results.append(dish)
                continue

    return results


# ============================================================
# main window
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mes plats")
        self.resize(1000, 700)

        # Chargement des plats
        self.dishes = load_dishes()

        # ----------------------------------------------------
        # Interface
        # ----------------------------------------------------

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Liste des plats
        self.dish_list = QListWidget()

        # Informations du plat sélectionné
        self.dish_name = QLabel("Sélectionnez un plat")
        self.dish_name.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        # Ajout des widgets
        layout.addWidget(self.dish_list, 1)
        layout.addWidget(self.dish_name, 3)

        # Remplissage de la liste
        self.update_dish_list()

        # Quand on sélectionne un plat
        self.dish_list.currentRowChanged.connect(
            self.show_dish
        )

    # --------------------------------------------------------
    # Liste des plats
    # --------------------------------------------------------
    #la liste des plats sur la gauche
    def update_dish_list(self):
        self.dish_list.clear()

        #a remplacer avec la vraie recherche
        search = "\\tags:sain"
        
        result = search_dishes(self.dishes,search)
        
        for dish in result:
            self.dish_list.addItem(dish["name"])

    # --------------------------------------------------------
    # Affichage d'un plat
    # --------------------------------------------------------

    #le plat à droite ou il y aura la description
    def show_dish(self, index):
        if index < 0 or index >= len(self.dishes):
            self.dish_name.setText("Aucun plat avec cette recherche")
            return

        dish = self.dishes[index]

        self.dish_name.setText(dish["name"])




# ============================================================
# Programme principal
# ============================================================

def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()