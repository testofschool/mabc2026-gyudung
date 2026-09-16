export async function handler(request) {
  // CORS 프리플라이트
  if (request.method === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  if (request.method !== 'POST') {
    return {
      statusCode: 405,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: true, message: 'POST 메서드만 지원됩니다.' }, null, 2),
    };
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: true, message: '유효하지 않은 JSON 요청입니다.' }, null, 2),
    };
  }

  if (!body) {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({ error: true, message: '요청 본문이 비어 있습니다.' }, null, 2),
    };
  }

  const oldText = body.old_text || '';
  const newText = body.new_text || '';

  // ---- 입력 validation ----
  const articleStartPattern = /\제\d+(?:의\d+)?조\b/;
  if (!oldText.trim()) {
    return { statusCode: 400, headers: corsHeaders, body: JSON.stringify({ error: true, message: '구판 입력이 비어 있습니다.' }, null, 2) };
  }
  if (!newText.trim()) {
    return { statusCode: 400, headers: corsHeaders, body: JSON.stringify({ error: true, message: '신판 입력이 비어 있습니다.' }, null, 2) };
  }
  if (!articleStartPattern.test(oldText)) {
    return { statusCode: 400, headers: corsHeaders, body: JSON.stringify({ error: true, message: '구판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다.' }, null, 2) };
  }
  if (!articleStartPattern.test(newText)) {
    return { statusCode: 400, headers: corsHeaders, body: JSON.stringify({ error: true, message: '신판에서 조문 패턴(제N조)을 찾을 수 없습니다. 행정규칙/지침 형식이 아닌 것으로 보입니다.' }, null, 2) };
  }

  // ---- 조문 파싱 ----
  const oldArticles = parseArticles(oldText);
  const newArticles = parseArticles(newText);
  const oldEnact = parseEnactmentDate(oldText);
  const newEnact = parseEnactmentDate(newText);

  const todayKst = todayKST();
  const diff = computeDiff(oldArticles, newArticles);

  const result = {
    diff,
    enactment: {
      old_date: oldEnact ? oldEnact.toISOString().slice(0, 10) : null,
      new_date: newEnact ? newEnact.toISOString().slice(0, 10) : null,
      reference_date: todayKst.toISOString().slice(0, 10),
      new_d_day_status: dDayStatus(newEnact, todayKst),
      old_d_day_status: dDayStatus(oldEnact, todayKst),
    },
  };

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    body: JSON.stringify(result, null, 2),
  };
}

// ---------------------------------------------------------------------------------------
// 헬퍼 함수 (admirl_diff.py의 로직을 JS로 재구현 — 계산 규칙은 동일)
// ---------------------------------------------------------------------------------------

const ARTICLE_RE = /제(\d+)조(?:의(\d+))?(?:\(([^)]*)\))?\s*(.*)/;
const ARTICLE_START_RE = /제\d+조(?:의\d+)?(?:\s|\(|$)/;

function assembleArticleNumber(base, branch) {
  return branch ? `${base}의${branch}` : base;
}

function parseArticles(text) {
  const articles = {};
  let currentNum = null;
  let currentTitle = null;
  let currentLines = [];

  const lines = text.split('\n');
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
        currentTitle = m[3] || '';
        const body = (m[4] || '').trim();
        currentLines = body ? [body] : [];
      }
    } else {
      if (ARTICLE_START_RE.test(stripped) || stripped.startsWith('부칙')) {
        const content = currentLines.join('\n').trim();
        articles[currentNum] = { title: currentTitle, content };
        const m = ARTICLE_RE.exec(stripped);
        if (m) {
          currentNum = assembleArticleNumber(m[1], m[2] || null);
          currentTitle = m[3] || '';
          const body = (m[4] || '').trim();
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
    const content = currentLines.join('\n').trim();
    articles[currentNum] = { title: currentTitle, content };
  }

  return articles;
}

// ---- 시행일 파싱 ----
const ENACT_SUBJECTS = ['지침', '규정', '훈령', '예규', '요령'];
const ENACT_BIS_PATTERNS = ENACT_SUBJECTS.map(subj =>
  new RegExp(`이\\s*${subj}(?:은|는)\\s*(\\d{4})\\s*년\\s*(\\d{1,2})\\s*월\\s*(\\d{1,2})\\s*일부터\\s*시행`)
);
const ENACT_HEADER_RE = /\[시행\s+(\d{4})\.?\s*(\d{1,2})\.?\s*(\d{1,2})\.?\s*\]/;

function parseEnactmentDate(text) {
  for (const line of text.split('\n')) {
    for (const pat of ENACT_BIS_PATTERNS) {
      const m = pat.exec(line);
      if (m) return new Date(parseInt(m[1]), parseInt(m[2]) - 1, parseInt(m[3]));
    }
    const m = ENACT_HEADER_RE.exec(line);
    if (m) return new Date(parseInt(m[1]), parseInt(m[2]) - 1, parseInt(m[3]));
  }
  return null;
}

// ---- Diff 판정 ----
function computeDiff(oldArticles, newArticles) {
  const diff = [];
  const allNums = [...new Set([...Object.keys(oldArticles), ...Object.keys(newArticles)])].sort();
  for (const num of allNums) {
    const old = oldArticles[num];
    const neu = newArticles[num];
    if (old && neu) {
      if (old.content !== neu.content || old.title !== neu.title) {
        const title = neu.title || `제${num}조`;
        diff.push({
          article_number: num,
          article_title: title,
          judgment: 'modified',
          old_content: old.content,
          new_content: neu.content,
        });
      }
    } else if (old && !neu) {
      const title = old.title || `제${num}조`;
      diff.push({
        article_number: num,
        article_title: title,
        judgment: 'deleted',
        old_content: old.content,
        new_content: '',
      });
    } else if (neu && !old) {
      const title = neu.title || `제${num}조`;
      diff.push({
        article_number: num,
        article_title: title,
        judgment: 'added',
        old_content: '',
        new_content: neu.content,
      });
    }
  }
  return diff;
}

// ---- D-day 판정 (KST) ----
function todayKST() {
  const now = new Date();
  const kstOffset = 9 * 60; // UTC+9
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const kst = new Date(utc + kstOffset * 60000);
  return new Date(Date.UTC(kst.getFullYear(), kst.getMonth(), kst.getDate()));
}

function dDayStatus(enactment, reference) {
  if (!enactment) return '시행일 미검출';
  const delta = Math.round((enactment - reference) / 86400000);
  if (delta === 0) return '오늘 시행';
  if (delta > 0) return `D-${delta}`;
  return '시행중';
}

const corsHeaders = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};
