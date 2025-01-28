"""# /// script
# dependencies = [""]
# ///"""
import random
import itertools # type: ignore
import msvcrt # type: ignore
from time import sleep

from AIdesign import AI

class Config():
    def __init__(self) -> None:
        self.player_num = 4
        self.score = [0,0,0,0]
        self.card_num = 7
        self.rule = {"after_decide": False,"pile_draw": False, "wildfour_anytime": False}

    def playerNum(self, num: None|int = None) -> int:
        if num != None:
            self.player_num = num
            self.score = list(itertools.repeat(0, conf_data.playerNum()))
        return self.player_num

    def cardNum(self, num: None|int = None) -> int:
        if num != None:
            self.card_num = num
        return self.card_num

    def continueRule(self, r:None|bool = None) -> bool:
        if r != None:
            self.rule["after_decide"] = r
        return self.rule["after_decide"]

    def pileDrawRule(self, r: None|bool = None) -> bool:
        if r != None:
            self.rule["pile_draw"] = r
        return self.rule["pile_draw"]
    
    def wildAnytimeRule(self, r: None|bool = None) -> bool:
        if r != None:
            self.rule["wildfour_anytime"] = r
        return self.rule["wildfour_anytime"]

class UnoAI(AI):
    def __init__(self, pattern: int) -> None:
        super().__init__(pattern)

class Play():
    def __init__(self, config:Config) -> None:
        self.player_num = config.playerNum() -1
        self.deck:list = self.__makeDeck()
        self.hand_num = config.cardNum()
        self.rule = config.rule #after_decide, pile_draw, wildfour_anytime
        self.hand_list:list = self.__makeHand()
        self.opened:tuple = ('', '')
        self.grave = []
        self.__setFromDeck()
        self.turn = random.randint(0,(self.player_num))
        self.skip = False
        self.reverse = False
        self.stuck = 0
        self.color = ""
        self.uno = False
        self.rank = 1
        self.score = config.score

    def __makeDeck(self):
        """デッキを作成する
        """
        colors = {'🔴', '🟡', '🟢', '🔵'}
        numbers = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '+2', 'Skip', 'Reverse'}#'⍉', '⇆'
        zeros = [('🔴','0'), ('🟡','0'), ('🟢','0'), ('🔵','0')]
        wilds = [('🌈',''), ('🌈', '+4')]*4
        deck = list(itertools.product(colors, numbers, repeat = 1))*2
        deck.extend(wilds)
        deck.extend(zeros)
        random.shuffle(deck) # type: ignore
        return deck

    def __makeHand(self):
        """手札を作成する
        """
        hand_list=[]
        for i in range(self.player_num +1):
            hand_list.append(self.deck[:self.hand_num])
            self.deck = self.deck[self.hand_num:]
        return hand_list

    def __setFromDeck(self):
        """デッキから1枚引いて, wildカード, +カード から始まっていないかチェックする
        """
        self.setCard()
        if self.opened[0] == '🌈' or ('+' in self.opened[1]):
            print("場のカード :" + str(self.opened))
            print("もう一度引きます")
            self.__setFromDeck()
        return

    def __selector(self, question: str, select: set[str]) -> str:
        inp = input(question).upper()
        if select >= {inp}:
            return inp
        else:
            print("you can't chose it.")
            selector(question, select)
            return inp

    def changeTurn(self):
        """ターンを一つ回す
        """
        self.uno = False
        if self.reverse == False:
            if self.turn < self.player_num:
                self.turn += 1
            else:
                self.turn = 0
        else:
            if self.turn > 0:
                self.turn -= 1
            else:
                self.turn = self.player_num
        
        if len(self.hand_list[self.turn]) == 0:
            self.changeTurn()
        if self.skip:
            self.skip = False
            if self.turn == 0:
                print("\nあなたのターンがスキップされました。 Skip Your turn")
            else:
                print("\nSkip Player"+ str(self.turn) + "\'s turn.")
            self.changeTurn()

    def drawDeck(self):
        """デッキから1枚引く
        """
        if len(self.deck) == 0:
            "山場がなくなったので使用済みカードを使います。 Use used cards for a deck."
            self.deck = self.grave.copy()
            random.shuffle(self.deck) # type: ignore
            self.grave = []
        self.hand_list[self.turn].append(self.deck.pop())

    def __cardEffect(self): #文字列や数値などのイミュータブルなオブジェクトは値渡し(変更しても反映されない)
        effect = ""
        if self.opened[0] == '🌈':
            if self.turn == 0:
                color = self.__selector("Decide color R: 🔴, Y: 🟡, G: 🟢, B: 🔵 ->",{'R', 'Y', 'G', 'B'})
                color_list = {'R': '🔴','Y': '🟡','G': '🟢','B': '🔵'}
                self.color = color_list[color]
            else:
                #自分の手札の一番多い色を選択
                hand = self.hand_list[self.turn]
                color = [raw[0] for raw in hand]
                color = max(set(color),key=color.count)
                if random.random() <= 0.8 and (color!= '🌈'): # 0.8 -> 経験値で更新したい
                    self.color = color
                else:
                    col = random.random()*4 # -> 経験値で更新したい, grave情報で変更させたい
                    if col <= 1:
                        self.color = '🔴'
                    elif col <= 2:
                        self.color = '🟡'
                    elif col <= 3:
                        self.color = '🟢'
                    elif col <= 4:
                        self.color = '🔵'
            effect = "color: " + self.color
        if self.opened[1] == 'Skip':
            self.skip = True
        elif self.opened[1] == 'Reverse':
            effect = "\n世界が反転する。。。  The world is reversed...."
            self.reverse = not self.reverse
        elif self.opened[1] == '+2':
            self.stuck += 2
        elif self.opened[1] == '+4':
            self.stuck += 4
        return effect
    
    def check_hand(self) -> list:
        cans = set()
        hand = self.hand_list[self.turn]
        for i in range(len(hand)):
            if hand[i] == ('🌈','+4'):
                if self.rule["wildfour_anytime"]:
                    cans.add(str(i))
            elif self.stuck > 0:
                if hand[i][1] == '+2' and self.rule["pile_draw"]:
                    if self.opened[1] == '+2':
                        cans.add(str(i))
                    if hand[i][0] == self.color:
                        cans.add(str(i))
            else:
                if hand[i][0] == self.opened[0] or (hand[i][1] == self.opened[1]):
                    cans.add(str(i))
                elif hand[i][0] == '🌈':
                    cans.add(str(i))
                elif hand[i][0] == self.color and (self.opened[0] == '🌈'):
                    cans.add(str(i))
        if len(cans) == 0 and (('🌈','+4') in hand):
            if self.stuck <= 0 or self.rule["pile_draw"]:
                cans.add(str(hand.index(('🌈','+4'))))
        return sorted(cans)

    def setCard(self,num: None|int = None):
        if num == None:
            self.opened = self.deck.pop()
        else:
            self.opened = self.hand_list[self.turn].pop(num)
            return self.__cardEffect()
        self.grave.append(self.opened)

    def checkPt(self, card: tuple):
        if card[0] == '🌈':
            pt = 50
        elif card[1] in ['+2', 'Skip', 'Reverse']:
            pt = 20
        else:
            pt = int(card[1])
        return pt

def selector(question: str, select: set[str]) -> str:
    inp = input(question).upper()
    if select >= {inp}:
        return inp
    else:
        print("you can't chose it.")
        return selector(question, select)

def config(conf_data):
    inp = selector("W: 人数変更(Change Player num), E: 手札枚数変更(Change Hand num), R: ルール変更(Change rule) Q: 戻る(Back) ->",{"Q","W","E","R"})
    if inp == "Q":
        pass
    elif inp == "W":
        inp = selector("人数入力 (2 ~ 9) 元値 : " + str(conf_data.playerNum()) + " ->",{'2', '3', '4', '5', '6', '7', '8', '9'})
        conf_data.playerNum(int(inp))
    elif inp == "E":
        inp = selector("手札枚数入力 (3 ~ 10) 元値 : " + str(conf_data.cardNum()) + " ->",{'3', '4', '5', '6', '7', '8', '9', '10'})
        conf_data.cardNum(int(inp))
    elif inp == "R":
        print("A: 1位決定後続行可否ルール変更, D: ドローカードの積み重ねルール変更, F: ドロー4の出せるタイミングルール変更")
        inp = selector("A: continue after 1st winner decide or not, D: be able to pile draw card or not, F: be able to set +4 card anytime or not(set only you have nothing else) ->",{"D","F"})
        if inp == "A":
            inp = selector("1位が決まった後もゲームを続けますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.continueRule(True)
            else:
                conf_data.continueRule(False)
        elif inp == "D":
            inp = selector("ドローカードを積み重ねられるようにしますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.pileDrawRule(True)
            else:
                conf_data.pileDrawRule(False)
        elif inp == "F":
            inp = selector("ドロー4をいつでも出せるようにしますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.wildAnytimeRule(True)
            else:
                conf_data.wildAnytimeRule(False)
    return

def main(data):
    if len(data.hand_list[0]) == 0:
        print("すでに試合は終了しています。 The game is already done.")
        print("次のゲームへ進む場合はRを選んでください。 Select \'R\' to restart.")
        return data.score
    print("Q : 一時停止 (pause)")
    print("UNO : 最後の１枚になったとき、打ち込む必要があります。 you have to type this word if you will have last one card.")
    if data.turn == 0:
        print("あなたからスタートします。 You are starter.")
    else:
        print("\n場のカード : " + str(data.opened))
        print(str(data.turn) + " 番プレーヤーからスタートします。 Start from player" + str(data.turn) + ".")
    print("進めるにはキーを押してください。 Press any key to continue.")

    while len(data.hand_list[0]) != 0:
        #if msvcrt.kbhit() and msvcrt.getch() == b'q':
        #    break
        key = msvcrt.getch() #キーウェイト 各ターンボタン押すまで待つ
        if key == b'q':
            break
        """elif key == b'c':
            inp = selector("コメントしますか? Do you want to say anything? Y/N ->",{"Y","N"})
            if inp == "Y":
                inp = selector("",{"",""})"""

        effect = ""
        hand = data.hand_list[data.turn] #リストは参照渡し
        cans = data.check_hand() #出せる手札の番号

        if data.turn == 0:
            print("\n場のカード : " + str(data.opened) + "  スタック (stuck) : " + str(data.stuck))
            if data.opened[0] == '🌈':
                print("     color : " + data.color)
            print("\nあなたのターンです。 Your turn")
            print("手札 (hand) : " + ",".join(map(str,hand)) + "\n")
        else:
            print("\nPlayer " + str(data.turn))

        #手札に応じて行動変化
        if len(cans) != 0:
            if data.turn == 0:
                print("以下から選んでください。You can put down them. Chose.")
                print(", ".join(map(lambda x: x + ": " + str(hand[int(x)]) ,cans)))
                cans.extend(["P","UNO"])
                inp = selector("P: パス (pass) ->",set(cans))
                if inp == "UNO":
                    data.uno = True
                    inp = selector(", ".join(map(lambda x: x + ": " + str(hand[int(x)]) ,cans[:-2])) + " ->",set(cans[:-2]))
                if inp == "P" and data.stuck > 0:
                    print(str(data.stuck)+"枚カードを引きます。 draw cards.")
                    hand.extend(data.deck[:data.stuck])
                    data.stuck = 0
                elif inp == "P":
                    print("1枚カードを引きます。 Draw a new card.")
                    data.drawDeck()
                    cans = data.check_hand()
                    if data.turn == 0:
                        print("Get" + str(hand[-1]))
                        if cans[-1] == str(len(hand)-1):
                            inp = selector("引いたカードを出しますか? Y/N ->",{"Y","N","UNO"})
                            if inp == "UNO":
                                data.uno = True
                                inp = "Y"
                            if inp == "Y":
                                effect = data.setCard(-1)
                                print("Set " + str(data.opened))
                else:
                    effect = data.setCard(int(inp))
                    print("Set " + str(data.opened))
            else:
                effect = data.setCard(int(cans[0])) # -> 経験値で更新したい, grave情報で変更させたい
                print("Set " + str(data.opened))
        elif data.stuck > 0:
            print(str(data.stuck)+"枚カードを引きます。 Draw "+str(data.stuck)+" cards.")
            data.hand_list[data.turn].extend(data.deck[:data.stuck-1])
            data.stuck = 0
        else:
            print("出せるカードがないので1枚カードを引きます。 Draw a new card.")
            data.drawDeck()
            cans = data.check_hand()
            if data.turn == 0:
                print("Get" + str(hand[-1]))
                if len(cans) != 0:
                    inp = selector("引いたカードを出しますか? Y/N ->",{"Y","N","UNO"})
                    if inp == "UNO":
                        data.uno = True
                        inp = "Y"
                    if inp == "Y":
                        effect = data.setCard(-1)
                        print("Set " + str(data.opened))
            else:
                cans = data.check_hand()
                if len(cans) != 0:
                    effect = data.setCard(-1)
                    print("I draw and set this. " + str(data.opened))

        #残り枚数・Unoチェック
        remain = len(hand)
        if remain == 0:
            if data.rank == 1:
                rank = "1st"
                #スコアの確定
                for ind in range(len(data.score)):
                    cards = data.hand_list[ind]
                    for card in cards:
                        pt = data.checkPt(card)
                        data.score[data.turn] += pt
                        data.score[ind] -= pt
            elif data.rank == 2:
                rank = "2nd"
            elif data.rank == 3:
                rank = "3rd"
            else:
                rank = str(data.rank) +"th"
            if data.turn == 0:
                print("あなたは " + str(data.rank) + "位です。 In " + rank + " place is YOU!!!!!!!")
            else:
                print("Player " + str(data.turn) + " の勝ち! In" + rank + " place is Player" + str(data.turn))
            data.rank += 1
            if data.rank == (data.player_num + 1):
                print("負けました。 You lose...")
                data.turn = 0
            if (not data.rule["after_decide"]) or (data.turn == 0):
                print("次のゲームへ進む場合はRを選んでください。 Select \'R\' to restart.")
                break
        elif remain == 1:
            if data.turn == 0 and (data.uno == False):
                print("UNO と言い忘れたので1枚引きます。 You Forgot to say \'UNO\'! Draw.")
                data.drawDeck()
                print("Get " + str(hand[-1]))
            elif data.turn !=0:
                print("UNO!!")
                data.uno = True
        else:
            print("  残り (remain) : " + str(remain))

        #カード効果の発動（説明）
        if effect != "":
            print(effect)

        #ターン変更
        data.uno = False
        data.changeTurn()
        sleep(0.1)
    return data.score

if __name__ == "__main__":
    conf_data = Config()
    i = selector("C: 設定 (Setting), Space: スタート (Start), Q: やめる (Exit) ->", {"C"," ","Q"})
    while i != "Q":
        if i == "C":
            config(conf_data)
            i = selector("C: 設定 (Setting), Space: スタート (Start), Q: やめる (Exit) ->", {"C"," ","Q"})
        elif i == " " or (i == "R"):
            print("🌈 = wild card")
            print("Game Start!")
            play_data = Play(conf_data)

            conf_data.score = main(play_data)

            print("スコア : " + str(conf_data.score[0]) + "Pt")
            for ind, pt in enumerate(conf_data.score[1:]):
                print("Player" + str(ind +1) + " : " + str(pt) + "Pt")
            print("*設定を変更すると途中のデータ, スコアは破棄されます。*")
            print("*If the setting is changed, data in progress will be discarded.*")
            i = selector("C: 設定 (Setting), E: 戻る (Continue), R: 次へ (Next game), Q: やめる (Exit) ->",{"C","E","R","Q"})
        elif i == "E":

            conf_data.score = main(play_data)

            print("スコア : " + str(conf_data.score[0]) + "Pt")
            for ind, pt in enumerate(conf_data.score[1:]):
                print("Player" + str(ind +1) + " : " + str(pt) + "Pt")
            print("*設定を変更すると途中のデータは破棄されます。*")
            print("*If the setting is changed, data in progress will be discarded.*")
            i = selector("C: 設定 (Setting), E: 戻る (Continue), R: 次へ (Next game), Q: やめる (Exit) ->",{"C","E","R","Q"})