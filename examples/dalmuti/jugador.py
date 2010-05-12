#!/usr/bin/env python

import sys
sys.path.append("../..")

import spade
import random
import time
import string
from cartas import Carta
from cartas import jugada

servidor="localhost"

nombreAgente = ""

class jugador(spade.Agent.Agent):

    class inicioBehav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            self.msg = None
            
            # Esperamos indefinidamente hasta que empiece la partida
            self.msg = self._receive(True)
        
            # En este punto habra empezado
            print nombreAgente+": Ok!! A ver si hay suerte..."

            # Escogemos una carta al azar para establecer los
            # roles iniciales de la partida
            lim = string.atoi(self.msg.getContent())

            carta = random.randint(0, lim-1)

            print nombreAgente+": Elijo la carta "+str(carta)

            #Enviamos nuestra eleccion
            self.myAgent.send2game("request", "Carta", str(carta))


    class cerrarBehav(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)

            print nombreAgente+": Bye!!"

            self.myAgent._kill()

    class impuestosBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent

            self.msg = self._receive(True)

            rol, cont = string.split(self.msg.getContent())
            
            if rol=="GD":
                print nombreAgente+": Soy el Gran Dalmuti!! A recaudar"
                a = max(mA.cartas)
                mA.cartas.remove(a)
                b = max(mA.cartas)
                mA.cartas.remove(b)

                # Avisamos a nuestro contrario que tiene que darnos 2 cartas
                mA.send2agent(cont, "inform", "Impuestos", "GP None")
                # Le mandamos nuestras 2 peores cartas
                mA.send2agent(cont, "inform", "Carta", str(a))
                mA.send2agent(cont, "inform", "Carta", str(b))
                
            elif rol=="MD":
                print nombreAgente+": Soy el Menor Dalmuti!! A recaudar"
                a = max(mA.cartas)
                mA.cartas.remove(a)

                # Avisamos a nuestro contrario que tiene que darnos 1 carta
                mA.send2agent(cont, "inform", "Impuestos", "MP None")
                # Le mandamos nuestra peor carta
                mA.send2agent(cont, "inform", "Carta", str(a))
            elif rol=="MP":
                print nombreAgente+": Soy el Menor Peon... Tome usted"
                a = min(mA.cartas)
                mA.cartas.remove(a)

                # Le mandamos nuestra mejor carta
                msg = self.msg.createReply()
                msg.setConversationId("Carta")
                msg.setContent(str(a))
                mA.send(msg)

            else: #GP
                print nombreAgente+": Soy el Gran Peon... Tome usted"
                a = min(mA.cartas)
                mA.cartas.remove(a)
                b = min(mA.cartas)
                mA.cartas.remove(b)

                # Le mandamos nuestras 2 mejores cartas
                msg = self.msg.createReply()
                msg.setConversationId("Carta")
                msg.setContent(str(a))
                mA.send(msg)
                msg.setContent(str(b))
                mA.send(msg)


    class tiradaMesaBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent
            #Esperamos que tiren los jugadores
            self.msg = self._receive(True)

            tirada = self.msg.getContent()
            vTira = string.split(tirada)

            if len(vTira)>0:
                mA.tiradaAct = map(string.atoi, vTira)
                # Ordenamos. Si es una tupla la primera sera el rango
                # aunque haya un bufon (rango 12 sera el ultimo)
                mA.tiradaAct.sort()
            else:
                mA.tiradaAct = []

    class recibirCartasBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            # Si nos dan una carta, pues la cogemos
            self.msg = self._receive(True) 

            carta = string.atoi(self.msg.getContent())
            print nombreAgente+": Recibo",Carta(carta)
            self.myAgent.cartas.append(carta)

    class revolucionBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            self.msg = self._receive(True)

            # Cuantos bufones tenemos
            nb = self.myAgent.cartas.count(12)

            if nb == 2:
                print nombreAgente+": Revolucion!!"
                self.myAgent.send2game("inform", "Revolucion", None)

    class tirarBehav(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg = None
            mA = self.myAgent
            #Esperamos nuestro turno
            self.msg = self._receive(True)

            self.tiro = []
            if len(mA.tiradaAct) == 0:
                print nombreAgente+": Me toca empezar a tirar"
                # Elijo la jugada para empezar
                self.empezar() 
            else:
                print nombreAgente+": Me toca superar ->",
                for i in map(lambda x: Carta(x), mA.tiradaAct):
                    print i,
                print
                # Elijo la jugada para superar
                self.superar()

            if len(self.tiro)==0:
                #Pasamos
                print nombreAgente+": Paso"
                mA.send2game("inform", "Tiro", "")
            else:
                try:
                    #Borramos las cartas que tiramos
                    map(mA.cartas.remove, self.tiro)
                    print nombreAgente+": Tiro ->",
                    for i in map(lambda x: Carta(x), self.tiro):
                        print i,
                    print
                    mA.send2game("inform", "Tiro", jugada(self.tiro) )
                    if len(mA.cartas) == 0:
                        mA.send2game("inform", "Salgo", None)
                except:
                    #Si hay algun problema al borrar las cartas, pasamos
                    print nombreAgente+": Paso"
                    mA.send2game("inform", "Tiro", "")

        def empezar(self):
            mA = self.myAgent
            
            mA.cartas.sort(reverse=True)
            #Numero peores cartas iguales
            NP=mA.cartas.count(mA.cartas[0])
            
            self.tiro = [mA.cartas[0]]*NP

        def superar(self):
            mA = self.myAgent
            jug = mA.tiradaAct
            tJug = len(jug)
            mA.cartas.sort(reverse=True)
            
            if tJug==1:
                for i in mA.cartas:
                    if i<jug[0]:
                        self.tiro = [i]
                        break

            else:
                # Numero de bufones
                NB = self.myAgent.cartas.count(12)

                for i in mA.cartas:
                    if i<jug[0] and (self.myAgent.cartas.count(i)+NB) >= tJug:
                        if NB > 0:
                            self.tiro = [i]*(tJug-1)+[12]
                        else:
                            self.tiro = [i]*tJug
                        break

    def _setup(self):
        self.tiradaAct = []
        self.cartas = []

        template = spade.Behaviour.ACLTemplate()
        template.setOntology("Dalmuti")
        template.setPerformative("request")
        template.setConversationId("Inicio")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento inicial
        self.addBehaviour(self.inicioBehav(), mt)

        template.setPerformative( "refuse" )
        template.setConversationId("FIN")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento de cerrar la conexion
        self.addBehaviour(self.cerrarBehav(), mt)

        template.setPerformative( "inform" )
        template.setConversationId("Tirada")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento de actualizar la tirada en la mesa
        self.addBehaviour(self.tiradaMesaBehav(), mt)

        template.setPerformative( "inform" )
        template.setConversationId("Carta")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento de actualizar la tirada en la mesa
        self.addBehaviour(self.recibirCartasBehav(), mt)

        template.setPerformative( "request" )
        template.setConversationId("Tira")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento tirar en nuestro turno
        self.addBehaviour(self.tirarBehav(), mt)

        template.setPerformative( "inform" )
        template.setConversationId("Impuestos")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento de pagar/cobrar impuestos
        self.addBehaviour(self.impuestosBehav(), mt)

        template.setPerformative( "inform" )
        template.setConversationId("Revolucion")
        mt = spade.Behaviour.MessageTemplate(template)
        # Comportamiento comprobar revolucion
        self.addBehaviour(self.revolucionBehav(), mt)

        # Avisamos de que queremos apuntarnos a la partida
        time.sleep(1)
        print nombreAgente+": Ey, quiero jugar!!"
        self.send2game("request", "Inicio", None)


    def send2game(self, perf, id, content):
         # Creamos el mensaje
         msg = spade.ACLMessage.ACLMessage()
         # Lo rellenamos
         msg.setOntology( "Dalmuti" )
         msg.setPerformative( perf )
         msg.setConversationId( id )
         msg.setContent( content )
         gameManager = spade.AID.aid(name="dalmuti@127.0.0.1",addresses=["xmpp://dalmuti@127.0.0.1"])
         msg.addReceiver( gameManager )
         # Enviamos al gameManager
         self.send(msg)

    def send2agent(self, dest, perf, id, content):
         # Creamos el mensaje
         msg = spade.ACLMessage.ACLMessage()
         # Lo rellenamos
         msg.setOntology( "Dalmuti" )
         msg.setPerformative( perf )
         msg.setConversationId( id )
         msg.setContent( content )

         receiver = spade.AID.aid(name=dest,addresses=["xmpp://"+dest])
         msg.addReceiver( receiver )
         self.send(msg)

if __name__ == "__main__":
    if len(sys.argv) != 3 :
        print "Uso: "+sys.argv[0]+" nombre_agente password"
    else:
        nombreAgente = sys.argv[1]
        print "Agente: "+nombreAgente

        ag = jugador(sys.argv[1]+"@"+servidor, sys.argv[2])
        ag.start()
