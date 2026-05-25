const inspectDataBtn = document.querySelector("#inspectDataBtn");
const buildIndexBtn = document.querySelector("#buildIndexBtn");
const searchByIdBtn = document.querySelector("#searchByIdBtn");
const searchByVectorBtn = document.querySelector("#searchByVectorBtn");
const indexStatus = document.querySelector("#indexStatus");
const healthBadge = document.querySelector("#healthBadge");
const resultsBody = document.querySelector("#resultsBody");
const datasetInfo = document.querySelector("#datasetInfo");
const queryStatus = document.querySelector("#queryStatus");
const registerBtn = document.querySelector("#registerBtn");
const loginBtn = document.querySelector("#loginBtn");
const logoutBtn = document.querySelector("#logoutBtn");
const loadUsersBtn = document.querySelector("#loadUsersBtn");
const authStatus = document.querySelector("#authStatus");
const userList = document.querySelector("#userList");

let authToken = localStorage.getItem("authToken") || "";
let currentUser = JSON.parse(localStorage.getItem("currentUser") || "null");

function clearAuthInputs() {
  document.querySelector("#authUsername").value = "";
  document.querySelector("#authPassword").value = "";
}

async function requestJson(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await fetch(url, { ...options, headers });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function postJson(url, payload) {
  return requestJson(url, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function getJson(url) {
  return requestJson(url);
}

function deleteJson(url) {
  return requestJson(url, { method: "DELETE" });
}

function authPayload() {
  return {
    username: document.querySelector("#authUsername").value.trim(),
    password: document.querySelector("#authPassword").value,
    role: document.querySelector("input[name='authRole']:checked").value,
  };
}

function roleLabel(role) {
  return role === "admin" ? "管理员" : "普通用户";
}

function saveSession(token, user) {
  authToken = token;
  currentUser = user;
  localStorage.setItem("authToken", token);
  localStorage.setItem("currentUser", JSON.stringify(user));
  renderAuthState();
}

function clearSession() {
  authToken = "";
  currentUser = null;
  localStorage.removeItem("authToken");
  localStorage.removeItem("currentUser");
  renderAuthState();
}

function renderAuthState(message) {
  if (currentUser) {
    authStatus.textContent =
      message || `已登录：${currentUser.username}（${roleLabel(currentUser.role)}）`;
    authStatus.className = "small text-success";
    logoutBtn.disabled = false;

    const isAdmin = currentUser.role === "admin";
    loadUsersBtn.disabled = !isAdmin;
    loadUsersBtn.classList.toggle("d-none", !isAdmin);
    if (!isAdmin) {
      userList.classList.add("d-none");
      userList.innerHTML = "";
    }
    return;
  }

  authStatus.textContent = message || "未登录";
  authStatus.className = "small text-secondary";
  logoutBtn.disabled = true;
  loadUsersBtn.disabled = true;
  loadUsersBtn.classList.add("d-none");
  userList.classList.add("d-none");
  userList.innerHTML = "";
}

function renderUsers(users) {
  userList.innerHTML = `
    <form id="adminCreateUserForm" class="row g-2 align-items-end mb-3">
      <div class="col-md-3">
        <label class="form-label" for="adminNewUsername">账号</label>
        <input id="adminNewUsername" class="form-control form-control-sm" placeholder="新账号">
      </div>
      <div class="col-md-3">
        <label class="form-label" for="adminNewPassword">密码</label>
        <input id="adminNewPassword" class="form-control form-control-sm" type="password" placeholder="至少 6 位">
      </div>
      <div class="col-md-3">
        <label class="form-label" for="adminNewRole">角色</label>
        <select id="adminNewRole" class="form-select form-select-sm">
          <option value="user">普通用户</option>
          <option value="admin">管理员</option>
        </select>
      </div>
      <div class="col-md-3">
        <button class="btn btn-sm btn-primary w-100" type="submit">新增用户</button>
      </div>
    </form>
    <div class="table-responsive">
      <table class="table table-sm align-middle mb-0">
        <thead>
          <tr>
            <th>ID</th>
            <th>账号</th>
            <th>角色</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>管理</th>
          </tr>
        </thead>
        <tbody>
          ${
            users.length
              ? users
                  .map(
                    (user) => `
                      <tr>
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${roleLabel(user.role)}</td>
                        <td>${user.is_active ? "启用" : "禁用"}</td>
                        <td>${user.created_at}</td>
                        <td>
                          <button
                            class="btn btn-sm btn-outline-danger delete-user-btn"
                            data-user-id="${user.id}"
                            ${currentUser?.id === user.id ? "disabled" : ""}
                          >
                            删除
                          </button>
                        </td>
                      </tr>
                    `
                  )
                  .join("")
              : '<tr><td colspan="6" class="text-secondary text-center py-3">暂无用户</td></tr>'
          }
        </tbody>
      </table>
    </div>
  `;
  userList.classList.remove("d-none");
}

function dataPath() {
  return document.querySelector("#dataPath").value.trim();
}

function setIndexReady(ready) {
  healthBadge.textContent = ready ? "索引已构建" : "未构建索引";
  healthBadge.className = ready ? "badge text-bg-success" : "badge text-bg-secondary";
}

function activeFilters() {
  const filters = {};
  const cellType = document.querySelector("#filterCellType").value.trim();
  const disease = document.querySelector("#filterDisease").value.trim();
  const ageGroup = document.querySelector("#filterAgeGroup").value.trim();

  if (cellType) filters.cell_type = cellType;
  if (disease) filters.disease = disease;
  if (ageGroup) filters.AgeGroup = ageGroup;
  return filters;
}

function renderDatasetInfo(info) {
  const fields = [
    ["文件", info.source_path || "-"],
    ["格式", info.format || "-"],
    ["细胞数", info.cell_count ?? "-"],
    ["基因数", info.gene_count ?? "-"],
    ["向量维度", info.vector_dim ?? "-"],
    ["向量来源", info.embedding_key || "-"],
  ];

  datasetInfo.innerHTML = fields
    .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
    .join("");
}

function renderResults(results) {
  if (!results.length) {
    resultsBody.innerHTML =
      '<tr><td colspan="8" class="text-center text-secondary py-4">没有匹配结果</td></tr>';
    return;
  }

  resultsBody.innerHTML = results
    .map((item, index) => {
      const metadata = item.metadata || {};
      return `
        <tr>
          <td>${index + 1}</td>
          <td class="cell-id">${item.cell_id}</td>
          <td>${item.distance}</td>
          <td>${item.score}</td>
          <td>${metadata.cell_type || "-"}</td>
          <td>${metadata.disease || "-"}</td>
          <td>${metadata.AgeGroup || "-"}</td>
          <td>${metadata.sex || "-"}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadUsers() {
  loadUsersBtn.disabled = true;
  try {
    const data = await getJson("/api/admin/users");
    renderUsers(data.users);
  } catch (error) {
    userList.innerHTML = `<div class="text-danger small">${error.message}</div>`;
    userList.classList.remove("d-none");
  } finally {
    loadUsersBtn.disabled = currentUser?.role !== "admin";
  }
}

registerBtn.addEventListener("click", async () => {
  registerBtn.disabled = true;
  authStatus.textContent = "正在注册...";
  try {
    const payload = authPayload();
    const data = await postJson("/api/auth/register", payload);
    authStatus.textContent = `注册成功：${data.user.username}（${roleLabel(data.user.role)}），请登录`;
    authStatus.className = "small text-success";
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.className = "small text-danger";
  } finally {
    registerBtn.disabled = false;
  }
});

loginBtn.addEventListener("click", async () => {
  loginBtn.disabled = true;
  authStatus.textContent = "正在登录...";
  try {
    const { username, password } = authPayload();
    const data = await postJson("/api/auth/login", { username, password });
    saveSession(data.token, data.user);
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.className = "small text-danger";
  } finally {
    loginBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  clearSession();
});

loadUsersBtn.addEventListener("click", loadUsers);

userList.addEventListener("submit", async (event) => {
  if (event.target.id !== "adminCreateUserForm") return;

  event.preventDefault();
  try {
    await postJson("/api/admin/users", {
      username: document.querySelector("#adminNewUsername").value.trim(),
      password: document.querySelector("#adminNewPassword").value,
      role: document.querySelector("#adminNewRole").value,
    });
    await loadUsers();
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.className = "small text-danger";
  }
});

userList.addEventListener("click", async (event) => {
  const deleteButton = event.target.closest(".delete-user-btn");
  if (!deleteButton) return;

  try {
    deleteButton.disabled = true;
    await deleteJson(`/api/admin/users/${deleteButton.dataset.userId}`);
    await loadUsers();
  } catch (error) {
    authStatus.textContent = error.message;
    authStatus.className = "small text-danger";
    deleteButton.disabled = false;
  }
});

clearAuthInputs();
window.setTimeout(clearAuthInputs, 100);
renderAuthState();

inspectDataBtn.addEventListener("click", async () => {
  indexStatus.textContent = "正在检查数据...";
  inspectDataBtn.disabled = true;
  try {
    const info = await postJson("/api/dataset/inspect", { data_path: dataPath() });
    renderDatasetInfo(info);
    indexStatus.textContent = "数据检查完成";
  } catch (error) {
    indexStatus.textContent = error.message;
  } finally {
    inspectDataBtn.disabled = false;
  }
});

buildIndexBtn.addEventListener("click", async () => {
  indexStatus.textContent = "正在构建索引，liver.h5ad 首次构建可能需要等待...";
  buildIndexBtn.disabled = true;
  try {
    const data = await postJson("/api/index/build", { data_path: dataPath() });
    renderDatasetInfo({ ...data, source_path: dataPath(), format: dataPath().split(".").pop() });
    indexStatus.textContent = `已构建：${data.cell_count} 个细胞，${data.vector_dim} 维，耗时 ${data.build_time_ms} ms`;
    setIndexReady(true);
  } catch (error) {
    indexStatus.textContent = error.message;
    setIndexReady(false);
  } finally {
    buildIndexBtn.disabled = false;
  }
});

searchByIdBtn.addEventListener("click", async () => {
  queryStatus.textContent = "正在查询...";
  try {
    const data = await postJson("/api/search/by-id", {
      cell_id: document.querySelector("#cellId").value.trim(),
      top_k: Number(document.querySelector("#topKId").value),
      filters: activeFilters(),
    });
    queryStatus.textContent = `查询完成，耗时 ${data.query_time_ms} ms`;
    renderResults(data.results);
  } catch (error) {
    queryStatus.textContent = error.message;
    resultsBody.innerHTML = `<tr><td colspan="8" class="text-danger py-4">${error.message}</td></tr>`;
  }
});

searchByVectorBtn.addEventListener("click", async () => {
  queryStatus.textContent = "正在查询...";
  try {
    const vector = document
      .querySelector("#queryVector")
      .value.split(",")
      .map((value) => Number(value.trim()));
    const data = await postJson("/api/search/by-vector", {
      vector,
      top_k: Number(document.querySelector("#topKVector").value),
      filters: activeFilters(),
    });
    queryStatus.textContent = `查询完成，耗时 ${data.query_time_ms} ms`;
    renderResults(data.results);
  } catch (error) {
    queryStatus.textContent = error.message;
    resultsBody.innerHTML = `<tr><td colspan="8" class="text-danger py-4">${error.message}</td></tr>`;
  }
});
