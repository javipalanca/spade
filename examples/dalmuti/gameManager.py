#!/usr/bin/env python

import sys
import os
sys.path.append(".."+os.sep+"..")
import spade
import string
import random
import time
from cartas import Carta
from cartas import jugada

servidor="127.0.0.1"

class gameManager(spade.Agent.Agent):

    jugadores = {}
    vKey = 0

    class inscripcionBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA=self.myAgent
            
            if mA.nInscritos < mA.nPlayers:
                print ">> Inscripcion: Esperando (",(mA.nPlayers-mA.nInscritos),"restantes )\n"
                # Esperamos indefinidamente un mensaje de un jugador
                self.msg = self._receive(True)

                # Nos solicitan entrar en la partida
                jugador, name = mA.datosSender(self.msg.getSender().getName())

                if mA.jugadores.has_key(jugador):
                    print "\n"+name+"!! Ya estas apuntado a la partida!!\n"
                    mA.send2player(mA.jugadores[jugador], "refuse", "FIN", None)
                else:
                    mA.jugadores[jugador] = mA.vKey
                    mA.vKey = mA.vKey+1

                    print "Bienvenid@ "+name+". Elige una carta"
                    mA.nInscritos = mA.nInscritos+1

                    # Contestamos indicando las cartas entre las que debe elegir
                    msg = self.msg.createReply()

                    msg.setContent( str(len(mA.baraja)) )

                    mA.send(msg)
            else:
                while mA.roles[-1] < 0:
                    print "Esperando a que todos saquen una carta\n"
                    time.sleep(1)
              
                print "Ya han elegido una carta cada uno"

                r = mA.roles
                tmp = sorted(r)

                # Asignamos los roles segun la carta sacada
                for i in range(len(tmp)):
                    mA.roles[r.index(tmp[i])] = i

                # Orden de juego
                for i in range(len(mA.roles)):
                    mA.orden[i] = mA.roles.index(i)

                mA.partida()

                while True:
                    self.msg = self._receive(True)
                    print "Partida Completa"
                    jugador, trash = mA.datosSender(self.msg.getSender().getName())
                    mA.send2player(mA.jugadores[jugador], "refuse", "FIN", None)


    class rolInicialBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent

            #Esperamos la carta elegida de cada jugador
            self.msg = self._receive(True)

            jugador, name = mA.datosSender(self.msg.getSender().getName())           
            
            numCarta = string.atoi(self.msg.getContent())
            numCarta = numCarta%len(mA.baraja)
            carta = mA.baraja.pop(numCarta)
            print "Ok.",name,"ha sacado:",carta

            # Apuntamos provisionalmente la carta como rol
            mA.roles[mA.jugadores[jugador]] = carta.getTipo()


    class saliendoBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent

            sale=[]
            while len(sale) < mA.nPlayers:
                # Esperamos a que salga un jugador
                self.msg = self._receive(True)

                jugador, name = mA.datosSender(self.msg.getSender().getName())

                print ">> Sale",name
                sale.append(mA.jugadores[jugador])
                mA.orden[mA.orden.index(mA.jugadores[jugador])] = -1

            mA.finP = True
            for i in sale:
                mA.roles[i] = sale.index(i)

            mA.orden = sale

    class revBehaviour(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent

            self.msg = self._receive(True)

            jugador, name = mA.datosSender(self.msg.getSender().getName())
            
            if mA.roles[mA.jugadores[jugador]] == mA.nPlayers-1:
                #Si la declara el Gran Peon
                print ">>",name,"Declara la GRAN REVOLUCION"
                #Intercambiamos los roles
                mA.orden.reverse()
                #Mostramos el resultado de la gran revolucion
                mA.mostrarRoles()
            else:
                print ">>",name,"Declara la Revolucion"
                mA.revolucion = True #Para que no hayan impuestos
            

    class partidaBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent

            print
            print "---------------------------------"
            print "-          NUEVA RONDA          -"
            print "---------------------------------"

            mA.mostrarRoles()

            mA.finP = False
            ply = 0
            # El ultimo en tirar
            ultTir = -1

            mA.repartir()

            # Revolucion
            for i in mA.orden[2:]:
                mA.send2player(i, "inform", "Revolucion", None)
            # Esperamos la respuesta
            print ">> Esperamos revolucionarios"
            time.sleep(5)

            if not mA.revolucion:
                mA.impuestos()
                time.sleep(1) # Esperamos que se pasen las cartas
            else:
                mA.revolucion = False

            while not mA.finP:
                if mA.orden[ply] < 0:
                    # Si tras salir nadie nos ha mejorado, tira el siguiente
                    if ultTir == ply:
                        ultTir = (ultTir+1)%mA.nPlayers
                    ply = (ply+1)%mA.nPlayers
                    continue

                # Si han pasado todos, empiezo a tirar
                if ultTir == ply:
                    mA.send2player(mA.orden[ply], "inform", "Tirada", "")
                    print ">> Inicia"
                    time.sleep(0.5)

                # Indicamos que tire al jugador que toca
                mA.send2player(mA.orden[ply], "request", "Tira", None)
                # Esperamos su tirada
                self.msg = self._receive(True, 1)
                
                if not self.msg:
                    continue
                
                tirada = self.msg.getContent()
                vTira = jugada(string.split(tirada))

                jugador, name = mA.datosSender(self.msg.getSender().getName())
                if len(vTira)==0:
                    print name,"PASA"
                else:
                    print name,"TIRA",
                    for i in map(lambda x: Carta(string.atoi(x)), string.split(tirada)):
                        print i,
                    print
                    ultTir = ply    
                    mA.send2all("inform", "Tirada", tirada)

                ply = (ply+1)%mA.nPlayers
                time.sleep(0.5)
            

            mA.nRondas = mA.nRondas-1

            if mA.nRondas<=0:
                print "\n>> FIN DE LA PARTIDA"
                mA.mostrarRoles()
                mA.send2all("refuse", "FIN", None)
                self.myAgent._kill()
                #Nos bloqueamos hasta que se muera el agente
                self.msg = self._receive(True)



    def partida(self):
        #Empieza una partida indefinidamente

        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Dalmuti")
        template.setPerformative("inform")
        template.setConversationId("Tiro")        
        mt = spade.Behaviour.MessageTemplate(template)

        self.addBehaviour(self.partidaBehav(), mt)

        template.setPerformative("inform")
        template.setConversationId("Salgo")
        mt = spade.Behaviour.MessageTemplate(template)
        # Anotamos los jugadores que van saliendo
        self.addBehaviour(self.saliendoBehav(), mt)


    def datosSender(self, sender):
        jugador = string.split(sender, "/")[0]
        name = string.split(sender, "@")[0]
        return (jugador, name)

    def send2player(self, nP, perf, id, content):
        msg = spade.ACLMessage.ACLMessage()
        msg.setOntology("Dalmuti")
        msg.setPerformative( perf )
        msg.setConversationId( id )
        msg.setContent( content )

        jugador = self.jugadores.keys()[ self.jugadores.values().index(nP) ]        

        receiver = spade.AID.aid(name=jugador,addresses=["xmpp://"+jugador])
        msg.addReceiver( receiver )

        self.send(msg)

    def send2all(self, perf, id, content):
        msg = spade.ACLMessage.ACLMessage()
        msg.setOntology("Dalmuti")
        msg.setPerformative( perf )
        msg.setConversationId( id )
        msg.setContent( content )

        for ply in self.jugadores.keys():
            receiver = spade.AID.aid(name=ply,addresses=["xmpp://"+ply])
            msg.addReceiver( receiver )

        self.send(msg)

    def setOptions(self, N, R):
        self.nPlayers = N
        self.nInscritos = 0
        self.nRondas = R
        # El rol de cada jugador ( {1,GranDalmuti} ... {len()-1,GranPeon} )
        self.roles = [-1]*N
        # El orden en que deben tirar orden[0], orden[1], ...
        self.orden = [-1]*N

    def repartir(self):
        self.crearBaraja()

        ply=0
        for c in self.baraja:
            self.send2player(self.orden[ply], "inform", "Carta", str(c.getTipo()))
            ply = (ply+1)%self.nPlayers

    def impuestos(self):
        print ">> Impuestos"
        gd = self.orden[0]  #Gran  Dalmuti
        md = self.orden[1]  #Menor Dalmuti
        mp = self.orden[-2] #Menor Peon
        gp = self.orden[-1] #Gran  Peon

        content = "GD "+self.jugadores.keys()[ self.jugadores.values().index(gp) ]
        self.send2player(gd, "inform", "Impuestos", content)

        content = "MD "+self.jugadores.keys()[ self.jugadores.values().index(mp) ]
        self.send2player(md, "inform", "Impuestos", content)

    def _setup(self):
        self.crearBaraja()
        self.revolucion = False

        # Preparamos la plantilla para el comportamiento inicial
        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Dalmuti")
        template.setPerformative("request")
        template.setConversationId("Inicio")

        mt = spade.Behaviour.MessageTemplate(template)

        insBhv = self.inscripcionBehav()
        self.addBehaviour(insBhv, mt)

        # Preparamos la plantilla para asignar roles
        template.setConversationId("Carta")
        mt = spade.Behaviour.MessageTemplate(template)

        rolBhv = self.rolInicialBehav()
        self.addBehaviour(rolBhv, mt)

        template.setPerformative("inform")
        template.setConversationId("Revolucion")
        mt = spade.Behaviour.MessageTemplate(template)

        self.addBehaviour(self.revBehaviour(), mt)


    def mostrarRoles(self):
        print "\n>> Roles"
        for it, i in enumerate(self.orden):
            jugador = self.jugadores.keys()[ self.jugadores.values().index(i)]
            name = string.split(jugador, "@")[0]
            print name,"->",
            if it == 0:
                print "Gran Dalmuti"
            elif it == 1:
                print "Menor Dalmuti"
            elif it == len(self.orden)-1:
                print "Gran Peon"
            elif it == len(self.orden)-2:
                print "Menor Peon"
            else:
                print "Comerciante",(it-1)
                
        print


    def crearBaraja(self):
        self.baraja = []
        
        for i in range(12):
            self.baraja = self.baraja + [i]*(i+1)
            
        # Los bufones son un caso especial
        self.baraja = self.baraja + [12,12]

        for i, c in enumerate(self.baraja):
            self.baraja[i] = Carta(c)

        self.barajar()

    def barajar(self):
        for i in range(len(self.baraja)):
            j = random.randint(0,len(self.baraja)-1)
            self.baraja[i], self.baraja[j] = self.baraja[j], self.baraja[i]
        
        
if __name__ == "__main__":
    if len(sys.argv) != 3 :
        print "Uso: "+sys.argv[0]+" jugadores rondas"
        print "\t-jugadores\tNumero de jugadores de la partida"
        print "\t-rondas   \tNumero de rondas que se van a jugar"
    else:
        try:
            N = string.atoi(sys.argv[1])
            R = string.atoi(sys.argv[2])
            if N>=4 and N<=40 and R > 0:
                ag = gameManager("dalmuti@"+servidor, "ElGranDalmuti")
                ag.start()
                ag.setOptions( N, R )
            else:
                print "Dalmuti: [4-40] jugadores y 1 ronda minimo"
        except:
            print "Uso: "+sys.argv[0]+" numero_jugadores"
            print "\t-jugadores\tNumero de jugadores de la partida"
            print "\t-rondas   \tNumero de rondas que se van a jugar"
