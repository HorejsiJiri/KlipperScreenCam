/* Development-only integration checks; not a runtime dependency. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require(process.env.KSC_PLAYWRIGHT_MODULE||"playwright");
const root=path.resolve(__dirname,"..");
const html=fs.readFileSync(path.join(root,"web/index.html"),"utf8");
const messages=JSON.parse(fs.readFileSync(path.join(root,"locales/cs.json"),"utf8"));
const icon="data:image/svg+xml;base64,"+fs.readFileSync(path.join(root,"assets/camera.svg")).toString("base64");
const camera=(index,name="Camera "+index)=>({uid:String(index),name,
  url:"http://camera.test/stream"+index,supported:true,rotation:0});

(async()=>{
  const browser=await chromium.launch({headless:true,
    ...(process.env.KSC_BROWSER_PATH?{executablePath:process.env.KSC_BROWSER_PATH}:{})});
  try {
    const page=await browser.newPage({viewport:{width:1024,height:600}});
    const errors=[];
    page.on("pageerror",error=>errors.push(error.message));
    await page.route("http://camera.test/**",route=>route.fulfill({
      contentType:"image/png",
      body:Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=","base64"),
    }));
    await page.setContent(html);
    await page.evaluate(({messages,icon})=>{
      window.events=[];
      window.replyToStreams=true;
      window.webkit={messageHandlers:{ksc:{postMessage:value=>{
        const event=JSON.parse(value);
        events.push(event);
        if(event.action==="fps") queueMicrotask(()=>KSC.setFps({value:event.value}));
        if(event.action==="stream" && replyToStreams) queueMicrotask(()=>{
          if(event.uid===null) KSC.streamStopped({generation:event.generation});
          else KSC.streamReady({generation:event.generation,
            url:"http://camera.test/stream"+event.uid+"?session="+event.generation});
        });
      }}}};
      KSC.configure({menuWidth:410,hideNameSingle:true,hideCursor:true});
      KSC.setAppearance({messages,icons:{camera:icon,settings:icon}});
    },{messages,icon});

    await page.evaluate(data=>KSC.setCameras(data),{cameras:[camera(1),camera(2)],preferred:"2"});
    assert.equal(await page.locator("#title").textContent(),"Camera 2");
    await page.locator("#gear").click();
    assert.equal(await page.locator("#menu").evaluate(element=>element.getBoundingClientRect().top),0);
    assert.equal(await page.locator("#gear").isVisible(),false);
    await page.locator("#list .camera").first().click();
    assert.equal(await page.locator("#title").textContent(),"Camera 1");
    assert.equal(await page.locator("#menu").isVisible(),false);
    const before=await page.locator("#video").getAttribute("src");
    await page.waitForTimeout(20);
    await page.locator("#gear").click();
    await page.locator("#list .camera").first().click();
    assert.notEqual(await page.locator("#video").getAttribute("src"),before);

    await page.locator("#gear").click();
    const order=await page.locator("#menu").evaluate(menu=>{
      const ids=["list","stream-toggle","fps-label","fps-stats","fps-options"];
      return [...menu.querySelectorAll("[id]")].map(node=>node.id).filter(id=>ids.includes(id));
    });
    assert.deepEqual(order,["list","stream-toggle","fps-label","fps-stats","fps-options"]);
    for(const [configured,expected] of [[15,["10","15","20","30","unlimited"]],
        [20,["10","20","30","unlimited"]],[null,["10","20","30","unlimited"]],
        [120,["10","20","30","120","unlimited"]]]) {
      await page.evaluate(value=>KSC.configure({maxFps:value,configuredMaxFps:value}),configured);
      assert.deepEqual(await page.locator("#fps-options button").evaluateAll(buttons=>buttons.map(b=>b.dataset.fps)),expected);
      const rects=await page.locator("#fps-options button").evaluateAll(buttons=>buttons.map(b=>{
        const r=b.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,right:r.right};
      }));
      assert.ok(rects.slice(0,3).every(r=>r.y===rects[0].y));
      assert.ok(rects.slice(3).every(r=>r.y===rects[3].y && r.y>rects[0].y));
      assert.ok(rects.slice(0,-1).every(r=>Math.abs(r.width-rects[0].width)<1));
      assert.ok(Math.abs(rects.at(-1).right-rects[2].right)<1);
      assert.equal(await page.locator("#fps-options [aria-pressed=true]").count(),1);
    }
    await page.evaluate(()=>KSC.configure({maxFps:15,configuredMaxFps:15}));
    assert.equal(await page.locator("#stream-toggle").evaluate(b=>getComputedStyle(b).color),"rgb(239, 83, 80)");
    assert.equal(await page.locator("#toggle-slash").isVisible(),true);
    await page.locator('[data-fps="15"]').click();
    assert.equal(await page.locator('[data-fps="15"]').getAttribute("aria-pressed"),"true");
    await page.locator("#close").click();

    const fpsSource=await page.locator("#video").getAttribute("src");
    const streamCount=await page.evaluate(()=>events.filter(event=>event.action==="stream").length);
    await page.locator("#gear").click();
    for(const value of ["10","20","30","unlimited"]) {
      await page.locator(`[data-fps="${value}"]`).click();
      assert.equal(await page.locator(`[data-fps="${value}"]`).getAttribute("aria-pressed"),"true");
      assert.equal(await page.locator("#fps-options [aria-pressed='true']").count(),1);
      assert.equal(await page.locator("#video").getAttribute("src"),fpsSource);
      assert.equal(await page.locator("#menu").isVisible(),true);
    }
    assert.equal(await page.evaluate(()=>events.filter(event=>event.action==="stream").length),streamCount);
    assert.equal(await page.locator("#fps-label").textContent(),"Limity snímků:");
    await page.evaluate(()=>KSC.setStreamStats({sourceFps:29.7,forwardedFps:10.1,maxFps:10}));
    assert.equal(await page.locator("#fps-stats").textContent(),"Zdroj: 30 FPS · Předáváno: 10 FPS");
    await page.evaluate(()=>KSC.setStreamStats({sourceFps:14.4,forwardedFps:14.5,maxFps:10}));
    assert.equal(await page.locator("#fps-stats").textContent(),"Zdroj: 14 FPS · Předáváno: 15 FPS");
    assert.equal(await page.locator('[data-fps="10"]').getAttribute("aria-pressed"),"true");
    assert.equal(await page.locator("#video").getAttribute("src"),fpsSource);
    await page.locator("#close").click();

    await page.evaluate(()=>{ window.replyToStreams=false; });
    await page.locator("#gear").click();
    await page.locator("#stream-toggle").click();
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    assert.equal(await page.locator("#paused").isVisible(),false);
    await page.evaluate(()=>{
      const stop=events.filter(event=>event.action==="stream").at(-1);
      if(stop.uid!==null) throw Error("Pause did not ask the host to close the stream");
      KSC.streamStopped({generation:stop.generation});
      window.replyToStreams=true;
    });
    assert.equal(await page.locator("#paused").isVisible(),true);
    assert.equal(await page.locator("#pause-label").textContent(),"Obraz vypnut");
    await page.locator("#gear").click();
    await page.locator('[data-fps="10"]').click();
    assert.equal(await page.locator("#paused").isVisible(),true);
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    await page.locator("#close").click();
    await page.locator("#gear").click();
    assert.equal(await page.locator("#toggle-label").textContent(),"Zapnout obraz");
    assert.equal(await page.locator("#toggle-slash").isVisible(),false);
    await page.locator("#stream-toggle").click();
    assert.ok(await page.locator("#video").getAttribute("src"));

    await page.locator("#gear").click();
    await page.locator("#stream-toggle").click();
    await page.locator("#gear").click();
    await page.locator("#list .camera").first().click();
    assert.ok(await page.locator("#video").getAttribute("src"));
    assert.equal(await page.locator("#paused").isVisible(),false);

    await page.evaluate(data=>KSC.setCameras(data),{cameras:[camera(1)],preferred:"1"});
    assert.equal(await page.locator("#title").isVisible(),false);
    assert.equal(await page.locator("#gear").isVisible(),true);

    const list=Array.from({length:12},(_,index)=>camera(index,
      index===3?"Velmi dlouhý název kamery ".repeat(12):"Kamera "+index));
    await page.evaluate(data=>KSC.setCameras(data),{cameras:list,preferred:"0"});
    await page.locator("#gear").click();
    const dimensions=await page.locator("#menu").evaluate(menu=>({
      width:menu.getBoundingClientRect().width,height:menu.getBoundingClientRect().height,
      scroll:menu.scrollHeight,client:menu.clientHeight,
      heights:[...menu.querySelectorAll("#list .camera")].map(button=>button.getBoundingClientRect().height),
    }));
    assert.ok(dimensions.width>=410 && dimensions.width<=1024);
    assert.ok(dimensions.height<=600);
    assert.ok(dimensions.scroll>dimensions.client);
    assert.ok(dimensions.heights.every(height=>height===dimensions.heights[0]));
    await page.locator("#list .camera").last().scrollIntoViewIfNeeded();
    await page.locator("#list .camera").last().click();
    assert.equal(await page.locator("#title").textContent(),"Kamera 11");

    const source=await page.locator("#video").getAttribute("src");
    await page.evaluate(()=>KSC.setAppearance({colors:{bg:"rgb(0, 43, 54)",text:"rgb(253, 246, 227)"}}));
    assert.equal(await page.locator("#video").getAttribute("src"),source);
    assert.equal(await page.locator("#menu").evaluate(element=>getComputedStyle(element).backgroundColor),"rgb(0, 43, 54)");
    assert.equal(await page.locator("#gear").evaluate(element=>getComputedStyle(element).cursor),"none");

    await page.evaluate(data=>KSC.setCameras(data),{cameras:[camera(1,"<img src=x onerror=alert(1)>")],preferred:"1"});
    assert.equal(await page.locator("#title img").count(),0);

    const languageSource=await page.locator("#video").getAttribute("src");
    for(const filename of fs.readdirSync(path.join(root,"locales")).filter(name=>name.endsWith(".json"))) {
      const translation=JSON.parse(fs.readFileSync(path.join(root,"locales",filename),"utf8"));
      await page.evaluate(data=>KSC.setAppearance(data),{messages:translation,language:translation._meta.code.replaceAll("_","-")});
      assert.equal(await page.locator("#menu-title").textContent(),translation.menu_title);
      assert.equal(await page.locator("[data-fps=unlimited]").textContent(),translation.fps_unlimited);
      assert.ok((await page.locator("#fps-label").textContent()).startsWith(translation.fps_limit));
      assert.ok((await page.locator("#fps-stats").textContent()).includes(translation.fps_source));
      assert.ok((await page.locator("#fps-stats").textContent()).includes(translation.fps_forwarded));
      assert.equal(await page.locator("#menu").getAttribute("dir"),translation._meta.direction||"ltr");
      assert.equal(await page.locator("#video").getAttribute("src"),languageSource);
    }
    const arabic=JSON.parse(fs.readFileSync(path.join(root,"locales/ar.json"),"utf8"));
    await page.evaluate(({data,cameras})=>{
      KSC.setAppearance({messages:data,language:"ar"});
      KSC.setCameras({cameras,preferred:"1"});
    },{data:arabic,cameras:[camera(1,"الكاميرا الأولى"),camera(2,"الكاميرا الثانية")]});
    await page.locator("#gear").click();
    assert.equal(await page.locator("#menu").evaluate(element=>getComputedStyle(element).direction),"rtl");
    const positions=await page.locator("#list .camera").first().evaluate(button=>({
      image:button.querySelector("img").getBoundingClientRect().x,
      label:button.querySelector("span").getBoundingClientRect().x,
    }));
    assert.ok(positions.image>positions.label);
    await page.locator("#close").click();
    await page.evaluate(data=>KSC.setAppearance({messages:data,language:"cs"}),messages);

    await page.evaluate(data=>{
      KSC.configure({startPaused:true});
      KSC.setCameras(data);
    },{cameras:[camera(1)],preferred:"1"});
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    assert.equal(await page.locator("#paused").isVisible(),true);
    // DPMS sleep is separate from manual pause and must invalidate late replies.
    await page.evaluate(data=>{
      KSC.configure({startPaused:false,displaySleeping:false,maxFps:20,configuredMaxFps:15});
      KSC.setCameras(data);
    },{cameras:[camera(1),camera(2)],preferred:"2"});
    assert.ok(await page.locator("#video").getAttribute("src"));
    const preSleep=await page.evaluate(()=>events.filter(e=>e.action==="stream").at(-1));
    await page.evaluate(()=>KSC.setDisplayPower({sleeping:true}));
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    await page.evaluate(generation=>KSC.streamReady({generation,url:"http://camera.test/stale"}),preSleep.generation);
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    const sleepingCount=await page.evaluate(()=>events.filter(e=>e.action==="stream").length);
    await page.evaluate(()=>document.querySelector("#video").dispatchEvent(new Event("error")));
    await page.waitForTimeout(30);
    assert.equal(await page.evaluate(()=>events.filter(e=>e.action==="stream").length),sleepingCount);
    await page.evaluate(()=>KSC.setDisplayPower({sleeping:false}));
    assert.ok((await page.locator("#video").getAttribute("src")).includes("stream2"));
    await page.locator("#gear").click();
    assert.equal(await page.locator('[data-fps="20"]').getAttribute("aria-pressed"),"true");
    await page.locator("#stream-toggle").click();
    assert.equal(await page.locator("#paused").isVisible(),true);
    await page.evaluate(()=>{KSC.setDisplayPower({sleeping:true});KSC.setDisplayPower({sleeping:false});});
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    assert.equal(await page.locator("#paused").isVisible(),true);
    // Starting the renderer while asleep must not connect until actual wake-up.
    await page.evaluate(data=>{
      KSC.configure({startPaused:false,displaySleeping:true});
      KSC.setCameras(data);
    },{cameras:[camera(1)],preferred:"1"});
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    await page.evaluate(()=>KSC.setDisplayPower({sleeping:false}));
    assert.ok(await page.locator("#video").getAttribute("src"));
    if(process.env.KSC_UI_SCREENSHOT) {
      await page.evaluate(({messages,cameras})=>{
        KSC.configure({startPaused:false,maxFps:15,configuredMaxFps:15});
        KSC.setAppearance({messages,language:"cs"});
        KSC.setCameras({cameras,preferred:"1"});
        KSC.setStreamStats({sourceFps:30,forwardedFps:15,maxFps:15});
      },{messages,cameras:[camera(1,"Tryska"),camera(2,"Celá tiskárna")]});
      await page.locator("#gear").click();
      await page.locator("#menu").screenshot({path:process.env.KSC_UI_SCREENSHOT});
    }
    assert.deepEqual(errors,[]);
    console.log("UI checks passed: DPMS sleep/wake and manual pause, live FPS/unlimited, paused FPS changes, selection, reconnect, pause/resume, single camera, scrolling, long labels, theme, escaped names, all locales and RTL.");
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
