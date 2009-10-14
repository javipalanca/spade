from logic import *
from copy import copy
import types

#from spade import *
import Agent
import Behaviour

class PreConditionFailed (Exception): pass
class PostConditionFailed(Exception): pass

class Goal:
    
    types = ["achieve","mantain","cease","query","perform"]
    
    def __init__(self, expression, typ="achieve"):
        self.type = typ
        self.expression = expression
        self.persistent = False
        self.priority = 0
        self.selected = False

    def testConflict(self, goal):
        # No conflict test at the moment
        return False
        
    def __str__(self):
        return str(self.expression)

class Service:
    def __init__(self, P=None, Q=None, inputs={},outputs={}):
        self.P = P #precondition
        self.Q = Q #postcontidion
        self.inputs  = inputs
        self.outputs = outputs
        
        self.myAgent = None
            
        
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
        
        
    def addBelieve(self, sentence):
        if isinstance(sentence,types.StringType):
            self.kb.tell(expr(sentence))
        else:
            self.kb.tell(sentence)
        self._needDeliberate = True
        
    def removeBelieve(self, sentence):
        if isinstance(sentence,types.StringType):
            self.kb.retract(expr(sentence))
        else:
            self.kb.retract(sentence)
        self._needDeliberate = True

    def askBelieve(self, sentence):
        if isinstance(sentence,types.StringType):
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