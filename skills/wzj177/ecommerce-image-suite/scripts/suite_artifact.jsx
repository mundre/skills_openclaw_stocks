import { useState, useEffect, useCallback } from "react";

const PROVIDERS = [
  {
    id: "openai", name: "DALL·E 3", company: "OpenAI", emoji: "🤖",
    keyLabel: "OpenAI API Key", keyPlaceholder: "sk-proj-...",
    async generate(key, prompt) {
      const r = await fetch("https://api.openai.com/v1/images/generations", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}` },
        body: JSON.stringify({ model: "dall-e-3", prompt, size: "1024x1024", quality: "hd", response_format: "b64_json", n: 1 })
      });
      if (!r.ok) { const e = await r.json(); throw new Error(e.error?.message || `HTTP ${r.status}`); }
      return (await r.json()).data[0].b64_json;
    }
  },
  {
    id: "gemini", name: "Gemini Imagen 3", company: "Google", emoji: "💎",
    keyLabel: "Google AI API Key", keyPlaceholder: "AIzaSy...",
    async generate(key, prompt) {
      const r = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key=${key}`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ instances: [{ prompt }], parameters: { sampleCount: 1, aspectRatio: "1:1", safetySetting: "block_only_high" } }) }
      );
      if (!r.ok) { const e = await r.json(); throw new Error(e.error?.message || `HTTP ${r.status}`); }
      return (await r.json()).predictions[0].bytesBase64Encoded;
    }
  },
  {
    id: "stability", name: "Stable Image Core", company: "Stability AI", emoji: "🎨",
    keyLabel: "Stability AI API Key", keyPlaceholder: "sk-...",
    async generate(key, prompt) {
      const fd = new FormData();
      fd.append("prompt", prompt); fd.append("output_format", "jpeg"); fd.append("aspect_ratio", "1:1");
      const r = await fetch("https://api.stability.ai/v2beta/stable-image/generate/core", {
        method: "POST", headers: { "Authorization": `Bearer ${key}`, "Accept": "application/json" }, body: fd
      });
      if (!r.ok) { const e = await r.json(); throw new Error(e.message || `HTTP ${r.status}`); }
      return (await r.json()).image;
    }
  },
  {
    id: "tongyi", name: "千问", company: "阿里云 DashScope", emoji: "☁️",
    keyLabel: "DashScope API Key", keyPlaceholder: "sk-...",
    async generate(key, prompt) {
      const sub = await fetch("https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}`, "X-DashScope-Async": "enable" },
        body: JSON.stringify({ model: "qwen-image-2.0-pro", input: { prompt }, parameters: { size: "1024*1024", n: 1 } })
      });
      if (!sub.ok) throw new Error(`通义提交失败 ${sub.status}`);
      const { output: { task_id } } = await sub.json();
      for (let i = 0; i < 30; i++) {
        await new Promise(r => setTimeout(r, 2000));
        const p = await (await fetch(`https://dashscope.aliyuncs.com/api/v1/tasks/${task_id}`, { headers: { "Authorization": `Bearer ${key}` } })).json();
        if (p.output?.task_status === "SUCCEEDED") {
          const blob = await (await fetch(p.output.results[0].url)).blob();
          return new Promise(r => { const fr = new FileReader(); fr.onloadend = () => r(fr.result.split(",")[1]); fr.readAsDataURL(blob); });
        }
        if (p.output?.task_status === "FAILED") throw new Error("通义任务失败");
      }
      throw new Error("千问超时");
    }
  },
  {
    id: "doubao", name: "豆包 Seedream", company: "字节跳动", emoji: "🫘",
    keyLabel: "火山引擎 API Key", keyPlaceholder: "your-ark-key",
    async generate(key, prompt) {
      const r = await fetch("https://ark.cn-beijing.volces.com/api/v3/images/generations", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${key}` },
        body: JSON.stringify({ model: "doubao-seedream-3-0-t2i-250415", prompt, size: "1024x1024", response_format: "b64_json", n: 1 })
      });
      if (!r.ok) { const e = await r.json(); throw new Error(e.error?.message || `HTTP ${r.status}`); }
      return (await r.json()).data[0].b64_json;
    }
  },
];

const IMAGE_TYPES = [
  { id: "white_bg",     icon: "⬜", name: "白底主图",   desc: "纯白底，符合平台规范" },
  { id: "key_features", icon: "✨", name: "核心卖点图", desc: "3大卖点图标化呈现" },
  { id: "selling_pt",   icon: "🎯", name: "卖点图",    desc: "宽松版型深度展示" },
  { id: "material",     icon: "🧵", name: "材质图",    desc: "面料微距特写" },
  { id: "lifestyle",    icon: "☀️", name: "场景展示图", desc: "校园/咖啡馆生活场景" },
  { id: "model",        icon: "👗", name: "模特展示图", desc: "AI模特户外穿搭" },
  { id: "multi_scene",  icon: "🔲", name: "多场景拼图", desc: "居家+户外双场景" },
];

// Canvas text overlay definitions per image type
const OVERLAY = {
  white_bg: null, model: null,
  key_features: (sp, lang) => {
    const titles = sp?.slice(0, 3).map(s => lang === "zh" ? s.zh_title : s.en_title) || ["Combed Cotton","Loose & Breathable","Cute Design"];
    return [
      { text: lang === "zh" ? "为什么选择我们" : "WHY CHOOSE US", x:.53, y:.115, fs:.031, w:"700", c:"#1a1a1a", a:"left" },
      { text: titles[0]||"", x:.60, y:.375, fs:.021, w:"600", c:"#333", a:"left" },
      { text: titles[1]||"", x:.60, y:.565, fs:.021, w:"600", c:"#333", a:"left" },
      { text: titles[2]||"", x:.60, y:.755, fs:.021, w:"600", c:"#333", a:"left" },
    ];
  },
  selling_pt: (sp, lang) => lang === "zh" ? [
    { text:"宽松版型设计",   x:.06,y:.095,fs:.036,w:"700",c:"#1a1a1a",a:"left" },
    { text:"活动自如无束缚", x:.06,y:.888,fs:.022,w:"600",c:"#444",  a:"left" },
    { text:"显瘦舒适两不误", x:.06,y:.944,fs:.022,w:"600",c:"#444",  a:"left" },
  ] : [
    { text:"LOOSE FIT DESIGN",          x:.05,y:.095,fs:.033,w:"700",c:"#1a1a1a",a:"left" },
    { text:"Unrestricted Movement",     x:.05,y:.888,fs:.022,w:"600",c:"#444",  a:"left" },
    { text:"Comfortable and Flattering",x:.05,y:.944,fs:.022,w:"600",c:"#444",  a:"left" },
  ],
  material: (sp, lang) => lang === "zh" ? [
    { text:"优质精梳棉",        x:.95,y:.095,fs:.034,w:"700",c:"#1a1a1a",a:"right" },
    { text:"亲肤柔软不刺激",    x:.95,y:.500,fs:.022,w:"600",c:"#444",  a:"right" },
    { text:"干爽透气，全天舒适", x:.95,y:.920,fs:.022,w:"600",c:"#444",  a:"right" },
  ] : [
    { text:"PREMIUM COMBED COTTON",  x:.95,y:.095,fs:.027,w:"700",c:"#1a1a1a",a:"right" },
    { text:"Soft and Skin-friendly", x:.95,y:.500,fs:.022,w:"600",c:"#444",  a:"right" },
    { text:"Keep Dry and Breathable",x:.95,y:.920,fs:.022,w:"600",c:"#444",  a:"right" },
  ],
  lifestyle: (sp, lang) => lang === "zh" ? [
    { text:"日常减龄穿搭",x:.05,y:.095,fs:.036,w:"700",c:"#fff",a:"left",shad:true },
    { text:"校园首选",    x:.05,y:.888,fs:.022,w:"600",c:"#fff",a:"left",shad:true },
    { text:"百搭轻松",    x:.05,y:.944,fs:.022,w:"600",c:"#fff",a:"left",shad:true },
  ] : [
    { text:"CASUAL EVERYDAY STYLE",x:.05,y:.095,fs:.029,w:"700",c:"#fff",a:"left",shad:true },
    { text:"Perfect for School",  x:.05,y:.888,fs:.022,w:"600",c:"#fff",a:"left",shad:true },
    { text:"Easy to Match",       x:.05,y:.944,fs:.022,w:"600",c:"#fff",a:"left",shad:true },
  ],
  multi_scene: (sp, lang) => lang === "zh" ? [
    { text:"一件多穿，随心切换",x:.50,y:.065,fs:.029,w:"700",c:"#fff",a:"center",shad:true },
    { text:"居家慵懒风",        x:.25,y:.945,fs:.022,w:"600",c:"#fff",a:"center",shad:true },
    { text:"出游活力风",        x:.75,y:.945,fs:.022,w:"600",c:"#fff",a:"center",shad:true },
  ] : [
    { text:"VERSATILE FOR ANY OCCASION",x:.50,y:.065,fs:.025,w:"700",c:"#fff",a:"center",shad:true },
    { text:"Home Lounging",             x:.25,y:.945,fs:.022,w:"600",c:"#fff",a:"center",shad:true },
    { text:"Outdoor Outings",           x:.75,y:.945,fs:.022,w:"600",c:"#fff",a:"center",shad:true },
  ],
};

async function applyOverlay(b64, typeId, sp, lang) {
  const cfg = OVERLAY[typeId];
  if (!cfg) return b64;
  return new Promise(res => {
    const img = new Image();
    img.onload = () => {
      const W = img.naturalWidth||1024, H = img.naturalHeight||1024;
      const cv = document.createElement("canvas");
      cv.width = W; cv.height = H;
      const ctx = cv.getContext("2d");
      ctx.drawImage(img, 0, 0, W, H);
      (cfg(sp, lang)||[]).forEach(t => {
        const fz = Math.round(t.fs * W);
        ctx.font = `${t.w||"600"} ${fz}px "Helvetica Neue","PingFang SC","Microsoft YaHei",Arial,sans-serif`;
        ctx.textAlign = t.a||"left";
        ctx.shadowColor = "transparent"; ctx.shadowBlur = 0;
        if (t.shad) { ctx.shadowColor = "rgba(0,0,0,0.55)"; ctx.shadowBlur = 8; ctx.shadowOffsetX=1; ctx.shadowOffsetY=1; }
        ctx.fillStyle = t.c||"#fff";
        ctx.fillText(t.text, t.x*W, t.y*H);
        ctx.shadowColor = "transparent"; ctx.shadowBlur = 0;
      });
      res(cv.toDataURL("image/jpeg",.93).split(",")[1]);
    };
    img.onerror = () => res(b64);
    img.src = `data:image/jpeg;base64,${b64}`;
  });
}

function buildPrompt(typeId, desc, sp) {
  const base = `${desc}. Photorealistic commercial product photography, 8K, ultra-high quality. CRITICAL: keep the product EXACTLY the same — same print, same proportions, same color, same structure. Do NOT alter clothing design, print pattern, color, or any detail.`;
  const map = {
    white_bg:     `${base} Pure white background RGB(255,255,255). Product perfectly centered, occupying 90% of frame. Slight 45-degree angle. Clean studio lighting, very subtle natural shadow underneath. No props, no text, no decorations.`,
    key_features: `${base} Clean light gray (#f5f5f5) background. LEFT HALF: complete front view of product (45% frame). RIGHT HALF: three minimalist thin-line outline icons vertically arranged representing fabric/fit/design features. Balanced modern infographic layout.`,
    selling_pt:   `${base} Cozy bedroom interior, soft white bedding, shallow bokeh background. Product laid flat on bed OR faceless model wearing it showing oversized silhouette and dropped shoulders. Soft warm lighting, lazy weekend mood. Keep upper-left and lower-left lighter.`,
    material:     `${base} Macro photography. Product partially folded at center frame. Strong directional side lighting revealing knit fabric texture. Cotton flower plant props in soft background. Ultra-sharp fabric detail. Keep right side lighter for text.`,
    lifestyle:    `${base} Sunny campus green lawn or warm cafe wooden table. Product with canvas tote bag, open notebook, vintage headphones. Shallow depth of field. Young carefree lifestyle. Keep upper-left and lower-left corners lighter.`,
    model:        `${base} Bright outdoor park, abundant sunlight. Young East-Asian female model, bright smile, confidently walking. Product paired with light blue denim shorts. Full body shot, product is clear visual focus. Editorial fashion photography.`,
    multi_scene:  `${base} SPLIT-SCREEN divided by a clean white vertical line at center. LEFT HALF – cozy warm home interior, soft diffused lighting, relaxed lounging setting. RIGHT HALF – bright outdoor park, abundant natural sunlight, vibrant outdoor context. Same product in both halves, keep top-center and bottom corners lighter for text overlay.`,
  };
  return map[typeId]||base;
}

async function callClaude(messages, system="") {
  const body = { model:"claude-sonnet-4-20250514", max_tokens:1000, messages };
  if (system) body.system = system;
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)
  });
  return (await r.json()).content?.map(b=>b.text||"").join("")||"";
}

const P = "#6c63ff";
const card = { background:"#fff", borderRadius:16, padding:24, boxShadow:"0 2px 12px rgba(0,0,0,0.07)" };

export default function App() {
  const [step, setStep] = useState("config");
  const [keys, setKeys] = useState(() => {
    try { return JSON.parse(localStorage.getItem("ecommerce_img_keys") || "{}"); } catch { return {}; }
  });
  const [showCfg, setShowCfg] = useState(false);
  const [imgB64, setImgB64] = useState(null);
  const [imgPrev, setImgPrev] = useState(null);
  const [note, setNote] = useState("");
  const [product, setProduct] = useState(null);
  const [editIdx, setEditIdx] = useState(null);
  const [provId, setProvId] = useState(null);
  const [lang, setLang] = useState(() => localStorage.getItem("ecommerce_img_lang") || "en");
  const [types, setTypes] = useState(IMAGE_TYPES.map(t=>t.id));
  const [final, setFinal] = useState({});
  const [errs, setErrs] = useState({});
  const [curGen, setCurGen] = useState(null);
  const [lightbox, setLightbox] = useState(null);

  useEffect(() => {
    try { localStorage.setItem("ecommerce_img_keys", JSON.stringify(keys)); } catch {}
  }, [keys]);
  useEffect(() => {
    try { localStorage.setItem("ecommerce_img_lang", lang); } catch {}
  }, [lang]);

  const configured = PROVIDERS.filter(p=>(keys[p.id]||"").trim().length>5);

  const onFile = useCallback(file => {
    if (!file?.type.startsWith("image/")) return;
    setImgPrev(URL.createObjectURL(file));
    const fr = new FileReader();
    fr.onload = e => setImgB64(e.target.result.split(",")[1]);
    fr.readAsDataURL(file);
  }, []);

  const analyze = async () => {
    setStep("analyze");
    try {
      const sys = "Expert e-commerce product analyst. Output ONLY valid JSON, nothing else.";
      const prom = `Analyze product image${note?` with extra info:\n${note}`:""}.
Return JSON:
{"product_name_zh":"简洁中文名","product_name_en":"English Name","product_description_for_prompt":"Detailed English for AI image gen: exact colors, style, print, silhouette (max 40 words)","selling_points":[{"icon":"fabric","en_title":"Combed Cotton","zh_title":"精梳棉","en_desc":"Soft skin-friendly","zh_desc":"亲肤柔软"},{"icon":"fit","en_title":"Loose Fit","zh_title":"宽松版型","en_desc":"Free movement","zh_desc":"活动自如"},{"icon":"design","en_title":"Cute Print","zh_title":"萌趣印花","en_desc":"Adorable cartoon","zh_desc":"可爱减龄"}],"target_audience_zh":"目标人群","usage_scenes":["campus","home","outdoor"]}`;
      const msgs = imgB64 ? [{ role:"user", content:[
        { type:"image", source:{ type:"base64", media_type:"image/jpeg", data:imgB64 } },
        { type:"text", text:prom }
      ]}] : [{ role:"user", content:prom }];
      const raw = await callClaude(msgs, sys);
      setProduct(JSON.parse(raw.replace(/```json|```/g,"").trim()));
      setStep("select");
    } catch(e) { alert("分析失败: "+e.message); setStep("upload"); }
  };

  const generate = async () => {
    const prov = PROVIDERS.find(p=>p.id===provId);
    if (!prov) return;
    setStep("generate");
    const newFinal={}, newErrs={};
    for (const tid of types) {
      setCurGen(tid);
      try {
        const prompt = buildPrompt(tid, product.product_description_for_prompt, product.selling_points);
        const b64 = await prov.generate(keys[provId], prompt);
        newFinal[tid] = await applyOverlay(b64, tid, product.selling_points, lang);
      } catch(e) { newErrs[tid]=e.message; }
    }
    setFinal(newFinal); setErrs(newErrs); setCurGen(null);
    setStep("results");
  };

  const STEP_LIST = [["config","配置"],["upload","上传"],["select","配置"],["generate","生成"],["results","完成"]];
  const ORDER = ["config","upload","analyze","select","generate","results"];
  const curIdx = ORDER.indexOf(step);

  const CfgPanel = ({inline}) => (
    <div style={inline?{}:card}>
      {!inline && <>
        <div style={{fontWeight:700,fontSize:17,marginBottom:4}}>⚙️ 图像生成 API 配置</div>
        <div style={{fontSize:13,color:"#888",marginBottom:6}}>配置至少一个供应商 API Key。Key 存于浏览器 localStorage，刷新后仍有效。</div>
        <div style={{fontSize:11,color:"#bbb",marginBottom:14}}>Claude Code / CLI 环境可通过环境变量预设：<code>OPENAI_API_KEY</code> / <code>QWEN_API_KEY</code> / <code>DOUBAO_API_KEY</code> 等，详见 <code>.env.example</code></div>
      </>}
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
        {PROVIDERS.map(p=>{
          const ok=(keys[p.id]||"").trim().length>5;
          return (
            <div key={p.id} style={{border:ok?`2px solid ${P}`:"1px solid #e0e0e0",borderRadius:10,padding:14,background:ok?"#f0eeff":"#fafafa"}}>
              <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:8}}>
                <span style={{fontSize:22}}>{p.emoji}</span>
                <div><div style={{fontWeight:700,fontSize:13}}>{p.name}</div><div style={{fontSize:11,color:"#999"}}>{p.company}</div></div>
                {ok && <div style={{marginLeft:"auto",color:P,fontSize:18}}>✓</div>}
              </div>
              <input type="password" value={keys[p.id]||""} placeholder={p.keyPlaceholder}
                onChange={e=>setKeys(k=>({...k,[p.id]:e.target.value}))}
                style={{width:"100%",padding:"6px 10px",borderRadius:6,border:"1px solid #ddd",fontSize:12,boxSizing:"border-box"}} />
            </div>
          );
        })}
      </div>
      {!inline && (
        <button onClick={()=>setStep("upload")}
          style={{marginTop:16,width:"100%",padding:"13px 0",borderRadius:10,border:"none",background:`linear-gradient(135deg,${P},#a78bfa)`,color:"#fff",fontWeight:700,fontSize:15,cursor:"pointer"}}>
          {configured.length>0?`✅ 已配置 ${configured.length} 个供应商，继续 →`:"跳过，先查看演示 →"}
        </button>
      )}
    </div>
  );

  return (
    <div style={{fontFamily:"system-ui,-apple-system,sans-serif",maxWidth:860,margin:"0 auto",padding:"16px 16px 60px",background:"#f4f5fb",minHeight:"100vh"}}>
      <style>{`*{box-sizing:border-box}@keyframes spin{to{transform:rotate(360deg)}}@keyframes pulse{0%,100%{opacity:.3;transform:scale(.8)}50%{opacity:1;transform:scale(1.2)}}`}</style>

      {/* Lightbox */}
      {lightbox && (
        <div onClick={()=>setLightbox(null)} style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.88)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1000,padding:20}}>
          <div onClick={e=>e.stopPropagation()} style={{maxWidth:680,width:"100%"}}>
            <img src={`data:image/jpeg;base64,${lightbox.b64}`} alt={lightbox.name} style={{width:"100%",borderRadius:12,display:"block"}} />
            <div style={{display:"flex",gap:10,marginTop:12}}>
              <button onClick={()=>setLightbox(null)} style={{flex:1,padding:"10px 0",borderRadius:8,border:"none",background:"#555",color:"#fff",cursor:"pointer"}}>✕ 关闭</button>
              <button onClick={()=>{const a=document.createElement("a");a.href=`data:image/jpeg;base64,${lightbox.b64}`;a.download=`${lightbox.id}.jpg`;a.click();}}
                style={{flex:2,padding:"10px 0",borderRadius:8,border:"none",background:P,color:"#fff",fontWeight:700,cursor:"pointer"}}>⬇️ 下载</button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div style={{textAlign:"center",marginBottom:22}}>
        <h1 style={{fontSize:23,fontWeight:800,margin:0,color:"#1a1a2e"}}>🛍️ 电商套图生成器</h1>
        <p style={{color:"#777",fontSize:13,marginTop:5}}>AI 分析 · 多模型生图 · Canvas 文案叠加 · 一键下载</p>
        <div style={{display:"flex",justifyContent:"center",alignItems:"center",gap:4,marginTop:14,flexWrap:"wrap"}}>
          {STEP_LIST.map(([s,label],i)=>{
            const idx=ORDER.indexOf(s); const done=curIdx>idx; const active=curIdx===idx||(s==="generate"&&step==="generate");
            return (
              <div key={s} style={{display:"flex",alignItems:"center",gap:4}}>
                <div style={{width:26,height:26,borderRadius:"50%",fontSize:11,fontWeight:700,display:"flex",alignItems:"center",justifyContent:"center",background:done||active?P:"#ddd",color:done||active?"#fff":"#999"}}>
                  {done?"✓":i+1}
                </div>
                <span style={{fontSize:11,color:done||active?P:"#bbb",fontWeight:active?700:400}}>{label}</span>
                {i<4&&<div style={{width:14,height:2,background:done?P:"#ddd"}} />}
              </div>
            );
          })}
        </div>
      </div>

      {step!=="config" && (
        <div style={{textAlign:"right",marginBottom:10}}>
          <button onClick={()=>setShowCfg(x=>!x)}
            style={{padding:"5px 14px",borderRadius:20,border:`1px solid ${P}`,background:"#fff",color:P,fontSize:12,cursor:"pointer"}}>
            ⚙️ API设置 {configured.length?`(${configured.length}✓)`:"(未配置)"}
          </button>
        </div>
      )}
      {showCfg && step!=="config" && <div style={{marginBottom:14}}><CfgPanel /></div>}

      {/* CONFIG */}
      {step==="config" && <CfgPanel />}

      {/* UPLOAD */}
      {step==="upload" && (
        <div style={card}>
          <div style={{fontWeight:700,fontSize:17,marginBottom:18}}>① 上传商品图片</div>
          <div onDrop={e=>{e.preventDefault();onFile(e.dataTransfer.files[0]);}} onDragOver={e=>e.preventDefault()}
            onClick={()=>document.getElementById("fi").click()}
            style={{border:`2px dashed ${imgPrev?P:"#ccc"}`,borderRadius:12,padding:36,textAlign:"center",cursor:"pointer",background:imgPrev?"#f0eeff":"#fafafa"}}>
            <input id="fi" type="file" accept="image/*" style={{display:"none"}} onChange={e=>onFile(e.target.files[0])} />
            {imgPrev ? <>
              <img src={imgPrev} alt="" style={{maxHeight:180,maxWidth:"100%",borderRadius:8,marginBottom:8}} />
              <div style={{color:P,fontSize:13,fontWeight:600}}>✓ 已上传 · 点击更换</div>
            </> : <>
              <div style={{fontSize:42,marginBottom:10}}>📦</div>
              <div style={{color:"#555",fontSize:15}}>拖拽或点击上传商品图片</div>
              <div style={{color:"#bbb",fontSize:12,marginTop:4}}>JPG · PNG · WEBP</div>
            </>}
          </div>
          <textarea value={note} onChange={e=>setNote(e.target.value)}
            placeholder="补充信息（可选）：商品名、材质、卖点、人群..."
            style={{marginTop:14,width:"100%",height:76,padding:12,borderRadius:8,border:"1px solid #e0e0e0",fontSize:13,resize:"vertical"}} />
          <button onClick={analyze} disabled={!imgB64}
            style={{marginTop:14,width:"100%",padding:"13px 0",borderRadius:10,border:"none",background:imgB64?`linear-gradient(135deg,${P},#a78bfa)`:"#e5e5e5",color:imgB64?"#fff":"#aaa",fontWeight:700,fontSize:15,cursor:imgB64?"pointer":"not-allowed"}}>
            ✨ AI 智能分析商品 →
          </button>
        </div>
      )}

      {/* ANALYZE */}
      {step==="analyze" && (
        <div style={{...card,textAlign:"center",padding:60}}>
          <div style={{fontSize:44}}>🔍</div>
          <div style={{fontWeight:700,fontSize:17,marginTop:14}}>AI 正在分析商品...</div>
          <div style={{color:"#888",fontSize:13,marginTop:6}}>识别颜色款式材质，提炼核心卖点</div>
          <div style={{display:"flex",gap:8,justifyContent:"center",marginTop:22}}>
            {[0,1,2].map(i=><div key={i} style={{width:10,height:10,borderRadius:"50%",background:P,animation:`pulse 1s ease ${i*.2}s infinite`}} />)}
          </div>
        </div>
      )}

      {/* SELECT */}
      {step==="select" && product && (
        <div style={{display:"flex",flexDirection:"column",gap:14}}>
          {/* Product card */}
          <div style={card}>
            <div style={{display:"flex",gap:14,alignItems:"flex-start",marginBottom:16}}>
              {imgPrev && <img src={imgPrev} alt="" style={{width:76,height:76,objectFit:"cover",borderRadius:8,flexShrink:0}} />}
              <div style={{flex:1}}>
                <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap"}}>
                  <span style={{fontWeight:700,fontSize:15}}>{product.product_name_zh}</span>
                  <span style={{fontSize:11,color:P,background:"#f0eeff",padding:"2px 8px",borderRadius:10}}>AI 分析完成 ✓</span>
                </div>
                <div style={{fontSize:12,color:"#999",marginTop:2}}>{product.product_name_en}</div>
                <div style={{fontSize:12,color:"#666",marginTop:6,lineHeight:1.5,fontStyle:"italic"}}>{product.product_description_for_prompt}</div>
              </div>
            </div>
            <div style={{fontWeight:600,fontSize:13,marginBottom:10,color:"#555"}}>核心卖点（点击卡片编辑）</div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:10}}>
              {product.selling_points?.map((sp,i)=>(
                <div key={i} onClick={()=>setEditIdx(editIdx===i?null:i)}
                  style={{border:editIdx===i?`2px solid ${P}`:"1px solid #e8e8e8",borderRadius:10,padding:12,cursor:"pointer",background:editIdx===i?"#f0eeff":"#fafafa"}}>
                  <div style={{fontSize:20,marginBottom:6}}>{sp.icon==="fabric"?"🧵":sp.icon==="fit"?"👗":"🎨"}</div>
                  {editIdx===i ? (
                    <div onClick={e=>e.stopPropagation()}>
                      {["zh_title","zh_desc","en_title","en_desc"].map(k=>(
                        <input key={k} value={sp[k]||""} placeholder={k}
                          onChange={e=>{const pts=[...product.selling_points];pts[i]={...pts[i],[k]:e.target.value};setProduct({...product,selling_points:pts});}}
                          style={{width:"100%",fontSize:12,border:"1px solid #ccc",borderRadius:4,padding:"3px 6px",marginBottom:4}} />
                      ))}
                    </div>
                  ) : (
                    <>
                      <div style={{fontWeight:600,fontSize:13,color:P}}>{sp.zh_title}</div>
                      <div style={{fontSize:11,color:"#666",marginTop:2}}>{sp.zh_desc}</div>
                      <div style={{fontSize:11,color:"#aaa",marginTop:4,fontStyle:"italic"}}>{sp.en_title}</div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Provider */}
          <div style={card}>
            <div style={{fontWeight:700,fontSize:15,marginBottom:12}}>② 选择图像生成模型</div>
            {configured.length===0 && (
              <div style={{background:"#fff8e1",borderRadius:8,padding:10,fontSize:13,color:"#e65100",marginBottom:12}}>
                ⚠️ 未配置任何 API Key → 点击右上角「API设置」
              </div>
            )}
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              {PROVIDERS.map(p=>{
                const ok=(keys[p.id]||"").trim().length>5; const sel=provId===p.id;
                return (
                  <div key={p.id} onClick={()=>ok&&setProvId(p.id)}
                    style={{border:sel?`2px solid ${P}`:ok?"1px solid #ddd":"1px dashed #e8e8e8",borderRadius:10,padding:12,cursor:ok?"pointer":"default",background:sel?"#f0eeff":ok?"#fff":"#f9f9f9",opacity:ok?1:.5,display:"flex",alignItems:"center",gap:10}}>
                    <span style={{fontSize:24}}>{p.emoji}</span>
                    <div style={{flex:1}}>
                      <div style={{fontWeight:700,fontSize:13,color:sel?P:"#222"}}>{p.name}</div>
                      <div style={{fontSize:11,color:"#888"}}>{p.company}</div>
                    </div>
                    <div style={{fontSize:12,color:ok?(sel?P:"#4caf50"):"#bbb",fontWeight:600}}>
                      {ok?(sel?"✓ 选中":"可用"):"未配置"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Lang + types */}
          <div style={card}>
            <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:12}}>
              <div style={{fontWeight:700,fontSize:15}}>③ 套图类型 & 文案语言</div>
              <div style={{display:"flex",border:"1px solid #e0e0e0",borderRadius:8,overflow:"hidden"}}>
                {[["en","English"],["zh","中文"]].map(([v,l])=>(
                  <button key={v} onClick={()=>setLang(v)}
                    style={{padding:"5px 12px",border:"none",fontSize:12,cursor:"pointer",background:lang===v?P:"#fff",color:lang===v?"#fff":"#666",fontWeight:lang===v?700:400}}>
                    {l}
                  </button>
                ))}
              </div>
            </div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
              {IMAGE_TYPES.map(t=>{
                const sel=types.includes(t.id);
                return (
                  <div key={t.id} onClick={()=>setTypes(prev=>sel?prev.filter(x=>x!==t.id):[...prev,t.id])}
                    style={{padding:"10px 12px",borderRadius:8,cursor:"pointer",border:sel?`2px solid ${P}`:"1px solid #e8e8e8",background:sel?"#f0eeff":"#fafafa",display:"flex",alignItems:"center",gap:8}}>
                    <span style={{fontSize:18}}>{t.icon}</span>
                    <div style={{flex:1}}>
                      <div style={{fontSize:13,fontWeight:sel?700:400,color:sel?P:"#333"}}>{t.name}</div>
                      <div style={{fontSize:11,color:"#aaa"}}>{t.desc}</div>
                    </div>
                    {sel && <span style={{color:P,fontSize:16}}>✓</span>}
                  </div>
                );
              })}
            </div>
          </div>

          <button onClick={generate} disabled={!provId||types.length===0}
            style={{padding:"14px 0",borderRadius:12,border:"none",background:provId&&types.length?`linear-gradient(135deg,${P},#a78bfa)`:"#e5e5e5",color:provId&&types.length?"#fff":"#aaa",fontWeight:700,fontSize:15,cursor:provId&&types.length?"pointer":"not-allowed"}}>
            🎨 开始生成 {types.length} 张套图 {provId?`（${PROVIDERS.find(p=>p.id===provId)?.name}）`:""} →
          </button>
        </div>
      )}

      {/* GENERATE */}
      {step==="generate" && (
        <div style={card}>
          <div style={{fontWeight:700,fontSize:17,marginBottom:6}}>🎨 正在生成套图...</div>
          <div style={{fontSize:13,color:"#888",marginBottom:18}}>每张完成后自动叠加 Canvas 文案</div>
          <div style={{display:"flex",flexDirection:"column",gap:10}}>
            {types.map(tid=>{
              const t=IMAGE_TYPES.find(x=>x.id===tid);
              const done=!!final[tid]; const active=curGen===tid; const err=errs[tid];
              return (
                <div key={tid} style={{display:"flex",alignItems:"center",gap:12,padding:"12px 16px",borderRadius:10,border:`1px solid ${done?"#86efac":active?P:"#e5e5e5"}`,background:done?"#f0fff4":active?"#f0eeff":"#f9f9f9"}}>
                  <span style={{fontSize:20}}>{t.icon}</span>
                  <div style={{flex:1}}>
                    <div style={{fontWeight:600,fontSize:13}}>{t.name}</div>
                    {err && <div style={{fontSize:12,color:"#e53e3e",marginTop:2}}>❌ {err}</div>}
                    {active && <div style={{fontSize:11,color:P,marginTop:2}}>AI 生图中 + Canvas 叠加文案...</div>}
                  </div>
                  {active && <div style={{width:18,height:18,border:`2px solid ${P}`,borderTopColor:"transparent",borderRadius:"50%",animation:"spin 0.8s linear infinite"}} />}
                  {done && <span style={{fontSize:18}}>✅</span>}
                  {!done&&!active&&!err && <span style={{color:"#ccc"}}>···</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* RESULTS */}
      {step==="results" && (
        <div style={{display:"flex",flexDirection:"column",gap:14}}>
          <div style={{...card,textAlign:"center"}}>
            <div style={{fontSize:40}}>🎉</div>
            <div style={{fontWeight:800,fontSize:18,marginTop:10}}>套图生成完成！</div>
            <div style={{color:"#888",fontSize:13,marginTop:4}}>
              {Object.keys(final).length} 张成功 {Object.keys(errs).length>0?`· ${Object.keys(errs).length} 张失败`:""} · 含 Canvas 文案叠加
            </div>
            <div style={{display:"flex",gap:8,justifyContent:"center",marginTop:10,flexWrap:"wrap"}}>
              <span style={{fontSize:12,background:"#f0eeff",color:P,padding:"4px 12px",borderRadius:20}}>
                {PROVIDERS.find(p=>p.id===provId)?.name}
              </span>
              <span style={{fontSize:12,background:"#f0eeff",color:P,padding:"4px 12px",borderRadius:20}}>
                {lang==="en"?"English 文案":"中文文案"}
              </span>
            </div>
          </div>

          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
            {types.filter(id=>final[id]).map(tid=>{
              const t=IMAGE_TYPES.find(x=>x.id===tid);
              return (
                <div key={tid} style={{background:"#fff",borderRadius:12,overflow:"hidden",boxShadow:"0 2px 8px rgba(0,0,0,0.07)"}}>
                  <div style={{cursor:"pointer",position:"relative"}} onClick={()=>setLightbox({b64:final[tid],id:tid,name:t.name})}>
                    <img src={`data:image/jpeg;base64,${final[tid]}`} alt={t.name}
                      style={{width:"100%",aspectRatio:"1",objectFit:"cover",display:"block"}} />
                    <div style={{position:"absolute",inset:0,background:"rgba(0,0,0,0.2)",display:"flex",alignItems:"center",justifyContent:"center"}}>
                      <span style={{fontSize:28,color:"rgba(255,255,255,0.9)"}}>🔍</span>
                    </div>
                  </div>
                  <div style={{padding:"10px 12px",display:"flex",alignItems:"center",gap:8}}>
                    <span style={{fontSize:16}}>{t.icon}</span>
                    <span style={{fontWeight:600,fontSize:13,flex:1}}>{t.name}</span>
                    <button onClick={()=>setLightbox({b64:final[tid],id:tid,name:t.name})}
                      style={{padding:"4px 10px",borderRadius:6,border:`1px solid ${P}`,background:"#f0eeff",color:P,fontSize:11,cursor:"pointer"}}>预览</button>
                    <button onClick={()=>{const a=document.createElement("a");a.href=`data:image/jpeg;base64,${final[tid]}`;a.download=`${tid}.jpg`;a.click();}}
                      style={{padding:"4px 10px",borderRadius:6,border:"none",background:P,color:"#fff",fontSize:11,cursor:"pointer"}}>↓</button>
                  </div>
                </div>
              );
            })}
          </div>

          {Object.keys(errs).length>0 && (
            <div style={{...card,background:"#fff5f5"}}>
              <div style={{fontWeight:700,fontSize:14,color:"#e53e3e",marginBottom:8}}>⚠️ 失败的图片</div>
              {Object.entries(errs).map(([id,msg])=>{
                const t=IMAGE_TYPES.find(x=>x.id===id);
                return <div key={id} style={{fontSize:13,color:"#555",marginBottom:4}}><b>{t?.icon} {t?.name}</b>：{msg}</div>;
              })}
            </div>
          )}

          <div style={{display:"flex",gap:10}}>
            <button onClick={()=>{Object.entries(final).forEach(([id,b64])=>{const a=document.createElement("a");a.href=`data:image/jpeg;base64,${b64}`;a.download=`${id}.jpg`;a.click();});}}
              style={{flex:2,padding:"13px 0",borderRadius:10,border:"none",background:`linear-gradient(135deg,${P},#a78bfa)`,color:"#fff",fontWeight:700,fontSize:14,cursor:"pointer"}}>
              ⬇️ 一键下载全部 ({Object.keys(final).length}张)
            </button>
            <button onClick={()=>{setStep("upload");setFinal({});setErrs({});setProduct(null);}}
              style={{flex:1,padding:"13px 0",borderRadius:10,border:`1px solid ${P}`,background:"#fff",color:P,fontWeight:700,fontSize:14,cursor:"pointer"}}>
              重新开始
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
