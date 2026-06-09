const samples = {
  "customer-service": `来源：官网表单
公司：某制造业企业
行业：制造业
感兴趣产品：AI 客服解决方案

客户留言：
我们想了解你们的 AI 客服方案，主要想降低售后咨询压力，最好能先做一个小范围试点。我们现在有 FAQ 和历史客服记录，希望一个月内看到 Demo。

销售备注：
客户暂未提供预算，也没有说明当前使用的客服系统。`,
  "growth-copilot": `来源：活动报名
公司：某 B2B SaaS 公司
行业：企业软件
感兴趣产品：AI 增长线索 Copilot

客户留言：
我们市场部每天会收到很多表单、社媒私信和邮件咨询，但销售反馈线索质量参差不齐。想看看 AI 能不能先做线索评分，并给销售生成标准跟进话术。

销售备注：
客户提到已有 CRM，但没有说明接口条件、预算和决策流程。`,
  "thin-lead": `来源：社媒私信
公司：未知
行业：未知
感兴趣产品：企业 AI 方案

客户留言：
你们这个 AI 怎么收费？多久能上线？有没有大客户案例？

销售备注：
客户只问价格、周期和案例，尚未说明业务场景。`
};

const leadText = document.querySelector("#lead-text");
const sampleSelect = document.querySelector("#sample-select");
const form = document.querySelector("#lead-form");
const answer = document.querySelector("#answer");
const trace = document.querySelector("#trace");
const status = document.querySelector("#status");
const button = document.querySelector("#analyze-button");

function setSample(value) {
  leadText.value = samples[value];
}

function renderMarkdown(markdown) {
  const escaped = markdown
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");

  return escaped
    .split(/\n{2,}/)
    .map((block) => {
      if (block.startsWith("## ")) {
        return `<h2>${block.slice(3)}</h2>`;
      }
      if (block.startsWith("> ")) {
        return `<p class="note">${block.slice(2).replaceAll("\n", "<br>")}</p>`;
      }
      return `<p>${block.replaceAll("\n", "<br>")}</p>`;
    })
    .join("");
}

function renderTrace(items) {
  trace.innerHTML = items
    .map((item, index) => {
      const detail = JSON.stringify(item, null, 2);
      return `<article class="trace-item">
        <div class="trace-title">${index + 1}. ${item.step}<span>${item.tool || item.routeDecision || ""}</span></div>
        <pre>${detail}</pre>
      </article>`;
    })
    .join("");
}

sampleSelect.addEventListener("change", (event) => {
  setSample(event.target.value);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  status.textContent = "分析中";
  answer.classList.remove("empty");
  answer.innerHTML = "正在执行 Skill、调用 Tool 并生成分析...";
  trace.innerHTML = "";

  try {
    const response = await fetch("/api/analyze-lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ leadText: leadText.value })
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "分析失败");
    }
    answer.innerHTML = renderMarkdown(payload.answer);
    renderTrace(payload.trace);
    status.textContent = payload.skill.name;
  } catch (error) {
    answer.innerHTML = `<p class="error">${error.message}</p>`;
    status.textContent = "出错";
  } finally {
    button.disabled = false;
  }
});

setSample(sampleSelect.value);
