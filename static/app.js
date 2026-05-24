const buildIndexBtn = document.querySelector("#buildIndexBtn");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const indexStatus = document.querySelector("#indexStatus");
const healthBadge = document.querySelector("#healthBadge");
const resultsBody = document.querySelector("#resultsBody");

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function setIndexReady(ready) {
  healthBadge.textContent = ready ? "索引已构建" : "未构建索引";
  healthBadge.className = ready ? "badge text-bg-success" : "badge text-bg-secondary";
}

function renderResults(results) {
  if (!results.length) {
    resultsBody.innerHTML = '<tr><td colspan="6" class="text-center text-secondary py-4">没有匹配结果</td></tr>';
    return;
  }

  resultsBody.innerHTML = results
    .map((item, index) => {
      const metadata = item.metadata || {};
      return `
        <tr>
          <td>${index + 1}</td>
          <td>${item.cell_id}</td>
          <td>${item.distance}</td>
          <td>${item.score}</td>
          <td>${metadata.cell_type || "-"}</td>
          <td>${metadata.batch || "-"}</td>
        </tr>
      `;
    })
    .join("");
}

buildIndexBtn.addEventListener("click", async () => {
  indexStatus.textContent = "正在构建索引...";
  buildIndexBtn.disabled = true;
  try {
    const data = await postJson("/api/index/build", {
      data_path: document.querySelector("#dataPath").value.trim(),
    });
    indexStatus.textContent = `已构建：${data.cell_count} 个细胞，向量维度 ${data.vector_dim}`;
    setIndexReady(true);
  } catch (error) {
    indexStatus.textContent = error.message;
    setIndexReady(false);
  } finally {
    buildIndexBtn.disabled = false;
  }
});

searchByIdBtn.addEventListener("click", async () => {
  try {
    const data = await postJson("/api/search/by-id", {
      cell_id: document.querySelector("#cellId").value.trim(),
      top_k: Number(document.querySelector("#topKId").value),
    });
    renderResults(data.results);
  } catch (error) {
    resultsBody.innerHTML = `<tr><td colspan="6" class="text-danger py-4">${error.message}</td></tr>`;
  }
});

searchByVectorBtn.addEventListener("click", async () => {
  try {
    const vector = document
      .querySelector("#queryVector")
      .value.split(",")
      .map((value) => Number(value.trim()));
    const data = await postJson("/api/search/by-vector", {
      vector,
      top_k: Number(document.querySelector("#topKVector").value),
    });
    renderResults(data.results);
  } catch (error) {
    resultsBody.innerHTML = `<tr><td colspan="6" class="text-danger py-4">${error.message}</td></tr>`;
  }
});
