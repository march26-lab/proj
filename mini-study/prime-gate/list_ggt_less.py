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

def main():
    Q_MAX = 1000000

    # p+q-r < 2*Q_MAX まで素数判定できるようにする
    odd_primes = make_odd_primes(Q_MAX * 2)

    ggtless_count = 0
    stp_count = 0

    with open('ggt_less.txt', 'w') as f:
        for q in odd_primes.flagged_numbers(start=5, stop=Q_MAX + 1):

            if odd_primes.is_flagged(q + 2):
                stp_count += 1

            if is_ggt_less(q, odd_primes):
                ggtless_count += 1
                print(q, file=f)

    print(f'GGT-less={ggtless_count}, STP={stp_count}')

def is_ggt_less(q, odd_primes):
    """素数qがGGTレス素数か判定する"""
    for p in odd_primes.flagged_numbers(start=5, stop=q + 1):

        # qがGGTになるのを崩す、pより小さい相方rを探す
        has_larger_term = False

        for r in odd_primes.flagged_numbers(start=3, stop=p):
            s = p + q - r

            if odd_primes.is_flagged(s):
                has_larger_term = True
                break

        # qがp+qのGGTになれるケースが1つでもあれば
        # qはGGTレスではない
        if not has_larger_term:
            return False

    return True

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
