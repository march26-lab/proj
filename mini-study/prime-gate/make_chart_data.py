import json

class OddNumberFlags:
    """1 <= n < stop の奇数に対するフラグリスト"""
    def __init__(self, stop):
        self.flags = bytearray(stop // 2)

    def add(self, odd_number):
        self.flags[odd_number // 2] = 1

    def is_flagged(self, odd_number):
        return self.flags[odd_number // 2]

    def flagged_numbers(self, start = 1, stop = None):
        """start <= n < stop の範囲にあるフラグ済み奇数を列挙する"""
        for i in range(start // 2,
                       len(self.flags) if stop is None else stop // 2):
            if self.flags[i]:
                yield i * 2 + 1

class Clause:
    """ASM句 C_q(p)"""
    def __init__(self, qm, p, d_list):
        self.qm = qm
        self.p = p
        self.d_list = d_list

class ModuloGateTracer:
    """法30下での関門(LTP要因に該当するpを除く)の振る舞いを追跡する"""
    def __init__(self, qm, p_start, p_stop):
        assert p_start in (7, 11)
        assert qm in (11, 17, 29)
        self.qm = qm
        self.p_start = p_start
        self.p_stop = p_stop
        self.odd_primes = make_odd_primes(p_stop)

    def trace(self):
        post_ASM = []
        logged_cycles = set()

        for p in self.odd_primes.flagged_numbers(start=self.p_start, stop=self.p_stop):
            cycle = p // 30 + 1
            if cycle not in logged_cycles:
                print(f'qm={self.qm}, cycle={cycle}')
                logged_cycles.add(cycle)

            if self.odd_primes.is_flagged(p - 2): # 上側双子素数をスキップ
                continue

            pre_ASM = tuple(post_ASM)
            Dp = {}
            r_list = list(self.odd_primes.flagged_numbers(start=3, stop=p))

            for r in reversed(r_list): # Dpがdの昇順になるように
                d = p - r
                if d == 4: # 4はDpに含めない
                    continue
            
                qm_d = self.qm + d
                maybe_prime = not (
                    qm_d % 2 == 0
                    or qm_d % 3 == 0
                    or qm_d % 5 == 0
                )
                Dp[d] = maybe_prime

            # 自動通過に寄与する前ASM句のdを集める
            auto_pass_dset = set()
            for C in pre_ASM:
                if all(d in Dp for d in C.d_list):
                    auto_pass_dset.update(C.d_list)

            # 自動通過でなければASM句を追加
            C_cand = Clause(self.qm, p,
                            [d for d, maybe_prime in Dp.items() if maybe_prime])
            if not auto_pass_dset:
                assert C_cand.d_list
                post_ASM.append(C_cand)

            self.update_info(p, pre_ASM, Dp,
                             C_cand, auto_pass_dset, post_ASM)
            
    def update_info(self, p, pre_ASM, Dp, C_cand, auto_pass_dset, post_ASM):
        """注目関門の集計処理"""
        pass # 具体的には継承クラスで行う。ここでは何もしない

class GateChartTracer(ModuloGateTracer):
    def __init__(self, qm, p_view_start, p_view_stop, d_view_start, d_view_stop):
        # 関門チャートはセルの表示ウインドウとは別に、必ずp=11から計算を始める
        super().__init__(qm, 11, p_view_stop)
        self.p_data_list = []
        self.p_view_start = p_view_start
        self.d_view_start = d_view_start
        self.d_view_stop = d_view_stop
        
    def update_info(self, p, pre_ASM, Dp, C_cand, auto_pass_dset, post_ASM):
        """注目関門の集計処理 : p < self.p_stop は保証されている"""
        # dに紐付く前ASM句の数
        C_count_at_d = {}
        for C in pre_ASM:
            for d in C.d_list:
                if d in C_count_at_d:
                    C_count_at_d[d] += 1
                else:
                    C_count_at_d[d] = 1

        # この関門で追加されうるASM句のdには0を対応させる
        for d, maybe_prime in Dp.items():
            if maybe_prime and (d not in C_count_at_d):
                C_count_at_d[d] = 0

        # Dp要素または上で句数が付与されたdのリスト
        union_d_list = sorted(set(Dp) | set(C_count_at_d))

        d_infos = []
        auto_pass_any = False
        
        for d in union_d_list:
            d_info = {'value': d}

            if d in Dp:
                d_info['maybe_prime'] = Dp[d]

            if d in auto_pass_dset:
                d_info['auto_pass'] = True
                auto_pass_any = True

            if d in C_count_at_d:
                d_info['clause_count'] = C_count_at_d[d]

            if self.d_view_start <= d < self.d_view_stop:
                d_infos.append(d_info)

        if p >= self.p_view_start:
            self.p_data_list.append({'value': p,
                                     'auto_pass': auto_pass_any,
                                     'd': d_infos})

def main():
    P_VIEW_MIN, P_VIEW_MAX = 11, 240
    D_VIEW_MIN, D_VIEW_MAX = 6, 110

    qm_data_list = []
    
    for qm in [11, 17, 29]:
        tracer = GateChartTracer(qm, P_VIEW_MIN, P_VIEW_MAX + 1,
                                 D_VIEW_MIN, D_VIEW_MAX + 1)
        tracer.trace()
        qm_data_list.append({'value': qm,
                             'p': tracer.p_data_list})

    chart_data = {'qm': qm_data_list}
    with open('chart_data.json', 'w') as f:
        json.dump(chart_data, f, indent=2)

def make_odd_primes(stop):
    """n < stop の奇素数フラグリストを作成する"""
    odd_composites = OddNumberFlags(stop)
    odd_primes = OddNumberFlags(stop)

    for odd in range(3, stop, 2):
        if odd_composites.is_flagged(odd):
            continue

        odd_primes.add(odd)
        
        for multiple in range(odd * 3, stop, odd * 2):
            odd_composites.add(multiple)

    return odd_primes

if __name__ == "__main__":
    main()
