Jak stworzyć własny plugin rozszerzający obiekty Message i Iq w Slixmpp
========================================================================

Wstęp i wymagania
------------------

* `'python3'`

Kod użyty w tutorialu jest kompatybilny z pythonem w wersji 3.6 lub nowszej.
Dla uzyskania kompatybilności z wcześniejszymi wersjami należy zastąpić f-strings starszym formatowaniem napisów `'"{}".format("content")'` lub `'%s, "content"'`.

Instalacja dla Ubuntu linux:

.. code-block:: bash

    sudo apt-get install python3.6

* `'slixmpp'`
* `'argparse'`
* `'logging'`
* `'subprocess'`

Wszystkie biblioteki wymienione powyżej, za wyjątkiem slixmpp, należą do standardowej biblioteki pythona. Zdarza się, że kompilując źródła samodzielnie, część z nich może nie zostać zainstalowana.

.. code-block:: python

    python3 --version
    python3 -c "import slixmpp; print(slixmpp.__version__)"
    python3 -c "import argparse; print(argparse.__version__)"
    python3 -c "import logging; print(logging.__version__)"
    python3 -m subprocess

Wynik w terminalu:

.. code-block:: bash

    ~ $ python3 --version
    Python 3.8.0
    ~ $ python3 -c "import slixmpp; print(slixmpp.__version__)"
    1.4.2
    ~ $ python3 -c "import argparse; print(argparse.__version__)"
    1.1
    ~ $ python3 -c "import logging; print(logging.__version__)"
    0.5.1.2
    ~ $ python3 -m subprocess # Nie powinno nic zwrócić

Jeśli któraś z bibliotek zwróci `'ImportError'` lub `'no module named ...'`, należy je zainstalować zgodnie z przykładem poniżej:

Instalacja Ubuntu linux:

.. code-block:: bash

    pip3 install slixmpp
    #or
    easy_install slixmpp

Jeśli jakaś biblioteka zwróci NameError, należy zainstalować pakiet ponownie.

* `Konta dla Jabber`

Do testowania niezbędne będą dwa prywatne konta jabbera. Można je stworzyć na jednym z dostępnych darmowych serwerów:
https://www.google.com/search?q=jabber+server+list

Skrypt uruchamiający klientów
------------------------------

Skrypt pozwalający testować klientów powinien zostać stworzony poza lokalizacją projektu. Pozwoli to szybko sprawdzać wyniki skryptów oraz uniemożliwi przypadkowe wysłanie swoich danych na gita.

Przykładowo, można stworzyć plik o nazwie `'test_slixmpp'` w lokalizacji `'/usr/bin'` i nadać mu uprawnienia wykonawcze:

.. code-block:: bash

    /usr/bin $ chmod 711 test_slixmpp

Plik zawiera prostą strukturę, która pozwoli nam zapisać dane logowania.

.. code-block:: python

    #!/usr/bin/python3
    #File: /usr/bin/test_slixmpp & permissions rwx--x--x (711)

    import subprocess
    import time

    if __name__ == "__main__":
        #~ prefix = ["x-terminal-emulator", "-e"] # Osobny terminal dla kazdego klienta, może być zastąpiony inną konsolą.
        #~ prefix = ["xterm", "-e"]
        prefix = []
        #~ suffix = ["-d"] # Debug
        #~ suffix = ["-q"] # Quiet
        suffix = []

        sender_path = "./example/sender.py"
        sender_jid = "SENDER_JID"
        sender_password = "SENDER_PASSWORD"

        example_file = "./test_example_tag.xml"

        responder_path = "./example/responder.py"
        responder_jid = "RESPONDER_JID"
        responder_password = "RESPONDER_PASSWORD"

        # Remember about the executable permission. (`chmod +x ./file.py`)
        SENDER_TEST = prefix + [sender_path, "-j", sender_jid, "-p", sender_password, "-t", responder_jid, "--path", example_file] + suffix
        RESPON_TEST = prefix + [responder_path, "-j", responder_jid, "-p", responder_password] + suffix

        try:
            responder = subprocess.Popen(RESPON_TEST)
            sender = subprocess.Popen(SENDER_TEST)
            responder.wait()
            sender.wait()
        except:
            try:
                responder.terminate()
            except NameError:
                pass
            try:
                sender.terminate()
            except NameError:
                pass
            raise

Skrypt uruchamiający powinien być dostosowany do potrzeb urzytkownika: można w nim pobierać ścieżki do projektu z linii komend (przez `'sys.argv[...]'` lub `'os.getcwd()'`), wybierać z jaką flagą mają zostać uruchomione programy oraz wiele innych. Jego należyte przygotowanie pozwoli zaoszczędzić czas i nerwy podczas późniejszych prac.

W przypadku testowania większych aplikacji, w tworzeniu pluginu szczególnie użyteczne jest nadanie unikalnych nazwy dla każdego klienta (w konsekwencji: różne linie poleceń). Pozwala to szybko określić, który klient co zwraca, bądź który powoduje błąd.

Stworzenie klienta i pluginu
-----------------------------

W stosownej dla nas lokalizacji powinniśmy stworzyć dwa klienty slixmpp (w przykładach: `'sender'` i `'responder'`), aby sprawdzić czy skrypt uruchamiający działa poprawnie. Poniżej przedstawiona została minimalna niezbędna implementacja, która może testować plugin w trakcie jego projektowania:

.. code-block:: python

    #File: $WORKDIR/example/sender.py
    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
		        # Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online.
            self.send_presence()
            self.get_roster()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        #xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin jest nazwą klasy example_plugin.

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

.. code-block:: python

    #File: $WORKDIR/example/responder.py
    import logging
    from argparse import ArgumentParser
    from getpass import getpass

    import asyncio
    import slixmpp
    import example_plugin

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)

        def start(self, event):
			# Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online
            self.send_presence()
            self.get_roster()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Responder.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message to")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Responder(args.jid, args.password)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin jest nazwą klasy example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

Następny plik, który należy stworzyć to `'example_plugin'`. Powinien być w lokalizacji dostępnej dla klientów (domyślnie w tej samej, co skrypty klientów).

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py
    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ Napis czytelny dla człowieka i dla znalezienia pluginu przez inny plugin
            self.xep = "ope"                                        ##~ Napis czytelny dla człowieka i dla znalezienia pluginu przez inny plugin poprzez dodanie tego do `slixmpp/plugins/__init__.py`, w polu `__all__` z prefixem xep 'xep_OPE'.

            namespace = ExampleTag.namespace


    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ Nazwa głównego pliku XML w tym rozszerzeniu.
        namespace = "https://example.net/our_extension"             ##~ Namespace obiektu jest definiowana w tym miejscu, powinien się odnosić do nazwy portalu xmpp; w wiadomości wygląda tak: <example_tag xmlns={namespace} (...)</example_tag>

        plugin_attrib = "example_tag"                               ##~ Nazwa pod którą można odwoływać się do danych zawartych w tym pluginie. Bardziej szczegółowo: tutaj rejestrujemy nazwę obiektu by móc się do niego odwoływać z zewnątrz. Można się do niego odwoływać jak do słownika: stanza_object['example_tag'], gdzie `'example_tag'` jest nazwą pluginu i powinno być takie samo jak name.

        interfaces = {"boolean", "some_string"}                     ##~ Zbiór kluczy dla słownika atrybutów elementu które mogą być użyte w elemencie. Na przykład `stanza_object['example_tag']` poda informacje o: {"boolean": "some", "some_string": "some"}, tam gdzie `'example_tag'` jest elementu.

Jeżeli powyższy plugin nie jest w domyślnej lokalizacji, a klienci powinni pozostać poza repozytorium, możemy w miejscu klientów dodać dowiązanie symboliczne do lokalizacji pluginu:

.. code-block:: bash

    ln -s $Path_to_example_plugin_py $Path_to_clients_destinations

Jeszcze innym wyjściem jest import relatywny z użyciem kropek '.' aby dostać się do właściwej ścieżki.

Pierwsze uruchomienie i przechwytywanie zdarzeń
-------------------------------------------------

Aby sprawdzić czy wszystko działa prawidłowo, można użyć metody `'start'`. Jest jej przypisane zdarzenie `'session_start'`. Sygnał ten zostanie wysłany w momencie, w którym klient będzie gotów do działania. Stworzenie własnej metoda pozwoli na zdefiniowanie działania tego sygnału.

W metodzie `'__init__'` zostało stworzone przekierowanie zdarzenia `'session_start'`. Kiedy zostanie on wywołany, metoda `'def start(self, event):'` zostanie wykonana. Jako pierwszy krok procesie tworzenia, można dodać linię `'logging.info("I'm running")'` w obu klientach (sender i responder), a następnie użyć komendy `'test_slixmpp'`.

Metoda `'def start(self, event):'` powinna wyglądać tak:

.. code-block:: python

    def start(self, event):
        # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
        self.send_presence()
        self.get_roster()

        #>>>>>>>>>>>>
        logging.info("I'm running")
        #<<<<<<<<<<<<

Jeżeli oba klienty uruchomiły się poprawnie, można zakomentować tą linię.

Budowanie obiektu Message
-------------------------

Wysyłający powinien posiadać informację o tym, do kogo należy wysłać wiadomość. Nazwę i ścieżkę odbiorcy można przekazać, na przykład, przez argumenty wywołania skryptu w linii komend. W poniższym przykładzie, są one trzymane w atrybucie `'self.to'`.

Przykład:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
        # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
            self.send_presence()
            self.get_roster()
            #>>>>>>>>>>>>
            self.send_example_message(self.to, "example_message")

        def send_example_message(self, to, body):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Domyślnie mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            msg.send()
            #<<<<<<<<<<<<

W przykładzie powyżej, używana jest wbudowana metoda `'make_message'`, która tworzy wiadomość o treści `'example_message'` i wysyła ją pod koniec działania metody start. Czyli: wiadomość ta zostanie wysłana raz, zaraz po uruchomieniu skryptu.

Aby otrzymać tę wiadomość, responder powinien wykorzystać odpowiednie zdarzenie: metodę, która określa co zrobić, gdy zostanie odebrana wiadomość której nie zostało przypisane żadne inne zdarzenie. Przykład takiego kodu:

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)

            #>>>>>>>>>>>>
            self.add_event_handler("message", self.message)
            #<<<<<<<<<<<<

        def start(self, event):
        # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
            self.send_presence()
            self.get_roster()

        #>>>>>>>>>>>>
        def message(self, msg):
            #Pokazuje cały XML wiadomości
            logging.info(msg)
            #Pokazuje wyłącznie pole 'body' wiadomości
            logging.info(msg['body'])
        #<<<<<<<<<<<<

Rozszerzenie Message o nowy tag
--------------------------------

Aby rozszerzyć obiekt Message o wybrany tag, plugin powinien zostać zarejestrowany jako rozszerzenie dla obiektu Message:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin.
            self.xep = "ope"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin przez dodanie go do `slixmpp/plugins/__init__.py` w metodzie  `__all__` z 'xep_OPE'.

            namespace = ExampleTag.namespace
            #>>>>>>>>>>>>
            register_stanza_plugin(Message, ExampleTag)             ##~ Zarejestrowany rozszerzony tag dla obiektu Message. Jeśli to nie zostanie zrobione, message['example_tag'] będzie polem tekstowym, a nie rozszerzeniem i nie będzie mogło zawierać atrybutów i pod-elementów.
            #<<<<<<<<<<<<

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ Nazwa głównego pliku XML dla tego rozszerzenia..
        namespace = "https://example.net/our_extension"             ##~ Nazwa obiektu, np. <example_tag xmlns={namespace} (...)</example_tag>. Powinna zostać zmieniona na własną.

        plugin_attrib = "example_tag"                               ##~ Nazwa, którą można odwołać się do obiektu. W szczególności, do zarejestrowanego obiektu można odwołać się przez: nazwa_obiektu['tag']. gdzie `'tag'` jest nazwą ElementBase extension. Nazwa powinna być taka sama jak "name" wyżej.

        interfaces = {"boolean", "some_string"}                     ##~ Lista kluczy słownika, które mogą być użyte z obiektem. Na przykład: `stanza_object['example_tag']` zwraca {"another": "some", "data": "some"}, gdzie `'example_tag'` jest nazwą rozszerzenia ElementBase.

        #>>>>>>>>>>>>
        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string
        #<<<<<<<<<<<<

Teraz, po rejestracji tagu, można rozszerzyć wiadomość.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
            self.send_presence()
            self.get_roster()
            self.send_example_message(self.to, "example_message")

        def send_example_message(self, to, body):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Default mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            #>>>>>>>>>>>>
            msg['example_tag']['some_string'] = "Work!"
            logging.info(msg)
            #<<<<<<<<<<<<
            msg.send()

Po uruchomieniu, obiekt logging powinien wyświetlić Message wraz z tagiem `'example_tag'` zawartym w środku <message><example_tag/></message>, oraz z napisem `'Work'` i nadaną przestrzenią nazw.

Nadanie oddzielnego sygnału dla rozszerzonej wiadomości
--------------------------------------------------------

Jeśli zdarzenie nie zostanie sprecyzowane, to zarówno rozszerzona jak i podstawowa wiadomość będą przechwytywane przez sygnał `'message'`. Aby nadać im oddzielne zdarzenie, należy zarejestrować odpowiedni uchwyt dla przestrzeni nazw i tagu, aby stworzyć unikalną kombinację, która pozwoli na przechwycenie wyłącznie pożądanych wiadomości (lub Iq object).

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin.
            self.xep = "ope"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin przez dodanie go do `slixmpp/plugins/__init__.py` w metodzie  `__all__` z 'xep_OPE'.

            namespace = ExampleTag.namespace

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Nazwa tego Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Przechwytuje wyłącznie Message z tagiem example_tag i przestrzenią nazw taką, jaką zdefiniowaliśmy w ExampleTag
                        self.__handle_message))                     ##~ Metoda do której zostaje przypisany przechwycony odpowiedni obiekt, powinna wywołać odpowiedni dla klienta wydarzenie.
            register_stanza_plugin(Message, ExampleTag)             ##~ Zarejestrowany rozszerzony tag dla obiektu Message. Jeśli to nie zostanie zrobione, message['example_tag'] będzie polem tekstowym, a nie rozszerzeniem i nie będzie mogło zawierać atrybutów i pod-elementów.

        def __handle_message(self, msg):
            # Tu można coś zrobić z przechwyconą wiadomością zanim trafi do klienta.
            self.xmpp.event('example_tag_message', msg)          ##~ Wywołuje zdarzenie, które może zostać przechwycone i obsłużone przez klienta, jako argument przekazujemy obiekt który chcemy dopiąć do wydarzenia.

Obiekt StanzaPath powinien być poprawnie zainicjalizowany, według schematu:
`'NAZWA_OBIEKTU[@type=TYP_OBIEKTU][/{NAMESPACE}[TAG]]'`

* Dla NAZWA_OBIEKTU można użyć `'message'` lub `'iq'`.
* Dla TYP_OBIEKTU, jeśli obiektem jest iq, można użyć typu spośród: `'get, set, error or result'`. Jeśli obiektem jest Message, można sprecyzować typ np. `'chat'`..
* Dla NAMESPACE powinna to byc przestrzeń nazw zgodna z rozszerzeniem tagu.
* TAG powinien zawierać tag, tutaj: `'example_tag'`.

Teraz program przechwyci wszystkie wiadomości typu message, które zawierają sprecyzowaną przestrzeń nazw wewnątrz `'example_tag'`. Można też sprawdzić co Message zawiera, czy na pewno posiada wymagane pola itd. Następnie wiadomość jest wysyłana do klienta za pośrednictwem wydarzenia `'example_tag_message'`.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)

        def start(self, event):
            # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
            self.send_presence()
            self.get_roster()
            #>>>>>>>>>>>>
            self.send_example_message(self.to, "example_message", "example_string")

        def send_example_message(self, to, body, some_string=""):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            # Default mtype == "chat";
            msg = self.make_message(mto=to, mbody=body)
            if some_string:
                msg['example_tag'].set_some_string(some_string)
            msg.send()
            #<<<<<<<<<<<<

Należy zapamiętać linię: `'self.xmpp.event('example_tag_message', msg)'`. W tej linii została zdefiniowana nazwa zdarzenia do przechwycenia wewnątrz pliku "responder.py". Tutaj to: `'example_tag_message'`.

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_message", self.example_tag_message) # Rejestracja uchwytu
            #<<<<<<<<<<<<

        def start(self, event):
            # Metody niewymagane, ale pozwalające na zobaczenie dostępności online.
            self.send_presence()
            self.get_roster()

        #>>>>>>>>>>>>
        def example_tag_message(self, msg):
            logging.info(msg) # Message jest obiektem który nie wymaga wiadomości zwrotnej, ale nic się nie stanie, gdy zostanie wysłana.
        #<<<<<<<<<<<<

Można odesłać wiadomość, ale nic się nie stanie jeśli to nie zostanie zrobione.
Natomiast obiekt komunikacji (Iq) już będzie wymagał odpowiedzi, więc obydwaj klienci powinni pozostawać online. W innym wypadku, klient otrzyma automatyczny error z powodu timeoutu, jeśli cell Iq nie odpowie za pomocą Iq o tym samym Id.

Użyteczne metody i inne
------------------------

Modyfikacja przykładowego obiektu `Message` na obiekt `Iq`
----------------------------------------------------------

Aby przerobić przykładowy obiekt Message na obiekt Iq, należy zarejestrować nowy uchwyt (handler) dla Iq, podobnie jak zostało to przedstawione w rozdziale `,,Rozszerzenie Message o tag''`. Tym razem, przykład będzie zawierał kilka rodzajów Iq o oddzielnych typami. Poprawia to czytelność kodu oraz usprawnia weryfikację poprawności działania. Wszystkie Iq powinny odesłać odpowiedź z tym samym Id i odpowiedzią do wysyłającego. W przeciwnym wypadku, wysyłający dostanie Iq zwrotne typu error.

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin.
            self.xep = "ope"                 ##~ Napis zrozumiały dla ludzi oraz do znalezienia pluginu przez inny plugin przez dodanie go do `slixmpp/plugins/__init__.py` w metodzie  `__all__` z 'xep_OPE'.

            namespace = ExampleTag.namespace
            #>>>>>>>>>>>>
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Nazwa tego Callbacka
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Obsługuje tylko Iq o typie 'get' oraz example_tag
                        self.__handle_get_iq))                      ##~ Metoda obsługująca odpowiednie Iq, powinna wywołać zdarzenie dla klienta.

            self.xmpp.register_handler(
                        Callback('ExampleResult Event:example_tag', ##~ Nazwa tego Callbacka
                        StanzaPath(f"iq@type=result/{{{namespace}}}example_tag"),   ##~ Obsługuje tylko Iq o typie 'result' oraz example_tag
                        self.__handle_result_iq))                   ##~ Metoda obsługująca odpowiednie Iq, powinna wywołać zdarzenie dla klienta.

            self.xmpp.register_handler(
                        Callback('ExampleError Event:example_tag',  ##~ Nazwa tego Callbacka
                        StanzaPath(f"iq@type=error/{{{namespace}}}example_tag"),    ##~ Obsługuje tylko Iq o typie 'error' oraz example_tag
                        self.__handle_error_iq))                    ##~ Metoda obsługująca odpowiednie Iq, powinna wywołać zdarzenie dla klienta.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Nazwa tego Callbacka
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Obsługuje tylko Iq z example_tag
                        self.__handle_message))                     ##~ Metoda obsługująca odpowiednie Iq, powinna wywołać zdarzenie dla klienta.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Rejestruje rozszerzenie taga dla obiektu Iq. W przeciwnym wypadku, Iq['example_tag'] będzie polem string zamiast kontenerem.
            #<<<<<<<<<<<<
            register_stanza_plugin(Message, ExampleTag)                  ##~ Rejestruje rozszerzenie taga dla obiektu Message. W przeciwnym wypadku, message['example_tag'] będzie polem string zamiast kontenerem.

            #>>>>>>>>>>>>
        # Wszystkie możliwe typy Iq to: get, set, error, result
        def __handle_get_iq(self, iq):
            # Zrób coś z otrzymanym iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Wywołuje zdarzenie, który może być obsłużony przez klienta lub inaczej.

        def __handle_result_iq(self, iq):
            # Zrób coś z otrzymanym Iq
            self.xmpp.event('example_tag_result_iq', iq)           ##~ Wywołuje zdarzenie, który może być obsłużony przez klienta lub inaczej.

        def __handle_error_iq(self, iq):
            # Zrób coś z otrzymanym Iq
            self.xmpp.event('example_tag_error_iq', iq)           ##~ Wywołuje zdarzenie, który może być obsłużony przez klienta lub inaczej.

        def __handle_message(self, msg):
            # Zrób coś z otrzymaną wiadomością
            self.xmpp.event('example_tag_message', msg)           ##~ Wywołuje zdarzenie, który może być obsłużony przez klienta lub inaczej.

Wydarzenia wywołane przez powyższe uchwyty mogą zostać przechwycone tak, jak w przypadku wydarzenia `'example_tag_message'`.

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_message", self.example_tag_message)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_get_iq", self.example_tag_get_iq)
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def example_tag_get_iq(self, iq): # Iq stanza powinno zawsze zostać zwrócone, w innym wypadku wysyłający dostanie informacje z błędem.
            logging.info(str(iq))
            reply = iq.reply(clear=False)
            reply.send()
            #<<<<<<<<<<<<

Domyślnie parametr `'clear'` dla `'Iq.reply'` jest ustawiony na True. Wtedy to, co jest zawarte wewnątrz Iq (z kilkoma wyjątkami) powinno zostać zdefiniowane ponownie. Jedyne informacje które zostaną w Iq po metodzie reply, nawet gdy parametr clean jest ustawiony na True, to ID tego Iq oraz JID wysyłającego.

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            #>>>>>>>>>>>>
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)
            #<<<<<<<<<<<<

        def start(self, event):
			# Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online
            self.send_presence()
            self.get_roster()

            #>>>>>>>>>>>>
            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag']['boolean'] = "True"
            iq['example_tag']['some_string'] = "Another_string"
            iq['example_tag'].text = "Info_inside_tag"
            iq.send()
            #<<<<<<<<<<<<

            #>>>>>>>>>>>>
        def example_tag_result_iq(self, iq):
            logging.info(str(iq))

        def example_tag_error_iq(self, iq):
            logging.info(str(iq))
            #<<<<<<<<<<<<

Dostęp do elementów
-------------------------

Jest kilka możliwości dostania się do pól wewnątrz Message lub Iq. Po pierwsze, z poziomu klienta, można dostać zawartość jak ze słownika:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        #...
        def example_tag_result_iq(self, iq):
            logging.info(str(iq))
            #>>>>>>>>>>>>
            logging.info(iq['id'])
            logging.info(iq.get('id'))
            logging.info(iq['example_tag']['boolean'])
            logging.info(iq['example_tag'].get('boolean'))
            logging.info(iq.get('example_tag').get('boolean'))
            #<<<<<<<<<<<<

Z rozszerzenia ExampleTag, dostęp do elementów jest podobny, tyle że, nie wymagane jest określanie tagu, którego dotyczy. Dodatkową zaletą jest fakt niejednolitego dostępu, na przykład do parametru `'text'` między rozpoczęciem a zakończeniem tagu. Pokazuje to poniższy przykład, ujednolicając metody obiektowych getterów i setterów.

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ Nazwa głównego pliku XML tego rozszerzenia.
        namespace = "https://example.net/our_extension"             ##~ Nazwa obiektu, np. <example_tag xmlns={namespace} (...)</example_tag>. Powinna zostać zmieniona na własną.

        plugin_attrib = "example_tag"                               ##~ Nazwa, którą można odwołać się do obiektu. W szczególności, do zarejestrowanego obiektu można odwołać się przez: nazwa_obiektu['tag']. gdzie `'tag'` jest nazwą ElementBase extension. Nazwa powinna być taka sama jak "name" wyżej.

        interfaces = {"boolean", "some_string"}                     ##~ Lista kluczy słownika, które mogą być użyte z obiektem. Na przykład: `stanza_object['example_tag']` zwraca {"another": "some", "data": "some"}, gdzie `'example_tag'` jest nazwą rozszerzenia ElementBase.

            #>>>>>>>>>>>>
        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text
            #<<<<<<<<<<<<

Atrybut `'self.xml'` jest dziedziczony z klasy `'ElementBase'` i jest to dosłownie `'Element'` z pakietu `'ElementTree'`.

Kiedy odpowiednie gettery i settery są tworzone, można sprawdzić, czy na pewno podany argument spełnia normy pluginu lub konwersję na pożądany typ. Dodatkowo, kod staje się bardziej przejrzysty w standardach programowania obiektowego, jak na poniższym przykładzie:

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag']['boolean'] = "True"  #Przypisanie wprost
            #>>>>>>>>>>>>
            iq['example_tag'].set_some_string("Another_string") #Przypisanie poprzez setter
            iq['example_tag'].set_text("Info_inside_tag")
            #<<<<<<<<<<<<
            iq.send()

Wczytanie ExampleTag ElementBase z pliku XML, łańcucha znaków i innych obiektów
--------------------------------------------------------------------------------

Jest wiele możliwości na wczytanie wcześniej zdefiniowanego napisu z pliku albo lxml (ElementTree). Poniższy przykład wykorzystuje parsowanie typu tekstowego do lxml (ElementTree) i przekazanie atrybutów.

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    #...
    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin
    #...

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ Nazwa głównego pliku XML tego rozszerzenia.
        namespace = "https://example.net/our_extension"             ##~ Nazwa obiektu, np. <example_tag xmlns={namespace} (...)</example_tag>. Powinna zostać zmieniona na własną.

        plugin_attrib = "example_tag"                               ##~ Nazwa, którą można odwołać się do obiektu. W szczególności, do zarejestrowanego obiektu można odwołać się przez: nazwa_obiektu['tag']. gdzie `'tag'` jest nazwą ElementBase extension. Nazwa powinna być taka sama jak "name" wyżej.

        interfaces = {"boolean", "some_string"}                     ##~ Lista kluczy słownika, które mogą być użyte z obiektem. Na przykład: `stanza_object['example_tag']` zwraca {"another": "some", "data": "some"}, gdzie `'example_tag'` jest nazwą rozszerzenia ElementBase.

            #>>>>>>>>>>>>
        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)
            #<<<<<<<<<<<<

Do przetestowania tej funkcjonalności, potrzebny jest pliku zawierający xml z tagiem, przykładowy napis z xml oraz przykładowy lxml (ET):

.. code-block:: xml

    #File: $WORKDIR/test_example_tag.xml

    <example_tag xmlns="https://example.net/our_extension" some_string="StringFromFile">Info_inside_tag<inside_tag first_field="3" secound_field="4" /></example_tag>

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    #...
    from slixmpp.xmlstream import ET
    #...

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
			# Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online
            self.send_presence()
            self.get_roster()

            #>>>>>>>>>>>>
            self.disconnect_counter = 3 # Ta zmienna służy tylko do rozłączenia klienta po otrzymaniu odpowiedniej ilości odpowiedzi z Iq.

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>

        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Przykład rozłączania się aplikacji po uzyskaniu odpowiedniej ilości odpowiedzi.

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()
            #<<<<<<<<<<<<

Jeśli Responder zwróci wysłane Iq, a Sender wyłączy się po trzech odpowiedziach, wtedy wszystko działa tak, jak powinno.

Łatwość użycia pluginu dla programistów
----------------------------------------

Każdy plugin powinien posiadać pewne obiektowe metody: wczytanie danych, jak w przypadku metod `setup` z poprzedniego rozdziału, gettery, settery, czy wywoływanie odpowiednich wydarzeń.
Potencjalne błędy powinny być przechwytywane z poziomu pluginu i zwracane z odpowiednim opisem błędu w postaci odpowiedzi Iq o tym samym id do wysyłającego. Aby uniknąć sytuacji kiedy plugin nie robi tego co powinien, a wiadomość zwrotna nigdy nie nadchodzi, wysyłający dostaje error z komunikatem timeout.

Poniżej przykład kodu podyktowanego tymi zasadami:

.. code-block:: python

    #File: $WORKDIR/example/example plugin.py

    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"                ##~ Tekst czytelny dla człowieka oraz do znalezienia pluginu przez inny plugin.
            self.xep = "ope"                 ##~ Tekst czytelny dla człowieka oraz do znalezienia pluginu przez inny plugin poprzez dodanie go do `slixmpp/plugins/__init__.py` do funkcji `__all__` z 'xep_OPE'.

            namespace = ExampleTag.namespace
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Nazwa tego Callbacku
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Obsługuje tylko Iq o typie 'get' oraz example_tag
                        self.__handle_get_iq))                      ##~ Metoda przechwytuje odpowiednie Iq, powinna wywołać zdarzenie u klienta.

            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',  ##~ Nazwa tego Callbacku
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),   ##~ Obsługuje tylko Iq o typie 'result' oraz example_tag
                     self.__handle_get_iq))                    ##~ Metoda przechwytuje odpowiednie Iq, powinna wywołać zdarzenie u klienta.

            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',   ##~ Nazwa tego Callbacku
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),   ##~ Obsługuje tylko Iq o typie 'error' oraz example_tag
                        self.__handle_get_iq))                     ##~ Metoda przechwytuje odpowiednie Iq, powinna wywołać zdarzenie u klienta.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Nazwa tego Callbacku
                        StanzaPath(f'message/{{{namespace}}}example_tag'),         ##~ Obsługuje tylko Message z example_tag
                        self.__handle_message))                     ##~ Metoda przechwytuje odpowiednie Iq, powinna wywołać zdarzenie u klienta.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Zarejestrowane rozszerzenia tagu dla Iq. Bez tego, iq['example_tag'] będzie polem tekstowym, a nie kontenerem i nie będzie można zmieniać w nim pól i tworzyć pod-elementów.
            register_stanza_plugin(Message, ExampleTag)             ##~ Zarejestrowane rozszerzenia tagu dla wiadomości Message. Bez tego, message['example_tag'] będzie polem tekstowym, a nie kontenerem i nie będzie można zmieniać w nim pól i tworzyć pod-elementów.

        # Wszystkie możliwe typy iq: get, set, error, result
        def __handle_get_iq(self, iq):
            if iq.get_some_string is None:
                error = iq.reply(clear=False)
                error["type"] = "error"
                error["error"]["condition"] = "missing-data"
                error["error"]["text"] = "Without some_string value returns error."
                error.send()
            # Zrób coś z otrzymanym Iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Wywołanie zdarzenia, które może być przesłane do klienta lub zmienione po drodze.

        def __handle_result_iq(self, iq):
            # Zrób coś z otrzymanym Iq
            self.xmpp.event('example_tag_result_iq', iq)           ##~ Wywołanie zdarzenia, które może być przesłany do klienta lub zmienione po drodze.

        def __handle_error_iq(self, iq):
            # Zrób coś z otrzymanym Iq
            self.xmpp.event('example_tag_error_iq', iq)           ##~ Wywołanie zdarzenia, które może być przesłane do klienta lub zmienione po drodze.

        def __handle_message(self, msg):
            # Zrób coś z otrzymaną wiadomością
            self.xmpp.event('example_tag_message', msg)           ##~ Wywołanie zdarzenia, które może być przesłane do klienta lub zmienione po drodze.

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ Nazwa głównego pliku XML tego rozszerzenia.
        namespace = "https://example.net/our_extension"             ##~ Nazwa obiektu, np. <example_tag xmlns={namespace} (...)</example_tag>. Powinna zostać zmieniona na własną.

        plugin_attrib = "example_tag"                               ##~ Nazwa, którą można odwołać się do obiektu. W szczególności, do zarejestrowanego obiektu można odwołać się przez: nazwa_obiektu['tag']. gdzie `'tag'` jest nazwą ElementBase extension. Nazwa powinna być taka sama jak "name" wyżej.

        interfaces = {"boolean", "some_string"}                     ##~ Lista kluczy słownika, które mogą być użyte z obiektem. Na przykład: `stanza_object['example_tag']` zwraca {"another": "some", "data": "some"}, gdzie `'example_tag'` jest nazwą rozszerzenia ElementBase.

        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)

        def setup_from_dict(self, data):
            #Poprawnośc kluczy słownika powinna być sprawdzona
            self.xml.attrib.update(data)

        def get_boolean(self):
            return self.xml.attrib.get("boolean", None)

        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text

        def fill_interfaces(self, boolean, some_string):
            #Jakaś walidacja, jeśli jest potrzebna
            self.set_boolean(boolean)
            self.set_some_string(some_string)

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass

    import asyncio
    import slixmpp
    import example_plugin

    class Responder(slixmpp.ClientXMPP):
        def __init__(self, jid, password):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_get_iq", self.example_tag_get_iq)
            self.add_event_handler("example_tag_message", self.example_tag_message)

        def start(self, event):
			# Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online
            self.send_presence()
            self.get_roster()

        def example_tag_get_iq(self, iq): # Iq zawsze powinien odpowiedzieć. Jeżeli użytkownik jest offline, zostanie zwrócony error.
            logging.info(iq)
            reply = iq.reply()
            reply["example_tag"].fill_interfaces(True, "Reply_string")
            reply.send()

        def example_tag_message(self, msg):
            logging.info(msg) # Na wiadomość Message można odpowiedzieć, ale nie trzeba.


    if __name__ == '__main__':
        parser = ArgumentParser(description=Responder.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message to")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Responder(args.jid, args.password)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPluggin jest nazwa klasy example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
			# Dwie niewymagane metody pozwalające innym użytkownikom zobaczyć dostępność online
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 5 # Aplikacja rozłączy się po odebraniu takiej ilości odpowiedzi.

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Przykład rozłączania się aplikacji po uzyskaniu odpowiedniej ilości odpowiedzi.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Przykład rozłączania się aplikacji po uzyskaniu odpowiedniej ilości odpowiedzi.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # Kiedy, aby otrzymać odpowiedż z błędem, potrzebny jest example_tag bez wartości bool.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin jest nazwą klasy z example_plugin.

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass


Tagi i atrybuty zagnieżdżone wewnątrz głównego elementu
---------------------------------------------------------

Aby stworzyć zagnieżdżony tag, wewnątrz głównego tagu, rozważmy atrybut `'self.xml'` jako Element z ET (ElementTree). W takim wypadku, aby stworzyć zagnieżdżony element można użyć funkcji 'append'.

Można powtórzyć poprzednie działania inicjalizując nowy element jak główny (ExampleTag). Jednak jeśli nie potrzebujemy dodatkowych metod, czy walidacji, a jest to wynik dla innego procesu który i tak będzie parsował xml, wtedy możemy zagnieździć zwyczajny Element z ElementTree za pomocą metody `'append'`. W przypadku przetwarzania typu tekstowego, można to zrobić nawet dzięki parsowaniu napisu na Element - kolejne zagnieżdżenia już będą w dodanym Elemencie do głównego. By nie powtarzać metody setup, poniżej przedstawione jest ręczne dodanie zagnieżdżonego taga konstruując ET.Element samodzielnie.

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py

    #(...)

    class ExampleTag(ElementBase):

    #(...)

        def add_inside_tag(self, tag, attributes, text=""):
            #Można rozszerzyć tag o tagi wewnętrzne do tagu, na przykład tak:
            itemXML = ET.Element("{{{0:s}}}{1:s}".format(self.namespace, tag)) #~ Inicjalizujemy Element z wewnętrznym tagiem, na przykład: <example_tag (...)> <inside_tag namespace="https://example.net/our_extension"/></example_tag>
            itemXML.attrib.update(attributes) #~ Przypisujemy zdefiniowane atrybuty, na przykład: <inside_tag namespace=(...) inner_data="some"/>
            itemXML.text = text #~ Dodajemy text wewnątrz tego tagu: <inside_tag (...)>our_text</inside_tag>
            self.xml.append(itemXML) #~ I tak skonstruowany Element po prostu dodajemy do elementu z tagiem `example_tag`.

Można też zrobić to samo używając słownika i nazw jako kluczy zagnieżdżonych elementów. W takim przypadku, pola funkcji powinny zostać przeniesione do ET.

Kompletny kod tutorialu
-------------------------

W poniższym kodzie zostały pozostawione oryginalne komentarze w języku angielskim.

.. code-block:: python

    #!/usr/bin/python3
    #File: /usr/bin/test_slixmpp & permissions rwx--x--x (711)

    import subprocess
    import time

    if __name__ == "__main__":
        #~ prefix = ["x-terminal-emulator", "-e"] # Separate terminal for every client; can be replaced with other terminal
        #~ prefix = ["xterm", "-e"]
        prefix = []
        #~ suffix = ["-d"] # Debug
        #~ suffix = ["-q"] # Quiet
        suffix = []

        sender_path = "./example/sender.py"
        sender_jid = "SENDER_JID"
        sender_password = "SENDER_PASSWORD"

        example_file = "./test_example_tag.xml"

        responder_path = "./example/responder.py"
        responder_jid = "RESPONDER_JID"
        responder_password = "RESPONDER_PASSWORD"

        # Remember about the executable permission. (`chmod +x ./file.py`)
        SENDER_TEST = prefix + [sender_path, "-j", sender_jid, "-p", sender_password, "-t", responder_jid, "--path", example_file] + suffix
        RESPON_TEST = prefix + [responder_path, "-j", responder_jid, "-p", responder_password] + suffix

        try:
            responder = subprocess.Popen(RESPON_TEST)
            sender = subprocess.Popen(SENDER_TEST)
            responder.wait()
            sender.wait()
        except:
            try:
                responder.terminate()
            except NameError:
                pass
            try:
                sender.terminate()
            except NameError:
                pass
            raise

.. code-block:: python

    #File: $WORKDIR/example/example_plugin.py

    import logging

    from slixmpp.xmlstream import ElementBase, ET, register_stanza_plugin

    from slixmpp import Iq
    from slixmpp import Message

    from slixmpp.plugins.base import BasePlugin

    from slixmpp.xmlstream.handler import Callback
    from slixmpp.xmlstream.matcher import StanzaPath

    log = logging.getLogger(__name__)

    class OurPlugin(BasePlugin):
        def plugin_init(self):
            self.description = "OurPluginExtension"   ##~ String data for Human readable and find plugin by another plugin with method.
            self.xep = "ope"                          ##~ String data for Human readable and find plugin by another plugin with adding it into `slixmpp/plugins/__init__.py` to the `__all__` declaration with 'xep_OPE'. Otherwise it's just human readable annotation.

            namespace = ExampleTag.namespace
            self.xmpp.register_handler(
                        Callback('ExampleGet Event:example_tag',    ##~ Name of this Callback
                        StanzaPath(f"iq@type=get/{{{namespace}}}example_tag"),      ##~ Handle only Iq with type get and example_tag
                        self.__handle_get_iq))                      ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleResult Event:example_tag', ##~ Name of this Callback
                        StanzaPath(f"iq@type=result/{{{namespace}}}example_tag"),   ##~ Handle only Iq with type result and example_tag
                        self.__handle_result_iq))                   ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleError Event:example_tag',  ##~ Name of this Callback
                        StanzaPath(f"iq@type=error/{{{namespace}}}example_tag"),    ##~ Handle only Iq with type error and example_tag
                        self.__handle_error_iq))                    ##~ Method which catch proper Iq, should raise proper event for client.

            self.xmpp.register_handler(
                        Callback('ExampleMessage Event:example_tag',##~ Name of this Callback
                        StanzaPath(f'message/{{{namespace}}}example_tag'),          ##~ Handle only Message with example_tag
                        self.__handle_message))                     ##~ Method which catch proper Message, should raise proper event for client.

            register_stanza_plugin(Iq, ExampleTag)                  ##~ Register tags extension for Iq object, otherwise iq['example_tag'] will be string field instead container where we can manage our fields and create sub elements.
            register_stanza_plugin(Message, ExampleTag)             ##~ Register tags extension for Message object, otherwise message['example_tag'] will be string field instead container where we can manage our fields and create sub elements.

        # All iq types are: get, set, error, result
        def __handle_get_iq(self, iq):
            if iq.get_some_string is None:
                error = iq.reply(clear=False)
                error["type"] = "error"
                error["error"]["condition"] = "missing-data"
                error["error"]["text"] = "Without some_string value returns error."
                error.send()
            # Do something with received iq
            self.xmpp.event('example_tag_get_iq', iq)           ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_result_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_result_iq', iq)        ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_error_iq(self, iq):
            # Do something with received iq
            self.xmpp.event('example_tag_error_iq', iq)         ##~ Call event which can be handled by clients to send or something other what you want.

        def __handle_message(self, msg):
            # Do something with received message
            self.xmpp.event('example_tag_message', msg)          ##~ Call event which can be handled by clients to send or something other what you want.

    class ExampleTag(ElementBase):
        name = "example_tag"                                        ##~ The name of the root XML element of that extension.
        namespace = "https://example.net/our_extension"             ##~ The namespace our stanza object lives in, like <example_tag xmlns={namespace} (...)</example_tag>. You should change it for your own namespace

        plugin_attrib = "example_tag"                               ##~ The name to access this type of stanza. In particular, given  a  registration  stanza,  the Registration object can be found using: stanza_object['example_tag'] now `'example_tag'` is name of ours ElementBase extension. And this should be that same as name.

        interfaces = {"boolean", "some_string"}                     ##~ A list of dictionary-like keys that can be used with the stanza object. For example `stanza_object['example_tag']` gives us {"another": "some", "data": "some"}, whenever `'example_tag'` is name of ours ElementBase extension.

        def setup_from_string(self, string):
            """Initialize tag element from string"""
            et_extension_tag_xml = ET.fromstring(string)
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_file(self, path):
            """Initialize tag element from file containing adjusted data"""
            et_extension_tag_xml = ET.parse(path).getroot()
            self.setup_from_lxml(et_extension_tag_xml)

        def setup_from_lxml(self, lxml):
            """Add ET data to self xml structure."""
            self.xml.attrib.update(lxml.attrib)
            self.xml.text = lxml.text
            self.xml.tail = lxml.tail
            for inner_tag in lxml:
                self.xml.append(inner_tag)

        def setup_from_dict(self, data):
            #There should keys should be also validated
            self.xml.attrib.update(data)

        def get_boolean(self):
            return self.xml.attrib.get("boolean", None)

        def get_some_string(self):
            return self.xml.attrib.get("some_string", None)

        def get_text(self, text):
            return self.xml.text

        def set_boolean(self, boolean):
            self.xml.attrib['boolean'] = str(boolean)

        def set_some_string(self, some_string):
            self.xml.attrib['some_string'] = some_string

        def set_text(self, text):
            self.xml.text = text

        def fill_interfaces(self, boolean, some_string):
            #Some validation if it is necessary
            self.set_boolean(boolean)
            self.set_some_string(some_string)

        def add_inside_tag(self, tag, attributes, text=""):
            #If we want to fill with additionaly tags our element, then we can do it that way for example:
            itemXML = ET.Element("{{{0:s}}}{1:s}".format(self.namespace, tag)) #~ Initialize ET with our tag, for example: <example_tag (...)> <inside_tag namespace="https://example.net/our_extension"/></example_tag>
            itemXML.attrib.update(attributes) #~ There we add some fields inside tag, for example: <inside_tag namespace=(...) inner_data="some"/>
            itemXML.text = text #~ Fill field inside tag, for example: <inside_tag (...)>our_text</inside_tag>
            self.xml.append(itemXML) #~ Add that all what we set, as inner tag inside `example_tag` tag.

~

.. code-block:: python

    #File: $WORKDIR/example/sender.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 6 # This is only for disconnect when we receive all replies for sended Iq

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_iq_with_inner_tag(self.to)
            # <iq from="SENDER/RESOURCE" to="RESPONDER/RESOURCE" id="1" xml:lang="en" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_iq_with_inner_tag(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=1)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")

            inner_attributes = {"first_field": "1", "secound_field": "2"}
            iq['example_tag'].add_inside_tag(tag="inside_tag", attributes=inner_attributes)

            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # For example, our condition to receive error respond is example_tag without boolean value.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

~

.. code-block:: python

    #File: $WORKDIR/example/responder.py

    import logging
    from argparse import ArgumentParser
    from getpass import getpass
    import time

    import asyncio
    import slixmpp
    from slixmpp.xmlstream import ET

    import example_plugin

    class Sender(slixmpp.ClientXMPP):
        def __init__(self, jid, password, to, path):
            slixmpp.ClientXMPP.__init__(self, jid, password)

            self.to = to
            self.path = path

            self.add_event_handler("session_start", self.start)
            self.add_event_handler("example_tag_result_iq", self.example_tag_result_iq)
            self.add_event_handler("example_tag_error_iq", self.example_tag_error_iq)

        def start(self, event):
            # Two, not required methods, but allows another users to see us available, and receive that information.
            self.send_presence()
            self.get_roster()

            self.disconnect_counter = 6 # This is only for disconnect when we receive all replies for sended Iq

            self.send_example_iq(self.to)
            # <iq to=RESPONDER/RESOURCE xml:lang="en" type="get" id="0" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string" boolean="True">Info_inside_tag</example_tag></iq>

            self.send_example_iq_with_inner_tag(self.to)
            # <iq from="SENDER/RESOURCE" to="RESPONDER/RESOURCE" id="1" xml:lang="en" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            self.send_example_message(self.to)
            # <message to="RESPONDER" xml:lang="en" from="SENDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" some_string="Message string">Info_inside_tag_message</example_tag></message>

            self.send_example_iq_tag_from_file(self.to, self.path)
            # <iq from="SENDER/RESOURCE" xml:lang="en" id="2" type="get" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag></iq>

            string = '<example_tag xmlns="https://example.net/our_extension" some_string="Another_string">Info_inside_tag<inside_tag first_field="1" secound_field="2" /></example_tag>'
            et = ET.fromstring(string)
            self.send_example_iq_tag_from_element_tree(self.to, et)
            # <iq to="RESPONDER/RESOURCE" id="3" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>

            self.send_example_iq_to_get_error(self.to)
            # <iq type="get" id="4" from="SENDER/RESOURCE" xml:lang="en" to="RESPONDER/RESOURCE"><example_tag xmlns="https://example.net/our_extension" boolean="True" /></iq>
            # OUR ERROR <iq to="RESPONDER/RESOURCE" id="4" xml:lang="en" from="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas">Without boolean value returns error.</text></error></iq>
            # OFFLINE ERROR <iq id="4" from="RESPONDER/RESOURCE" xml:lang="en" to="SENDER/RESOURCE" type="error"><example_tag xmlns="https://example.net/our_extension" boolean="True" /><error type="cancel" code="503"><service-unavailable xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" /><text xmlns="urn:ietf:params:xml:ns:xmpp-stanzas" xml:lang="en">User session not found</text></error></iq>

            self.send_example_iq_tag_from_string(self.to, string)
            # <iq to="RESPONDER/RESOURCE" id="5" xml:lang="en" from="SENDER/RESOURCE" type="get"><example_tag xmlns="https://example.net/our_extension" some_string="Reply_string" boolean="True">Info_inside_tag<inside_tag secound_field="2" first_field="1" /></example_tag></iq>


        def example_tag_result_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def example_tag_error_iq(self, iq):
            self.disconnect_counter -= 1
            logging.info(str(iq))
            if not self.disconnect_counter:
                self.disconnect() # Example disconnect after first received iq stanza extended by example_tag with result type.

        def send_example_iq(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get")
            iq['example_tag'].set_boolean(True)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")
            iq.send()

        def send_example_iq_with_inner_tag(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=1)
            iq['example_tag'].set_some_string("Another_string")
            iq['example_tag'].set_text("Info_inside_tag")

            inner_attributes = {"first_field": "1", "secound_field": "2"}
            iq['example_tag'].add_inside_tag(tag="inside_tag", attributes=inner_attributes)

            iq.send()

        def send_example_message(self, to):
            #~ make_message(mfrom=None, mto=None, mtype=None, mquery=None)
            msg = self.make_message(mto=to)
            msg['example_tag'].set_boolean(True)
            msg['example_tag'].set_some_string("Message string")
            msg['example_tag'].set_text("Info_inside_tag_message")
            msg.send()

        def send_example_iq_tag_from_file(self, to, path):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=2)
            iq['example_tag'].setup_from_file(path)

            iq.send()

        def send_example_iq_tag_from_element_tree(self, to, et):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=3)
            iq['example_tag'].setup_from_lxml(et)

            iq.send()

        def send_example_iq_to_get_error(self, to):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=4)
            iq['example_tag'].set_boolean(True) # For example, our condition to receive error respond is example_tag without boolean value.
            iq.send()

        def send_example_iq_tag_from_string(self, to, string):
            #~ make_iq(id=0, ifrom=None, ito=None, itype=None, iquery=None)
            iq = self.make_iq(ito=to, itype="get", id=5)
            iq['example_tag'].setup_from_string(string)

            iq.send()

    if __name__ == '__main__':
        parser = ArgumentParser(description=Sender.__doc__)

        parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                            action="store_const", dest="loglevel",
                            const=logging.ERROR, default=logging.INFO)
        parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                            action="store_const", dest="loglevel",
                            const=logging.DEBUG, default=logging.INFO)

        parser.add_argument("-j", "--jid", dest="jid",
                            help="JID to use")
        parser.add_argument("-p", "--password", dest="password",
                            help="password to use")
        parser.add_argument("-t", "--to", dest="to",
                            help="JID to send the message/iq to")
        parser.add_argument("--path", dest="path",
                            help="path to load example_tag content")

        args = parser.parse_args()

        logging.basicConfig(level=args.loglevel,
                            format=' %(name)s - %(levelname)-8s %(message)s')

        if args.jid is None:
            args.jid = input("Username: ")
        if args.password is None:
            args.password = getpass("Password: ")

        xmpp = Sender(args.jid, args.password, args.to, args.path)
        xmpp.register_plugin('OurPlugin', module=example_plugin) # OurPlugin is a class name from example_plugin

        xmpp.connect()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            try:
                xmpp.disconnect()
                asyncio.get_event_loop().run_until_complete(xmpp.disconnected)
            except:
                pass

~

.. code-block:: python

    #File: $WORKDIR/test_example_tag.xml

.. code-block:: xml

    <example_tag xmlns="https://example.net/our_extension" some_string="StringFromFile">Info_inside_tag<inside_tag first_field="3" secound_field="4" /></example_tag>

Źródła i bibliogarfia
----------------------

Slixmpp - opis projektu:

* https://pypi.org/project/slixmpp/

Oficjalna strona z dokumentacją:

* https://slixmpp.readthedocs.io/

Oficjalna dokumentacja PDF:

* https://buildmedia.readthedocs.org/media/pdf/slixmpp/latest/slixmpp.pdf

Dokumentacje w formie Web i PDF różnią się; pewne szczegóły potrafią być wspomniane tylko w jednej z dwóch.
