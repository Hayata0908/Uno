"""
ゲーム用AIのキャラ付けと成長
 ゲームキャラ設定などをexcelなどに記入する場合はpandasをインストール
0 : 底辺(消極的、思考なし)
1 : 考えなし（積極的、思考なし）
2 : 凡夫(思考あり)
3 : インテリ(消極的、思考あり)
4 : 最強最悪(積極的、思考あり)
積極的&怒り -> 殴りかかるとか
消極的&怒り -> 愚痴をこぼすとか
"""
from time import time
from random import random

def round(num:float):
    if 0<num<=1:
        return num
    elif num<=0:
        return 0.00000001
    else:
        return 1

class AI():
    def __init__(self,pattern:list[float]) -> None:
        """AIもどき感情モデル+感情表現(深層学習とか重いからTBDリストに入れとく)
        
        pattern: [感情起伏(0~1), 感情の現れやすさ積極性(0~1)] #思考能力は場合によって専門性が必要なためTBD
        """
        self.pattern = list(map(round, pattern)) #patternリストに0があれば0.00000001にする
        #社会的ルール/自立性の学習（特定動作と状況で恥、疑惑など意思を持つ、目的を持ちそれに向かって行動する）感情モデルではないがTBD
        self.learn = [0.2+(random()*0.5)] #集中力
        #瞬間的な快度、覚醒度、心の余裕(快への傾きやすさ)を正規表現(0~1) 0.5,0.5が最も能力を発揮できる?
        self.feel: list[float] = [0.2+(random()*0.5), 0.2+(random()*0.5), 0.00000001+(random()*0.2)] #0.2~0.7でスタート
        """快/不快(嫌), 覚醒/睡眠
            快&覚醒: 喜び/興味/感嘆(容認)                   すぐに現れる感情
            快&睡眠: 眠り/平穏/安心
            覚醒が最も高い: 驚愕                            すぐに現れる感情
            覚醒が次に高い: 警戒
            不快&覚醒: 悲痛/憎悪/憤怒/恐怖/恥                すぐに現れる感情
                怒りと恐怖は似ているが、行動はまったくの別物。覚醒度や相手の明確さで変わる？
            不快&睡眠: 退屈/悲哀/心配
        """
        self.natural = self.feel[0] #自然な状態(与えられる影響に対する期待値) 長期的な快度
        self.start = time() #生まれた時間 感情の変化量に使う
        self.previous = self.start
        self.lap = 0.1
        self.u_time = 10

    def changeFeel(self,situation:float,effect:float):
        """感情の変更
            状況と効果、感情起伏パターンから新たな快度を作成し、快度を更新。
            現在の快度との差異によって覚醒度を変更
            situation:  相手より優位か, 環境は快適か(暑い寒いなどの快度)[0~1] →心の余裕
            effect:  与えられた影響(不快なセリフ,待たされているなど)[0~1] #不快~快
            
            感情変化値 : (situation+effect-self.natural*2)/2*self.pattern[0]

            self.pattern[0]: 感情起伏
        """
        situation = round(situation)
        effect = round(effect)

        elapsed = (time() - self.start) / self.u_time + 50 #経過量
        lap = (time() - self.previous) / self.u_time #ラップタイム
        if lap >= 0.1:
            self.lap = lap
        self.natural = (self.natural*elapsed+self.feel[0])/(elapsed+1) #経過量が大きいほど自然な状態が固定される
        gradient_feel = (situation+effect-self.natural*2)*self.pattern[0] #期待値との差異

        
        if (self.feel[0] > 0.7 and (self.feel[1] < 0.3)) or (self.feel[0] < 0.3 and (self.feel[1] > 0.7)): #快適で睡眠時と不快で覚醒時
            self.feel[2] = (self.feel[2]+self.natural)/2 #自然な状態で心の余裕が変化
            self.pattern[0] = (self.pattern[0]*elapsed+self.feel[0])/(elapsed+1) #自然な状態で感情起伏が変化 (変化量は経過量に反比例)
        
        if gradient_feel < 0:
            gradient_feel += (self.feel[2]*self.pattern[0]) #マイナスのとき、心の余裕を発揮
            if gradient_feel > 0:
                gradient_feel = 0

        self.feel[0] = round(gradient_feel+self.feel[0])
        self.feel[1] = round((self.feel[1]+abs(gradient_feel)/self.pattern[0]+self.learn[0])/(2+self.lap)) #呼び出されるラップが短いほど覚醒度が高い
        #print(str(self.lap) + " " + str(self.feel[1]))
        self.previous = time()

    def changeMove(self):
        """行動の変更
        覚醒度が0.1以下の時: 睡眠
        覚醒度が0.1~0.2の時: 従順
        覚醒度が0.2~0.4の時: 比較的睡眠
        覚醒度が0.4~0.6の時: 不快なことに対処、快を継続、増大させる(max能力発揮)
        覚醒度が0.6~0.8の時: 比較的覚醒
        覚醒度が0.8~0.9の時: 緊張
        覚醒度が0.9以上の時: 驚愕
        """
        if self.feel[1]<=0.1:
            return "睡眠"
        elif self.feel[1]<=0.2:
            return "従順"
        elif self.feel[1]<=0.4:
            if self.feel[0] <= 0.3:
                return "悲哀"
            elif self.feel[0] >= 0.7:
                return "安心"
            else:
                return "退屈"
        elif self.feel[1]<=0.6:
            if self.feel[0] <= 0.3:
                return "不安"
            elif self.feel[0] >= 0.7:
                return "愉快"
            else:
                return "平穏"
        elif self.feel[1]<=0.8:
            if self.feel[0] <= 0.3:
                if self.pattern[1]>0.5:
                    return "憤怒"
                else:
                    return "恐怖" #逃避
            elif self.feel[0] >= 0.7:
                if self.pattern[1]>0.5:
                    return "歓喜"
                else:
                    return "感嘆"
            else:
                return "興味"
        elif self.feel[1]<=0.9:
            return "緊張"
        else:
            return "驚愕"
