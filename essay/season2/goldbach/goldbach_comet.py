import matplotlib.pyplot as plt
import math

def main():
    n_max = 10000
    prime_set = make_prime_set(n_max + 1)
    prime_list = sorted(prime_set)

    dots = {}

    for n in range(4, n_max + 1, 2):
        for p in prime_list:
            q = n - p
            if q < p:
                break
            
            if q not in prime_set:
                continue

            if n in dots:
                dots[n].append((p,q))
            else:
                dots[n] = [(p,q)]

    show_dots(dots)

def make_prime_set(stop):
    primes = {2}
    for odd in range(3, stop, 2):
        primes.add(odd)

    for odd in range(3, stop, 2):
        if odd in primes:
            for multiple in range(odd * odd, stop, odd * 2):
                primes.discard(multiple)

    return primes

def show_dots(dots):
    x, y, z = [], [], []
    
    for n, pairs in dots.items():
        Gn = len(pairs)
        x.append(n)
        y.append(Gn)
        z.append(n / math.log(n) ** 2)

    fig, ax = plt.subplots()
    
    # 背景色の設定
    ax.set_facecolor('#1B1B3A')  # グラフ内部の背景
    fig.patch.set_facecolor('#0B0B1A')  # グラフ外側の枠部分の背景
    
    # 点のプロット
    plt.scatter(x, y, s=0.2, color='#FFFDD0', alpha=0.8)

    # 見積もり曲線のプロット
    plt.plot(x, z, color='#00FFFF', linewidth=1, alpha=0.9, linestyle='--')

    # 枠線や文字、目盛りの色を白系に変更（暗い背景で見えるようにする）
    ax.spines['top'].set_color('#444455')
    ax.spines['bottom'].set_color('#444455')
    ax.spines['left'].set_color('#444455')
    ax.spines['right'].set_color('#444455')

    ax.tick_params(colors='white')  # 目盛りの色
    ax.xaxis.label.set_color('white')  # X軸ラベルの色
    ax.yaxis.label.set_color('white')  # Y軸ラベルの色

    # 軸ラベルとタイトル
    ax.set_xlabel('n', fontsize=14)
    ax.set_ylabel('G(n)', fontsize=14)
    ax.set_title('Goldbach\'s Comet', color='white', fontsize=14)

    # グリッド線
    ax.grid(True, color='#88331b', alpha=0.5, linestyle='--')    

    plt.show()

if __name__ == "__main__":
    main()
