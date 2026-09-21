#les imports: 
import sys
import tomllib
from pathlib import Path
import tomli_w
import re
import unicodedata
from datetime import date

    
    
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
    QPushButton,
    QDialog,
)
from PySide6.QtCore import Qt

import emoji
from PySide6.QtGui import QIcon

from new_dish_dialog import NewDishDialog


#################################################################################################
# chemin de fichier

APP_DIR = Path(__file__).parent
DISHES_DIR = APP_DIR / "plat"


def make_filename(name):
    # Retire les accents
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Minuscules + remplacement des caractères bizarre
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")

    if not name:
        name = "nouveau_plat"

    return name


def emoji_to_icon(emoji_text, size=64):
    label = QLabel()
    label.setText(emoji_text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    label.setStyleSheet("QLabel {background: transparent;}")

    font = label.font()
    font.setPointSize(size)
    label.setFont(font)

    # Le label est rendu en image
    pixmap = label.grab()

    return QIcon(pixmap)


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
def create_separator(thickness):
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Plain)
    separator.setFixedHeight(thickness)
    return separator

#prend le temp en minute et rend le joooli
def cooking_time_to_text(minute):
    
    #si l'utilisateur n'a pa rentrer un chiffre
    try:
        minute = int(minute)
    except:
        return minute
    
    #si le temp est en dessous d'une heure
    if minute < 60:
        return str(minute) + "min"
    hour = minute // 60
    minute = minute % 60
    return str(hour) + "h " + str(minute) + "min"    
    
#rend les listes jooooli
def pretty_list(lst):
    result = ""
    for i in range(len(lst)):
        result = result + "- " + str(lst[i])
        if i != len(lst):
            result = result + "\n"
    return result
    
    
        
        

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
        
        self.setWindowIcon(emoji_to_icon(emoji.emojize(":pancakes:")))



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



        # Le titre
        dish_title_layout = QHBoxLayout()
        dish_title_layout.setContentsMargins(0,0,0,0)
        
        self.dish_name = QLabel("Sélectionnez un plat")
        self.dish_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.dish_mark = QLabel("")
        self.dish_mark.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.dish_time = QLabel("")
        self.dish_time.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        
        dish_title_layout.addWidget(self.dish_mark,alignment=Qt.AlignmentFlag.AlignLeft)
        
        dish_title_layout.addWidget(self.dish_name,alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        
        dish_title_layout.addWidget(self.dish_time,alignment=Qt.AlignmentFlag.AlignRight)
        
        
        
        
        #la description du plat
        self.dish_description_container = QWidget()
        self.description_layout = QVBoxLayout(self.dish_description_container)
        self.description_layout.setContentsMargins(0,0,0,0)
        
        self.dish_description = QLabel("")
        self.dish_description.setWordWrap(True)
        self.dish_description.setStyleSheet("font-size: 16px;")
        
        
        self.description_layout.addWidget(self.dish_description)
        self.description_layout.addWidget(create_separator(1))
        
        
        
        
        
        #les ingrédients
        self.dish_necessary_ingredients = QLabel("")
        self.dish_necessary_ingredients.setWordWrap(True)
        self.dish_necessary_ingredients.setStyleSheet("font-size: 16px;")
        
        self.dish_unnecessary_ingredients = QLabel("")
        self.dish_unnecessary_ingredients.setWordWrap(True)
        self.dish_unnecessary_ingredients.setStyleSheet("font-size: 16px;")
        
        
        
        #la recette
        self.dish_recipe = QLabel("")
        self.dish_recipe.setWordWrap(True)
        self.dish_recipe.setStyleSheet("font-size: 16px;")
        self.dish_recipe_separator = create_separator(1)
        
        
        
        ####################################################################################################
        # Ajout des widgets
        
        #la barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(emoji.emojize(":magnifying_glass_tilted_left: Recherchez un plat: "))
        self.search_bar.textChanged.connect(self.search)
        
        # topic menu
        self.topic_menu = QComboBox()
        self.topic_menu.addItems(lst_searchable_topics_user)
        
        self.topic_menu.currentTextChanged.connect(lambda: self.search(self.search_bar.text()))
        
        bar_layout.addWidget(self.search_bar, 6)
        bar_layout.addWidget(self.topic_menu, 1)
        
        
        
        
        
        
        
        
        
        #le bouton plus
        self.new_dish_button = QPushButton()
        self.new_dish_button.setIcon(emoji_to_icon(emoji.emojize(":plus:")))
        self.new_dish_button.setFixedSize(30, 30)
        
        self.new_dish_button.clicked.connect(self.new_dish)
        
        bar_layout.addWidget(self.new_dish_button)
        
        
        
        
        
        
        main_layout.addLayout(bar_layout)
        
        #la liste a gauche
        content_layout.addWidget(self.dish_list, 1)
        
        #####################################
        #la boite à droite
        right_layout = QVBoxLayout()
        
        ingredients_layout = QHBoxLayout()
        
        right_layout.addStretch(1)
        
        
        
        right_layout.addLayout(dish_title_layout)
        
        right_layout.addSpacing(20)
        right_layout.addWidget(create_separator(5))
        
        right_layout.addWidget(self.dish_description_container)
        
        
        
        
        #ingredient layout
        ingredients_layout.addWidget(self.dish_necessary_ingredients,alignment=Qt.AlignmentFlag.AlignTop)
        ingredients_layout.addStretch(1)
        ingredients_layout.addWidget(self.dish_unnecessary_ingredients,alignment=Qt.AlignmentFlag.AlignTop)
        ingredients_layout.addStretch(2)
        
        right_layout.addLayout(ingredients_layout)
        
        
        right_layout.addStretch(5)
        
        right_layout.addWidget(self.dish_recipe_separator)
        right_layout.addWidget(self.dish_recipe)
        
        right_layout.addStretch(10)
        
        #rajout du block de droite au bloc de contenu
        content_layout.addLayout(right_layout,3)
        
        main_layout.addLayout(content_layout)

        ####################################################
        # Remplissage de la liste
        self.search("")

        # Quand on sélectionne un plat
        self.dish_list.currentItemChanged.connect(
            self.show_dish
        )
        
        #cache les trucs inutile au demarage
        self.dish_recipe_separator.setVisible(False)
        self.dish_description_container.setVisible(False)
        
        
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
        #si il n'y a pas de selection, cacher tous
        if current_item is None:
            self.dish_name.setText("Aucun plat avec cette recherche")
            self.dish_description.setText("")
            self.dish_recipe.setText("")
            self.dish_necessary_ingredients.setText("")
            self.dish_unnecessary_ingredients.setText("")
            
            self.dish_recipe_separator.setVisible(False)
            self.dish_description_container.setVisible(False)
            
            self.dish_time.setText("")
            self.dish_mark.setText("")
            
            return
        
        #recupere la recherche
        dish = current_item.data(Qt.ItemDataRole.UserRole)
        
        ###############################################################
        # UPDATE LES AFFICHAGES
        
        #affiche le nom du plat
        self.dish_name.setText(dish["name"])
        
        #le temp de cuisson
        if dish.get("cooking_time",0) not in [0,-1]:
            self.dish_time.setText(cooking_time_to_text(dish["cooking_time"]))
        else:
            self.dish_time.setText("")
        
        
        #la note sur 10
        if dish.get("mark","") != "" and dish.get("mark","") != -1:
            self.dish_mark.setText(str(dish["mark"]) + "/10")
        else:
            self.dish_mark.setText("")
            
            
        
        #la description, met rien si la description est vide
        if dish.get("description","") != "":
            self.dish_description_container.setVisible(True)
            self.dish_description.setText("• Description: \n" + dish.get("description","")+ "\n\n\n") #met du vide si la description n'existe pas
        else:
            self.dish_description_container.setVisible(False)
            self.dish_description.setText("")
        
        
        #la recette, met rien si la description est vide
        if dish.get("recipe","") != "":
            self.dish_recipe.setText("• Recette: \n" + dish.get("recipe",""))
            self.dish_recipe_separator.setVisible(True)
        else:
            self.dish_recipe_separator.setVisible(False)
            self.dish_recipe.setText("")
            
        #les ingrédients necessaires
        if dish.get("necessary_ingredients",[]) != []:
            self.dish_necessary_ingredients.setText("• Ingrédients: \n" + pretty_list(dish.get("necessary_ingredients",[])))
        else:
            self.dish_necessary_ingredients.setText("")
        
        #les ingrédients pas necessaires
        if dish.get("unnecessary_ingredients",[]) != []:
            self.dish_unnecessary_ingredients.setText("• Ingrédients supplémentaires: \n" + pretty_list(dish.get("unnecessary_ingredients",[])))
        else:
            self.dish_unnecessary_ingredients.setText("")

    
    #################################################################################################
    def new_dish(self):

        dialog = NewDishDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        dish = dialog.get_data()

        # Date d'ajout
        dish["added_date"] = date.today().isoformat()

        # Nom du fichier
        filename = make_filename(dish["name"])
        path = DISHES_DIR / f"{filename}.toml"

        # Évite d'écraser une recette existante
        number = 2

        while path.exists():
            path = DISHES_DIR / f"{filename}_{number}.toml"
            number += 1

        # Écriture du TOML
        with open(path, "wb") as file:
            tomli_w.dump(dish, file)

        # Ajoute immédiatement le plat à l'application
        dish["_file"] = path
        self.dishes.append(dish)

        # Actualise la liste
        self.search(self.search_bar.text())




#################################################################################################
#lancer le truc
def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()