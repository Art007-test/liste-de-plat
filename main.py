
import sys
import tomllib
from pathlib import Path


    
    
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt


#################################################################################################
# Configuration
#################################################################################################

APP_DIR = Path(__file__).parent
DISHES_DIR = APP_DIR / "plat"


#################################################################################################
# used for text normalization
import unicodedata
def normalize(text):
    text = text.lower()

    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    

#################################################################################################
# Gestion des plats
#################################################################################################

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



#################################################################################################
#verifie la recherche

def search_dishes(dishes, search,topic):
    search = normalize(search)

    # retourne tous les plats si la recherche est vide
    if not search:
        return dishes
    
    results = []
    if topic in ["name"]:
        results = search_from_str(search,dishes,topic)
    elif topic in ["cooking_time","mark"]:
        results = search_from_int(search,dishes,topic)
    else:
        results = search_from_list(search,dishes,topic)

    return results


def search_from_str(search,dishes,topic):
    results = []
    for dish in dishes:
        if search in normalize(dish[topic]):
            results.append(dish)
            continue
    return results


def search_from_int(search,dishes,topic):
    results = []
    error = False
    mode = ""
    
    if search[0] == "<":
        search,error,mode = int_search_mode(search,"<")
    elif search[0] == "=":
        search,error,mode = int_search_mode(search,"=")
    elif search[0] == ">":
        search,error,mode = int_search_mode(search,">")
    else:
        return dishes
    if error:
        return dishes
    
    for dish in dishes:
        if mode == "<":
            if search < dish[topic]:
                results.append(dish)
                continue
        if mode == "=":
            if dish[topic] == search:
                results.append(dish)
                continue
        if mode == ">":
            if search > dish[topic]:
                results.append(dish)
                continue
    return results

def int_search_mode(search,mode):
    search = search.replace(mode,"")
    error = False
    try:
        search = int(search)
    except:
        print("Pas que des chiffres dans la recherche.")
        error = True
    return search,error,mode


def search_from_list(search,dishes,topic):
    results = []
    for dish in dishes:
        if any(search in normalize(i)
            for i in dish[topic]):
                results.append(dish)
                continue
    return results



#################################################################################################
# une ligne qui permet de faire un separateur
def create_separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Plain)
    separator.setFixedHeight(1)
    return separator

def cooking_time_to__text(minute):
    #si le temp est en dessous d'une heure
    if minute < 60:
        return str(minute) + "min"
    hour = minute // 60
    minute = minute % 60
    return str(hour) + "h " + str(minute) + "min"    
    
    
    
    
    
        
        

#################################################################################################
# main window
#################################################################################################

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mes plats")
        self.resize(1000, 700)

        # Chargement des plats
        self.dishes = load_dishes()



        #################################################################################################
        # Interface
        #################################################################################################

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
        
        self.dish_description = QLabel("")
        self.dish_description.setWordWrap(True)
        self.dish_description.setStyleSheet("font-size: 16px;")
        
        ####################################################################################################
        # Ajout des widgets
        
        #la liste a gauche
        layout.addWidget(self.dish_list, 1)
        
        #la boite à droite
        right_layout = QVBoxLayout()
        
        right_layout.addStretch(1)
        
        right_layout.addWidget(self.dish_name,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addSpacing(20)
        right_layout.addWidget(create_separator())
        
        right_layout.addWidget(self.dish_description)
        
        right_layout.addStretch(10)
        
        layout.addLayout(right_layout,3)
        
        

        # Remplissage de la liste
        self.update_dish_list()

        # Quand on sélectionne un plat
        self.dish_list.currentRowChanged.connect(
            self.show_dish
        )

    
    #################################################################################################
    #la liste des plats sur la gauche
    def update_dish_list(self):
        self.dish_list.clear()

        #a remplacer avec la vraie recherche
        topic = "name"
        search = ""
        
        result = search_dishes(self.dishes,search,topic)
        
        for dish in result:
            self.dish_list.addItem(dish["name"])

    
    #################################################################################################
    #le plat à droite ou il y aura la description
    def show_dish(self, index):
        if index < 0 or index >= len(self.dishes):
            self.dish_name.setText("Aucun plat avec cette recherche")
            self.dish_description.setText("")
            return

        dish = self.dishes[index]
        self.dish_name.setText(dish["name"] + "       " + cooking_time_to__text(dish["cooking_time"]))
        self.dish_description.setText("Description: \n" + dish.get("description","")) #met du vide si la description n'existe pas





#################################################################################################
#lancer le truc
def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()