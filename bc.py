import plotly.graph_objects as go
import networkx as nx
import random

# 네트워크와 UNL 생성
nodes = 10
G = nx.Graph()
G.add_nodes_from(range(nodes))
for i in range(nodes):
    for j in range(i + 1, nodes):
        if random.random() < 0.3:
            G.add_edge(i, j)

# UNL 설정
unl = {node: random.sample(range(nodes), max(1, nodes // 3)) for node in G.nodes}

# 노드 위치 고정      
positions = nx.spring_layout(G)

# 합의 단계 시뮬레이션
frames = []
transaction_status = {i: "pending" for i in range(nodes)}

# 각 단계 상태 설정
def create_frame(status, step):
    node_colors = []
    for node in G.nodes():
        if status[node] == "pending":
            node_colors.append("gray")
        elif status[node] == "voting":
            node_colors.append("orange")
        elif status[node] == "confirmed":
            node_colors.append("green")
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = positions[edge[0]]
        x1, y1 = positions[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = positions[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[f"Node {node}" for node in G.nodes],
        marker=dict(
            size=20,
            color=node_colors,
            line=dict(width=2)
        ),
        textposition="top center")

    return go.Frame(
        data=[edge_trace, node_trace],
        name=f"Step {step}"
    )

# 초기 상태
frames.append(create_frame(transaction_status, 0))

# 1단계: 투표 시작
for node in transaction_status:
    transaction_status[node] = "voting"
frames.append(create_frame(transaction_status, 1))

# 2단계: 합의 도출
for node in transaction_status:
    votes = sum(1 for peer in unl[node] if transaction_status[peer] == "voting")
    if votes / len(unl[node]) >= 0.8:  # 80% 이상 투표
        transaction_status[node] = "confirmed"
frames.append(create_frame(transaction_status, 2))

fig = go.Figure(
    data=frames[0].data,
    layout=go.Layout(
        title="Ripple RPCA Consensus Process",
        titlefont_size=20,
        showlegend=False,
        hovermode='closest',
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(frame=dict(duration=1000, redraw=True), fromcurrent=True)
                        ]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(frame=dict(duration=0, redraw=False))
                        ]
                    )
                ]
            )
        ]
    ),
    frames=frames
)

fig.show()