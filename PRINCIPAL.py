######################################################################
#                PROJET D'APPRENTISSAGE AUTONOME                     #
#                 UNE IA POUR LE JEU DE PUISSANCE 4                  #
######################################################################
# Realise Par :                                                      #
#    ~ KAMAL SAMNOUNI                                                #
#    ~ ABDELMONSSIF OUFASKA                                          #
######################################################################


import numpy
import random
import math
from MOTEUR import*
import matplotlib.pyplot as plt



######### PARAMETRES DE NEURONES ###################################
epsilon=0.1
gamma=0.9
alpha=0.8
sizeInput=42
sizeHiddenLayer=30
sizeOutput=7
####################################################################


def sigmoid(x):
    if x>100:
        returnValue=1
    elif x<-100:
        returnValue=-1
    else:
        returnValue=(math.exp(x)-math.exp(-x))/(math.exp(x)+math.exp(-x))
    return returnValue
        
class NN:
    def __init__(self,sizeInput,sizeHiddenLayer,sizeOutput):
        self.sizeInput=sizeInput
        self.sizeHiddenLayer=sizeHiddenLayer
        self.sizeOutput=sizeOutput

        #below are the weights
        self.HiddenLayerEntryWeights=numpy.zeros([sizeHiddenLayer,sizeInput])
        self.LastLayerEntryWeights=numpy.zeros([sizeOutput,sizeHiddenLayer])

        #random initialization
        for i in range(0,sizeHiddenLayer):
            for j in range(0,sizeInput):
                self.HiddenLayerEntryWeights[i,j]=random.uniform(-0.1,0.1)
                
        for i in range(0,sizeOutput):
            for j in range(0,sizeHiddenLayer):
                self.LastLayerEntryWeights[i,j]=random.uniform(-0.1,0.1)

        self.HiddenLayerEntryDeltas=numpy.zeros(sizeHiddenLayer)
        self.LastLayerEntryDeltas=numpy.zeros(sizeOutput)

        self.HiddenLayerOutput=numpy.zeros(sizeHiddenLayer)
        self.LastLayerOutput=numpy.zeros(sizeOutput)

    def output(self,x):
        for i in range(0, self.sizeHiddenLayer):
            self.HiddenLayerOutput[i]=sigmoid(numpy.dot(self.HiddenLayerEntryWeights[i],x))
        for i in range(0, self.sizeOutput):
            self.LastLayerOutput[i]= \
            sigmoid(numpy.dot(self.LastLayerEntryWeights[i],self.HiddenLayerOutput))

    def retropropagation(self,x,y,actionIndex):
        self.output(x)
       
        #deltas computation
        self.LastLayerEntryDeltas[actionIndex]=2*(self.LastLayerOutput[actionIndex]-y)* \
            (1+self.LastLayerOutput[actionIndex])*(1-self.LastLayerOutput[actionIndex])

        for i in range(0,self.sizeHiddenLayer):
            #here usually you need a sum
            self.HiddenLayerEntryDeltas[i]=self.LastLayerEntryDeltas[actionIndex]* \
            (1+self.HiddenLayerOutput[i])*(1-self.HiddenLayerOutput[i])*self.LastLayerEntryWeights[actionIndex,i]

        #weights update
        for i in range(0,self.sizeHiddenLayer):
            self.LastLayerEntryWeights[actionIndex,i]-=alpha*self.LastLayerEntryDeltas[actionIndex]* \
            self.HiddenLayerOutput[i]

        for i in range(0,self.sizeHiddenLayer):
            for j in range(0,self.sizeInput):
                self.HiddenLayerEntryWeights[i,j]-=alpha*self.HiddenLayerEntryDeltas[i]*x[j]


########################################### APPRENTISSAGE #####################################################

myNN1 = NN(sizeInput, sizeHiddenLayer, sizeOutput)
victoires = [0] * 3  # Jaunes, Rouges, Nulles
victoire =numpy.zeros([NB_PARTIES,2]) # Pour le graphe d'apprentissage

def competition(couleur):
    global victoires
    global sizeHiddenLayer
    global sizeInput
    global sizeOutput
    global gamma 
    global alpha
    global epsilon

    
    listePositions = initialise_liste_positions()
    state1=random.randint(1, 7)
    frstState1=state1
    state2=random.randint(1, 7)
    frstState2=state2
    """ Recompense de chaque case """
    reward=[3,4,5,7,5,4,3,4,6,8,10,8,6,4,5,8,11,13,11,8,5,5,8,11,13,11,8,5,4,6,8,10,8,6,4,3,4,5,7,5,4,3]
    finPartie = False
    for i in range(NB_PARTIES):

        affiche_joueur_qui_commence_console(couleur)
        if MODE_GRAPHIQUE:
            affiche_joueur_qui_commence_fenetre(couleur)
        couleurJoueur = couleur
        while not finPartie:
            """ Tanq que la partie n'est pas encore fini """
            ###### Premier Joueur ####### Notre Agent ##########################
            
            if random.uniform(0, 1) < epsilon:
                       colonne = random.randint(1, NB_COLONNES)
                       while colonne_pleine(listePositions, colonne):
                        colonne = random.randint(1, NB_COLONNES)     
            else:
                x=numpy.zeros(sizeInput)
                x[state1-1]=1 
                myNN1.output(x)
                colonne = numpy.argmax(myNN1.LastLayerOutput)+1 ###### colonne=action # on a ajouté 1 parce que argmax donne une valeur entre 0et 6  
                while colonne_pleine(listePositions, colonne):
                    colonne = random.randint(1, NB_COLONNES)                  
            action1=colonne  
            next_state1 ,listePositions = jouer(listePositions, couleurJoueur, action1) ## next_state1 notre nouvelle position sur la grille
            x=numpy.zeros(sizeInput)
            x[next_state1-1]=1
            myNN1.output(x)
            next_max = numpy.max(myNN1.LastLayerOutput)
            target = reward[next_state1-1]+gamma*next_max
            x=numpy.zeros(sizeInput)
            x[state1-1]=1
            myNN1.retropropagation(x,target,action1-1)
            finPartie, couleurJoueur, victoires = fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
            state1=next_state1
            
            
            ###### Deuxieme Joueur ####### Si ALEATOIRE = False l'Agent joue contre lui meme , Sinon le deuxieme joueur est aleatoire#######
            if not finPartie:
                if ALEATOIRE:
                    colonne = random.randint(1, NB_COLONNES)
                    while colonne_pleine(listePositions, colonne):
                        colonne = random.randint(1, NB_COLONNES) 
                    position ,listePositions = jouer(listePositions, couleurJoueur, colonne) 
                    finPartie, couleurJoueur, victoires= fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
                      
                else :
                    if random.uniform(0, 1) < epsilon:
                            colonne = random.randint(1, NB_COLONNES)
                            while colonne_pleine(listePositions, colonne):
                                colonne = random.randint(1, NB_COLONNES)     
                    else:
                       
                        x=numpy.zeros(sizeInput)
                        x[state2-1]=1 
                        myNN1.output(x)
                        """ Le deuxième joueur utilise la stratigie du premier joueur (lui meme) """
                        colonne = numpy.argmax(myNN1.LastLayerOutput)+1
                        while colonne_pleine(listePositions, colonne):
                            colonne = random.randint(1, NB_COLONNES)                      
                    action2=colonne
                    next_state2,listePositions = jouer(listePositions, couleurJoueur, action2)             
                    state2=next_state2
               
                    finPartie, couleurJoueur, victoires = fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
                                                 
        victoire[i,0]=victoires[0] # Pour le graphe d'apprentissage
        victoire[i,1]=victoires[1]
        # Bilan de chaque partie
        affiche_victoires_console(victoires)  # Jaunes, Rouges, Nulles
        if MODE_GRAPHIQUE:
            affiche_victoires_fenetre(victoires)  # Jaunes, Rouges, Nulles
        # Initialisation 
        listePositions = initialise_liste_positions()
        finPartie = False
        if MODE_GRAPHIQUE:
            initialise_fenetre(NB_PARTIES)
            
            
if NB_PARTIES > 1:
    competition('yellow')  # Le premier joueur a la couleur jaune (notre Agent)
            
print("....................... fin de l'apprentissage ...............................")

plt.plot(numpy.arange(1,NB_PARTIES+1),victoire[:,0],c='yellow',label="Joueur 1")   
plt.plot(numpy.arange(1,NB_PARTIES+1),victoire[:,1],c='red',label="Joueur 2")   
plt.xlabel('Episode')
plt.ylabel('Victoires cumules')
plt.title("Evolution de l'apprentissage")
plt.grid()
plt.legend()
print("................... Vous pouvez jouer contre l'IA directement ...................")

########################################## JOUER CONTRE L'IA #######################################################

finPartie = True
listePositions = []
couleurJoueur = ''
victoires = [0] * 3  # Jaunes, Rouges, Nulles
blocageJoueur = False
state=state=random.randint(1, 7) # initialisation de premiere state

        

def mouse_clic(event):
    "Gestion du clic de souris"
    global finPartie
    global listePositions
    global couleurJoueur
    global victoires
    global blocageJoueur  # Indispensable pour les cas ou l'on clique trop vite
    global state
    if not blocageJoueur:
        if finPartie:
            blocageJoueur = True
            listePositions = initialise_liste_positions()
            destruction_jetons()
            efface_message_fenetre()
            fenetreJeu.update()
            time.sleep(1)
            couleurJoueur = random.choice([ 'red'])
            # Affiche joueur qui commence
            affiche_joueur_qui_commence_console(couleurJoueur)
            affiche_joueur_qui_commence_fenetre(couleurJoueur)
            if couleurJoueur == 'red' :
                x=numpy.zeros(sizeInput)
                x[state-1]=1
                myNN1.output(x)
                # choisir l'action qui maximise le gain par Neurones
                action = numpy.argmax(myNN1.LastLayerOutput)+1
                while colonne_pleine(listePositions, action):
                            action = random.randint(1, NB_COLONNES)    
                next_state,listePositions = jouer(listePositions, couleurJoueur, action)
                state=next_state
                finPartie, couleurJoueur, victoires = fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
            finPartie = False
            blocageJoueur = False
        else:
            x = event.x
            colonne = col = 0
            while col < NB_COLONNES:
                col = col + 1
                ray = rayon()
                if x > col*ESPACEMENT+2*(col-1)*ray and x < col*ESPACEMENT+2*col*ray:
                    colonne = col
            if (colonne and not colonne_pleine(listePositions, colonne)):
                blocageJoueur = True
                position,listePositions = jouer(listePositions, couleurJoueur, colonne)
                finPartie, couleurJoueur, victoires = fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
                if not finPartie :
                    x=numpy.zeros(sizeInput)
                    x[state-1]=1
                    myNN1.output(x)
                    action = numpy.argmax(myNN1.LastLayerOutput)+1
                    while colonne_pleine(listePositions, action):
                            action = random.randint(1, NB_COLONNES)  
                    next_state,listePositions = jouer(listePositions, couleurJoueur, action)
                    state=next_state
                    finPartie, couleurJoueur, victoires = fin_partie(listePositions, couleurJoueur, victoires)  # Teste si la partie est finie
                if finPartie:
                    # Bilan
                    affiche_victoires_console(victoires)  # Jaunes, Rouges, Nulles
                    affiche_victoires_fenetre(victoires)  # Jaunes, Rouges, Nulles
                    
                blocageJoueur = False



grille.bind('<Button-1>', mouse_clic)
finPartie = False
listePositions = initialise_liste_positions()
couleurJoueur = 'yellow'
affiche_joueur_qui_commence_console(couleurJoueur)
affiche_joueur_qui_commence_fenetre(couleurJoueur)

fenetreJeu.mainloop()

#############################################################################################################################

    