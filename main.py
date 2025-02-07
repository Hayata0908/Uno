"""# /// script
# dependencies = [""]
# ///"""
import random
from dataclasses import dataclass, field
import itertools # type: ignore
import msvcrt # type: ignore
from time import sleep,time

from AIdesign import AI #TBD

@dataclass
class ConfigArgs():
    """
    Data class for Config

    Attributes:
        player_num (int) : number of players
        card_num (int) : number of hands
        score (list[int]) : score for all players (length of list is number of player)
        r_after_decide (bool) : the game continue after 1st winner decide or not
        r_pile_draw (bool) : player can pile draw or not
        r_wildfour_anytime (bool) : player can set wild4 anytime or only when the player can't set the other cards.
    """
    player_num:int = 4
    card_num:int = 7
    score:list = field(default_factory=lambda: [0,0,0,0]) # type: ignore
    r_after_decide:bool = False
    r_pile_draw:bool = False
    r_wildfour_anytime = False

class UnoCpu(AI):
    def __init__(self, pattern: list|None = None) -> None:
        if pattern == None:
            pattern = [0.4+random.random()*0.6,0.1+random.random()*0.9]
        super().__init__(pattern)
        self.feels = ("睡眠","従順","悲哀","退屈","安心","不安","愉快","平穏","歓喜","感嘆","興味","恐怖","憤怒","緊張","驚愕")
        self.now = 7

    def actRecieve(self,situation,effect=None) -> None:
        if effect == None:
            effect = situation
        super().changeFeel(situation, effect)
        self.now = self.feels.index(super().changeMove())

    def makeLine(self) -> str:
        """セリフを作る
        """
        act = ""
        if self.now == 0:
            act = "Zzz"
        elif self.now == 1:
            act = "・・・"
        elif self.now == 2:
            act = "あ～ぁ。"
        elif self.now == 3:
            if self.pattern[1]>0.5:
                act = "めんどくさいなぁ。"
            else:
                act = "ふあぁあ"
        elif self.now == 4:
            act = "ふぅ。"
        elif self.now == 5:
            act = "ど、どうしよう、、。"
        elif self.now == 6:
            act = "いいね。"
        elif self.now == 7:
            if self.pattern[1]>0.6:
                act = "へぇ。"
        elif self.now == 8:
            if self.pattern[1]>0.3:
                act = "やった!"
        elif self.now == 9:
            act = "ほぇえ。"
        elif self.now == 10:
            if self.pattern[1]>0.5:
                act = "面白いね。"
            else:
                act = "なるほど。"
        elif self.now == 11:
            act = "うぅぅ。"
        elif self.now == 12:
            act = "この～！"
        elif self.now == 13:
            act = "ドキドキ"
        elif self.now == 14:
            act = "ええっ！"
        return act
    
    def makeAct(self) -> bool:
        """正常な行動を行うか否か
        """
        if random.random() < (abs(self.now-7)-1)/10:
            return False
        return True

class CpuManager():
    def __init__(self, num:int) -> None:
        self.cpus = []
        self.situation = []
        for i in range(num):
            self.cpus.append(UnoCpu())
            self.situation.append(0.5)
        self.u_time = 7

    def changeCpuNum(self, num:int) -> None:
        self.cpus = []
        for i in range(num):
            self.cpus.append(UnoCpu())

    def setTurnTime(self, elapsed):
        self.u_time = (self.u_time + elapsed)/2
        for cpu in self.cpus:
            cpu.u_time = self.u_time

    def checkSituation(self, hands:list, score:list):
        hand_num = list(map(lambda x: len(x), hands))
        if len(set(hand_num)) == 1:
            hand_nor = [0.5]*len(hand_num)
        else:
            hand_nor = list(map(lambda x: 1-(x-min(hand_num))/(max(hand_num)-min(hand_num)), hand_num))
        for i, hand in enumerate(hands):
            if len(hand) == 0:
                hand_nor[i] = 1

        if len(set(score)) == 1:
            score_nor = [0.5]*len(score)
        else:
            score_nor = list(map(lambda x: 1-(x-min(score))/(max(score)-min(score)), score))
        self.situation = list((x*2 + y)/3 for x, y in zip(hand_nor, score_nor))[1:]

    def actRecieve(self, effect = None, player = None):
        if player == None:
            for ind, cpu in enumerate(self.cpus):
                cpu.actRecieve(self.situation[ind],effect)
        else:
            self.cpus[player-1].actRecieve(self.situation[player-1],effect)
            #print(self.cpus[player-1].feels[self.cpus[player-1].now])

    def makeLine(self, player: int|None = None):
        lines=[]
        if player == None:
            for ind, cpu in enumerate(self.cpus):
                line = cpu.makeLine()
                if line != "":
                    lines.append("Player " + str(ind+1) + " : " +line)
            if len(lines) != 0:
                print(random.choice(lines))
        else:
            line = self.cpus[player-1].makeLine()
            if line != "":
                print("Player " + str(player) + " : "+ self.cpus[player-1].makeLine())

class UnoPlay():
    def __init__(self, config:ConfigArgs, cpus:CpuManager) -> None:
        self.player_num = config.player_num -1
        self.cpus = cpus
        self.deck:list = self.__makeDeck()
        self.hand_num = config.card_num
        self.r_after_decide = config.r_after_decide
        self.r_pile_draw = config.r_pile_draw
        self.r_wildfour_anytime = config.r_wildfour_anytime
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
                self.cpus.actRecieve(0.3, self.turn)
                self.cpus.makeLine(self.turn)
            self.changeTurn()

    def drawDeck(self, d_num:int = 1):
        """デッキから1枚引く
        """
        if len(self.deck) < d_num:
            "山場がなくなったので使用済みカードを使います。 Use used cards for a deck."
            self.deck = self.grave.copy()
            random.shuffle(self.deck) # type: ignore
            self.grave = []
        for i in range(d_num):
            self.hand_list[self.turn].append(self.deck.pop())

    def __cardeffect(self): #文字列や数値などのイミュータブルなオブジェクトは値渡し(変更しても反映されない)
        describe = ""
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
                if self.uno and (color!= '🌈'): # -> 経験値で更新したい
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
            describe = "color: " + self.color
        if self.opened[1] == 'Skip':
            self.skip = True
        elif self.opened[1] == 'Reverse':
            describe = "\n世界が反転する。。。  The world is reversed...."
            self.reverse = not self.reverse
        elif self.opened[1] == '+2':
            self.stuck += 2
        elif self.opened[1] == '+4':
            self.stuck += 4
        return describe
    
    def check_hand(self) -> list:
        cans = set()
        hand = self.hand_list[self.turn]
        for i in range(len(hand)):
            if hand[i] == ('🌈','+4'):
                if self.r_wildfour_anytime:
                    cans.add(str(i))
            elif self.stuck > 0:
                if hand[i][1] == '+2' and self.r_pile_draw:
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
            if self.stuck <= 0 or self.r_pile_draw:
                cans.add(str(hand.index(('🌈','+4'))))
        return sorted(cans)

    def setCard(self,num: None|int = None):
        if num == None:
            self.opened = self.deck.pop()
        else:
            self.opened = self.hand_list[self.turn].pop(num)
            return self.__cardeffect()
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

def config(conf_data,cpus):
    inp = selector("W: 人数変更(Change Player num), E: 手札枚数変更(Change Hand num), R: ルール変更(Change rule) Z: 戻る(Back) ->",{"Z","W","E","R"})
    if inp == "Z":
        pass
    elif inp == "W":
        inp = selector("人数入力 (2 ~ 9) 元値 : " + str(conf_data.player_num) + " ->",{'2', '3', '4', '5', '6', '7', '8', '9'})
        conf_data.player_num = int(inp)
        conf_data.score = [0]*conf_data.player_num
        cpus.changeCpuNum(conf_data.player_num-1)
    elif inp == "E":
        inp = selector("手札枚数入力 (3 ~ 10) 元値 : " + str(conf_data.card_num) + " ->",{'3', '4', '5', '6', '7', '8', '9', '10'})
        conf_data.card_num = int(inp)
    elif inp == "R":
        print("A: 1位決定後続行可否ルール変更, D: ドローカードの積み重ねルール変更, F: ドロー4の出せるタイミングルール変更")
        inp = selector("A: continue after 1st winner decide or not, D: be able to pile draw card or not, F: be able to set +4 card anytime or not(set only you have nothing else) ->",{"A","D","F"})
        if inp == "A":
            inp = selector("1位が決まった後もゲームを続けますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.r_after_decide = True
            else:
                conf_data.r_after_decide = False
        elif inp == "D":
            inp = selector("ドローカードを積み重ねられるようにしますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.r_pile_draw = True
            else:
                conf_data.r_pile_draw = False
        elif inp == "F":
            inp = selector("ドロー4をいつでも出せるようにしますか? Y/N ->",{"Y","N"})
            if inp == "Y":
                conf_data.r_wildfour_anytime = True
            else:
                conf_data.r_wildfour_anytime = False
    return

def main(data):
    if len(data.hand_list[0]) == 0:
        print("すでに試合は終了しています。 The game is already done.")
        print("次のゲームへ進む場合はRを選んでください。 Select \'R\' to restart.")
        return data.score
    print("q : 一時停止 (pause), c : コメント (comment)")
    print("UNO : 最後の１枚になったとき、打ち込む必要があります。 you have to type this word if you will have last one card.")
    if data.turn == 0:
        print("あなたからスタートします。 You are starter.")
    else:
        print("\n場のカード : " + str(data.opened))
        print(str(data.turn) + " 番プレーヤーからスタートします。 Start from player" + str(data.turn) + ".")
    print("進めるにはキーを押してください。 Press any key to continue.")

    turn_start = time()

    while len(data.hand_list[0]) != 0:
        data.cpus.checkSituation(data.hand_list,data.score)
        #data.cpus.actRecieve()

        #if msvcrt.kbhit() and msvcrt.getch() == b'q':
        #    break
        key = msvcrt.getch() #キーウェイト 各ターンボタン押すまで待つ
        if key == b'q':
            break
        elif key == b'c':
            #inp = selector("コメントしますか? Do you want to say anything? Y/N ->",{"Y","N"})
            #if inp == "Y":
            inp = selector("0:コメントしない, 1:褒め称える, 2:喜ぶ, 3:煽る, 4:怒る ->",{"0","1","2","3","4","5"})
            if inp == "0":
                pass
            elif inp == "1" or inp == "3":
                person = selector("どのPlayerに？ " + '/'.join(map(str,list(range(1,data.player_num+1)))) + " ->",set(map(lambda x: str(x),list(range(1,data.player_num+1)))))
                print("Player"+person+ ("さん、やるじゃん！" if inp == "1" else "、 まじで草ww"))
                if inp == "1":
                    data.cpus.actRecieve(1, int(person)-1)
                    data.cpus.makeLine(int(person))
                else:
                    data.cpus.actRecieve(0, int(person)-1)
                    data.cpus.makeLine(int(person))
            elif inp == "2":
                print("やったね～！")
                data.cpus.actRecieve(0.2)
                data.cpus.makeLine()
            elif inp == "4":
                print("おいこら")
                data.cpus.actRecieve(0.7)
                data.cpus.makeLine()
            else:
                print("はい。リセット～～。")
                data.cpus.makeLine()

        describe = ""
        hand = data.hand_list[data.turn] #リストは参照渡し
        cans = data.check_hand() #出せる手札の番号

        if data.turn == 0:
            cpus.setTurnTime(time() - turn_start)
            print("\n場のカード : " + str(data.opened) + ("  スタック (stuck) : " + str(data.stuck) if data.stuck != 0 else ""))
            if data.opened[0] == '🌈':
                print("     color : " + data.color)
            print("\nあなたのターンです。 Your turn")
            print("手札 (hand) : " + ",".join(map(str,hand)) + "\n")
            turn_start = time()
        else:
            print("\nPlayer " + str(data.turn))
            data.uno = data.cpus.cpus[data.turn-1].makeAct() #Unoチェック

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
                    data.drawDeck(data.stuck)
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
                                describe = data.setCard(-1)
                                print("Set " + str(data.opened))
                else:
                    describe = data.setCard(int(inp))
                    print("Set " + str(data.opened))
            else:
                #cansにskip, reverseがあれば優先。色変え（wild除く）の選択肢がある場合、手札にその色が多ければ優先。次に数字。最後にwild。
                #残り手札2枚以下のプレーヤーがいる場合、wild優先。
                describe = data.setCard(int(cans[0])) # -> 経験値で更新したい, grave情報で変更させたい
                data.cpus.actRecieve(0.7, data.turn) #自分のターンが来たらうれしいよね？
                print("Set " + str(data.opened))
        elif data.stuck > 0:
            print(str(data.stuck)+"枚カードを引きます。 Draw "+str(data.stuck)+" cards.")
            data.drawDeck(data.stuck)
            data.stuck = 0
            if data.turn != 0:
                data.cpus.actRecieve(0.1, data.turn)
                data.cpus.makeLine(data.turn)
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
                        describe = data.setCard(-1)
                        print("Set " + str(data.opened))
            else:
                data.cpus.actRecieve(0.3, data.turn)
                cans = data.check_hand()
                if len(cans) != 0:
                    data.cpus.actRecieve(0.8, data.turn)
                    data.cpus.makeLine(data.turn)
                    describe = data.setCard(-1)
                    print("I draw and set this. " + str(data.opened))

        #残り枚数・Unoチェック
        remain = len(hand)
        if remain == 0:
            if data.rank == 1:
                rank = "1st"
                #スタックの確認
                if data.stuck > 0:
                    data.changeTurn()
                    print(("あなたは" if data.turn == 0 else "Player"+str(data.turn)) +"は"+str(data.stuck)+"枚カードを引きました。"+ ("You" if data.turn == 0 else "Player"+str(data.turn)) +" drew "+str(data.stuck)+" cards")
                    data.drawDeck(data.stuck)
                    data.reverse = not data.reverse
                    data.changeTurn()
                    data.reverse = not data.reverse
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
            data.cpus.checkSituation()
            if data.turn == 0:
                print("\n🎉あなたは " + str(data.rank) + "位です。 In " + rank + " place is YOU!!!!!!!")
                data.cpus.actRecieve(0.1)
                data.cpus.makeLine()
                break
            else:
                print("\n🎉Player " + str(data.turn) + " の勝ち! In " + rank + " place is Player" + str(data.turn))
                data.cpus.actRecieve(0.9, data.turn)
                data.cpus.makeLine(data.turn)
                if data.rank == (data.player_num):
                    print("負けました。 You lose...")
                    data.turn = 0
            if (not data.r_after_decide) or (data.turn == 0):
                break
            data.rank += 1
        elif remain == 1:
            if data.turn == 0:
                if data.uno == False:
                    print("UNO と言い忘れたので1枚引きます。 Forgot to say \'UNO\'! Draw.")
                    data.drawDeck()
                    print("Get " + str(hand[-1]))
            else:
                if data.uno == True:
                    print("Uno!")
                else:
                    data.cpus.actRecieve(0.2, data.turn)
                    print("Player " + str(data.turn) + " : やってしまったのです。")
                    print("UNO と言い忘れたので1枚引きます。 Forgot to say \'UNO\'! Draw.")
        else:
            print("  残り (remain) : " + str(remain))

        #カード効果の発動（説明）
        if describe != "":
            print(describe)

        #ターン変更
        data.uno = False
        data.changeTurn()
        sleep(0.1)
    return data.score

if __name__ == "__main__":
    conf_data = ConfigArgs()
    cpus = CpuManager(conf_data.player_num-1)
    i = selector("Space: スタート (Start), C: 設定 (Setting), Q: やめる (Exit) ->", {" ","C","Q"})
    while i != "Q":
        if i == "C":
            config(conf_data, cpus)
            i = selector("Space: スタート (Start), C: 設定 (Setting), Q: やめる (Exit) ->", {" ","C","Q"})
        elif i == " ":
            print("🌈 = wild card")
            print("Game Start!")
            play_data = UnoPlay(conf_data,cpus)

            conf_data.score = main(play_data)

            print("スコア : " + str(conf_data.score[0]) + "Pt")
            for ind, pt in enumerate(conf_data.score[1:]):
                print("Player" + str(ind +1) + " : " + str(pt) + "Pt")
            print("*設定を変更すると途中のデータ, スコアは破棄されます。*")
            print("*If the setting is changed, data in progress will be discarded.*")
            i = selector("Z: 戻る (Continue), Space: 次へ (Next game), C: 設定 (Setting), Q: やめる (Exit) ->",{"Z"," ","C","Q"})
        elif i == "Z":

            conf_data.score = main(play_data)

            print("スコア : " + str(conf_data.score[0]) + "Pt")
            for ind, pt in enumerate(conf_data.score[1:]):
                print("Player" + str(ind +1) + " : " + str(pt) + "Pt")
            print("*設定を変更すると途中のデータは破棄されます。*")
            print("*If the setting is changed, data in progress will be discarded.*")
            i = selector("Z: 戻る (Continue), Space: 次へ (Next game), C: 設定 (Setting), Q: やめる (Exit) ->",{"Z"," ","C","Q"})