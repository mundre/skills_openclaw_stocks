# Filesystem Blueprint - my-study-pal

用这个文件创建概念解释系统的最小可运行骨架。

## 1. 创建基础目录结构

创建：

```text
mystudy/
  study-detail/
```

创建基础文件：
- `mystudy/study-summary.md`
- `mystudy/user-profile.md`

可选参考内置模板资源：
- `assets/mystudy-template/study-summary.md`
- `assets/mystudy-template/user-profile.md`
- `assets/mystudy-template/study-detail/study-detail-template.md`

## 2. 补齐基础文件

### `study-summary.md`

至少包含：
- 标题
- 时间 / 学习主题 / 是否完成 的表头

### `user-profile.md`

至少包含：
- 用户工作 / 专业 / 业务领域
- 用户爱好领域
- 用户最近的 5 个学习知识点
- 用户教学偏好 > 讲解式
  - 输出结构
  - 回答长度
  - 术语风格
- 用户教学偏好 > 引导式（预留）
- 语言风格偏好

### `study-detail/` 模板

至少包含：
- 学习主题
- 日期
- 对话记录

## 3. 定义可运行状态

概念解释系统只有在以下条件都满足时才算可运行：

- `mystudy/` 目录存在
- `study-detail/` 目录存在
- `study-summary.md` 存在
- `user-profile.md` 存在
- `user-profile.md` 中至少存在讲解式默认配置

## 4. 检查首次运行安全性

首次使用时必须保证：
- 不覆盖已有文件
- 模板字段完整
- 没有遗留旧的 `config.md` 依赖
- 后续记录路径明确可用
- 内置模板与 references 中描述的字段口径一致
