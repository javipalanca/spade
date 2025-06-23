import datetime
from typing import Optional

from slixmpp import ElementBase, Iq, register_stanza_plugin

NS = "urn:ietf:params:xml:ns:vcard-4.0"


class _VCardElementBase(ElementBase):
    namespace = NS


class VCard4(_VCardElementBase):
    name = plugin_attrib = "vcard"
    interfaces = {"full_name", "given", "surname", "birthday"}

    def set_full_name(self, full_name: str):
        self["fn"]["text"] = full_name

    def get_full_name(self):
        return self["fn"]["text"]

    def set_given(self, given: str):
        self["n"]["given"] = given

    def get_given(self):
        return self["n"]["given"]

    def set_surname(self, surname: str):
        self["n"]["surname"] = surname

    def get_surname(self):
        return self["n"]["surname"]

    def set_birthday(self, birthday: datetime.date):
        self["bday"]["date"] = birthday

    def get_birthday(self):
        return self["bday"]["date"]

    def add_tel(self, number: str, name: Optional[str] = None):
        tel = Tel()
        if name:
            tel["parameters"]["type_"]["text"] = name
        tel["uri"] = f"tel:{number}"
        self.append(tel)

    def add_address(
        self, country: Optional[str] = None, locality: Optional[str] = None
    ):
        adr = Adr()
        if locality:
            adr["locality"] = locality
        if country:
            adr["country"] = country
        self.append(adr)

    def add_nickname(self, nick: str):
        el = Nickname()
        el["text"] = nick
        self.append(el)

    def add_note(self, note: str):
        el = Note()
        el["text"] = note
        self.append(el)

    def add_impp(self, impp: str):
        el = Impp()
        el["uri"] = impp
        self.append(el)

    def add_url(self, url: str):
        el = Url()
        el["uri"] = url
        self.append(el)

    def add_email(self, email: str):
        el = Email()
        el["text"] = email
        self.append(el)


class _VCardTextElementBase(_VCardElementBase):
    interfaces = {"text"}
    sub_interfaces = {"text"}


class Fn(_VCardTextElementBase):
    name = plugin_attrib = "fn"


class Nickname(_VCardTextElementBase):
    name = plugin_attrib = "nickname"


class Note(_VCardTextElementBase):
    name = plugin_attrib = "note"


class _VCardUriElementBase(_VCardElementBase):
    interfaces = {"uri"}
    sub_interfaces = {"uri"}


class Url(_VCardUriElementBase):
    name = plugin_attrib = "url"


class Impp(_VCardUriElementBase):
    name = plugin_attrib = "impp"


class Email(_VCardTextElementBase):
    name = plugin_attrib = "email"


class N(_VCardElementBase):
    name = "n"
    plugin_attrib = "n"
    interfaces = sub_interfaces = {"given", "surname", "additional"}


class BDay(_VCardElementBase):
    name = plugin_attrib = "bday"
    interfaces = {"date"}

    def set_date(self, date: datetime.date):
        d = Date()
        d.xml.text = date.strftime("%Y-%m-%d")
        self.append(d)

    def get_date(self):
        for elem in self.xml:
            try:
                return datetime.date.fromisoformat(elem.text)
            except ValueError:
                return None


class Date(_VCardElementBase):
    name = "date"


class Tel(_VCardUriElementBase):
    name = plugin_attrib = "tel"


class Parameters(_VCardElementBase):
    name = plugin_attrib = "parameters"


class Type(_VCardTextElementBase):
    name = "type"
    plugin_attrib = "type_"


class Adr(_VCardElementBase):
    name = plugin_attrib = "adr"
    interfaces = sub_interfaces = {"locality", "country"}


register_stanza_plugin(Parameters, Type)
register_stanza_plugin(Tel, Parameters)
for p in N, Fn, Nickname, Note, Url, Impp, Email, BDay, Tel, Adr:
    register_stanza_plugin(VCard4, p, iterable=True)
register_stanza_plugin(Iq, VCard4)
