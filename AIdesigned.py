import numpy as np
from random import random
from situation import Situation

def round(num:float):
    if 0<num<=1:
        return num
    elif num<=0:
        return 0.00000001
    else:
        return 1

class EmotionModel:
    def __init__(self, traits=None, bio_factors=None):
        """
        感情モデルの初期化
        :param traits: 性格特性 (辞書形式)
        :param bio_factors: 生物的要因 (辞書形式)
        """
        # 影響要因のリスト
        self.factor_keys = {
            #五感(全部)
            "sencse": ["hearing", "eyesight", "touch", "smell", "taste"],
            #環境（全部）->天気など明るいとpleasantの絶対増加、テスト前の緊張なども　役割->与えられるとpleasantの絶対増加
            "situation": ["time", "weather", "serenity", "temp", "openness"],#serenity:静けさ time: 睡眠からの時間経過で不満増加、変化率の計算
            #認知（全部）
            "cognitive": ["freely", "pain", "role", "relationship"], #自由度->強制されたと感じるか(pleasant、awakening) 傷->健康だと0.5傷があると下がる
            #行動(択一: pleasantを高め, awakeningを適応値にするように)
            "behavior": ["eat", "sleep", "exercise", "talk", "interact", "play", "relax", "challenge", "escape","consider"]
        }

        # 最新の影響要因を保存する（変更されなかった場合に使用）
        self.latest_factors = {key: np.random.rand(len(values)) for key, values in self.factor_keys.items()}

        print(self.latest_factors)

        # **性格特性と生物的要因をユーザー入力として受け取る**
        self.traits = traits if traits else {
            "nervously": 0.2, #神経質（awakeningの増加割合）
            "optimism": 0.6, #楽観性（pleasantの増加割合）
            "extraversion": 0.5, #外向性（表現の大きさ）
            "curiosity": 0.7, #好奇心->時間がたつほど下がりやすい（挑戦のpleasant）
            "selfefficacy": 0.3, #自己効力感 トラウマ、過去の経験（pleasant、selfcontrolの絶対増加）
            "selfesteem": 0.6, #自分への満足度->幸福度、自己効力感、見た目などで変化（pleasantの絶対増加、selfcontrolの低下）
            "relationship": 0.5, #社会とのつながり->発話で増加（pleasant、awakening、道徳観の増加）
            "moral": 0.7 #含宗教,教育（selfcontrolの絶対増加）
        }

        self.bio_factors = bio_factors if bio_factors else {
            "hormon": 0.5, #0.5 pleasant&awakeningで増加（自己効力感、外向性の増加）
            "rate": 0.6, #心拍数 0 awakening、運動で増加（awakeningの増加）
            "bloodsugar": 0.6, #0.2 血糖値->食事で増加（急激な増加でawakeningの低下）
            "stress":0.2, #感情の不安定性（pleasant、selfcontrolの低下、awakeningの増加）
            "stamina":1 #行動への余力
        }


        #不満->pleasant、selfcontrolの絶対低下、awakeningの増加割合
        self.desire = {
            "fatigue":0.00000001, #疲労 makes 睡眠
            "libido":0.00000001, #含む 排泄
            "hungry":0.00000001, #飲食
            "danger":0.00000001, #安全
            "reject":0.00000001, #承認
            "stagnate":0.00000001 #自己実現
        }

        # **現在の感情ベクトル**
        self.current_emotion = {"pleasant": 0.5, "awakening": 0.5, "selfcontrol": 0.5}

        # **感情減衰率 (感情ごとに異なる減衰)**
        self.decay_rates = {"pleasant": 0.05, "awakening": 0.07, "selfcontrol": 0.03}

        self.behavior_cost = {
            "eat": 1-self.desire["hungry"], #hungry,stamina ->食事量分増加 bloodsuger->増加
            "sleep": -self.desire["fatigue"]+self.current_emotion["awakening"], #fatigue,stamina ->回復
            "exercise": 1-self.bio_factors["stamina"], #stamina ->減少
            "talk": 1-self.traits["extraversion"], #stamina ->減少 reject -> 減少
            "interact": 1.1-self.traits["extraversion"], #stamina ->減少 reject -> 減少
            "play": 0.5-self.bio_factors["stamina"], #stamina ->減少
            "relax": self.current_emotion["awakening"], #awakening ->減少 fatigue,stamina ->増加
            "challenge": 1-self.bio_factors["stamina"]*self.traits["curiosity"]-self.desire["reject"], #stamina ->減少 stagnate ->減少
            "escape": 1-self.bio_factors["stamina"]*self.desire["danger"]+self.current_emotion["selfcontrol"], #danger ->減少
            "consider": -max(self.desire.values()) #desier ->増加
        }

        # 各要因がどのベクトルに影響するかを設定
        self.factor_weight = {
            "pleasant": ["weather", "serenity", "temp", "roll", "openness", "freely", "pain", "relationship"],
            "awakening": ["騒音", "疲労", "心拍数", "アドレナリン", "時間帯"],
            "selfcontrol": ["自己効力感", "不安", "ストレス", "道徳観", "周囲の雰囲気"]
        }

    def update_external_factors(self, **factor_inputs):
        """
        外部からの影響を受けて感情ベクトルを更新
        """
        new_emotion = self.convert_factors2vector(**factor_inputs)
        
        for key in self.current_emotion:
            self.current_emotion[key] = np.clip(new_emotion[key], 0, 1)

    def update_internal_state(self):
        """
        内部要因の更新 (バイアス、ホルモンバランス、感情減衰)
        """
        # **バイアスの更新**

        # **感情の減衰**
        for key in self.current_emotion:
            self.current_emotion[key] *= (1 - self.decay_rates[key])
            self.current_emotion[key] = np.clip(self.current_emotion[key], 0, 1)

    def save_situation(self, **situation):
        for param in self.factor_keys["situation"]:
            if param in situation and (situation[param] is not None):
                self.latest_factors["situation"][param] = np.array(situation[param])

    def convert_factors2vector(self, **factor_inputs)->dict:
        """
        影響要因を受け取って感情ベクトルを計算する
        変更がない場合は latest_factors を使用
        :return: {"pleasant": Δpleasant, "awakening": Δawakening, "selfcontrol": Δselfcontrol}
        """
        for category in self.factor_keys.keys():
            if category in factor_inputs and factor_inputs[category] is not None:
                self.latest_factors[category] = np.array(factor_inputs[category])
            else:
                factor_inputs[category] = self.latest_factors[category]

        # **影響要因の合計**
        total_factors = sum(np.sum(factor_inputs[key]) for key in self.factor_keys.keys())

        # **感情ベクトルの計算**
        confort = np.clip(0.5 + (total_factors * 0.2), 0, 1)
        awakening = np.clip(0.5 + (np.sum(factor_inputs["physiological"]) * 0.2), 0, 1)
        selfcontrol = np.clip(0.5 + (np.sum(factor_inputs["cognitive"]) * 0.2), 0, 1)

        return {"pleasant": confort, "awakening": awakening, "selfcontrol": selfcontrol}

    def learn_from_experience(self, past_events):
        """
        過去の経験を学習し、影響要因の重みを調整
        :param past_events: 過去の影響要因の履歴 (リスト形式)
        """
        for event in past_events:
            category, impact = event["category"], np.array(event["impact"])
            if category in self.latest_factors:
                self.latest_factors[category] = (self.latest_factors[category] + impact) / 2

if __name__ == "__main__":
    # 使用例
    situation = Situation()
    scenarios = situation.generate_random_scenario()
    model = EmotionModel()
    model.update_external_factors(external=[0.2, 0.3], internal=[0.1, 0.2], cognitive=[0.4, 0.5], behavior=[0.3], physiological=[0.6, 0.4, 0.2, 0.1, 0.3])
    model.update_internal_state()
    model.learn_from_experience([{"category": "external", "impact": [0.1, 0.2]}])

    print(model.current_emotion)
