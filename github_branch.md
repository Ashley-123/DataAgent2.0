# 1) 确认远程并抓取最新分支
git remote set-url origin https://github.com/Ashley-123/DataAgent2.0.git
git fetch origin --prune

# 2) 将远程 feature/backend 与 frontend 分支拉到本地（建立对应本地分支）
git fetch origin feature/backend:feature/backend
git fetch origin frontend:frontend

# 3) 基于 origin/main 创建本地 develop 分支（如已存在可改为：git switch develop）
git switch develop origin/main

# 4) 合并 feature/backend 到 develop
git merge --no-ff --no-edit feature/backend

# 5) 合并 frontend 到 develop
git merge --no-ff --no-edit frontend

# 6) 如有冲突：解决后执行
# (根据冲突文件编辑修复后)
git add -A
git commit -m "Resolve merge conflicts between feature/backend and frontend"

# 7) 推送到远程并设置上游，创建远程 develop 分支
git push -u origin develop

# 查看远程分支
git branch -vv
git ls-remote --heads origin develop

# 可选：删除本地已合并的功能分支（若不再需要）
git branch -d feature/backend
git branch -d frontend





服务器拉取构建
cd /DataAgent2.0
git fetch origin --prune
git checkout develop
git reset --hard origin/develop

docker compose down || true
docker compose build
docker compose up -d

docker compose ps
docker exec sqlbot sh -lc "grep -n '<title>' /opt/sqlbot/frontend/dist/*.html || true"