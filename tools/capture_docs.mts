/** Capture real documentation and form interactions from local servers. */
import { mkdirSync } from 'node:fs';
import { chromium, type Browser, type BrowserContext, type Page, type ConsoleMessage } from '../playground/node_modules/playwright/index.mjs';

const output: string = new URL('../docs/_build/visual/', import.meta.url).pathname;
const assets: string = new URL('../docs/_static/', import.meta.url).pathname;
mkdirSync(output, { recursive: true });
const browser: Browser = await chromium.launch();
const context: BrowserContext = await browser.newContext({
  viewport: { width: 960, height: 1000 },
  recordVideo: { dir: output, size: { width: 960, height: 1000 } },
});
let page: Page = await context.newPage();
const errors: string[] = [];
page.on('pageerror', (error: Error): void => { errors.push(error.message); });
page.on('console', (message: ConsoleMessage): void => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:8779/_static/playground/index.html');
await page.locator('#start').click();
await page.waitForFunction((): boolean => document.querySelector('#status')?.textContent === 'Ready. Add tags, then save.', undefined, { timeout: 150_000 });
await page.locator('#id_tags_tags_input_tag').fill('Post');
await page.locator('.ui-menu-item').waitFor();
await page.screenshot({ path: `${assets}form-demo.png`, fullPage: true });
await page.locator('.ui-menu-item').first().click();
await page.getByRole('button', { name: 'Save with Django' }).click();
await page.waitForFunction((): boolean => document.querySelector('#status')?.textContent?.startsWith('Saved.') === true);
await page.screenshot({ path: `${assets}saved-order.png`, fullPage: true });
await page.close();
await page.video()?.saveAs(`${assets}form-demo.webm`);
page = await context.newPage();
page.on('pageerror', (error: Error): void => { errors.push(error.message); });
page.on('console', (message: ConsoleMessage): void => { if (message.type() === 'error') errors.push(message.text()); });
await page.goto('http://127.0.0.1:8779/_static/playground/index.html');
await page.locator('#start').click();
await page.waitForFunction((): boolean => document.querySelector('#status')?.textContent === 'Ready. Add tags, then save.', undefined, { timeout: 150_000 });
for (const width of [1280, 768, 375]) {
  await page.setViewportSize({ width, height: 950 });
  await page.screenshot({ path: `${output}interactive-${width}.png`, fullPage: true });
  await page.locator('.editor').screenshot({ path: `${output}editor-${width}.png` });
  await page.locator('.stored').screenshot({ path: `${output}stored-${width}.png` });
  const overflow: boolean = await page.evaluate((): boolean => document.documentElement.scrollWidth > innerWidth);
  if (overflow) throw new Error(`Playground overflows at ${width}px`);
  for (const route of ['index', 'playground', 'forms', 'ordering', 'configuration', 'admin', 'example-project', 'getting-started']) {
    const docs: Page = await context.newPage();
    docs.on('pageerror', (error: Error): void => { errors.push(error.message); });
    docs.on('console', (message: ConsoleMessage): void => { if (message.type() === 'error') errors.push(message.text()); });
    await docs.setViewportSize({ width, height: 950 });
    await docs.goto(`http://127.0.0.1:8779/${route}.html`);
    await docs.screenshot({ path: `${output}${route}-${width}.png`, fullPage: true });
    await docs.locator('h1').screenshot({ path: `${output}${route}-heading-${width}.png` });
    await docs.close();
  }
}
await page.close();
await context.close();
await browser.close();
if (errors.length) throw new Error(errors.join('\n'));
console.log('Captured forms, saved order, recording and responsive documentation. No console errors.');
