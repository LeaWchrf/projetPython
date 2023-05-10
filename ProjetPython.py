!pip install stanza
!pip install spacy

from enum import IntEnum
import stanza
from stanza import Document
from stanza.utils.conll import CoNLL
import spacy
from enum import IntEnum
from spacy.tokens import Doc
from typing import Callable
from lxml import etree
import re


################################################
#Code Lea                    
################################################
from enum import IntEnum
import stanza
from stanza import Document
from stanza.utils.conll import CoNLL
import spacy
from enum import IntEnum
from spacy.tokens import Doc
from typing import Callable
from lxml import etree
import re

class Conllu:
    
    #à quoi se réfère la colonne de façon plus "propre"
    class Colonnes(IntEnum):

        ID = 0
        FORM = 1
        LEMMA = 2
        UPOS = 3
        XPOS = 4
        FEATS = 5
        HEAD = 6
        DEPREL = 7
        DEPS = 8
        MISC = 9

    def __init__(self,txt)->list:

        content=txt
        #fonction qui permet de supprimer le caractère retour à la ligne 
        content=content.rstrip("\n")

        #création du tableau
        lignes=content.split("\n")

        self._sentences=[]
        self._commentaires=[]
        buffer=[]
        buffercomm=[]

        #je m'occupe des commentaires et lignes vides trouvables dans le conll
        #j'enlève les lignes vides mais je garde les commentaires qui pour moi sont intéréssants dans le conll
        for line in lignes:
            
            #si je tombe sur une ligne vide cela signifie qu'après c'est une nouvelle phrase
            #donc on ajoute la phrase précédente qui est dans le buffer !
            if line=='':
                self._sentences.append(buffer)
                self._commentaires.append(buffercomm)
                buffer=[]
                buffercomm=[]
                continue
            elif not line[0].isdigit():
                continue
            elif line[0]=='#':
                buffercomm.append(line)
                continue
            else:
                data=line.split("\t")
                data[0]=int(data[0])

                if len(data) != 10:
                    print("Attention ! Il n'y a pas 10 colonnes.")

            buffer.append(data)

        self._sentences.append(buffer)
        self._commentaires.append(buffercomm)
        
    def to_dict(self, labels, colonnes):
        
        donnees=[]
        selectlabels=[]
        
        #on sélectionne seulement les labels dont on a besoin
        for coln in colonnes:
            selectlabels.append(labels[coln])
        
        #on prends chaque phrases et seulement la forme de chaque token
        for sent in self._sentences:
            donnees.append([])
            for tok in sent:
            
                dict_token={}
                for cle,i in zip(selectlabels, colonnes):
                    dict_token[cle]=tok[i]
                donnees[-1].append(dict_token)
                
        return(donnees)
                

    #affichage plus clair des données ! + permet de récupérer le conllu modifié en texte :-) 
    def __repr__(self):
        
        sortie=''
         
        for phrase,commentaires in zip(self._sentences,self._commentaires):
            for comm in commentaires:
                sortie+=comm+'\n'
            for tok in phrase:
                sortie+='\t'.join([str(col) for col in tok])+'\n'
                
            sortie+='\n'
            
        return(sortie)
            
class Stanza:
    
    """ 
        Méthodes suivantes :
    - méthode tokenize()
    - méthode pos()
    - méthode lemma()
    - méthode deprel()   
    
    """
    
    clefs=['id', 'text', 'lemma', 'upos', 'xpos', 'feats', 'head', 'deprel', 'deps', 'misc' ]
    
    #constructeur, une pipeline pour chaque processeur
    def __init__(self):
        
        self._pipelinetok=stanza.Pipeline(lang='fr',
                                          processors='tokenize')
        self._pipelinepos=stanza.Pipeline(lang='fr', 
                                          processors='tokenize,pos',
                                          tokenize_pretokenized=True)
        self._pipelinelemma=stanza.Pipeline(lang='fr', 
                                            processors='tokenize,lemma', 
                                            tokenize_pretokenized=True, 
                                            lemma_pretagged=True)
        self._pipelinedeprel=stanza.Pipeline(lang='fr', 
                                             processors='tokenize,depparse', 
                                             tokenize_pretokenized=True,
                                             depparse_pretagged=True)
        
    def tokenize(text:str):

        nlp = stanza.Pipeline(lang='fr', processors='tokenize')
        doc = nlp(text)
        for i, sentence in enumerate(doc.sentences):
            print(f'====== Sentence {i+1} tokens =======')
            print(*[f'id: {token.id}\ttext: {token.text}' for token in sentence.tokens], sep='\n')
    
    def pos(self, doc: Conllu):
        
        #on prends chaque phrases et seulement la forme de chaque token
        cols=[Conllu.Colonnes.ID, Conllu.Colonnes.FORM]
        donnees=doc.to_dict(Stanza.clefs, cols)
                    
        pos=self._pipelinepos(Document(donnees))
        
        #relier les données récupérées dans la liste de phrases[tokens[colonnes]] qu'on avait déjà
        for  newsentence, sentence in zip(pos.to_dict(), doc._sentences):
            for newtok, tok in zip(newsentence, sentence):
                
                if 'upos' in newtok:
                    tok[Conllu.Colonnes.UPOS]=newtok['upos']
                
                if 'feats' in newtok:
                    tok[Conllu.Colonnes.FEATS]=newtok['feats']
        
    def lemma(self, doc: Conllu):
        
        #on prends chaque phrases et seulement la forme de chaque token
        cols=[Conllu.Colonnes.ID, Conllu.Colonnes.FORM, Conllu.Colonnes.UPOS]
        donnees=doc.to_dict(Stanza.clefs, cols)
                    
        lemma=self._pipelinelemma(Document(donnees))
        
        #relier les données récupérées dans la liste de phrases[tokens[colonnes]] qu'on avait déjà
        for  newsentence, sentence in zip(lemma.to_dict(), doc._sentences):
            for newtok, tok in zip(newsentence, sentence):
                
                if 'lemma' in newtok:
                    tok[Conllu.Colonnes.LEMMA]=newtok['lemma']  
        

    def deprel(self, doc: Conllu)->list:
        
        donnees=[]
        
        #on prends chaque phrases et seulement la forme de chaque token
        cols=[Conllu.Colonnes.ID, Conllu.Colonnes.FORM, Conllu.Colonnes.UPOS, Conllu.Colonnes.FEATS, Conllu.Colonnes.LEMMA]
        donnees=doc.to_dict(Stanza.clefs, cols)
                    
        deprel=self._pipelinedeprel(Document(donnees))
        
        #relier les données récupérées dans la liste de phrases[tokens[colonnes]] qu'on avait déjà
        for  newsentence, sentence in zip(deprel.to_dict(), doc._sentences):
            for newtok, tok in zip(newsentence, sentence):
                
                if 'deprel' in newtok:
                    tok[Conllu.Colonnes.DEPREL]=newtok['deprel']
                    
                if 'head' in newtok:
                    tok[Conllu.Colonnes.HEAD]=newtok['head']             
          

################################################
#Code Marie
################################################
class Spacy:
    def __init__(self):
        # charge le modèle spacy pour la langue française
        self.nlp = spacy.load("fr_core_news_sm")

    """
    # je ne sais pas si ça marche juste je mets ça parce que j'ai tenté un truc mais je suis pas sûre que ce soit bien ça qui est demandé
    def tokenize(self, text:str):
        # utilise la méthode nlp de spaCy pour traiter le texte et représente celui ci sous la variable doc
        doc = self.nlp(text)
        
        sentences = []
        #itère sur chaque phrase dans l'objet Doc à l'aide de sents
        for sent in doc.sents:
            tokens = []
            # boucle sur chaque tok de la phrase analysée et l'ajoute à la liste tokens
            for tok in sent:
                tokens.append(tok.text for tok in doc)
            # ajoute finalement la lste de tokens à la liste sentences
            sentences.append(tokens)
        
        return sentences # il faudrait en sortie avoir une instance de la classe conll. Il faut
        # donc commencer par segmenter les phrases, puis tokeniser : list = donnée en entrée[list = phrases[str = tokens]]
        """
        
        
    def pos(self, doc:Conllu): 
        # on parcourt les phrases du doc conllu et on prend la colonne Form pour l'ajouter à la liste tokens 
        for sent in doc._sentences:
            tokens = []
            for tok in sent:
                tokens.append(tok[Conllu.Colonnes.FORM])
            # on traite cette liste avec spaCy pour trouver les tags de chaque token que l'on retrouve dans la variable doc_tag
            with self.nlp.select_pipes(enable=["tok2vec", "morphologizer"]):
                doc_tag = self.nlp(Doc(self.nlp.vocab, tokens))
            # on met les données que l'on obtient à l'issue du traitement dans le conllu 
            for tok, token_tag in zip(sent, doc_tag):
                tok[Conllu.Colonnes.UPOS]=token_tag.pos_
                # on a ajouté la colonne qui donne les traits morphologiques
                tok[Conllu.Colonnes.FEATS]=token_tag.morph
        
    def lemma(self, doc:Conllu):
        # on refait le même traitement que pour la méthode précédente mais en ajoutant une liste pos qui contiendra les données recueillies lors du traitement précédent
        for sent in doc._sentences:
            tokens = []
            pos = []
            for tok in sent:
                tokens.append(tok[Conllu.Colonnes.FORM])
                pos.append(tok[Conllu.Colonnes.UPOS])
            # traitement de la liste par spacy pour récupérer la lemmatisation
            with self.nlp.select_pipes(enable=["lemmatizer"]):
                doc_lemme = self.nlp(Doc(self.nlp.vocab, tokens, pos=pos))
            # report des données dans le conllu dans la colonne correspondante 
            for tok, token_lemme in zip(sent, doc_lemme):
                tok[Conllu.Colonnes.LEMMA]=token_lemme.lemma_
        
    def deprel(self,doc:Conllu):
        # on parcourt toujours le document en ajoutant encore une fois les données récupérées pour les autres méthodes sous forme de liste
        for sent in doc._sentences:
            tokens = []
            pos = []
            lemmes = []
            for tok in sent:
                tokens.append(tok[Conllu.Colonnes.FORM])
                pos.append(tok[Conllu.Colonnes.UPOS])
                lemmes.append(tok[Conllu.Colonnes.LEMMA])
            # traitement des données par spaCy dans le but de récupérer les relations de dépendances
            with self.nlp.select_pipes(enable=["tok2vec", "parser"]):
                doc_deprel = self.nlp(Doc(self.nlp.vocab, tokens, pos=pos, lemmas=lemmes))
            # on remet les données dans le conllu avec les traitements qui ont été effectués
            for tok, token_deprel in zip(sent, doc_deprel):
                tok[Conllu.Colonnes.DEPREL]=token_deprel.dep_
                # on souhaitait récupérer les données concrnant la tête mais il semble que les chiffres sont erronées mais on ne sait pas pourquoi
                tok[Conllu.Colonnes.HEAD]=token_deprel.head.i
                
def xml_tokenizer(file_path, xpath_query):
    
    f=open(file_path,mode='r',encoding='utf8')
    content=f.read()
    f.close()
    # charger le modèle spaCy pour la langue française
    nlp = spacy.load("fr_core_news_sm")
    
    # analyse le fichier xml
    with open(file_path, "rb") as f:
        xml = etree.parse(f)
    
    # extrait les zones de texte à traiter avec l'expression XPath
    text_zones = xml.xpath(xpath_query)
    
    # parcourt les zones de texte et les tokeniser
    tokens = ""
    offset = 0
    
    # extrait le texte de la zone
    for zone in text_zones:
        text = zone.text
        print ("line=",zone.sourceline)
        m=re.match(r'^((.*\n){'+str(zone.sourceline-1)+'}.*)'+text,content)
        if m:
            offset=len(m.group(1))
            print(" ",offset)
        # tokenise le texte avec spaCy
        doc = nlp(text)
        
        # ajoute les informations SpaceAfter et Offset à chaque token
        for sent in doc.sents:
            for token in sent:
                # calcul de la position de début et de fin du token dans le fichier xml à l'aide de la focntion index()
                start = content.index(text) +  + token.idx + offset
                end = start + len(token.text)
                # ajoute le token avec les informations SpaceAfter et Offset
                tokens += '\t'.join((str(token.i+1), token.text, token.lemma_, token.pos_, token.tag_, "_", str(token.head.i+1), token.dep_, "_", "SpaceAfter=" + str(token.whitespace_ != "") +"| Offset=" + str(start))) + '\n'
            # ajoute la longueur de la zone de texte pour calculer les positions de début et de fin du texte suivant
        offset += len(text)
    
    return Conllu(tokens)
    
################################################
#Code Lea                    
################################################
#utilisation de Factory 
#fournir à notre fonction des éléments 
#valeur de retour retourne une fonction
#donc création d'une fonction personnalisée qui s'occupera de stanza / spacy
from typing import Callable
    
def pipeline(pos, lemma, deprel)->Callable:
    """Fonction qui génère une pipeline personnalisée qui appliquera selon ce que l'utilisateur veut en processeurs.
    Pour chaque étape la pipeline récupère la classe du processeur choisi et crée une fonction qui va l'appeler 
    automatiquement!
    
    """

    def choix(source: str):
        conll= Conllu(source)
        pos.pos(conll)
        lemma.lemma(conll)
        deprel.deprel(conll)
        
        return conll
    return choix

# exemple d'utilisation de la fonction xml_tokenizer pour transformer un fichier xml au format conllu
file_path = "text.xml"
xpath_query = "//Description"
tokens = xml_tokenizer(file_path, xpath_query)

# les tests realises fait en binome

stan=Stanza()
spc=Spacy()

func=pipeline(pos=stan, lemma=stan, deprel=spc)

with open("test.csv",mode="r",encoding="utf-8") as f:
    co=func(f.read())
print(co)