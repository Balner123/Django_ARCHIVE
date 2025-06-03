## DJANGO - ARCHIVAČNÍ SYSTÉM   
---
tento projekt obsahuje webovou aplikaci v Djangu jenž má za cíl organizovat a uložit do databáze dokumenty či fotografie , které by jinak skončily v nepopsaných a navždy již zapomenutých bednách ve sklepě.

---
"""
Práce s DB je zde poněkud zvláštně řešená, kvůli tomu jakým způsobem je DB navržená, a to se zásadou : "vše co je stejné , patří do jedné tabulky". Proto je v hlavní tabulce vše co zdílí veškeré archivované objekty + typ , v specifických tabulkách jsou již hodnoty pro jednotlivé typy objektů. V models.py s těmito fakty pracuje pomocí tzv. Polymorphic models, kdy je vytvořen obecný základní model který obsahuje hlavní tabulku DB a poté jsou vytvořeny modely pro jetnotlivé typy objektů které z tohoto zakladního modelu přebírají vlastnosti + přidávají své vlastní. Toto přináší některé výhody pro další práci, avšak velikostí těchto výhod si nejsem tolik jist...(  Omezí se duplikace kódu, nebo např. při přidávání objektu si si model sám zajistí přidělení dat do správných tabulek)
"""
(PS: berte to se špetkou soli, dokonale nevím co dělám)
### Start-up
```
git clone {github url}
python -m .venv venv
pip install -r requirements.txt
python ./manage.py runserver
```
---

### Requirements
```
asgiref==3.8.1
Django==5.2
sqlparse==0.5.3
tzdata==2025.2
django-polymorphic
setuptools==78.1.0
django-crispy-forms
crispy-bootstrap5
```
