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
      window.webkit={messageHandlers:{ksc:{postMessage:value=>events.push(JSON.parse(value))}}};
      KSC.configure({menuWidth:410,hideNameSingle:true,hideCursor:true});
      KSC.setAppearance({messages,icons:{camera:icon,settings:icon}});
    },{messages,icon});

    await page.evaluate(data=>KSC.setCameras(data),{cameras:[camera(1),camera(2)],preferred:"2"});
    assert.equal(await page.locator("#title").textContent(),"Camera 2");
    await page.locator("#gear").click();
    assert.equal(await page.locator("#menu").evaluate(element=>element.getBoundingClientRect().top),0);
    assert.equal(await page.locator("#gear").isVisible(),false);
    await page.locator(".camera").first().click();
    assert.equal(await page.locator("#title").textContent(),"Camera 1");
    assert.equal(await page.locator("#menu").isVisible(),false);
    const before=await page.locator("#video").getAttribute("src");
    await page.waitForTimeout(20);
    await page.locator("#gear").click();
    await page.locator(".camera").first().click();
    assert.notEqual(await page.locator("#video").getAttribute("src"),before);

    await page.locator("#gear").click();
    await page.locator("#stream-toggle").click();
    assert.equal(await page.locator("#video").getAttribute("src"),null);
    assert.equal(await page.locator("#paused").isVisible(),true);
    assert.equal(await page.locator("#pause-label").textContent(),"Obraz vypnut");
    await page.locator("#gear").click();
    assert.equal(await page.locator("#stream-toggle").textContent(),"Zapnout obraz");
    await page.locator("#stream-toggle").click();
    assert.ok(await page.locator("#video").getAttribute("src"));

    await page.locator("#gear").click();
    await page.locator("#stream-toggle").click();
    await page.locator("#gear").click();
    await page.locator(".camera").first().click();
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
      heights:[...menu.querySelectorAll(".camera")].map(button=>button.getBoundingClientRect().height),
    }));
    assert.ok(dimensions.width>=410 && dimensions.width<=1024);
    assert.ok(dimensions.height<=600);
    assert.ok(dimensions.scroll>dimensions.client);
    assert.ok(dimensions.heights.every(height=>height===dimensions.heights[0]));
    await page.locator(".camera").last().scrollIntoViewIfNeeded();
    await page.locator(".camera").last().click();
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
    const positions=await page.locator(".camera").first().evaluate(button=>({
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
    assert.deepEqual(errors,[]);
    console.log("UI checks passed: selection, reconnect, pause/resume, single camera, scrolling, long labels, theme, escaped names, all locales and RTL.");
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
