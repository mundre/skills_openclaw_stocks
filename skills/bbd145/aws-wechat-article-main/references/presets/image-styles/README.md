# 配图风格预设

本目录下的 `.md` 文件为**配图风格预设**。生成配图时按 config 的 `default_image_style` 或用户指定加载。

## Schema

- 每个文件描述一种视觉风格：风格名、描述、适用场景、**prompt 要点或关键词**（供 Agent/脚本生成图片时使用）。
- 完整风格库与 Type×Style 矩阵见 [shared/image-styles/styles.md](../../../shared/image-styles/styles.md)。可基于内置风格名（如 `flat-vector`、`notion-line`）写简短说明与约束。
- 文件名即预设名（不含后缀）。

## 示例

见 `flat-vector.example.md`。复制后重命名并按需修改。
