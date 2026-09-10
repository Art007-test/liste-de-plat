
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
    QLineEdit,
    QComboBox,
    QListWidgetItem,
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

lst_searchable_topics_user = ["Nom","Temps de cuisson","Ingredients","Note","Tags"]
lst_searchable_topics = ["name","cooking_time","necessary_ingredients","mark","tags"]

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
        
        self.searched_dishes = self.dishes



        #################################################################################################
        # Interface
        #################################################################################################

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        content_layout = QHBoxLayout()
        bar_layout = QHBoxLayout()

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
        
        #la barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Recherchez un plat: ")
        self.search_bar.textChanged.connect(self.search)
        
        # topic menu
        self.topic_menu = QComboBox()
        self.topic_menu.addItems(lst_searchable_topics_user)
        
        self.topic_menu.currentTextChanged.connect(lambda: self.search(self.search_bar.text()))
        
        bar_layout.addWidget(self.search_bar, 6)
        bar_layout.addWidget(self.topic_menu, 1)
        
        main_layout.addLayout(bar_layout)
        
        
        #la liste a gauche
        content_layout.addWidget(self.dish_list, 1)
        
        #la boite à droite
        right_layout = QVBoxLayout()
        
        right_layout.addStretch(1)
        
        right_layout.addWidget(self.dish_name,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        
        right_layout.addSpacing(20)
        right_layout.addWidget(create_separator())
        
        right_layout.addWidget(self.dish_description)
        
        right_layout.addStretch(10)
        
        #rajout du block de droite au bloc de contenu
        content_layout.addLayout(right_layout,3)
        
        main_layout.addLayout(content_layout)

        # Remplissage de la liste
        self.search("")

        # Quand on sélectionne un plat
        self.dish_list.currentItemChanged.connect(
            self.show_dish
        )
    #################################################################################################
    #la liste des plats sur la gauche
    def search(self,text):
        
        topic = lst_searchable_topics[self.topic_menu.currentIndex()]
        result = search_dishes(self.dishes,text,topic)
        
        self.dish_list.clear()
        
        for dish in result:
            item = QListWidgetItem(dish["name"])
            item.setData(Qt.ItemDataRole.UserRole, dish)
            self.dish_list.addItem(item)
            
            

    #################################################################################################
    #le plat à droite ou il y aura la description
    def show_dish(self, current_item, previous_item):
        if current_item is None:
            self.dish_name.setText("Aucun plat avec cette recherche")
            self.dish_description.setText("")
            return
        dish = current_item.data(Qt.ItemDataRole.UserRole)
        
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