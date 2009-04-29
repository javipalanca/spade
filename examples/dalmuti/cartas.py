# Clase para manejar las cartas del juego del Dalmuti

class Carta:
    
    def __init__(self, tipo):
        self.__tipo = tipo #Valor de 0 a 12


    def __cmp__(self, otro):
        # Comparamos segun el rango
        if self.__tipo < otro.getTipo():
            return 1
        if self.__tipo > otro.getTipo():
            return -1
        return 0

    def __str__(self):
        nombreCarta = [
            'Dalmuti(1)',
            'Arzobispo(2)',
            'Sheriff del Condado(3)',
            'Baronesa(4)',
            'Abadesa(5)',
            'Caballero(6)',
            'Costurera(7)',
            'Obrero(8)',
            'Cocinera(9)',
            'Pastora(10)',
            'Picapedrero(11)',
            'Campesino(12)',
            'Bufon(13)'
            ]
        return nombreCarta[self.__tipo]

    def getTipo(self):
        return self.__tipo


#Clase para manejar una jugada de una o mas cartas

class jugada:
    
    def __init__(self, cartas):
        self.cartas = cartas

    def __cmp__(self, otra):
        #Comparamos segun el numero de cartas
        if len(self.cartas) < len(otra.cartas):
            return -1
        if len(self.cartas) > len(otra.cartas):
            return 1

        # Ordenamos por si hay un bufon
        self.cartas.sort()
        otra.cartas.sort()

        #Comparamos segun el valor de la jugada
        if self.cartas[-1] < otra.cartas[-1]:
            return -1
        if self.cartas[-1] > otra.cartas[-1]:
            return 1

        #Es la misma jugada        
        return 0

    def __str__(self):
        res = ""
        if len(self.cartas)>0:
            for i in self.cartas:
                res = res+str(i)+" "

        return res

    def __len__(self):
        return len(self.cartas)
