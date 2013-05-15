# -*- coding: utf-8 -*-
import time

import sys
sys.path.append("..")

import spade

host = "127.0.0.1"


if __name__ == "__main__":
        jida = "a@" + host
        jidb = "b@" + host
        jidc = "c@" + host

        a = spade.Agent.Agent(jida, "secret")
        a.start()
        #a.setDebugToScreen()

        b = spade.Agent.Agent(jidb, "secret", "work")
        b.start()
        b2 = spade.Agent.Agent(jidb, "secret", "home")
        b2.start()
        #b.setDebugToScreen()

        c = spade.Agent.Agent(jidc, "secret", "travel")
        c.start()
        #c.setDebugToScreen()

        a.roster.acceptAllSubscriptions()
        b.roster.acceptAllSubscriptions()
        c.roster.acceptAllSubscriptions()
        b2.roster.acceptAllSubscriptions()
        b.roster.followbackAllSubscriptions()
        b2.roster.followbackAllSubscriptions()
        c.roster.followbackAllSubscriptions()
        a.roster.subscribe(jidb)
        a.roster.subscribe(jidc)
        
        a.wui.start()
        b.wui.start()
        b2.wui.start()
        c.wui.start()


        alive = True
        while alive:
            try:
                time.sleep(1)
            except:
                alive=False

        a.stop()
        b.stop()
        c.stop()
