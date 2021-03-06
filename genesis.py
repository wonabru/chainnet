from wallet import CWallet



class CGenesis:
    def __init__(self):
        self.e = 65537
        #self.initAccountPubKey = CWallet().getPublicKey(self.getPrivKey())
        self.initAccountPubKey = 'g9MsRcZGTHomRZD6pN4Nr1uq8L+scPZ/mOAsWBsU3LSBS99k4A5rA/XP5n7VfFpF4DNXhSJce4ZAo' \
                                 'Qbm3v0qyfrs5J9F9blhYZT2N8eNgmj2lCC0IC1YmZ5Pn/iSkpNKWk/ttGJj/hy+ozjcT0py8NJ' \
                                 'JzDLzeydCMrd1aG4Snbg='
        self.first_accountPubKey = '2x0PpHUGF1P2q/wB3j+Fi1WHrl5zoPp/XvaEPhnL+lDwTNdjyMviD9T0AT' \
                                   'RX6dKwtQkJraRBryLL/gdooa3VVRJ+thSH11suQNsJ4peI6vEAMwvyamF5M' \
                                   'TJ3Hn+U0SJ0DgtTe7k5D7qAwu4k5MfbbpEwVAu0qsMcIjSqxvSd5+Q='
        self.signature_init = 'MV1q7Ok7rDtrDVLms4IkBNxqpudRR0gmjfY5AcfrfyBGKjjwFM/aivoYq8+Za' \
                              'PA/J2oevSBW+outASBzHBqkFVFem8ZosBE260fNKfUvFGiDh+2Xc7QtJ3QVTPm' \
                              'U0pL+PQj4gUjMRcHp8+OvJsRJcTQr823tQSvaOqt7qD/bwJI='
        self.signature_wonabru = 'o4OgtH371UgJlluvS247Dh09OKCAtJ2V5NvUoXXCUAF81WdUoQruxrDIpk' \
                                 '2GLWmDJ5cjNGaGqsLqa56C1WJ0Od3SpxIr8dESjyg76ocLZln8VEq' \
                                 'vaFM1EkIF+uYooLahRrax4dpbUT9C8ePX2wEIBtWoxuqvcG9MNY1AJAr0c2w='

        self.signature_init = 'Rh/cLRPQu17zypC674QRCY1ExiUqGlHN4CQ9H3RN6aEyLi+0PjqViY6Bfggax24R3Rr6Vdk3dDsOD2niYBlqtUjEm76SZUrS87eYtug4ONiIaNg1IboyC8vKGQrnngNj8cNH9zi4cG+Vxhe3RF0IKrQrdpmKhEA8nJM6caHfsYk='
        self.signature_wonabru = 'QuTyCR2zHZoAK6z8BPFcZMAJB/vZ87utIMoPbaj6M/wvGd0WoERueY2LWOP4C7yeru8TXySK9GPt8W3szIaj/gya8Jy1VPxADdaCnY8tBP1dYEJauhW6UzR7uu5SGMRkfDSesooUUjXj5JoAcNDKfmWNufKt6U0bZTYHQPCfMn4='
        self.first_accountPubKey = 'fSmWlIfKCxdmKA9ESrOaCqj0GMyOtDcfEKcsKKcXUJCnC7TJBkcHOUCZNFhxJKZzzFCB3eqiTzJRVaoN48icOvId/hlHyIHJgTBxMz88wo9e/ULEvp5oeYRhYlFArihVzDQFa+FQjNadcpIYxH1SB/W5dBRwbjVbhx+wH7FuAcc='

    def getPrivKey(self):
        return CWallet().privfromJson({"d": "260360158136291685259871724233088127320409021650909687793"
                                       "2879118742715555180033795778602066631893544447789492234164910"
                                       "385949806819743078737167196436727012038203821157078420974670926"
                                       "06301999711804406195907397851657077319070828630702591501084799914"
                                       "32733151210696830300122267288326422618641019322363130479430113",
                                  "q": "12594088244373820944436226815539318310684829844188840940167646926"
                                       "25535036425497468032905730900044799851526676498396726898246440347"
                                       "4063608333703134281537371",
                                  "p": "1029372272012708261757893385925179370640841586366892692717034035205"
                                        "9760819835453753397459089964949202673384397510362334982430"
                                       "481530324517540053232321434873",
                                  "u": "377596467689180211077614258124840469687532496364253032467368"
                                       "5873812089354681429077815909347193266596757509199560433033881"
                                       "070862812708412505555990015444924",
                                  "n": "12964005230039620252907015036517168059715579738592666926689492"
                                       "387558224383819622768115958337703571434620481686107769771460567"
                                       "73207305137146313072123338232928678776923321210634716327013768448"
                                       "473054123152212622679157860646693498709948178821887146362034334062"
                                       "40728215174705916932152806228964670724820983092138883",
                                  "e": "65537"})
