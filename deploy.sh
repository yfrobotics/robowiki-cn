echo "====> compiling markdown to html"
rm -rf site
mkdocs build
echo "====> deploying to github"
git worktree add /tmp/site gh-pages
rm -rf /tmp/site/*
cp -rp site/* /tmp/site/
cd /tmp/site && \
    git add -A && \
    git commit -m "deployed on `date +'%Y-%m-%d %H:%M:%S'` by ${USER}" && \
    git push origin gh-pages
echo "====> clean everything"
git worktree remove /tmp/site
rm -rf /tmp/site
echo "====> finished"
