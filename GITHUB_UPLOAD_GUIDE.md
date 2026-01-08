# 将项目上传到 GitHub 的详细步骤说明

## 概述
本指南将详细说明如何在 Cursor 中将您的项目上传到 GitHub 个人主页仓库。整个过程分为以下几个主要步骤。

---

## 步骤 1：在 GitHub 上创建仓库

**操作位置**：GitHub 网站 (https://github.com)

**具体操作**：
1. 登录您的 GitHub 账户
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: 输入仓库名称（例如：Final_Project 或 Kinodynamic-RRT）
   - **Description**: 可选，填写项目描述
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有本地项目）
4. 点击 "Create repository"

**这一步在做什么**：
- 在 GitHub 上创建一个空的远程仓库，作为代码的云端存储位置
- 生成仓库的唯一 URL（例如：`https://github.com/yourusername/repository-name.git`）

**重要信息**：创建完成后，GitHub 会显示仓库的 URL，请记下这个 URL，后续步骤需要使用。

---

## 步骤 2：初始化本地 Git 仓库

**操作位置**：Cursor 终端

**命令**：
```bash
git init
```

**这一步在做什么**：
- 在当前项目目录中创建一个隐藏的 `.git` 文件夹
- 将当前目录标记为 Git 仓库，使 Git 可以追踪文件变化
- 建立版本控制的基础架构

**结果**：如果成功，终端会显示 "Initialized empty Git repository in ..."

---

## 步骤 3：配置 Git 用户信息（首次使用需要）

**操作位置**：Cursor 终端

**命令**：
```bash
git config user.name "您的GitHub用户名"
git config user.email "您的GitHub邮箱"
```

**示例**：
```bash
git config user.name "JohnDoe"
git config user.email "john@example.com"
```

**这一步在做什么**：
- 设置 Git 的提交者身份信息
- 每次提交代码时，Git 会记录谁提交的代码
- 这些信息会显示在 GitHub 的提交历史中

**注意**：
- 如果之前已经配置过，可以跳过此步骤
- 可以使用 `git config --global` 来全局设置（对所有项目生效）

---

## 步骤 4：添加文件到暂存区

**操作位置**：Cursor 终端

**命令**：
```bash
git add .
```

**或者选择性地添加文件**：
```bash
git add README.md
git add *.py
git add .gitignore
```

**这一步在做什么**：
- `git add .` 会将当前目录下所有未忽略的文件添加到暂存区（staging area）
- `.gitignore` 文件中列出的文件（如 `__pycache__/`）不会被添加
- 暂存区是准备提交的文件集合，是提交前的"待提交区"

**常用命令说明**：
- `git add .` - 添加所有文件
- `git add <文件名>` - 添加指定文件
- `git status` - 查看哪些文件被添加了（绿色）和哪些还未添加（红色）

---

## 步骤 5：创建首次提交

**操作位置**：Cursor 终端

**命令**：
```bash
git commit -m "Initial commit: Add Kinodynamic RRT path planning project"
```

**这一步在做什么**：
- 将暂存区的所有文件创建为一个快照（commit）
- `-m` 后面的是提交信息，说明这次提交做了什么
- 这个提交只保存在本地，还没有上传到 GitHub
- 每个提交都有唯一的 ID，记录项目的版本历史

**提交信息建议**：
- 使用清晰、描述性的中文或英文
- 例如："初始提交：添加运动学RRT路径规划项目"

---

## 步骤 6：添加 GitHub 远程仓库地址

**操作位置**：Cursor 终端

**命令**：
```bash
git remote add origin https://github.com/您的用户名/仓库名.git
```

**示例**：
```bash
git remote add origin https://github.com/johndoe/Final_Project.git
```

**这一步在做什么**：
- 将 GitHub 上的远程仓库地址添加为 "origin"（远程仓库的别名）
- Git 现在知道您的本地仓库应该连接到哪个远程仓库
- "origin" 是默认的远程仓库名称，可以自定义

**验证远程仓库**：
```bash
git remote -v
```
此命令会显示已配置的远程仓库地址。

---

## 步骤 7：将代码推送到 GitHub

**操作位置**：Cursor 终端

**命令**：
```bash
git branch -M main
git push -u origin main
```

**这一步在做什么**：
- `git branch -M main`：将本地分支重命名为 "main"（GitHub 的默认主分支名称）
- `git push -u origin main`：
  - 将本地的 "main" 分支上传到远程仓库 "origin"
  - `-u` 参数设置上游分支，以后可以直接使用 `git push` 而不需要指定分支
  - 首次推送会将所有提交和文件上传到 GitHub

**身份验证**：
- GitHub 现在要求使用 Personal Access Token（个人访问令牌）而不是密码
- 如果提示输入用户名和密码：
  - 用户名：您的 GitHub 用户名
  - 密码：使用 Personal Access Token（不是 GitHub 密码）

**如何创建 Personal Access Token**：
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 设置权限（至少勾选 `repo`）
4. 生成后复制并保存（只显示一次）

---

## 步骤 8：验证上传成功

**操作位置**：GitHub 网站

**操作**：
1. 刷新您的 GitHub 仓库页面
2. 应该能看到所有项目文件
3. 查看提交历史，应该能看到您的首次提交

**这一步在做什么**：
- 确认所有文件都成功上传到 GitHub
- 验证提交历史是否正确
- 确保代码已经安全地存储在云端

---

## 后续更新代码的流程

当您修改了代码后，想要再次上传更新：

**步骤 1**：查看修改了哪些文件
```bash
git status
```

**步骤 2**：添加修改的文件到暂存区
```bash
git add .
```
或者只添加特定文件：
```bash
git add 文件名.py
```

**步骤 3**：创建提交
```bash
git commit -m "描述本次修改的内容"
```

**步骤 4**：推送到 GitHub
```bash
git push
```

---

## 常见问题

### Q1: 如果忘记了远程仓库地址怎么办？
```bash
git remote -v  # 查看当前远程仓库地址
```

### Q2: 如果远程仓库地址填错了怎么办？
```bash
git remote remove origin  # 删除错误的远程地址
git remote add origin 正确的地址  # 重新添加正确的地址
```

### Q3: 推送时提示 "Permission denied"？
- 检查是否使用了正确的 Personal Access Token
- 确认 Token 有 `repo` 权限

### Q4: 推送时提示 "Updates were rejected"？
- 远程仓库有您本地没有的提交（可能您在网页上修改了文件）
- 先拉取远程更新：`git pull origin main --rebase`
- 然后再推送：`git push`

---

## 完整命令序列（一次性执行）

如果您熟悉所有步骤，可以按顺序执行以下命令：

```bash
# 1. 初始化仓库
git init

# 2. 配置用户信息（如果还没配置过）
git config user.name "您的GitHub用户名"
git config user.email "您的GitHub邮箱"

# 3. 添加所有文件
git add .

# 4. 创建首次提交
git commit -m "Initial commit: Add Kinodynamic RRT path planning project"

# 5. 添加远程仓库（替换为您的实际仓库地址）
git remote add origin https://github.com/您的用户名/仓库名.git

# 6. 重命名分支并推送
git branch -M main
git push -u origin main
```

---

## 总结

整个上传过程的核心是：
1. **本地准备**：初始化 Git、添加文件、创建提交
2. **连接远程**：添加 GitHub 仓库地址
3. **上传代码**：推送到远程仓库

每一步都有其重要作用，确保了代码的版本控制和远程备份。

