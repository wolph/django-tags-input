import { expect, type Locator, type Page, test } from '@playwright/test';
import type { Client } from '../src/client.js';
import type { Snapshot, Store } from '../src/storage.js';

declare global {
  interface Window {
    client: Client;
    worker: Worker;
  }
}

async function start(page: Page): Promise<void> {
  await page.goto('/_static/playground/index.html');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
}

async function client(page: Page): Promise<void> {
  await page.goto('/');
  await page.evaluate(async (): Promise<void> => {
    const url: string = '/_static/playground/client.js';
    const module: typeof import('../src/client.js') = await import(url);
    window.client = new module.Client();
    await window.client.start();
    await window.client.dispatch({ action: 'load', mode: 'create' });
  });
}

test('incomplete draft and committed tags survive documentation navigation', async ({
  page,
}): Promise<void> => {
  await start(page);
  const input: Locator = page.locator('#tag-field .tagsinput input');
  await input.fill('DraftSpam');
  await input.press('Enter');
  await input.fill('unfinished');
  await page.locator('#mode').selectOption('existing');
  await page.locator('#mode').selectOption('create');
  await expect(input).toHaveValue('unfinished');
  await expect(page.locator('input[name=tags]')).toHaveValue(/DraftSpam/);
  await start(page);
  await expect(input).toHaveValue('unfinished');
  await expect(page.locator('input[name=tags]')).toHaveValue(/DraftSpam/);
});

test('blocked storage offers explicit temporary mode', async ({
  page,
}): Promise<void> => {
  await page.addInitScript((): void => {
    const NativeWorker: typeof Worker = Worker;
    window.Worker = class extends NativeWorker {
      constructor(url: string | URL, options?: WorkerOptions) {
        super(url, options);
        window.worker = this;
      }
    };
    IDBFactory.prototype.open = (): IDBOpenDBRequest => {
      throw new DOMException('Storage blocked', 'SecurityError');
    };
  });
  await page.goto('/_static/playground/index.html');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toContainText('Storage blocked');
  await expect(page.locator('#tag-form')).toBeHidden();
  await page.locator('#temporary').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
  await expect(page.locator('#storage-status')).toContainText(
    'Temporary session',
  );
  await page.locator('#tag-field .tagsinput input').fill('TemporaryDraft');
  await page.evaluate((): void => {
    window.worker.dispatchEvent(new ErrorEvent('error'));
  });
  await page.getByRole('button', { name: 'Save with Django' }).click();
  await expect(page.locator('#start')).toHaveText('Retry');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
  await expect(page.locator('#storage-status')).toContainText(
    'Temporary session',
  );
  await expect(page.locator('#tag-field .tagsinput input')).toHaveValue(
    'TemporaryDraft',
  );
});

test('incompatible data is retained until explicit reset', async ({
  page,
}): Promise<void> => {
  await page.goto('/');
  await page.evaluate(async (): Promise<void> => {
    const url: string = '/_static/playground/storage.js';
    const module: typeof import('../src/storage.js') = await import(url);
    const store: Store = new module.Store();
    await store.open();
    await store.write({
      schema: 999,
      epoch: 'retained',
      database: null,
      drafts: {},
    });
    store.close();
  });
  await page.goto('/_static/playground/index.html');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toContainText('incompatible format', {
    timeout: 150_000,
  });
  await expect(page.locator('#temporary')).toBeVisible();
  const retained: unknown = await page.evaluate(async (): Promise<unknown> => {
    return new Promise((resolve, reject): void => {
      const open: IDBOpenDBRequest = indexedDB.open(
        'django-tags-input-showcase',
        1,
      );
      open.onerror = (): void => reject(open.error);
      open.onsuccess = (): void => {
        const read: IDBRequest<unknown> = open.result
          .transaction('state')
          .objectStore('state')
          .get('current');
        read.onsuccess = (): void => {
          open.result.close();
          resolve(read.result);
        };
      };
    });
  });
  expect(retained).toMatchObject({ schema: 999, epoch: 'retained' });
  await page.locator('#reset').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
  );
  await expect(page.locator('#tag-field .tagsinput input')).toBeVisible();
});

test('quota failure preserves input and explicit temporary recovery', async ({
  page,
}): Promise<void> => {
  await start(page);
  await page.evaluate((): void => {
    IDBObjectStore.prototype.put = (): IDBRequest<IDBValidKey> => {
      throw new DOMException('Storage quota exhausted', 'QuotaExceededError');
    };
  });
  await page.locator('#tag-field .tagsinput input').fill('UnsavedSpam');
  await expect(page.locator('#status')).toContainText('quota');
  await page.getByRole('button', { name: 'Save with Django' }).click();
  await expect(page.locator('#status')).toContainText('quota');
  await expect(page.locator('#tag-field .tagsinput input')).toHaveValue(
    'UnsavedSpam',
  );
  await page.locator('#temporary').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
  await expect(page.locator('#tag-field .tagsinput input')).toHaveValue(
    'UnsavedSpam',
  );
});

test('startup retry replaces a failed worker and busy inputs reject edits', async ({
  page,
}): Promise<void> => {
  let attempts: number = 0;
  await page.route('**/manifest.json', async (route): Promise<void> => {
    attempts += 1;
    if (attempts === 1)
      await route.fulfill({ status: 503, body: 'Unavailable' });
    else await route.continue();
  });
  await page.goto('/_static/playground/index.html');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toContainText(
    'manifest could not be loaded',
  );
  await page.locator('#start').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
  await page.evaluate((): void => {
    const submit: HTMLButtonElement | null = document.querySelector(
      'button[type=submit]',
    );
    submit?.click();
  });
  // Capture synchronously with submission, before the worker can reply.
  const disabled: boolean = await page.evaluate((): boolean => {
    const form: HTMLFormElement | null = document.querySelector('#tag-form');
    form?.dispatchEvent(new SubmitEvent('submit', { cancelable: true }));
    return (
      document.querySelector<HTMLInputElement>('#tag-field .tagsinput input')
        ?.disabled ?? false
    );
  });
  expect(disabled).toBe(true);
  await expect(page.locator('#status')).toContainText('Saved.');
});

test('worker failure rejects pending calls and later requests without hanging', async ({
  page,
}): Promise<void> => {
  await page.addInitScript((): void => {
    const NativeWorker: typeof Worker = Worker;
    window.Worker = class extends NativeWorker {
      constructor(url: string | URL, options?: WorkerOptions) {
        super(url, options);
        window.worker = this;
      }
    };
  });
  await client(page);
  const messages: string[] = await page.evaluate(
    async (): Promise<string[]> => {
      window.worker.postMessage = (): void => {
        queueMicrotask((): void => {
          window.worker.dispatchEvent(new ErrorEvent('error'));
        });
      };
      const messages: string[] = [];
      for (let index: number = 0; index < 2; index += 1) {
        try {
          await window.client.dispatch({ action: 'load', mode: 'create' });
        } catch (error: unknown) {
          messages.push(String(error));
        }
      }
      return messages;
    },
  );
  expect(messages).toHaveLength(2);
  expect(messages[0]).toContain('worker stopped');
  expect(messages[1]).toContain('Start the example first');
});

test('concurrent tab saves use latest SQLite and stale saves fail after reset', async ({
  page,
  context,
}): Promise<void> => {
  await client(page);
  const second: Page = await context.newPage();
  await client(second);
  await Promise.all([
    page.evaluate(async (): Promise<void> => {
      await window.client.dispatch({
        action: 'save',
        mode: 'create',
        values: 'ConcurrentSpam',
      });
    }),
    second.evaluate(async (): Promise<void> => {
      await window.client.dispatch({
        action: 'save',
        mode: 'composite',
        values: 'Ada - Lovelace',
      });
    }),
  ]);
  const stored: unknown[] = await page.evaluate(
    async (): Promise<unknown[]> => {
      return Promise.all([
        window.client.dispatch({ action: 'load', mode: 'create' }),
        window.client.dispatch({ action: 'load', mode: 'composite' }),
      ]);
    },
  );
  expect(stored[0]).toMatchObject({ stored: ['ConcurrentSpam'] });
  expect(stored[1]).toMatchObject({ stored: ['Ada - Lovelace'] });
  await second.evaluate(async (): Promise<void> => {
    await window.client.dispatch({ action: 'reset', mode: 'create' });
  });
  const failure: string = await page.evaluate(async (): Promise<string> => {
    try {
      await window.client.dispatch({
        action: 'save',
        mode: 'create',
        values: 'StaleSpam',
      });
      return 'success';
    } catch (error: unknown) {
      return String(error);
    }
  });
  expect(failure).toContain('reset in another tab');
  const snapshot: Snapshot = await second.evaluate(
    async (): Promise<Snapshot> => window.client.store.read(),
  );
  expect(snapshot.drafts).toEqual({});
});

test('superseded autocomplete settles and mode changes invalidate replies', async ({
  page,
}): Promise<void> => {
  await start(page);
  const replies: unknown[] = await page.evaluate(
    async (): Promise<unknown[]> => {
      const url: string = '/_static/playground/client.js';
      const module: typeof import('../src/client.js') = await import(url);
      const original: Client['dispatch'] = module.Client.prototype.dispatch;
      module.Client.prototype.dispatch = async function (
        payload,
      ): ReturnType<Client['dispatch']> {
        if (payload.action === 'suggest')
          await new Promise<void>((resolve): void => {
            setTimeout(resolve, 100);
          });
        return original.call(this, payload);
      };
      const request: (term: string) => Promise<unknown> = (
        term: string,
      ): Promise<unknown> =>
        new Promise((resolve, reject): void => {
          jQuery.ajax({
            url: `/tags-input/?term=${term}`,
            dataType: 'json',
            success: (data: unknown): void => {
              resolve(data);
            },
            error: (): void => {
              reject(new Error('Suggestion failed'));
            },
          });
        });
      const first: Promise<unknown> = request('P');
      const second: Promise<unknown> = request('R');
      const select: HTMLSelectElement | null = document.querySelector('#mode');
      if (!select) throw new Error('Missing mode select');
      select.value = 'composite';
      select.dispatchEvent(new Event('change'));
      return Promise.all([first, second]);
    },
  );
  expect(replies).toEqual([[], []]);
  await expect(page.locator('#id_contacts_tags_input_tag')).toBeVisible();
});

test('startup timeout permits a bounded retry', async ({
  page,
}): Promise<void> => {
  await page.goto('/');
  await page.clock.install();
  const result: Promise<string> = page.evaluate(async (): Promise<string> => {
    const url: string = '/_static/playground/client.js';
    const module: typeof import('../src/client.js') = await import(url);
    const NativeWorker: typeof Worker = Worker;
    window.Worker = class extends NativeWorker {
      override postMessage(): void {}
    };
    window.client = new module.Client();
    try {
      await window.client.start(true);
      return 'unexpected success';
    } catch (error: unknown) {
      return String(error);
    }
  });
  await expect
    .poll(
      async (): Promise<boolean> =>
        page.evaluate((): boolean => Boolean(window.client)),
    )
    .toBe(true);
  await page.clock.fastForward(150_001);
  expect(await result).toContain('worker timed out');
  const stopped: string = await page.evaluate(async (): Promise<string> => {
    try {
      await window.client.dispatch({ action: 'load', mode: 'create' });
      return 'unexpected success';
    } catch (error: unknown) {
      return String(error);
    }
  });
  expect(stopped).toContain('Start the example first');
});

test('worker retries preserve temporary SQLite and every mode draft', async ({
  page,
}): Promise<void> => {
  await page.goto('/');
  const states: unknown[] = await page.evaluate(
    async (): Promise<unknown[]> => {
      const url: string = '/_static/playground/client.js';
      const module: typeof import('../src/client.js') = await import(url);
      const temporary: Client = new module.Client();
      await temporary.start(true);
      await temporary.dispatch({ action: 'load', mode: 'create' });
      await temporary.dispatch({
        action: 'save',
        mode: 'create',
        values: 'TemporarySpam',
      });
      await temporary.store.draft(
        'existing',
        { tags: 'Python', incomplete: 'Djan' },
        temporary.epoch,
      );
      await temporary.start();
      const first: unknown = await temporary.dispatch({
        action: 'load',
        mode: 'create',
      });
      const firstDraft: unknown = await temporary.draft('existing');
      const firstPersistent: boolean = temporary.store.persistent;
      await temporary.start(true);
      return [
        first,
        firstDraft,
        firstPersistent,
        await temporary.dispatch({ action: 'load', mode: 'create' }),
        await temporary.draft('existing'),
        temporary.store.persistent,
      ];
    },
  );
  expect(states).toEqual([
    expect.objectContaining({ stored: ['TemporarySpam'] }),
    { tags: 'Python', incomplete: 'Djan' },
    false,
    expect.objectContaining({ stored: ['TemporarySpam'] }),
    { tags: 'Python', incomplete: 'Djan' },
    false,
  ]);
});
