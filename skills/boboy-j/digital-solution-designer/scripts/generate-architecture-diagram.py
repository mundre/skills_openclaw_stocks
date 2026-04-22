#!/usr/bin/env python3
"""
架构图生成脚本

功能：将 Graphviz DOT 格式的架构描述转换为可视化图表（PNG/SVG）
支持类型：业务架构图、功能架构图、数据架构图、技术架构图、流程图

使用方式：
    python generate-architecture-diagram.py --diagram-type business --input business.dot --output business.png
    python generate-architecture-diagram.py --diagram-type functional --input functional.dot --output functional.svg
"""

import argparse
import sys
from graphviz import Digraph


def generate_diagram(dot_content: str, output_path: str, diagram_type: str = "architecture") -> str:
    """
    生成架构图

    Args:
        dot_content: Graphviz DOT 格式的图表描述
        output_path: 输出文件路径（PNG 或 SVG）
        diagram_type: 图表类型（用于设置图表属性）

    Returns:
        输出文件路径

    Raises:
        ValueError: 如果 DOT 内容为空
        Exception: 如果生成失败
    """
    if not dot_content or dot_content.strip() == "":
        raise ValueError("DOT 内容不能为空")

    # 根据输出格式确定渲染引擎
    output_format = output_path.split('.')[-1].lower()
    if output_format not in ['png', 'svg', 'pdf']:
        raise ValueError(f"不支持的输出格式: {output_format}，支持的格式: png, svg, pdf")

    # 创建 Digraph 对象
    # 设置引擎为 dot（适合层次化布局）或 fdp（适合力导向布局）
    engine = 'dot'  # 架构图通常使用层次化布局

    # 根据 diagram_type 设置布局方向
    if diagram_type in ['data']:
        # 数据架构图通常需要水平布局（从左到右）
        graph_attr = {'rankdir': 'LR', 'fontname': 'Arial', 'fontsize': '10'}
    else:
        # 其他架构图使用垂直布局（从上到下）
        graph_attr = {'rankdir': 'TB', 'fontname': 'Arial', 'fontsize': '10'}

    dot = Digraph(engine=engine, format=output_format)
    dot.graph_attr.update(graph_attr)
    dot.node_attr.update({'fontname': 'Arial', 'fontsize': '10'})
    dot.edge_attr.update({'fontname': 'Arial', 'fontsize': '9'})

    # 解析 DOT 内容并添加到图中
    # 这里使用简单的方式：直接解析 body 部分
    # 注意：这只是一个简化实现，完整的 DOT 解析会更复杂
    try:
        # 提取 DOT 的 body 部分（去掉 digraph G { ... }）
        if 'digraph' in dot_content:
            # 查找第一个 { 和最后一个 }
            start = dot_content.find('{')
            end = dot_content.rfind('}')
            if start != -1 and end != -1:
                body = dot_content[start + 1:end].strip()
            else:
                body = dot_content
        else:
            body = dot_content

        # 解析节点和边
        for line in body.split(';'):
            line = line.strip()
            if not line:
                continue

            # 解析节点定义
            if '->' not in line and '[' in line:
                # 节点定义：NodeName [label="Label", shape=box]
                node_def = line.split('[', 1)
                if len(node_def) == 2:
                    node_name = node_def[0].strip()
                    attrs_str = node_def[1].rstrip(']').strip()

                    # 解析属性
                    attrs = {}
                    for attr in attrs_str.split(','):
                        attr = attr.strip()
                        if '=' in attr:
                            key, value = attr.split('=', 1)
                            attrs[key.strip()] = value.strip().strip('"')

                    # 添加节点
                    label = attrs.get('label', node_name)
                    shape = attrs.get('shape', 'box')
                    dot.node(node_name, label=label, shape=shape)
            # 解析边定义
            elif '->' in line:
                # 边定义：Node1 -> Node2 [label="Label"]
                edge_def = line.split('->', 1)
                if len(edge_def) == 2:
                    node1 = edge_def[0].strip()
                    rest = edge_def[1].strip()

                    # 检查是否有边属性
                    if '[' in rest:
                        node2 = rest.split('[', 1)[0].strip()
                        attrs_str = rest.split('[', 1)[1].rstrip(']').strip()

                        # 解析属性
                        attrs = {}
                        for attr in attrs_str.split(','):
                            attr = attr.strip()
                            if '=' in attr:
                                key, value = attr.split('=', 1)
                                attrs[key.strip()] = value.strip().strip('"')

                        # 添加边
                        label = attrs.get('label', '')
                        if label:
                            dot.edge(node1, node2, label=label)
                        else:
                            dot.edge(node1, node2)
                    else:
                        dot.edge(node1, rest)

    except Exception as e:
        raise Exception(f"解析 DOT 内容失败: {str(e)}")

    # 渲染并保存
    try:
        output_file = dot.render(output_path.replace(f'.{output_format}', ''), cleanup=True)
        print(f"架构图已生成: {output_file}.{output_format}")
        return f"{output_file}.{output_format}"
    except Exception as e:
        raise Exception(f"生成架构图失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='生成架构图（支持 Graphviz DOT 格式）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 生成业务架构图（PNG）
  python generate-architecture-diagram.py --diagram-type business --input business.dot --output business.png

  # 生成功能架构图（SVG）
  python generate-architecture-diagram.py --diagram-type functional --input functional.dot --output functional.svg

  # 从标准输入读取
  echo "digraph G { A -> B }" | python generate-architecture-diagram.py --output test.png
        """
    )

    parser.add_argument(
        '--diagram-type',
        choices=['business', 'functional', 'data', 'technical', 'flow'],
        default='architecture',
        help='图表类型（business: 业务架构, functional: 功能架构, data: 数据架构, technical: 技术架构, flow: 流程图）'
    )

    parser.add_argument(
        '--input',
        '-i',
        help='输入文件路径（Graphviz DOT 格式），如果不指定则从标准输入读取'
    )

    parser.add_argument(
        '--output',
        '-o',
        required=True,
        help='输出文件路径（支持格式: png, svg, pdf）'
    )

    args = parser.parse_args()

    # 读取 DOT 内容
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                dot_content = f.read()
        except FileNotFoundError:
            print(f"错误: 文件不存在: {args.input}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取文件失败: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        # 从标准输入读取
        dot_content = sys.stdin.read()

    # 生成图表
    try:
        generate_diagram(dot_content, args.output, args.diagram_type)
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
