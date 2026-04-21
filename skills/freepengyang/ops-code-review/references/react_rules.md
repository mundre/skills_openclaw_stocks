# React + TypeScript 代码审计专项规则

## 重点关注场景

### 🔴 高危：安全相关

#### 潜在 XSS（ dangerouslySetInnerHTML）
```tsx
// ❌ 危险：直接渲染用户输入
function DisplayContent({ content }) {
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
}

// ✅ 安全：使用 React 的转义，或使用 DOMPurify 清洗
import DOMPurify from 'dompurify';
function DisplayContent({ content }) {
  return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }} />;
}
```

#### URL 跳转（钓鱼风险）
```tsx
// ❌ 危险：允许任意跳转
<a href={userInputUrl}>跳转</a>

// ✅ 安全：验证 URL
function isValidUrl(url: string) {
  return /^https?:\/\//.test(url);
}
<a href={isValidUrl(url) ? url : '#'}>跳转</a>
```

#### 不安全的 eval
```tsx
// ❌ 危险
const result = eval(props.expression);

// ✅ 安全：使用 Function 构造或预定义表达式
const safeEval = new Function('return ' + expression)();
```

#### 敏感信息暴露
```tsx
// ❌ 危险：暴露 API Key
const API_KEY = 'sk-xxxxxxx';

// ✅ 安全：环境变量
const API_KEY = process.env.REACT_APP_API_KEY;
```

### 🟡 中危：Hook 使用错误

#### 闭包陷阱（过时 state）
```tsx
// ❌ 危险：在 setInterval 中使用过时的 state
useEffect(() => {
  const timer = setInterval(() => {
    setCount(count + 1);  // count 永远是初始值
  }, 1000);
  return () => clearInterval(timer);
}, []);
```

#### 缺少依赖项（ESLint react-hooks/exhaustive-deps）
```tsx
// ❌ 危险：缺少依赖
useEffect(() => {
  fetchData(id);
}, []);  // 缺少 id

// ✅ 安全：完整依赖
useEffect(() => {
  fetchData(id);
}, [id]);
```

#### 错误使用 useEffect 初始化
```tsx
// ❌ 危险：setState 在渲染时调用
function Component({ user }) {
  const [name, setName] = useState(user.name);  // 每次渲染都执行
  setName(user.name);  // 触发无限循环
}

// ✅ 安全：在 useEffect 中处理
useEffect(() => {
  setName(user.name);
}, [user.name]);
```

### 🟢 低危：类型与规范

#### any 类型滥用
```tsx
// ❌ 危险
function getData(data: any) { ... }

// ✅ 安全
function getData(data: Record<string, unknown>) { ... }
// 或定义具体接口
```

#### 缺少 key 导致渲染问题
```tsx
// ❌ 危险
{items.map(item => <Item name={item.name} />)}

// ✅ 安全
{items.map((item, index) => <Item key={item.id || index} name={item.name} />)}
```

#### 组件过大（>300行建议拆分）
- 建议拆分为子组件或 Hook
- 建议使用 React.lazy 延迟加载

### TypeScript 专项检查
- 严格模式 `strict: true` 是否开启
- `noImplicitAny` 是否启用
- 类型断言是否过度使用
- `as` 类型断言代替 `!` 非空断言
