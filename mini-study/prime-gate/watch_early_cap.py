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
        self.R = ResidueClause(self)

class ResidueClause:

    """ASM剰余句 R_q(p)"""
    def __init__(self, C):
        self.qm = C.qm
        self.p = C.p
        self.dm_list = sorted(set([d % 30 for d in C.d_list]))
        self.B = BlockSet(self)

class BlockSet:
    """阻止p族集合"""
    def __init__(self, R):
        emptyset = frozenset()
        d2set = frozenset({7, 11, 17, 23, 29})
        d6set = frozenset({1, 11})
        d8set = frozenset({11, 13, 17, 23, 29})
        d12set = frozenset({7, 17})
        d14set = frozenset({11, 17, 19, 23, 29})
        d18set = frozenset({13, 23})
        d20set = frozenset({11, 17, 23, 29})
        d24set = frozenset({19, 29})
        d26set = frozenset({1, 11, 17, 23, 29})

        block_pm_table = {
            0: {11: emptyset, 17: emptyset, 29: emptyset},
            2: {11: d2set, 17: d2set, 29: d2set},
            6: {11: d6set, 17: d6set, 29:emptyset},
            8: {11: d8set, 17: emptyset, 29:d8set},
            12: {11: d12set, 17: d12set, 29: d12set},
            14: {11: emptyset, 17: d14set, 29: d14set},
            18: {11: d18set, 17: emptyset, 29:d18set},
            20: {11: d20set, 17: d20set, 29: d20set},
            24: {11: emptyset, 17: d24set, 29: d24set},
            26: {11: d26set, 17: d26set, 29:emptyset}
            }

        block_set = set()
        for d in R.dm_list:
            block_set.update(block_pm_table[d][R.qm])

        self.block_pm = set(block_set)

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

class GateCapTracer(ModuloGateTracer):
    def __init__(self, qm, p_stop):
        # CAPの追跡では、p=7から計算を始める
        super().__init__(qm, 7, p_stop)
        self.first_appears = {}
        
    def update_info(self, p, pre_ASM, Dp, C_cand, auto_pass_dset, post_ASM):
        """注目関門の集計処理 : p < self.p_stop は保証されている"""
        pm = p % 30
        if pm not in self.first_appears:
            # このp族のうち最初にCMP・LTP要因をクリアした関門のCAP
            b_list = [C.R.B.block_pm for C in post_ASM]
            CAP = set.intersection(*b_list)

            self.first_appears[pm] = {
                'cycle': p // 30 + 1,
                'p': p,
                'status': 'auto-pass' if auto_pass_dset else 'update-ASM',
                'CAP': CAP,
                'R': C_cand.R.dm_list,
                'B': C_cand.R.B.block_pm
                }

def main():
    CYCLE_MAX = 10

    results = {}
    
    for qm in [11, 17, 29]:
        tracer = GateCapTracer(qm, CYCLE_MAX * 30 + 1)
        tracer.trace()

        results[qm] = tracer.first_appears

    for qm, result in results.items():
        print(f'-------- result (qm={qm}) --------')
        if len(result) != 8:
            print('WARN: Insufficient p-families in the result')

        for pm, info in result.items():
            cycle, p, status, CAP, R, B = (info['cycle'], info['p'], info['status'],
                                           info['CAP'], info['R'], info['B'])
            print(f'[cycle={cycle}],',
                  f'p={p}≡{pm},',
                  f'{status},',
                  f'CAP={sorted(CAP)},',
                  f'R={R},',
                  f'B(R)={sorted(B)}'
                  )

        
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
