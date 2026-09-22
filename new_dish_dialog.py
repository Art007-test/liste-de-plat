from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QDialogButtonBox,
    QMessageBox,
)


class NewDishDialog(QDialog):

    def __init__(self, parent=None, dish=None):
        super().__init__(parent)
        
        self.dish = dish

        self.setWindowTitle("Modifier le plat" if dish else "Nouveau plat")
        self.resize(500, 600)

        layout = QFormLayout(self)

        # Nom
        self.name_edit = QLineEdit()
        layout.addRow("Nom :", self.name_edit)

        # Temps de cuisson
        self.cooking_time_edit = QSpinBox()
        self.cooking_time_edit.setRange(-1, 100000)
        self.cooking_time_edit.setValue(-1)
        layout.addRow("Temps de préparation :", self.cooking_time_edit)

        # Note
        self.mark_edit = QSpinBox()
        self.mark_edit.setRange(-1, 10)
        self.mark_edit.setValue(-1)
        layout.addRow("Note :", self.mark_edit)

        
        # Description
        self.description_edit = QTextEdit()
        layout.addRow("Description :", self.description_edit)

        # Recette
        self.recipe_edit = QTextEdit()
        layout.addRow("Recette :", self.recipe_edit)
        
        
        
        # Ingrédients nécessaires
        self.necessary_ingredients_edit = QTextEdit()
        self.necessary_ingredients_edit.setPlaceholderText("Un ingrédient par ligne")
        layout.addRow("Ingrédients :",self.necessary_ingredients_edit)
                
                
        # Ingrédients
        self.ingredients_edit = QTextEdit()
        self.ingredients_edit.setPlaceholderText("Un ingrédient par ligne")
        layout.addRow("Ingrédients optionnels:", self.ingredients_edit)

        

        # Tags
        self.tags_edit = QTextEdit()
        self.tags_edit.setPlaceholderText(
            "Un tag par ligne"
        )
        layout.addRow("Tags :", self.tags_edit)

        

        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        
        if dish is not None:
            self.load_dish(dish)

    def text_to_list(self, text):
        """Transforme plusieurs lignes en liste."""

        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    def validate(self):
        """Vérifie les données avant de fermer la fenêtre."""

        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du plat ne peut pas être vide."
            )
            return

        self.accept()

    def get_data(self):

        return {
            "name": self.name_edit.text().strip(),

            "cooking_time": self.cooking_time_edit.value(),

            "unnecessary_ingredients": self.text_to_list(
                self.ingredients_edit.toPlainText()
            ),

            "necessary_ingredients": self.text_to_list(
                self.necessary_ingredients_edit.toPlainText()
            ),

            "tags": self.text_to_list(
                self.tags_edit.toPlainText()
            ),

            "recipe": self.recipe_edit.toPlainText(),

            "description": self.description_edit.toPlainText(),

            "mark": self.mark_edit.value(),
        }
    def load_dish(self, dish):

        self.name_edit.setText(dish.get("name", ""))

        self.cooking_time_edit.setValue(
            dish.get("cooking_time", -1)
        )

        self.mark_edit.setValue(
            dish.get("mark", -1)
        )

        self.ingredients_edit.setPlainText(
            "\n".join(dish.get("unnecessary_ingredients", []))
        )

        self.necessary_ingredients_edit.setPlainText(
            "\n".join(dish.get("necessary_ingredients", []))
        )

        self.tags_edit.setPlainText(
            "\n".join(dish.get("tags", []))
        )

        self.description_edit.setPlainText(
            dish.get("description", "")
        )

        self.recipe_edit.setPlainText(
            dish.get("recipe", "")
        )