## Utilisation de notre code
Notre code prends en charge essentiellement des fichiers CoNLL-U, de ce fait il faut : 

* créer un objet CoNLL-U
```python
conll = Conllu('test.csv')
```
* appeler les fonctions `pos()`, `lemma()` et `deprel()`dans cet ordre précis, depuis un ou plusieurs processeurs au choix
```python
# Pour Stanza
stan = Stanza()
stan.pos(conll)
stan.lemma(conll)
stan.deprel(conll)

# Pour Spacy
spac = Spacy()
spac.pos(conll)
spac.lemma(conll)
spac.deprel(conll)

# On peut évidemment mélanger les deux :
spac.pos(conll)
stan.lemma(conll)
stan.deprel(conll)
```
* On peut récupérer la forme textuelle du CoNLL-U juste en faisant appel à sa représentation `__repr__()`
```python
str(conll) 
repr(conll)
print(conll)
# etc...
```
La méthode de construction `__init__()` prend un texte brut en entrée au format CoNLL-U, le lit, le stocke sous forme de tableau et extrait les commentaires et les lignes de données. Une autre méthode `to_dict()` permet de récupérer les données de chaque token, de chaque phrase sous forme de dictionnaire, et une autre méthode `__repr__()` permet d'afficher les données sous forme de chaîne de caractères.

## Fonction de tokenisation maison pour les fichiers XML

Cette fonction appelée `xml_tokenizer`, permet de traiter les fichiers XML en tokenisant le texte à l'aide
de la bibliothèque Spacy. Les tokens obtenus sont formatés selon le format CoNLL-U, largement
utilisé pour l'annotation linguistique.

La fonction `xml_tokenizer()` prend deux paramètres d'entrée :

* `file_path` : le chemin vers le fichier XML à traiter

* `xpath_query` : une expression XPath utilisée pour extraire les zones de texte à tokeniser

La fonction permet d'effectuer différentes taches :

1. Lit le contenu du fichier XML spécifié par `file_path`
2. Charge le modèle de langue française de Spacy (fr_core_news_sm)
3. Analyse le fichier XML à l'aide du module `lxml_etree`
4. Extrait les zones de texte à traiter en fonction de l'expression XPath fournie
5. ltère sur les zones de texte extraites
6. Tokenise le texte de chaque zone à l'aide du modèle Spacy
7. Collecte les informations sur chaque token, y compris son index, son texte, son lemme, sa partie du discours, son étiquette morphologique, l'index de son parent, la relation de dépendance et des fonctionnalités supplémentaires telles que les espaces vides et les offsets
8. Formate les informations sur les tokens dans une chaîne représentant le format CoNLL-U

En résumé, cette fonction prend un fichier XML, extrait les zones de texte spécifiées par une requête
XPath, les tokenise à l'aide de Spacy, puis renvoie les résultats au format CoNLL-U.

### Exemple d'utilisation

Dans l'exemple, un fichier XML avec le nom "text_xml” est traité, et les zones de texte correspondant
à la requête XPath "//Description" sont tokenisées. Les tokens obtenus sont ensuite écrits dans un fichier nommé "file_conllu" au format CoNLL-U. Enfin, les informations sur les tokens sont affichées
dans la console.

Le code repose sur les bibliothèques suivantes :

* Spacy : une bibliothèque de traitement du langage naturel
* lxml : une bibliothèque de traitement XML et HTML
* re : le module d'expressions régulières pour les correspondances de motifs.

