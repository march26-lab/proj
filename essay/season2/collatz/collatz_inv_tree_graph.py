import matplotlib.pyplot as plt

def main():
    MAX_DEPTH = 18
    LABEL_MAX_DEPTH = 6

    draw_collatz_tree(MAX_DEPTH, LABEL_MAX_DEPTH)

def build_collatz_tree(max_depth):
    edges = []
    layers = {0: [1]}
    queue = [1]
    
    for depth in range(max_depth):
        next_queue = []
        for number in queue:
            # 2倍の操作
            child_mult = number * 2
            edges.append((number, child_mult))
            next_queue.append(child_mult)
            
            # 逆3n+1の操作
            if number % 6 == 4 and number != 4:
                child_inv = (number - 1) // 3
                edges.append((number, child_inv))
                next_queue.append(child_inv)
                
        queue = next_queue
        layers[depth + 1] = queue
        
    return layers, edges

def draw_collatz_tree(max_depth, label_max_depth):
    layers, edges = build_collatz_tree(max_depth)
    
    # 各ノードの座標 (x, y) を計算
    pos = {}
    for depth, nodes in layers.items():
        n_nodes = len(nodes)
        for i, node in enumerate(nodes):
            # 各層で中心を0として横に均等配置
            x = i - (n_nodes - 1) / 2.0
            y = -depth
            pos[node] = (x, y)
            
    plt.figure(figsize=(10, 6))
    
    # エッジ（線）をまとめて高速描画
    edge_x = []
    edge_y = []
    for parent, child in edges:
        if parent in pos and child in pos:
            px, py = pos[parent]
            cx, cy = pos[child]
            # Noneを挟むことで、複数の離れた線分を一度のplotで効率よく描画
            edge_x.extend([px, cx, None])
            edge_y.extend([py, cy, None])
            
    plt.plot(edge_x, edge_y, color='gray', linewidth=0.6, alpha=0.6)
    
    # ノードの描画（深さに応じて切り替え）
    for depth, nodes in layers.items():
        if depth <= label_max_depth:
            # 指定深さまでは数値をボックス付きで表示
            for node in nodes:
                if node in pos:
                    x, y = pos[node]
                    plt.text(x, y, str(node), fontsize=9, ha='center', va='center',
                             bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='skyblue', alpha=0.8))
        else:
            # 指定を超える深さは小さな点（散布図）でシルエットを表現
            xs = [pos[node][0] for node in nodes if node in pos]
            ys = [pos[node][1] for node in nodes if node in pos]
            plt.scatter(xs, ys, s=5, color='dodgerblue', alpha=0.7)

    plt.title(f"Collatz Inverse Tree (Depth: {max_depth})", fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
