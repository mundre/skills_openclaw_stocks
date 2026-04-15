---
name: todo4google
description: 管理，同步每日ToDo到Google Task：创建本地todo文件；解析本地todo文件；总结todo；自动生成下一天todo；新建Google task；更新Google task完成情况；归档到云端google drive。触发条件：用户说"总结todo/task"、"生成下一天的todo"、"创建Google task"、"更新Google task"、或类似表述。
---
# Todo Manager

## 默认设置
默认工作目录 `workspace/archive/todos/`  
默认文件命名格式 `todos-YYYYMMDD.md`  
默认Google Task List `openclaw`  
默认todo任务模版:
```
# 今日任务 YYYY-MM-DD
---
## ToDos
- [ ] **[{priority}] {title}**
  - taskId: xxx
  - due: yyyy-mm-dd （默认当天）
  - 第一行notes
  第二行notes（续）
  第三行notes（续）

- [ ] **下一个任务**
  ...

---
## Works
---
## Summary
```
**注意大模块的顺序是ToDos → Works → Summary**

## 本地操作

### 创建本地todo文件
总结用户需求，创建当天的todo文件 `todos-YYYYMMDD.md`，如果文件已存在则追加。  
todo格式参照上文默认todo任务模版。  
新建的本地todo默认没有taskId

###  读取并解析本地任务文件
默认读取当天的文件 `todos-YYYYMMDD.md`  
只解析文件中的 todo 项，忽略其他内容。

**解析规则**：
1. 任务标题行 `- [ ] **[{priority}] {title}**` 依次提取:
    完成状态:status 
    优先级:priority（p0/p1/p2，默认p1）如无则自动添加p1
    任务标题:title 
    
2. 子行 `- taskId: xxx` → 提取 taskId
3. 子行 `- due: YYYY-MM-DD` → 提取 截止日期:due （默认当天）
4. 子行 `- xxx`（非 taskId/due/priority）→ 归入 notes
5. **多行 notes**：从第一条 notes 行开始，所有后续不包含 `taskId:`、`due:` 的行都属于该任务的 notes，直到下一个任务

### 总结今日完成情况

在**文件末尾**添加完成情况小结，格式如下：

```
---
## Summary
**已完成（N/M）**：
1. ✅ 第一项任务
2. ✅ 第二项任务

**未完成（M/N）**：
- ❌ 第一项任务
- ❌ 第二项任务
```

### 生成下一天 todo 文件
生成 `todos-YYYYMMDD+1.md`，内容为当天未完成的任务列表  
注意，如果未完成任务中包含 **taskId，due**，则保留以便后续同步
格式参照上文的 todo 任务模版。  

## Google 云端同步
### 新建google task
将本地todo文件中的任务同步到google task中

1. 解析本地任务文件

2. 向Google Task创建新任务
默认Google Task List `OpenClaw`
对于本地todo中，**没有任务id**的任务（**无论是否已经标记完成**）执行如下：
  ```bash
  gog task add {taskList} --title "[{priority}] {title}" --notes "$(printf notes)" --due {due}
  ```
**注意：并发提起tool_use, notes 注意 $(printf ...) 语法**  

3. 回写入本地todo文件
等待所有任务均创建完毕，更新今日todo文件，**并按照priority排序**, **proiority要用方括号包裹**

### 更新google task完成情况

对于本地任务文件中，**有任务id且任务已完成**的执行如下：  
  ```bash
  gog task update {taskList} {taskId} --notes "$(printf notes)" --due {due} --status "completed" 
  ```
**注意：并发提起tool_use, notes 注意 $(printf ...) 语法** 

### 归档todo文件
将目标文件上传到云端google drive, 默认转成Google Doc格式
```bash
gog drive upload {filePath} --convert-to doc
```
