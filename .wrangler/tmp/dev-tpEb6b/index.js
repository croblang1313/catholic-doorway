var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/index.js
var MONTHS = [
  "january",
  "february",
  "march",
  "april",
  "may",
  "june",
  "july",
  "august",
  "september",
  "october",
  "november",
  "december"
];
function json(body, status = 200, maxAge = 3600) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": `public, max-age=${maxAge}`
    }
  });
}
__name(json, "json");
function clean(s) {
  return s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
}
__name(clean, "clean");
async function readings(url, env, ctx) {
  const base = env.USCCB_BASE || "https://bible.usccb.org";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(url.searchParams.get("date") || "");
  if (!m) return json({ error: "Use ?date=YYYY-MM-DD" }, 400, 60);
  const [, y, mo, d] = m;
  const page = `${base}/bible/readings/${mo}${d}${y.slice(2)}.cfm`;
  const audio = `https://bible.usccb.org/podcasts/audio/daily-mass-reading-podcast-${MONTHS[+mo - 1]}-${+d}-${y}`;
  const cache = caches.default;
  const cacheKey = new Request(`https://catholicdoorway.com/api/readings?date=${y}-${mo}-${d}`);
  const hit = await cache.match(cacheKey);
  if (hit) return hit;
  let res;
  try {
    res = await fetch(page, { headers: { "User-Agent": "CatholicDoorway.com (readings links)" }, cf: { cacheTtl: 3600 } });
  } catch (e) {
    return json({ page, audio, error: "unavailable" }, 200, 120);
  }
  if (!res.ok) return json({ page, audio, error: "unavailable" }, 200, 120);
  const out = { date: `${y}-${mo}-${d}`, page, audio, video: null, title: "", lectionary: "", readings: [] };
  let cur = null, inTitle = false, inName = false, inAddr = false;
  const rewritten = new HTMLRewriter().on("h2:not(.visually-hidden)", {
    element() {
      inTitle = !out.title_done;
    },
    text(t) {
      if (inTitle) {
        out.title += t.text;
        if (t.lastInTextNode) {
          inTitle = false;
          out.title_done = true;
        }
      }
    }
  }).on("header.content-header h3.name", {
    element() {
      cur = { name: "", citation: "", url: "" };
      out.readings.push(cur);
      inName = true;
    },
    text(t) {
      if (inName && cur) {
        cur.name += t.text;
        if (t.lastInTextNode) inName = false;
      }
    }
  }).on("header.content-header p.address a", {
    element(el) {
      if (cur && !cur.url) {
        cur.url = (el.getAttribute("href") || "").trim();
        inAddr = true;
      }
    },
    text(t) {
      if (inAddr && cur) {
        cur.citation += t.text;
        if (t.lastInTextNode) inAddr = false;
      }
    }
  }).on('a[href*="/podcasts/video/"]', {
    element(el) {
      const h = el.getAttribute("href");
      if (!out.video && h && /\/podcasts\/video\/\d{4}-/.test(h)) out.video = h.startsWith("http") ? h : "https://bible.usccb.org" + h;
    }
  }).on("div.innerblock, p", {
    text(t) {
      if (!out.lectionary) {
        const m2 = /Lectionary:\s*(\d+)/.exec(t.text);
        if (m2) out.lectionary = m2[1];
      }
    }
  }).transform(res);
  await rewritten.text();
  delete out.title_done;
  out.title = clean(out.title);
  out.readings = out.readings.map((r) => ({ name: clean(r.name), citation: clean(r.citation), url: r.url.startsWith("http") ? r.url : "" })).filter((r) => r.name && r.citation).slice(0, 12);
  const response = json(out, 200, out.readings.length ? 21600 : 300);
  if (out.readings.length) ctx.waitUntil(cache.put(cacheKey, response.clone()));
  return response;
}
__name(readings, "readings");
var worker_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/readings") return readings(url, env, ctx);
    return env.ASSETS.fetch(request);
  }
};

// ../../../tmp/claude-0/-home-claude/4d643c91-b7ab-5a0d-ac5a-13a2ee4c599e/scratchpad/npm/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../../tmp/claude-0/-home-claude/4d643c91-b7ab-5a0d-ac5a-13a2ee4c599e/scratchpad/npm/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-u9xwq9/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = worker_default;

// ../../../tmp/claude-0/-home-claude/4d643c91-b7ab-5a0d-ac5a-13a2ee4c599e/scratchpad/npm/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-u9xwq9/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
