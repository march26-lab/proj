import json

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button

class Chart:
    def __init__(self, org_data, p_view_min, d_view_min, d_view_max):
        p_list = [p_data_list['value'] for p_data_list in org_data['qm'][0]['p']]
        self.p_list = [p for p in p_list if p >= p_view_min]
        self.d_list = list(range((d_view_min + 1) // 2 * 2, (d_view_max + 2) // 2 * 2, 2))
        self.chart_data = self.convert_chart_data(org_data)

    def convert_chart_data(self, org_data):
        conv_data = []
        p_set = set(self.p_list)
        d_set = set(self.d_list)

        for q_data in org_data['qm']:
            p_dict = {}
            for p_data in q_data['p']:
                p = p_data['value']
                if p not in p_set:
                    continue
                
                d_dict = {}
                for d_data in p_data['d']:
                    d = d_data['value']
                    if d in d_set:
                        d_dict[d] = d_data

                p_dict[p] = {'auto_pass': p_data['auto_pass'], 'd_dict': d_dict}

            conv_data.append({'q': q_data['value'], 'p_dict': p_dict})

        return conv_data
    
    def draw_chart(self):
        self.current_index = 0
        self.fig, self.ax = plt.subplots(figsize=(12, 8))

        # チャート領域の下にボタン専用スペースを確保
        self.fig.subplots_adjust(
            left=0.08,
            right=0.98,
            top=0.88,
            bottom=0.10
        )

        ax_prev = self.fig.add_axes((0.34, 0.02, 0.12, 0.04))
        ax_next = self.fig.add_axes((0.54, 0.02, 0.12, 0.04))

        btn_prev = Button(ax_prev, 'Prev')
        btn_next = Button(ax_next, 'Next')    

        # ボタンに関数を紐付け
        btn_prev.on_clicked(self.go_prev)
        btn_next.on_clicked(self.go_next)

        # 初回表示（最初のページを描画）
        self.update_chart()

        plt.show()

    # 「戻る」ボタンが押されたときの処理
    def go_prev(self, event):
        if self.current_index > 0:
            self.current_index -= 1
        self.update_chart()

    # 「次へ」ボタンが押されたときの処理
    def go_next(self, event):
        if self.current_index < len(self.chart_data) - 1:
            self.current_index += 1
        self.update_chart()

    # チャートを更新する関数の定義
    def update_chart(self):
        data = self.chart_data[self.current_index]
        q = data['q']
    
        # 画面全体のタイトルを変更
        self.fig.suptitle(f"Gate Chart [q equiv {q} (mod 30)]", fontsize=16, fontweight='bold')

        # チャートを更新
        self.ax.clear()

        num_rows = len(self.p_list)
        num_cols = len(self.d_list)

        # 背景色の定義
        COLOR_WHITE = "#ffffff"
        COLOR_BLACK = "#000000"
        COLOR_RED = "#ff0000"
        COLOR_ORANGE = "#fce4d6"  # 薄いオレンジ
        COLOR_BLUE = "#bdd7ee"    # 薄いブルー
        
        # セル背景と枠線の描画
        for i in range(num_rows):
            p = self.p_list[i]
            p_item = data['p_dict'].get(p, None)
            
            for j in range(num_cols):
                d = self.d_list[j]
                d_item = None if p_item is None else p_item['d_dict'].get(d, None)
                
                # セルの背景色を設定
                cell_color = COLOR_WHITE
                if p_item is not None and d_item is not None and 'maybe_prime' in d_item:
                    cell_color = COLOR_ORANGE if d_item['maybe_prime'] else COLOR_BLUE
                        
                rect = patches.Rectangle((j, i), 1, 1, facecolor=cell_color, edgecolor="gray", linewidth=0.8)
                self.ax.add_patch(rect)
        
                # 句数が存在すれば中央に値を描画
                clause_count = None if d_item is None else d_item.get('clause_count', None)
                if clause_count is not None:
                    self.ax.text(j + 0.5, i + 0.5, str(clause_count),
                                 ha='center', va='center', fontsize=8, color='gray')

                # 自動通過に寄与したセルは赤く太い枠線にする
                auto_pass = False if d_item is None else d_item.get('auto_pass', False)
                if auto_pass:
                    highlight_rect = patches.Rectangle(
                        (j, i), 1, 1,
                        fill=False,         # 中身を塗りつぶさない（数字が透ける）
                        edgecolor=COLOR_RED,
                        linewidth=1.2,
                        zorder=3            # テキストや他のセルの上に表示
                    )
                    self.ax.add_patch(highlight_rect)                    
    
        # 軸ラベル・見出しの調整
        # 軸の範囲と反転（行は上から下に向かって増えるように）
        self.ax.set_xlim(0, num_cols)
        self.ax.set_ylim(num_rows, 0)

        # 目盛り位置の設定
        self.ax.set_xticks([x + 0.5 for x in range(num_cols)])
        self.ax.set_yticks([y + 0.5 for y in range(num_rows)])
        
        # 目盛りラベルの設定
        x_list = [str(d) if d in (6, 8) or d % 10 == 0 else "" for d in self.d_list]
        
        self.ax.set_xticklabels(x_list, fontsize=8)
        self.ax.set_yticklabels(self.p_list, fontsize=8)

        # X軸の目盛りを上側に表示
        self.ax.xaxis.tick_top()
        self.ax.xaxis.set_label_position('top')
        
        # 軸ラベル（p, d）の配置
        self.ax.set_xlabel('d', fontsize=14, labelpad=15, fontweight='bold')
        self.ax.set_ylabel('p', fontsize=14, labelpad=15, rotation=0, fontweight='bold', va='center')

        # 自動追加関門は縦軸ラベルを目立たせる
        for label in self.ax.get_yticklabels():
            p = int(label.get_text())
            p_item = data['p_dict'].get(p, None)
            auto_pass = False if p_item is None else p_item.get('auto_pass', False)
            if auto_pass:
                plt.setp(
                    label,
                    color=COLOR_WHITE,
                    fontweight="bold",
                    bbox=dict(
                        facecolor=COLOR_BLACK, edgecolor="none", boxstyle="square,pad=0.3"
                    ),
                )
        
        # 不要な枠線（外枠）を消して表っぽく見せる
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # アスペクト比を等しくして正方形のセルにする
        self.ax.set_aspect('equal')

        # 画面を再描画
        plt.draw()

def main():
    P_VIEW_MIN = 11
    D_VIEW_MIN = 6
    D_VIEW_MAX = 110

    with open('chart_data.json', 'r') as f:
        load_data = json.load(f)

    chart = Chart(load_data, P_VIEW_MIN, D_VIEW_MIN, D_VIEW_MAX)

    chart.draw_chart()

if __name__ == "__main__":
    main()
