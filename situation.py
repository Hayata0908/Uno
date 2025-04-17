"""シチュエーションメーカー
    自動でランダムなシチュエーションを生成する。
"""
import random

class Situation():
    def __init__(self) -> None:
        # シチュエーションのカテゴリ
        self.time = {#覚醒度に与える影響
            "街角にまばらに人が見え始めたころ":0.4,
            "人々が足早に喧噪の中を突き進むころ":0.6,
            "太陽がちょうど真上に上ったころ":0.9,
            "街の音が一層はっきりと聞こえるころ":1,
            "街に明かりがともり始めるころ":0.7,
            "カレーのにおいが漂うころ":0.5,
            "誰もが眠りについたころ":0.2
            }
        self.weather = {#快度に与える影響*0.4で使用
            "虹がかかっている。": 1,
            "雲ひとつない空が広がっている。":0.9,
            "空にはさまざまな形の雲が浮かんでいる。":0.8,
            "どんよりとした灰色の空がみえる。":0.5,
            "しんしんと雨が降っている。":0.6,
            "雨は降りやむ気配がない。":0.3,
            "遠くで雷鳴が轟いている。":0.1,
            "雪がまばらにちらついている。":0.7
            }
        self.serenity = {#快度に与える影響*0.6で使用
            "物音ひとつしない。":0.7,
            "話し声がかすかに聞こえる。":0.8,
            "鳥のさえずりが響いている。": 0.9,
            "ラジオから穏やかな音楽が流れている。":0.7,
            "人々の活気にあふれた喧噪が聞こえる。":0.5,
            "しきりに電車が通って騒がしい。":0.2
            }
        self.openness = {#快度に与える影響*0.3で使用
            "緑に囲まれたけもの道で":0.7,
            "古びた本の並ぶ書庫で":0.7,
            "使われていない教室の一角で":0.3,
            "ぬいぐるみが並べられたベッドの上で":0.6,
            "高い壁に囲まれた場所で":0.1,
            "雑多にものが置かれたオフィスで":0.5,
            "特別に用意されたリングの上で":0.4
            }
        self.temp = {#快度に与える影響
            "手がかじかみ凍えている。":0.2,
            "薄手のアウターに身を包んでいる。":0.8,
            "袖をまくり襟を広げている。":0.8,
            "吹き出る汗をぬぐっている。":0.4,
            "乾燥した暑さに息が詰まりそうだ。": 0.2
            }
        
        self.situation = []

    def generate_random_scenario(self):
        scenario = {
            "time": random.choice(list(self.time.keys())),
            "weather": random.choice(list(self.weather.keys())),
            "対象": "\nあなたたちは",
            "openness": random.choice(list(self.openness.keys())),
            "temp": random.choice(list(self.temp.keys())),
            "場所": "\nここでは",
            "serenity": random.choice(list(self.serenity.keys())),
        }
        self.situation = {
            "time": self.time[scenario["time"]],
            "weather": self.weather[scenario["weather"]],
            "serenity": self.serenity[scenario["serenity"]],
            "temp": self.temp[scenario["temp"]],
            "openness": self.openness[scenario["openness"]],
        }
        return [" ".join([f"{value}" for value in scenario.values()]),self.situation]

if __name__ == "__main__":
    # 使用例
    situation = Situation()
    # ランダムにシチュエーションを生成（例: 3つ）
    scenarios = [situation.generate_random_scenario() for _ in range(3)]

    # 結果を表示
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}: {scenario[0]} \nしかし状況に関係なくその時はやってくる。 今、ゲームが始まる！\n")
        print(scenario[1])
