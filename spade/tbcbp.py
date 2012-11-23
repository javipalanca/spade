# -*- coding: utf-8 -*-
import Queue
import time
import random
from odict import odict
from copy import copy, deepcopy
from uuid import uuid4
from math import sqrt, pow, ceil, log, floor
import math
import types

import dblite


class TimeOut(Exception):
    pass


class TooMuchPlans(Exception):
    pass


class CaseDB:
    def __init__(self):
        self.db = dblite.Base("caseDB")
        self.db.create("P", "Q", "inputs", "outputs", "case", mode="override")
        self.db.open()

    def add(self, case):
        P = sorted(case.getP())
        Q = sorted(case.getQ())
        I = sorted(case.getInputs())
        O = sorted(case.getOutputs())

        self.db.insert(P=P, Q=Q, inputs=I, outputs=O, case=case)

    def get(self, P=None, Q=None, inputs=None, outputs=None):
        res = []
        query = "self.db("
        if P is not None:
            query += "P=" + str(sorted(P)) + ","
        if Q is not None:
            query += "Q=" + str(sorted(Q)) + ","
        if inputs is not None:
            query += "inputs=" + str(sorted(inputs)) + ","
        if outputs is not None:
            query += "outputs=" + str(sorted(outputs))
        query += ")"
        for record in eval(query):
            res.append(record["case"])

        return res


class Case(dict):

    def __init__(self, P=[], Q=[], inputs=[], outputs=[], services=[], QoS=1, ID=None):
        dict.__init__(self)
        self.P = P
        self.Q = Q
        self.inputs = inputs
        self.outputs = outputs
        self.QoS = QoS
        self.services = services
        self.time = 0
        if ID is None:
            self.ID = str(uuid4())
        else:
            self.ID = ID

        self.rewards = 0
        self.punishments = 0
        self.executions = 0
        self.trust = 0

    def getID(self):
        return self.ID

    def getP(self):
        return self.P

    def getQ(self):
        return self.Q

    def getInputs(self):
        return self.inputs

    def getOutputs(self):
        return self.outputs

    def getQoS(self):
        return self.QoS

    def getTime(self):
        return self.time

    def reward(self):
        self.rewards += 1
        self.executions += 1
        self.trust = min(1.0, float(self.rewards) / float(self.executions))
        self.QoS = self.trust

    def punish(self):
        if self.rewards > 0:
            self.rewards -= 1
        self.punishments += 1
        self.executions += 1
        self.trust = max(0.0, float(self.rewards) / float(self.executions))
        self.QoS = self.trust

    def __add__(self, y):
        #if str(self.Q)!=str(y.getP()):
        for sentence in self.outputs:
            if sentence not in y.inputs:
                raise TypeError
        return Case(P=self.P, Q=y.getQ(), inputs=self.getInputs(), outputs=y.getOutputs(), services=self.services + y.services, QoS=self.QoS * y.QoS, ID=str(uuid4()))

    def __iadd__(self, y):
        self = self + y
        return self

    def __eq__(self, y):
        if not issubclass(y.__class__, Case):
            return False
        if self.services != y.services:
            return False
        #if self.P!=y.getP():
        if sorted(self.P) != sorted(y.P):
            return False
        #if self.Q!=y.getQ():
        if sorted(self.Q) != sorted(y.Q):
            return False
        if sorted(self.inputs) != sorted(y.inputs):
            return False
        if sorted(self.outputs) != sorted(y.outputs):
            return False
        return True

    def __ne__(self, y):
        return not self == y

    def __str__(self):
        return "{ID: " + self.ID + " P: " + str(self.P) + " Q: " + str(self.Q) + " I: " + str(self.inputs) + " O: " + str(self.outputs) + " SERVICES:" + str(self.services) + " QoS: " + str(self.QoS) + "}"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.services)


class Plan(dict):

    def __init__(self, cases):
        '''
        Creates a new plan composed of a list of cases
        Usage:
        cases: a list of cases with at least 1 case
        '''
        dict.__init__(self)

        if not isinstance(cases, types.ListType):
            raise TypeError
        if len(cases) <= 0:
            raise Exception("cases must have at least one case")

        self.P = (cases[0]).getP()
        self.Q = (cases[-1:][0]).getQ()
        self.inputs = (cases[0]).getInputs()
        self.outputs = (cases[-1:][0]).getOutputs()
        self.cases = cases

        self.active_case = 0
        self.active_service = -1

    def getP(self):
        return self.P

    def getQ(self):
        return self.Q

    def getInputs(self):
        return self.inputs

    def getOutputs(self):
        return self.outputs

    '''def match(self,P=[],Q=[]):
        if (P!=[] and sorted(P)==sorted(self.P)) and (Q!=[] and sorted(Q)==sorted(self.Q)): return True
        elif (P==None and Q==self.Q): return True
        elif (Q==None and P==self.P): return True
        else: return False
    '''

    def getActiveCase(self):
        return self.active_case

    def getNextService(self):
        if len(self.cases) <= 0:
            return None

        self.active_service += 1
        if self.active_service < len(self.cases[self.active_case].services):
            return self.cases[self.active_case].services[self.active_service]
        else:
            self.active_service = 0
            self.active_case += 1
            if self.active_case >= len(self.cases):
                self.active_case = 0
                self.active_service = -1
                return None
            return deepcopy(self.cases[self.active_case].services[self.active_service])

    def getCases(self):
        '''returns all the cases of the plan'''
        return self.cases

    def getCase(self):
        '''
        compose a new composite case by joining all the cases of the plan
        returns a Case
        '''
        if len(self.cases) == 0:
            return None
        case = self.cases[0]
        for c in self.cases[1:]: case += c
        return case

    def getServices(self):
        '''
        returns all the services of the cases that compose the plan
        returns a list of DF.Service
        '''
        services = []
        for c in self.cases:
            for s in c.services:
                services.append(s)
        return services

    def insertCase(self, case):
        '''
        inserts a new case at the beginning of the plan
        the outputs of the new case MUST match with the inputs of the plan
        returns the Plan with the new case added
        '''
        if sorted(case.getOutputs()) != sorted(self.inputs):
            raise Exception
        self.cases.insert(0, case)
        self.P = case.getP()
        self.inputs = case.getInputs()
        return self

    def getCasebyID(self, ID):
        for c in self.cases:
            if c.getID() == ID:
                return c
        return None

    def getTime(self):
        t = 0
        for case in self.cases:
            t += case.getTime()
        return t

    def getQoS(self):
        q = 1
        for case in self.cases:
            q = q * case.getQoS()
        return q

    def __len__(self):
        return len(self.cases)

    def __str__(self):
        return "{P: " + str(self.P) + " Q: " + str(self.Q) + " I: " + str(self.inputs) + " O: " + str(self.outputs) + " CASES: " + str(self.cases) + "}"

    def __repr__(self):
        return self.__str__()


class TBCBP:

    def __init__(self, rl={'maxth': 0.95, 'limit': 10000}):
        self.db = CaseDB()  # dict()
        self.services = dict()

        #RL values
        self.threshold = 0.0
        self.max_threshold = rl['maxth']
        self.limit_steps = rl['limit']
        self.steps = 1
        self.RLlimit = log(self.limit_steps)

    def getCaseTime(self, case):
        t = 0
        for name in case.services:
            t += self.services[name]["time"]
        return t

    def registerService(self, service, time=1, QoS=1):
        '''
        registers a DF.Service
        time and QoS parameters are optional
        '''
        name = service.getName()
        P = service.getP()
        Q = service.getQ()
        I = service.getInputs()
        O = service.getOutputs()
        self.services[name] = {'name': name, 's': service, "P": P, "Q": Q, "inputs": I, "outputs": O, "time": time, "QoS": QoS}

        case = Case(P=P, Q=Q, inputs=I, outputs=O, services=[name], QoS=QoS)
        case.time = time  # self.getCaseTime(case)
        self.addCase(case)

        return case
        #print "TBCBP::Service Registered: "+str(case)

    def delService(self, name):
        #TODO
        pass

    def getService(self, name):
        '''returns a DF.Service'''
        if name in self.services:
            #print color_red + str(self.services[name]['s']) + color_none
            #s = self.services[name]["s"](P=self.services[name]["P"],Q=self.services[name]["Q"],inputs=self.services[name]["inputs"],outputs=self.services[name]["outputs"],name=name)
            #return s
            return self.services[name]['s']
        return None

    def getServiceInfo(self, name):
        '''
        returns info of a service
        Usage:
        name - string with the name of the service
        returns a dict with the info of the service
        '''
        if name in self.services:
            return self.services[name]

    def addCase(self, case):
        '''
        inserts a new case in the case-base
        services of the case MUST be registered in the TBCBP
        '''
        for s in case.services:
            if s not in self.services.keys():
                return False
        case.time = self.getCaseTime(case)

        self.db.add(case)

        return True

    def addPlan(self, plan):
        case = plan.getCase()
        self.addCase(case)

    def getCases(self, P=None, Q=None, inputs=None, outputs=None):
        '''
        returns a list of cases where the P,Q,inputs and outputs match.
        it only compares parameters if they are not None
        '''
        return self.db.get(P, Q, inputs, outputs)

    def getCase(self, case):
        '''
        returns the case of the case-base whose parameters (P,Q,inputs and outputs) match with the 'case' parameters
        '''
        try:
            res = self.db.get(P=case.getP(), Q=case.getQ(), inputs=case.getInputs(), outputs=case.getOutputs())
        except:
            return None
        for r in res:
            if r.services == case.services:
                return r
        return None

    def getCaseOfService(self, name):
        '''
        returns the case that represents the service 'name' in the case-base
        Usage:
        name - string with the name of the service
        '''
        service = self.getService(name)
        if service is None:
            return None
        case = self.getCase(Case(P=service.getP(), Q=service.getQ(), inputs=service.getInputs(), outputs=service.getOutputs(), services=[name]))
        return case

    def planMatchesInKB(self, case, kb):
        '''
        returns True if all the Preconditions and Inputs of the case are true in the knowledge-base
        otherwise returns False
        Usage:
        case - the case that we want to compare. instance of Case
        kb   - the knowledge base of the agent. instance of kb.KB
        '''
        Preconditions_matched = True
        Inputs_matched = True
        for p in case.getP():
            if kb.ask(p) is False:
                Preconditions_matched = False
                break  # preconditions do not match
        for i in case.getInputs():
            if kb.get(i) is None:
                Inputs_matched = False
                break  # inputs do not match
        if Preconditions_matched and Inputs_matched:
            return True
        else:
            return False

    def composePlan(self, Goal, kb, tout=20, use_rl=True):

        #print "TBCBP::DB:: "+str(self.db)
        #print "TBCBP::SERVICES:: "+str(self.services)
        #print "TBCBP::composePlan::GOAL::"+str(Goal)+"::KB::"+str(kb.kb.clauses)+"::TOUT::"+str(tout)

        MAXPLANS = 1000

        results = []
        plans = Queue.Queue()

        t1 = time.time()

        try:
            try:
            #print "TBCBP::composePlan::getCases for "+str(Goal.expression)+" -> "+str(self.getCases(Q=[Goal.expression]))
                for case in self.getCases(Q=[Goal.expression]):  # .values():
                    if tout != -1 and (time.time() - t1) > tout:
                        raise TimeOut
                    #for case in cases:
                    new_plan = Plan(cases=[case])
                    #if Preconditions match and have all inputs, the plan is finished
                    if self.planMatchesInKB(case, kb):
                        results.append(new_plan)
                    else:
                        plans.put(new_plan)

                if tout != -1 and (time.time() - t1) > tout:
                    raise TimeOut
                if len(results) > MAXPLANS:
                    raise TooMuchPlans

                while plans.qsize() > 0:
                    if len(results) > MAXPLANS:
                        raise TooMuchPlans
                    p = plans.get()
                    for case in self.getCases(outputs=p.getInputs()):  # .values():
                        #for case in cases:
                        new_plan = deepcopy(p)
                        new_plan.insertCase(case)
                        if self.planMatchesInKB(new_plan, kb):
                        #if new_plan not in results:
                            results.append(new_plan)
                        else:
                            plans.put(new_plan)
                        if tout != -1 and (time.time() - t1) > tout:
                            raise TimeOut

            except TimeOut:
                pass
                #print "TIMEOUT!"
            except TooMuchPlans:
                pass
                #print "TOOMUCHPLANS!"

        finally:
            pass

        if results == []:
            #print "NO PLANS FOUND!"
            return None
        sumT = 0
        sumQ = 0
        for plan in results:
            sumT += plan.getTime()
            sumQ += plan.getQoS()

        #print "selecting best plan"
        plans = []
        exploit = odict()
        last = 0
        normalize = 10000

        best_plan = results[0]
        if sumT == 0:
            T = 0.0
        else:
            T = (1.0 / float(best_plan.getTime()) / float(sumT))
        if sumQ == 0:
            Q = 0.0
        else:
            Q = (float(best_plan.getQoS()) / float(sumQ))
        f = T + Q
        plans.append(best_plan)
        if int(f * normalize) > 0:
            exploit[int(f * normalize)] = best_plan
            last = int(f * normalize)

        for plan in results[1:]:
            if sumT == 0:
                T = 0.0
            else:
                T = (1.0 / float(plan.getTime()) / float(sumT))
            if sumQ == 0:
                Q = 0.0
            else:
                Q = (float(plan.getQoS()) / float(sumQ))
            if T + Q > f:
                best_plan = plan
                f = T + Q
            plans.append(plan)
            if int(last + (f * normalize)) > 0:
                exploit[int(last + (f * normalize))] = plan
                last = last + int(f * normalize)

        #mini reinforcement learning
        if use_rl:
            explore = random.random()
            if explore > self.threshold:
            #explore!
                best_plan = random.choice(plans)
            else:
                #exploit!
                if last == 0:
                    best_plan = random.choice(plans)
                else:
                    i = random.randint(1, last)
                    for k in exploit.keys():
                        if i <= k:
                            best_plan = exploit[k]
                            break

        #adjust threshold
        self.steps += 1
        if self.steps > self.limit_steps:
            self.threshold = self.max_threshold
        else:
            self.threshold = (self.max_threshold * log(self.steps)) / self.RLlimit

        self.addPlan(best_plan)
        return best_plan

    def retain(self, case, QoS=None):
        if QoS is not None:
            case.QoS = QoS

        c = self.getCase(case)
        if c:
            c.QoS = case.QoS

    def reward(self, c):
        case = self.getCase(c)
        if case is not None:
            case.reward()
            return case
        return False

    def punish(self, c):
        case = self.getCase(c)
        if case is not None:
            case.punish()
            return case
        return False
