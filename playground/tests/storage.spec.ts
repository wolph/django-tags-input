import { expect, type Page, test } from '@playwright/test';
import type { Snapshot, Store } from '../src/storage.js';

declare global {
  interface Window {
    store: Store;
  }
}

async function loadStore(page: Page): Promise<void> {
  await page.goto('/');
  await page.evaluate(async (): Promise<void> => {
    // The emitted module is loaded exactly as it is by the documentation.
    const url: string = '/_static/playground/storage.js';
    const module: typeof import('../src/storage.js') = await import(url);
    const store: Store = new module.Store();
    await store.open();
    window.store = store;
  });
}

test('SQLite bytes and drafts survive navigation', async ({
  page,
}): Promise<void> => {
  await loadStore(page);
  await page.evaluate(async (): Promise<void> => {
    const store: Store = window.store;
    await store.locked(async (): Promise<void> => {
      const snapshot: Snapshot = await store.read();
      snapshot.database = new Uint8Array([0, 127, 255]);
      snapshot.drafts.create = { tags: 'Python,Redis', incomplete: 'part' };
      await store.write(snapshot);
    });
  });
  await loadStore(page);
  const saved: { bytes: number[]; draft: Snapshot['drafts']['create'] } =
    await page.evaluate(async () => {
      const store: Store = window.store;
      return store.locked(async () => {
        const snapshot: Snapshot = await store.read();
        return {
          bytes: Array.from(snapshot.database ?? []),
          draft: snapshot.drafts.create,
        };
      });
    });
  expect(saved).toEqual({
    bytes: [0, 127, 255],
    draft: { tags: 'Python,Redis', incomplete: 'part' },
  });
});

test('reset in a second tab rejects stale drafts', async ({
  context,
  page,
}): Promise<void> => {
  await loadStore(page);
  const epoch: string = await page.evaluate(async (): Promise<string> => {
    const store: Store = window.store;
    return store.locked(
      async (): Promise<string> => (await store.read()).epoch,
    );
  });
  const second: Page = await context.newPage();
  await loadStore(second);
  await second.evaluate(async (): Promise<void> => {
    const store: Store = window.store;
    await store.locked(async (): Promise<void> => {
      await store.reset();
    });
  });
  const error: string = await page.evaluate(
    async (old: string): Promise<string> => {
      try {
        await window.store.draft(
          'create',
          { tags: 'stale', incomplete: '' },
          old,
        );
        return 'unexpected success';
      } catch (failure: unknown) {
        return String(failure);
      }
    },
    epoch,
  );
  expect(error).toContain('reset in another tab');
});
