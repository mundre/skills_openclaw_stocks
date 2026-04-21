#!/usr/bin/env python3
"""
生成 D3.js 人物关系图可视化 HTML
用法: python3 generate_html.py [数据文件] [输出文件]

示例:
  python3 generate_html.py graph_data.json character-graph.html
"""

import json
import sys
import os

GROUP_COLORS = {
    "主角": "#FFD700", "主角爱人": "#FF6B9D", "主角挚友": "#FF69B4",
    "七星宗兄弟": "#4FC3F7", "七星宗": "#29B6F6", "七星宗反派": "#EF5350",
    "凡间": "#FF9800", "修妖界": "#81C784", "超级神兽": "#BA68C8",
    "上界": "#E040FB", "魔界": "#F44336", "鬼界": "#90A4AE",
    "缥缈宫": "#00BCD4", "其他": "#666"
}
GROUP_NAMES = {
    "主角": "主角", "主角爱人": "爱人", "主角挚友": "挚友",
    "七星宗兄弟": "七星宗兄弟", "七星宗": "七星宗", "七星宗反派": "七星宗反派",
    "凡间": "凡间", "修妖界": "修妖界", "超级神兽": "超级神兽",
    "上界": "上界", "魔界": "魔界", "鬼界": "鬼界",
    "缥缈宫": "缥缈宫", "其他": "其他"
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0f; color: #e0e0e0; overflow: hidden; }}
        #container {{ width: 100vw; height: 100vh; }}
        .node circle {{ stroke: #fff; stroke-width: 0.5px; cursor: pointer; }}
        .node text {{ font-size: 7px; fill: #fff; pointer-events: none; text-shadow: 0 0 2px #000; }}
        .link {{ stroke-opacity: 0.1; }}
        #tooltip {{ position: absolute; background: rgba(15,15,30,0.98); border: 1px solid #558; border-radius: 12px; padding: 16px; pointer-events: none; opacity: 0; transition: opacity 0.2s; width: 380px; z-index: 100; box-shadow: 0 8px 32px rgba(0,0,0,0.7); }}
        #tooltip h3 {{ color: #7cf; margin-bottom: 8px; font-size: 18px; font-weight: 600; border-bottom: 1px solid #334; padding-bottom: 8px; }}
        #tooltip .desc {{ color: #c0c0c0; font-size: 13px; line-height: 1.6; margin-bottom: 10px; }}
        #tooltip .meta {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        #tooltip .meta span {{ background: rgba(80,120,200,0.2); padding: 4px 10px; border-radius: 12px; font-size: 11px; color: #8cf; }}
        #tooltip .relations {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #334; font-size: 11px; color: #999; line-height: 1.8; }}
        #stats {{ position: absolute; top: 15px; left: 15px; background: rgba(20,20,30,0.92); padding: 12px 18px; border-radius: 10px; font-size: 13px; z-index: 10; border: 1px solid #334; }}
        #legend {{ position: absolute; top: 60px; left: 15px; background: rgba(20,20,30,0.92); padding: 12px 16px; border-radius: 10px; font-size: 10px; z-index: 10; border: 1px solid #334; max-height: 75vh; overflow-y: auto; min-width: 110px; }}
        .legend-item {{ display: flex; align-items: center; margin: 4px 0; }}
        .legend-dot {{ width: 9px; height: 9px; border-radius: 50%; margin-right: 7px; flex-shrink: 0; }}
        #title {{ position: absolute; top: 15px; left: 50%; transform: translateX(-50%); font-size: 18px; color: #7cf; z-index: 10; text-shadow: 0 0 10px rgba(100,200,255,0.5); white-space: nowrap; }}
        #search {{ position: absolute; bottom: 25px; left: 50%; transform: translateX(-50%); z-index: 10; }}
        #search input {{ background: rgba(20,20,30,0.95); border: 1px solid #445; border-radius: 25px; padding: 10px 20px; color: #fff; font-size: 14px; width: 240px; outline: none; }}
        #search input:focus {{ border-color: #6af; box-shadow: 0 0 12px rgba(100,150,255,0.3); }}
    </style>
</head>
<body>
    <div id="title">{title}</div>
    <div id="stats">人物: <span id="node-count">-</span> | 关系: <span id="link-count">-</span></div>
    <div id="legend"></div>
    <div id="container"></div>
    <div id="tooltip"></div>
    <div id="search"><input type="text" placeholder="搜索人物..."></div>

    <script>
        const groupColors = {json_colors};
        const groupNames = {json_names};

        const graphData = {json_data};
        const nodes = graphData.nodes;
        const links = graphData.links;

        document.getElementById('node-count').textContent = nodes.length;
        document.getElementById('link-count').textContent = links.length;

        const nodeMap = {{}};
        nodes.forEach(n => nodeMap[n.id] = n);

        const groups = [...new Set(nodes.map(n => n.group))].sort();
        groups.forEach(g => {{
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = '<span class="legend-dot" style="background:' + (groupColors[g]||'#666') + '"></span>' + (groupNames[g]||g);
            document.getElementById('legend').appendChild(item);
        }});

        const width = window.innerWidth;
        const height = window.innerHeight;
        const svg = d3.select('#container').append('svg').attr('viewBox', [0, 0, width, height]);
        const g = svg.append('g');
        svg.call(d3.zoom().scaleExtent([0.02, 4]).on('zoom', e => g.attr('transform', e.transform)));

        const sim = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(d => 40 - Math.sqrt(d.weight)*0.5))
            .force('charge', d3.forceManyBody().strength(-50))
            .force('center', d3.forceCenter(width/2, height/2))
            .force('collision', d3.forceCollide().radius(8));

        const link = g.append('g').selectAll('line').data(links).join('line')
            .attr('class', 'link')
            .attr('stroke', d => d.weight > 80 ? '#FFD700' : d.weight > 40 ? '#FF9800' : '#446')
            .attr('stroke-width', d => Math.max(0.3, Math.sqrt(d.weight)/6));

        const node = g.append('g').selectAll('g').data(nodes).join('g')
            .attr('class', 'node')
            .call(d3.drag().on('start', e => {{ if (!e.active) sim.alphaTarget(0.3).restart(); e.subject.fx = e.subject.x; e.subject.fy = e.subject.y; }})
                   .on('drag', e => {{ e.subject.fx = e.x; e.subject.fy = e.y; }})
                   .on('end', e => {{ if (!e.active) sim.alphaTarget(0); e.subject.fx = null; e.subject.fy = null; }}));

        node.append('circle').attr('r', d => 4 + Math.sqrt(d.freq)/2.5).attr('fill', d => groupColors[d.group]||'#666');
        node.append('text').text(d => d.name).attr('dy', d => 8 + Math.sqrt(d.freq)/2.5).attr('text-anchor', 'middle').style('font-size', '7px');

        const tip = d3.select('#tooltip');
        node.on('mouseover', (event, d) => {{
            const nid = d.id;
            const rels = links.filter(l => l.source.id === nid || l.target.id === nid)
                .sort((a,b) => b.weight - a.weight).slice(0, 15)
                .map(l => {{
                    const oid = l.source.id === nid ? l.target.id : l.source.id;
                    const on = nodeMap[oid];
                    const name = on ? on.name : oid;
                    const label = l.label || '同现';
                    return name + ' (' + label + ' ' + l.weight + '章)';
                }});
            
            const descText = d.rich_desc || d.desc || '小说人物，共出场' + d.freq + '章。';
            
            tip.style('opacity', 1)
               .html('<h3>'+d.name+'</h3>' +
                     '<div class="desc">'+descText+'</div>' +
                     '<div class="meta"><span>出场'+d.freq+'章</span><span>'+(groupNames[d.group]||d.group)+'</span></div>' +
                     '<div class="relations">主要关系：<br>' + rels.join('<br>') + '</div>')
               .style('left', (event.pageX+15)+'px').style('top', (event.pageY-10)+'px');
        }}).on('mouseout', () => tip.style('opacity', 0));

        sim.on('tick', () => {{
            link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            node.attr('transform', d => 'translate('+d.x+','+d.y+')');
        }});

        d3.select('#search input').on('input', function() {{
            const q = this.value.toLowerCase();
            node.style('opacity', d => d.name.toLowerCase().includes(q) || d.id.toLowerCase().includes(q) ? 1 : 0.08);
            link.style('opacity', d => d.source.name.toLowerCase().includes(q) || d.target.name.toLowerCase().includes(q) ? 0.25 : 0.02);
        }});
    </script>
</body>
</html>'''

def generate_html(data_path, output_path, title='小说人物关系图谱'):
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    json_data = json.dumps(data, ensure_ascii=False, indent=None, separators=(',', ':'))
    json_colors = json.dumps(GROUP_COLORS, ensure_ascii=False)
    json_names = json.dumps(GROUP_NAMES, ensure_ascii=False)
    
    html = HTML_TEMPLATE.format(
        title=title,
        json_data=json_data,
        json_colors=json_colors,
        json_names=json_names
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 已生成: {output_path}")
    print(f"节点: {len(data['nodes'])}, 关系: {len(data['links'])}")

if __name__ == '__main__':
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'graph_data.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'character-graph.html'
    title = sys.argv[3] if len(sys.argv) > 3 else '小说人物关系图谱'
    
    generate_html(data_path, output_path, title)
