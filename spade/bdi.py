from logic import *
from copy import copy
import types

import Agent
import Behaviour

class PreConditionFailed (Exception): pass
class PostConditionFailed(Exception): pass
class ServiceFailed(Exception): pass
class KBConfigurationFailed(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class Goal:
    
    types = ["achieve","mantain","cease","query","perform"]
    
    def __init__(self, expression, typ="achieve"):
        self.type = typ
        self.expression = expression
        self.persistent = False
        self.priority = 0
        self.selected = False
        self.unreachable = False

    def testConflict(self, goal):
        # No conflict test at the moment
        return False
        
    def __str__(self):
        if self.unreachable:
            return "UNREACHABLE("+str(self.expression)+")"
        else:
            return str(self.expression)

    def __repr__(self):
       return self.__str__()

class Service:
    def __init__(self, P=None, Q=None):
        self.P = P #precondition
        self.Q = Q #postcontidion
        
        self.myAgent = None
 
    def setP(self, P): self.P = P

    def setQ(self, Q): self.Q = Q

    def getP(self): return self.P

    def getQ(self): return self.Q

    def reward(self):
        self.trust -= 1
        if self.trust<0: self.trust=0
        #print "Service "+self.name+" rewarded!"

    def punish(self):
        self.trust += 10
        if self.trust>1000: self.trust=1000
        #print "Service "+self.name+" punished!"
        
    def run(self):
        raise NotImplementedError
        
    def addBelieve(self,sentence):
        if self.myAgent:
            self.myAgent.addBelieve(sentence)
        else:
            raise NotImplementedError
    def removeBelieve(self,sentence):
        if self.myAgent:
            self.myAgent.removeBelieve(sentence)
        else:
            raise NotImplementedError
    def askBelieve(self,sentence):
        if self.myAgent:
            return self.myAgent.askBelieve(sentence)
        else:
            raise NotImplementedError
            
    def __str__(self):
        return "[P:"+str(self.P)+" Q:"+str(self.Q)+"]"

class Plan:
    def __init__(self, P=None, Q=None):
        self.P = P
        self.Q = Q
        
        self.myAgent = None
        
        self.services = []
        self.next = None
        
    def addOwner(self, owner):
        self.myAgent = owner
        for service in self.services:
            service.myAgent = owner
        
    def appendService(self, service):
        if len(self.services)>0:
            lastService = self.services[len(self.services)-1]
            out = copy(lastService.outputs.keys()).sort()
            ins = copy(service.inputs.keys()).sort()
        
            if out == ins:
                if self.myAgent:
                    service.myAgent = self.myAgent
                self.services.append(service)
        else:
            if self.myAgent:
                service.myAgent = self.myAgent
            self.services.append(service)
        
    def nextService(self):
        if self.next==None:
            self.next = 0
        elif self.next == len(self.services)-1:
            return None
        else:
            outs = self.services[self.next].outputs
            self.next += 1
            self.services[self.next].inputs.update(outs)

        if self.myAgent.askBelieve(self.services[self.next].P) != False:
            return self.services[self.next]
        else:
            raise PreconditionFailed()

    def __str__(self):
        s = "Plan(P:"+str(self.P)+" Q:"+str(self.Q)+") => "
        for i in range(len(self.services)):
            s+= "S"+str(i)+":"+str(self.services[i])+", "
        return s

class BDIAgent(Agent.Agent):
    
    def __init__(self,agentjid, password, port=5222, debug=[], p2p=False):
        Agent.Agent.__init__(self,agentjid, password, port=port, debug=debug, p2p=p2p)
        
        self.goals           = [] # active goals
        self.kb              = FolKB() # knowledge base
        self.plans           = [] # plan library
        self.intentions      = [] # selected plans for execution
        self.services        = [] # services offered by the agent
        
        self.defaultMailbox  = []
        
        self._needDeliberate = True
        
    def configureKB(self, typ, sentence=None, path=None):
        """
        Supported Knowledge Bases are: ["ECLiPSe", "Flora2", "SPARQL", "SWI", "XSB"]
        """
        try:
            if typ not in ["ECLiPSe", "Flora2", "SPARQL", "SWI", "XSB"]:
                raise KBConfigurationFailed(typ + " is not a valid KB.")
            if   typ=="SPARQL": import SPARQLKB
            elif typ=="XSB":    import XSBKB
            elif typ=="Flora2": import Flora2KB
            elif typ=="SWI":    import SWIKB
            elif typ=="ECLiPSe":import ECLiPSeKB
            else: raise KBConfigurationFailed("Could not import "+str(typ)+" KB.")

            typ+="KB"
            #module = eval("__import__("+typ+")")

            if path!=None:
                self.kb = eval(typ+"."+typ+"("+str(sentence)+", '"+path+"')")
            else:
                self.kb = eval(typ+"."+typ+"("+str(sentence)+")")
        except KBConfigurationFailed as e:
            self.DEBUG(str(e)+" Using Fol KB.", 'warn')
            self.kb = FolKB()
        
        
    def addBelieve(self, sentence, type="insert"):
        if isinstance(sentence,types.StringType):
            try:
                if issubclass(Flora2KB.Flora2KB,self.kb.__class__):
        		    self.kb.tell(sentence,type)
            except:
                if issubclass(FolKB, self.kb.__class__):
                    self.kb.tell(expr(sentence))
                else:
                	self.kb.tell(sentence)
        else:
        	self.kb.tell(sentence)
        self._needDeliberate = True
        self.newBelieveCB(sentence)
        
    def removeBelieve(self, sentence, type="delete"):
        if isinstance(sentence,types.StringType):
            try:
                if issubclass(Flora2KB.Flora2KB,self.kb.__class__):
        		    self.kb.retract(sentence,type)
            except:
                if issubclass(FolKB, self.kb.__class__):
                    self.kb.retract(expr(sentence))
                else:
                	self.kb.retract(sentence)
        else:
        	self.kb.retract(sentence)
        self._needDeliberate = True

    def askBelieve(self, sentence):
        if isinstance(sentence,types.StringType) and issubclass(FolKB, self.kb.__class__):
            return self.kb.ask(expr(sentence))
        else:
        	return self.kb.ask(sentence)
            
    def addPlan(self, plan):
        plan.addOwner(self)
        self.plans.append(plan)
        self.DEBUG("Plan added: "+str(plan),"ok")

    def addGoal(self, goal):
        #First add the goal if no conflicts
        if goal not in self.goals:
            conflict = False
            for g in self.goals:
                if g.testConflict(goal):
                    conflict = True
                    break
            if not conflict and self.askBelieve(goal.expression)==False:
                self.DEBUG("Goal added: "+str(goal),"ok")
                self.goals.append(goal)
            
    def selectIntentions(self):
        for goal in self.goals: #deliberate over goals
            if not goal.selected: #if the goal is not already selected for execution
                self.DEBUG("Found not selected goal")
                for plan in self.plans: #search for a plan
                    self.DEBUG("Compare plan.Q " + str(plan.Q) + " with goal " + str(goal.expression),"ok")
                    if plan.Q == goal.expression: #plan must pursue for the goal
                        #self.DEBUG("askBelieve plan.P -> " + str(self.askBelieve(plan.P)))
                        if self.askBelieve(plan.P)!=False: #preconditions of the plan must be acomplished
                            self.intentions.append(plan)   #instantiate plan as intention
                            self.intentionSelectedCB(plan)
                            goal.selected = True #flag goal as selected
                            break #stop searching plans for this goal
        
        
    def run(self):
        """
        periodic agent execution
        """
        #Init The agent
        self._setup()
        self.behavioursGo.acquire()
        self._running = True
        self.behavioursGo.notifyAll()
        self.behavioursGo.release()

        #Start the Behaviours
        #if (self._defaultbehaviour != None):
        #    self._defaultbehaviour.start()

        #If this agent supports P2P, wait for P2PBEhaviour to properly start
        if self.p2p:
            while not self.p2p_ready:
                time.sleep(0.1)

        #############
        # Main Loop #
        #############
        while not self.forceKill():
            try:
                #get and process all messages
                self.getMessages()
                
                #deliberate about current goals
                #self.DEBUG("deliberate about current goals")
                if self._needDeliberate:
                    for goal in copy(self.goals):
                        if self.askBelieve(goal.expression)!=False:
                            if goal.persistent:
                                goal.selected = False
                            else:
                                self.goals.remove(goal)
                            self.goalCompletedCB(goal)
                    #for intention in copy(self.intentions):
                    #    if self.bk.ask(intention.Q):
                    #        self.intentions.remove(intention)
                    self._needDeliberate = False
                    
                #select intentions
                #self.DEBUG("select intentions")
                self.selectIntentions()
                
                #run intentions
                #self.DEBUG("run intentions")
                for intention in copy(self.intentions):
                    service = intention.nextService()
                    
                    if service == None: #intention has finished
                        self.DEBUG("Intention finished: "+ str(intention),"ok")
                        self.intentions.remove(intention) #delete intention
                        if self.askBelieve(intention.Q)==False: #check its postcondition
                            raise PostConditionFailed()
                        else:
                            for goal in copy(self.goals): #delete the goal that raised the intention
                                if goal == intention.Q:
                                    if goal.persistent: #if goal is persistent, deselect it
                                        goal.selected = False
                                    else:
                                        self.goals.remove(goal)
                    else:
                        service.run()
                        if self.askBelieve(service.Q)==False:
                            raise PostConditionFailed()
                        else: self.serviceCompletedCB(service)
                    if self._needDeliberate: break
                
            except Exception, e:
                self.DEBUG("Agent " + self.getName() + " Exception in run: " + str(e), "err")
                self._kill()

        self._shutdown()
        
    def getMessages(self):
        #Check for queued messages
        proc = False
        msg = self._receive(block=True, timeout=0.01)
        if msg != None:
            bL = copy(self._behaviourList)
            for b in bL:
                t = bL[b]
                if (t != None):
                    if (t.match(msg) == True):
                        if ((b == types.ClassType or type(b) == types.TypeType) and issubclass(b, Behaviour.EventBehaviour)):
                            b = b()
                            b.setAgent(self)
                            b.postMessage(msg)
                            b.start()
                        else:
                            b.postMessage(msg)
                        proc = True

            if (proc == False):
                self.defaultMailbox.append(msg)
            #    #If no template matches, post the message to the Default behaviour
            #    if (self._defaultbehaviour != None):
            #        self._defaultbehaviour.postMessage(msg)

    def intentionSelectedCB(self, intention=None):
        #callback executed when a new intention is selected for execution
        #must be overloaded
        pass
    def goalCompletedCB(self, goal=None):
        #callback executed when a goal is completed succesfully
        #must be overloaded
        pass
    def serviceCompletedCB(self, service=None):
        #callback executed when a service is completed succesfully
        #must be overloaded
        pass
    def newBelieveCB(self, believe=None):
        #callback executed when a believe is added to the knowledge base
        #must be overloaded
        pass
