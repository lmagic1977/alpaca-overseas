# 羊驼出海 LLAMA VISA 官网

静态站点，部署在 Vercel。

- `index.html`：整站页面（含新加坡职位数据）
- `logo.svg`：品牌标志与 favicon
- `api/lead.js`：预约表单接口，目前把预约写入 Vercel 运行日志（搜索 `NEW_LEAD`）
- `api/jobs.js`：新加坡职位查询，凭查询码返回职位（数据 `api/_jobs.json` 由 build.py 生成，不公开）。查询码用 `python3 tools/job_codes.py new 20` 生成、`revoke 码` 作废，仓库只存哈希
- `vercel.json`：Vercel 配置
