# -*- coding: utf-8 -*-
from logic import *
import random

import Behaviour
import tbcbp
import DF
from FlexQueue import FlexQueue
from Queue import Queue


class PreConditionFailed (Exception):
    pass


class PostConditionFailed(Exception):
    pass


class ServiceFailed(Exception):
    pass


class Goal:

    types = ["achieve", "mantain", "cease", "query", "perform"]

    def __init__(self, expression, typ="achieve"):
        self.type = typ
        self.expression = expression
        self.persistent = False
        self.priority = 0
        self.selected = False
        self.unreachable = False
        self.done = False

    def testConflict(self, goal):
        # No conflict test at the moment
        return False

    def __str__(self):
        if self.unreachable:
            return "UNREACHABLE(" + str(self.expression) + ")"
        elif self.done:
            return "DONE(" + str(self.expression) + ")"
        else:
            return str(self.expression)

    def __repr__(self):
        return self.__str__()


class PlanList(dict):
    #plans hash table. PID is the PlanID
    def add(self, plan):
        pid = random.randint(1, 100000000)
        while pid in self:
            pid = random.randint(1, 100000000)
        self[pid] = plan
        plan.pid = pid
        return pid


#class BDIAgent(Agent.Agent):
class BDIBehaviour(Behaviour.PeriodicBehaviour):

    #def __init__(self,agentjid, password, port=5222, debug=[], p2p=False):
    #    Agent.Agent.__init__(self,agentjid, password, port=port, debug=debug, p2p=p2p)
    def __init__(self, period):
        Behaviour.PeriodicBehaviour.__init__(self, period)
        self.goals = []  # active goals
        self.plans = PlanList()  # plan library
        self.intentions = []  # selected plans for execution
        #self.services        = [] # services offered by the agent
        self.TBCBP = tbcbp.TBCBP()
        self.active_goals = FlexQueue()
        self.prepared_goals = FlexQueue()
        self.scheduler = Queue()

        self._needDeliberate = True

    def configureKB(self, typ, sentence=None, path=None):
        self.myAgent.kb.configure(typ, sentence, path)

    def addBelieve(self, sentence, type="insert"):
        self.myAgent.addBelieve(sentence, type)
        self._needDeliberate = True

    def removeBelieve(self, sentence, type="delete"):
        self.myAgent.removeBelieve(sentence, type)

    def askBelieve(self, sentence):
        return self.myAgent.askBelieve(sentence)

    def saveFact(self, name, sentence):
        self.myAgent.kb.set(name, sentence)
        self._needDeliberate = True

    def getFact(self, name):
        return self.myAgent.kb.get(name)

    def addPlan(self, P, Q, inputs, outputs, services):
        '''Adds a new plan to the Planner (TBCBP)
        Usage: addPlan (P, Q, services)
        P - precondition of the plan
        Q - postcondition of the plan
        services - list of services names (strings)

        Return: None'''
        cases = []
        for s in services:
            c = self.TBCBP.getCaseOfService(str(s))
            if c is None:
                self.myAgent.DEBUG("Plan was not added. Service " + str(s) + " does not exist.", "err", 'bdi')
                return False
            cases.append(c)

        plan = tbcbp.Plan(cases)
        self.TBCBP.addPlan(plan)
        self.myAgent.DEBUG("Plan added: " + str(plan), "ok", 'bdi')
        self._needDeliberate = True
        return True

    def addGoal(self, goal):
        #First add the goal if no conflicts
        if goal not in self.goals:
            conflict = False
            for g in self.goals:
                if g.testConflict(goal):
                    conflict = True
                    break
            if not conflict and self.askBelieve(goal.expression) is False:
                self.myAgent.DEBUG("Goal added: " + str(goal), "ok", 'bdi')
                self.goals.append(goal)
                self._needDeliberate = True

    def registerServiceInTBCBP(self, service, time=1):
        '''Registers new service in the Planner (TBCBP)
        Usage: registerService(service, time)
        service - A DF.Service class
        time    - the estimated execution time of the service (optional)

        Returns: None'''

        self.TBCBP.registerService(service=service, time=time)
        self._needDeliberate = True

    def unregisterServiceInTBCBP(self, name=None, service=None):
        if not name:
            name = service.getName()
        self.TBCBP.delService(name)
        self._needDeliberate = True

    def getPlan(self, goal):
        '''Finds a plan for a specified goal.
        If there is not an existing plan, it composes a new one (when possible)
        Usage getPlan( goal )
        goal - a Goal object to be achieved

        Returns: TBCBP.Plan object or None is there is no available plan'''

        self.myAgent.DEBUG("Composing a plan for goal " + str(goal), 'info', 'bdi')
        plan = self.composePlan(goal)

        if plan is None:
            #goal is unreachable
            self.myAgent.DEBUG("No plan found for Goal " + str(goal), 'warn', 'bdi')
            return None

        plan['index'] = 0
        plan['goal'] = goal
        plan.agent_owner = self.myAgent
        return plan

    def composePlan(self, goal, tout=-1):
        '''
        calls the Temporal-Bounded Case Based Planner
        '''
        return self.TBCBP.composePlan(goal, self.myAgent.kb, tout=20)

    def selectIntentions(self):
        '''
        Prepares new plan for active goals
        Looks for all prepared goals and selects a new plan for it.
        then the goal is archived in prepared_goals
        and the plan is stored in self.plans
        '''

        #while not self.prepared_goals.empty(): #return
        goal = self.prepared_goals.get()
        self.myAgent.DEBUG("Got goal " + str(goal), 'info', 'bdi')

        if goal is not None:
            if self.askBelieve(goal.expression) is True:
                goal.done = True
                return None  # continue
            if goal in self.active_goals:
                return None  # continue

            self.myAgent.DEBUG("Activate Goal: " + str(goal), 'info', 'bdi')
            plan = self.getPlan(goal)
            if plan is not None:
                #activate plan
                self.myAgent.DEBUG("Got a plan for goal " + str(goal), 'info', 'bdi')
                goal.selected = True
                self.active_goals.put(goal)
                plan.agent = self
                #init plan
                pid = self.plans.add(plan)
                #activate first service
                self.insertNextService(plan, pid)
                self.planSelectedCB(plan)
            else:
                goal.unreachable = True
                self.myAgent.DEBUG("Goal is Unreachable: " + str(goal), 'warn', 'bdi')
                return None

    def insertNextService(self, plan, pid):
        '''Selects the next service of a plan to be executed
        Usage: insertNextService( plan, pid)
        plan - the running plan (TBCBP.Plan)
        pid  - the plan identifier'''

        service_name = plan.getNextService()
        self.myAgent.DEBUG("next service is " + str(service_name), 'info', 'bdi')
        if service_name is None:
            self.EndPlan(pid, plan)
            return
        service = self.TBCBP.getService(service_name)
        if service:
            service.pid = pid
            service.agent_owner = self

            self.scheduler.put(service)

        else:  # plan has finished
            self.EndPlan(pid, plan)

    def EndPlan(self, pid, plan):
        '''Finishes the execution of a plan.
        If the plan run well, its case is rewarded. Otherwise, it is punished.
        Finally goal is setted as done and not active.
        Usage: EndPlan ( pid, plan)
        pid  - Plan identifier
        plan - TBCBP.Plan object
        '''
        del self.plans[pid]
        #check its postcondition
        if len(plan.getQ()) > 0 and self.askBelieve(plan.getQ()[0]) is False:
            #logging.error(color_red+"PLAN FAILED "+str(plan)+color_none)
            self.TBCBP.punish(plan.getCase())
            for goal in self.goals:  # deselect the goal that raised the plan
                if goal.expression == plan.getQ():
                    goal.selected = False
                    goal.done = False
                    self.active_goals.remove(goal)
        else:
            self.TBCBP.reward(plan.getCase())
            self.myAgent.DEBUG("Rewarding Plan", 'ok', 'bdi')
            for goal in self.goals:  # delete the goal that raised the intention
                if goal.expression in plan.getQ():
                    if goal.persistent:  # if goal is persistent, deselect it
                        self.prepared_goals.put(goal)
                    self.active_goals.remove(goal)
                    goal.done = True
                    goal.selected = False
                    self.myAgent.DEBUG("Goal " + str(goal.expression) + " was completed!", 'ok', 'bdi')
                    self.myAgent.DEBUG("Calling goal completed CB: " + str(self.goalCompletedCB), 'info', 'bdi')
                    self.goalCompletedCB(goal)

    def EndService(self, service, plan):
        '''Finishes the execution of a service.
        If the service failed, it is punished and the plan is finished.
        Otherwise, the next service of the plan is selected.
        Usage: EndService ( service, plan)
        service - the current running DF.Service
        plan    - the TBCBP.Plan where the service belongs
        '''

        agent = self
        pid = plan.pid
        #service has been executed
        if len(service.getQ()) > 0 and self.askBelieve(service.getQ()[0]) is False:
            #service failed
            self.myAgent.DEBUG("Service execution failed: " + str(service.getQ()))
            self.punishService(service)
            #cancel plan and reactivate goal
            self.EndPlan(pid, plan)
            return

        #5.2.1 select next service
        self.insertNextService(plan, pid)

        self.serviceCompletedCB(service)

    def deliberate(self):
        self.myAgent.DEBUG("deliberate about current goals: " + str(self.goals), 'info', 'bdi')
        for goal in self.goals:
            if (goal.unreachable is False) and (goal.done is False):  # or ((goal.done==True) and (goal.persistent==True))):
                if self.askBelieve(goal.expression) is False:
                    self.myAgent.DEBUG("Deliberate about " + str(goal), 'info', 'bdi')
                    if goal not in self.active_goals:
                        self.prepared_goals.put(goal)
                else:
                    self.myAgent.DEBUG("Goal " + str(goal) + "is already in the KB: " + str(self.askBelieve(goal.expression)), 'warn', 'bdi')
                    goal.done = True

    def discover(self):
        #TODO: use PubSub features
        s = DF.Service()
        results = self.myAgent.searchService(s)
        if results is not None:
            self.myAgent.DEBUG("Discovered " + str(len(results)) + " services.", 'info', 'bdi')
            for service in results:
                if self.TBCBP.getService(service.getName()) is None:
                    self.registerServiceInTBCBP(service)

    def punishService(self, service):
        P = service.getP()
        Q = service.getQ()
        I = service.getInputs()
        O = service.getOutputs()
        self.TBCBP.punish(tbcbp.Case(P=P, Q=Q, inputs=I, outputs=O, services=[service.getName()]))
        return

        ####Init The agent
        ###self._setup()
        ###self.behavioursGo.acquire()
        ###self._running = True
        ###self.behavioursGo.notifyAll()
        ###self.behavioursGo.release()
        #############
        # Main Loop #
        #############
        ###while not self.forceKill():
        ###    try:
        ###        #get and process all messages
        ###        self.getMessages()
    def _onTick(self):
        """
        periodic behaviour execution
        """
        #discover new services
        self.myAgent.DEBUG("Discover new services...", 'info', 'bdi')
        self.discover()

        #deliberate about current goals
        #if self._needDeliberate:
        self.myAgent.DEBUG("Deliberating...", 'info', 'bdi')
        self.deliberate()
        #self._needDeliberate = False

        #select intentions
        self.DEBUG("select intentions", 'info', 'bdi')
        self.selectIntentions()

        self.myAgent.DEBUG("Init scheduler", 'info', 'bdi')
        #run a service each iteration
        if not self.scheduler.empty():
            service = self.scheduler.get()
            self.myAgent.DEBUG("Got service for execution: " + str(service), 'info', 'bdi')

            #if service!=None:
            pid = service.pid
            plan = self.plans[pid]
            try:
                result = self.myAgent.invokeService(service)
            except:
                self.myAgent.DEBUG("Service failed!", 'warn', 'bdi')

            self.EndService(service, plan)
        else:
            self.myAgent.DEBUG("NOP", 'info', 'bdi')

        self.myAgent.DEBUG("Restarting BDI cycle", 'info', 'bdi')

    def planSelectedCB(self, plan):
        #callback executed when a new plan is selected for execution
        #must be overloaded
        pass

    def goalCompletedCB(self, goal):
        #callback executed when a goal is completed succesfully
        #must be overloaded
        pass

    def serviceCompletedCB(self, service):
        #callback executed when a service is completed succesfully
        #must be overloaded
        pass
