const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const askButton = document.querySelector("#ask-button");
const resultPanel = document.querySelector("#result-panel");
const emptyState = document.querySelector("#empty-state");
const resultQuestion = document.querySelector("#result-question");
const resultMeta = document.querySelector("#result-meta");
const answerContent = document.querySelector("#answer-content");
const answerLoading = document.querySelector("#answer-loading");
const copyButton = document.querySelector("#copy-button");
const sourceCount = document.querySelector("#source-count");
const sourcesList = document.querySelector("#sources-list");

let isRequesting = false;

function resizeInput() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
}

function setLoading(question) {
  isRequesting = true;
  askButton.disabled = true;
  askButton.querySelector("span").textContent = "Thinking";
  resultPanel.hidden = false;
  resultPanel.setAttribute("aria-busy", "true");
  emptyState.hidden = true;
  resultQuestion.textContent = question;
  resultMeta.textContent = "SEARCHING KNOWLEDGE...";
  answerContent.textContent = "";
  answerContent.classList.remove("error-message");
  answerLoading.hidden = false;
  copyButton.hidden = true;
  sourcesList.replaceChildren();
  sourceCount.textContent = "SEARCHING";

  window.setTimeout(() => {
    resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 80);
}

function clearLoading() {
  isRequesting = false;
  askButton.disabled = false;
  askButton.querySelector("span").textContent = "Ask";
  resultPanel.removeAttribute("aria-busy");
  answerLoading.hidden = true;
}

function safeExternalUrl(value) {
  if (!value) return null;

  try {
    const url = new URL(value);
    if (url.protocol === "http:" || url.protocol === "https:") {
      return url.href;
    }
  } catch {
    return null;
  }

  return null;
}

function appendInlineMarkdown(container, text) {
  const tokenPattern = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let cursor = 0;

  for (const match of text.matchAll(tokenPattern)) {
    if (match.index > cursor) {
      container.append(document.createTextNode(text.slice(cursor, match.index)));
    }

    const token = match[0];
    const element = document.createElement(token.startsWith("**") ? "strong" : "code");
    element.textContent = token.startsWith("**") ? token.slice(2, -2) : token.slice(1, -1);
    container.append(element);
    cursor = match.index + token.length;
  }

  if (cursor < text.length) {
    container.append(document.createTextNode(text.slice(cursor)));
  }
}

function renderMarkdown(text) {
  answerContent.replaceChildren();
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let paragraphLines = [];
  let activeList = null;

  const flushParagraph = () => {
    if (paragraphLines.length === 0) return;
    const paragraph = document.createElement("p");
    appendInlineMarkdown(paragraph, paragraphLines.join(" ").trim());
    answerContent.append(paragraph);
    paragraphLines = [];
  };

  const closeList = () => {
    activeList = null;
  };

  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      closeList();
      return;
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      closeList();
      const heading = document.createElement(`h${Math.min(headingMatch[1].length + 3, 6)}`);
      appendInlineMarkdown(heading, headingMatch[2]);
      answerContent.append(heading);
      return;
    }

    const orderedMatch = line.match(/^\d+[.)]\s+(.+)$/);
    const unorderedMatch = line.match(/^[-*]\s+(.+)$/);
    const listMatch = orderedMatch || unorderedMatch;
    if (listMatch) {
      flushParagraph();
      const listTag = orderedMatch ? "OL" : "UL";
      if (!activeList || activeList.tagName !== listTag) {
        activeList = document.createElement(listTag.toLowerCase());
        answerContent.append(activeList);
      }
      const item = document.createElement("li");
      appendInlineMarkdown(item, listMatch[1]);
      activeList.append(item);
      return;
    }

    closeList();
    paragraphLines.push(line);
  });

  flushParagraph();
}

function appendPath(container, path, fallbackTitle) {
  const items = (path || fallbackTitle || "Notion")
    .split(">")
    .map((item) => item.trim())
    .filter(Boolean);

  items.forEach((item, index) => {
    if (index > 0) {
      const separator = document.createElement("span");
      separator.className = "path-separator";
      separator.textContent = "/";
      container.append(separator);
    }

    const label = document.createElement("span");
    label.textContent = item;
    container.append(label);
  });
}

function createSourceCard(source, index) {
  const card = document.createElement("article");
  card.className = "source-card";

  const sourceIndex = document.createElement("span");
  sourceIndex.className = "source-index";
  sourceIndex.textContent = String(index + 1).padStart(2, "0");

  const body = document.createElement("div");
  body.className = "source-body";

  const title = document.createElement("h4");
  title.className = "source-title";
  title.textContent = source.page_title || source.title || "제목 없는 문서";

  const path = document.createElement("div");
  path.className = "source-path";
  appendPath(path, source.page_path, source.title);

  const excerpt = document.createElement("p");
  excerpt.className = "source-excerpt";
  excerpt.textContent = source.content || "이 문서에서 관련 근거를 찾았습니다.";

  body.append(title, path, excerpt);
  card.append(sourceIndex, body);

  const href = safeExternalUrl(source.page_url) || safeExternalUrl(source.source);
  if (href) {
    const link = document.createElement("a");
    link.className = "source-link";
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", `${title.textContent} Notion에서 열기`);
    link.innerHTML = `
      <span>Notion에서 열기</span>
      <svg viewBox="0 0 16 16" aria-hidden="true">
        <path d="M6 3h7v7M13 3 6.5 9.5"></path>
        <path d="M11 9v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h3"></path>
      </svg>
    `;
    card.append(link);
  }

  return card;
}

function renderSources(sources) {
  sourcesList.replaceChildren();
  sourceCount.textContent = `${sources.length} ${sources.length === 1 ? "SOURCE" : "SOURCES"}`;

  if (sources.length === 0) {
    const empty = document.createElement("div");
    empty.className = "no-sources";
    empty.textContent = "표시할 출처가 없습니다.";
    sourcesList.append(empty);
    return;
  }

  sources.forEach((source, index) => {
    sourcesList.append(createSourceCard(source, index));
  });
}

function renderResult(data, elapsedMs) {
  const answer = typeof data.answer === "string" ? data.answer.trim() : "";
  const sources = Array.isArray(data.sources) ? data.sources : [];

  renderMarkdown(answer || "답변을 생성하지 못했습니다.");
  resultMeta.textContent = `${sources.length} SOURCES · ${(elapsedMs / 1000).toFixed(1)} SEC`;
  copyButton.hidden = !answer;
  renderSources(sources);
}

function renderError(error) {
  answerContent.classList.add("error-message");
  answerContent.textContent = error.message;
  resultMeta.textContent = "REQUEST FAILED";
  sourceCount.textContent = "0 SOURCES";
  renderSources([]);
}

async function askKnowledgeBase(question) {
  const endpoint = new URL("/ask", window.location.origin);
  endpoint.searchParams.set("query", question);
  endpoint.searchParams.set("top_k", "5");
  endpoint.searchParams.set("min_rerank_score", "0.0");

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 120_000);
  const startedAt = performance.now();

  try {
    const response = await fetch(endpoint, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });

    if (!response.ok) {
      let detail = "서버에서 답변을 가져오지 못했습니다.";
      try {
        const errorBody = await response.json();
        if (typeof errorBody.detail === "string") detail = errorBody.detail;
      } catch {
        // JSON 오류 응답이 아니면 기본 안내 문구를 사용한다.
      }
      throw new Error(`${detail} (${response.status})`);
    }

    const data = await response.json();
    renderResult(data, performance.now() - startedAt);
  } catch (error) {
    if (error.name === "AbortError") {
      renderError(new Error("답변 생성 시간이 2분을 넘었습니다. Ollama 상태를 확인한 뒤 다시 시도해 주세요."));
    } else if (error instanceof TypeError) {
      renderError(new Error("서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해 주세요."));
    } else {
      renderError(error);
    }
  } finally {
    window.clearTimeout(timeoutId);
    clearLoading();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (isRequesting) return;

  const question = input.value.trim();
  if (!question) {
    input.focus();
    return;
  }

  const currentUrl = new URL(window.location.href);
  currentUrl.searchParams.set("q", question);
  window.history.replaceState({}, "", currentUrl);

  setLoading(question);
  askKnowledgeBase(question);
});

input.addEventListener("input", resizeInput);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.question;
    resizeInput();
    input.focus();
  });
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(answerContent.textContent);
    copyButton.querySelector("span").textContent = "복사됨";
    window.setTimeout(() => {
      copyButton.querySelector("span").textContent = "복사";
    }, 1400);
  } catch {
    copyButton.querySelector("span").textContent = "복사 실패";
  }
});

const initialQuery = new URLSearchParams(window.location.search).get("q");
if (initialQuery) {
  input.value = initialQuery;
  resizeInput();
}
