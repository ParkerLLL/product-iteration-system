#!/usr/bin/env sh

# 确保脚本抛出遇到的错误
set -e

# 构建
npm run build

# 进入构建文件夹
cd dist

# 创建 .nojekyll 文件，阻止 GitHub Pages 使用 Jekyll 处理文件
touch .nojekyll

# 创建 404.html（如果不存在）
cp index.html 404.html

git init
git add -A
git commit -m 'deploy'

# 部署到 gh-pages 分支
git push -f git@github.com:ParkerLLL/product-iteration-system.git main:gh-pages

cd - 