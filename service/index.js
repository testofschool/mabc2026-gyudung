const http = require('http');

function assembleArticleNumber(base, branch) {
  return branch ? base + "의" + branch : base;
}

const ARTICLE_RE = new RegExp("제(\\d+)조(?:의(\\d+))?(?:\\(([^)]*)\\))?\\s*(.*)");
const ARTICLE_START_RE = new RegExp("제\\d+조(?:의\\d+)?(?:\\s|\\(|$)");

function parseArticles(text) {
  const articles = {};
  let currentNum = null;
  let currentTitle = null;
  let currentLines = [];

  const lines = text.split("\n");
  for (const line of lines) {
    const stripped = line.trim();
    if (!stripped) {
      if (currentNum !== null) currentLines.push(stripped);
      continue;
    }

    if (currentNum === null) {
      const m = ARTICLE_RE.exec(stripped);
      if (m) {
        currentNum = assembleArticleNumber(m[1], m[2] || null);
        currentTitle = m[3] || "";
        const body = (m[4] || "").trim();
        currentLines = body ? [body] : [];
      }
    } else {
      if (ARTICLE_START_RE.test(stripped) || stripped.startsWith("부칙")) {
        const content = currentLines.join("\n").trim();
        articles[currentNum] = { title: currentTitle, content };
        const m = ARTICLE_RE.exec(stripped);
        if (m) {
          currentNum = assembleArticleNumber(m[1], m[2] || null);
          currentTitle = m[3] || "";
          const body = (m[4] || "").trim();
          currentLines = body ? [body] : [];
        } else {
          currentNum = null;
          currentTitle = null;
          currentLines = [];
        }
      } else {
        currentLines.push(stripped);
      }
    }
  }

  if (currentNum !== null) {
    const content = currentLines.join("\n").trim();
    articles[currentNum] = { title: currentTitle, content };
  }

  return articles;
}

const ENACT_SUBJECTS = ["지침", "규정", "훈령", "예규", "요령"];
const ENACT_BIS_PATTERNS = ENACT_SUBJECTS.map(function(subj) {
  return new RegExp("이\\s*" + subj + "(?:은|는)\\s*(\\d{4})\\s*년\\s*(\\d{1,2})\\s*월\\s*(\\d{1,2})\\s*일부터\\s*시행");
});
const ENACT_HEADER_RE = new RegExp("\\[시행\\s+(\\d{4})\\.?\\s*(\\d{1,2})\\.?\\s*(\\d{1,2})\\.?\\s*\\]");

function parseEnactmentDate(text) {
  const lines = text.split("\n");
  for (const line of lines) {
    for (const pat of ENACT_BIS_PATTERNS) {
      const m = pat.exec(line);
      if (m) return new Date(parseInt(m[1], 10), parseInt(m[2], 10) - 1, parseInt(m[3], 10));
    }
    const m = ENACT_HEADER_RE.exec(line);
    if (m) return new Date(parseInt(m[1], 10), parseInt(m[2], 10) - 1, parseInt(m[3], 10));
  }
  return null;
}

function computeDiff(oldArticles, newArticles) {
  const diff = [];
  const allNums = Object.keys(oldArticles).concat(Object.keys(newArticles));
  const uniqueNums = Array.from(new Set(allNums)).sort();
  for (const num of uniqueNums) {
    const old = oldArticles[num];
    const neu = newArticles[num];
    if (old && neu) {
      if (old.content !== neu.content || old.title !== neu.title) {
        const title = neu.title || ("제" + num + "조");
        diff.push({
          article_number: num,
          article_title: title,
          judgment: "modified",
          old_content: old.content,
          new_content: neu.content,
        });
      }
    } else if (old && !neu) {
      const title = old.title || ("제" + num + "조");
      diff.push({
        article_number: num,
        article_title: title,
        judgment: "deleted",
        old_content: old.content,
        new_content: "",
      });
    } else if (neu && !old) {
      const title = neu.title || ("제" + num + "조");
      diff.push({
        article_number: num,
        article_title: title,
        judgment: "added",
        old_content: "",
        new_content: neu.content,
      });
    }
  }
  return diff;
}

function todayKST() {
  const now = new Date();
  const kstOffset = 9 * 60;
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const kst = new Date(utc + kstOffset * 60000);
  return new Date(Date.UTC(kst.getFullYear(), kst.getMonth(), kst.getDate()));
}

function dDayStatus(enactment, reference) {
  if (!enactment) return "시행일 미검출";
  const delta = Math.round((enactment - reference) / 86400000);
  if (delta === 0) return "오늘 시행";
  if (delta > 0) return "D-" + delta;
  return "시행중";
}

const server = http.createServer(function(req, res) {
  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");

  if (req.method === "OPTIONS") {
    res.writeHead(200);
    res.end("");
    return;
  }

  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: true, message: "POST 메서드만 지원됩니다." }, null, 2));
    return;
  }

  const url = req.url || "";
  if (url.startsWith("/api/")) {
    handleApi(req, res);
  } else {
    serveIndex(res);
  }
});

function serveIndex(res) {
  const fs = require("fs");
  const path = require("path");
  const indexPath = path.join(__dirname, "public", "index.html");
  fs.readFile(indexPath, function(err, data) {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(data);
  });
}

function parseBody(req) {
  return new Promise(function(resolve, reject) {
    var body = "";
    req.on("data", function(chunk) { body += chunk; });
    req.on("end", function() {
      if (!body) { resolve({}); return; }
      try { resolve(JSON.parse(body)); } catch (e) { reject(e); }
    });
    req.on("error", reject);
  });
}

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data, null, 2));
}

function sendError(res, statusCode, message) {
  sendJSON(res, statusCode, { error: true, message: message });
}

function handleApi(req, res) {
  parseBody(req).then(function(body) {
    if (!body || typeof body !== "object") {
      sendError(res, 400, "요청 본문이 비어 있거나 객체가 아닙니다.");
      return;
    }

    const oldText = body.old_text || "";
    const newText = body.new_text || "";

    if (!oldText.trim()) {
      sendError(res, 400, "구판 입력이 비어 있습니다.");
      return;
    }
    if (!newText.trim()) {
      sendError(res, 400, "신판 입력이 비어 있습니다.");
      return;
    }

    const articleStartPattern = new RegExp("제\\d+(?:의\\d+)?조\\b");
    if (!articleStartPattern.test(oldText)) {
      sendError(res, 400, "구판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다.");
      return;
    }
    if (!articleStartPattern.test(newText)) {
      sendError(res, 400, "신판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다.");
      return;
    }

    const oldArticles = parseArticles(oldText);
    const newArticles = parseArticles(newText);
    const oldEnact = parseEnactmentDate(oldText);
    const newEnact = parseEnactmentDate(newText);

    const todayKst = todayKST();
    const diff = computeDiff(oldArticles, newArticles);

    const result = {
      diff: diff,
      enactment: {
        old_date: oldEnact ? oldEnact.toISOString().slice(0, 10) : null,
        new_date: newEnact ? newEnact.toISOString().slice(0, 10) : null,
        reference_date: todayKst.toISOString().slice(0, 10),
        new_d_day_status: dDayStatus(newEnact, todayKst),
        old_d_day_status: dDayStatus(oldEnact, todayKst),
      },
    };

    sendJSON(res, 200, result);
  }).catch(function(e) {
    sendError(res, 400, "유효하지 않은 JSON 요청입니다.");
  });
}

const PORT = process.env.PORT || 3000;
server.listen(PORT, function() {
  console.log("규정다름 서버 실행: http://localhost:" + PORT);
});
