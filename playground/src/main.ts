import { Client } from './client.js';
import { type FormResult, isMode, type Mode } from './protocol.js';
import type { Draft } from './storage.js';

declare global {
  interface JQuery {
    importTags(value: string): JQuery;
  }
}

const root: HTMLElement | null = document.querySelector('[data-playground]');

function required<T extends HTMLElement>(selector: string): T {
  const element: T | null = document.querySelector<T>(selector);
  if (!element) throw new Error(`Missing example element: ${selector}`);
  return element;
}

async function mount(): Promise<void> {
  const form: HTMLFormElement = required('#tag-form');
  const field: HTMLElement = required('#tag-field');
  const status: HTMLElement = required('#status');
  const saved: HTMLElement = required('#saved-tags');
  const errors: HTMLElement = required('#errors');
  const start: HTMLButtonElement = required('#start');
  const temporary: HTMLButtonElement = required('#temporary');
  const reset: HTMLButtonElement = required('#reset');
  const modeInput: HTMLSelectElement = required('#mode');
  const client: Client = new Client();
  let mode: Mode = 'create';
  let busy: boolean = false;
  let rendering: boolean = false;
  let draftQueue: Promise<void> = Promise.resolve();
  let suggestionId: number = 0;

  function failure(error: unknown): void {
    status.textContent = error instanceof Error ? error.message : String(error);
    start.textContent = 'Retry';
    start.hidden = false;
    start.disabled = false;
    temporary.hidden = false;
    temporary.disabled = false;
    reset.hidden = !client.store.persistent;
  }

  function setBusy(value: boolean): void {
    busy = value;
    form.setAttribute('aria-busy', String(value));
    for (const button of form.querySelectorAll<HTMLButtonElement>('button'))
      button.disabled = value;
    for (const input of field.querySelectorAll<HTMLInputElement>('input'))
      input.disabled = value;
    field.style.pointerEvents = value ? 'none' : '';
    modeInput.disabled = value;
    reset.disabled = value;
  }

  async function render(result: FormResult): Promise<void> {
    rendering = true;
    try {
      // Django escapes submitted values before rendering this trusted template.
      jQuery(field).html(result.field_html);
      await new Promise<void>((resolve): void => {
        jQuery((): void => resolve());
      });
      saved.replaceChildren(
        ...result.stored.map((label: string): HTMLLIElement => {
          const item: HTMLLIElement = document.createElement('li');
          item.textContent = label;
          return item;
        }),
      );
      errors.textContent = Object.values(result.errors).flat().join(' ');
      const draft: Draft | undefined = await client.draft(mode);
      if (draft !== undefined) restoreDraft(draft);
    } finally {
      rendering = false;
    }
    setBusy(busy);
  }

  function currentDraft(): Draft {
    return {
      tags:
        field.querySelector<HTMLInputElement>(
          'input[name]:not([name$="_incomplete"]):not([name$="_default"])',
        )?.value ?? '',
      incomplete:
        field.querySelector<HTMLInputElement>('.tagsinput input')?.value ?? '',
    };
  }

  function restoreDraft(draft: Draft): void {
    jQuery(field)
      .find('input[name]:not([name$="_incomplete"]):not([name$="_default"])')
      .first()
      .importTags(draft.tags);
    const input: HTMLInputElement | null =
      field.querySelector('.tagsinput input');
    if (input) input.value = draft.incomplete;
  }

  async function perform(action: 'load' | 'save' | 'reset'): Promise<boolean> {
    if (busy) return false;
    setBusy(true);
    try {
      await draftQueue;
      const input: HTMLInputElement | null = field.querySelector(
        'input[name]:not([name$="_incomplete"]):not([name$="_default"])',
      );
      const incomplete: HTMLInputElement | null =
        field.querySelector('.tagsinput input');
      const values: string = [input?.value ?? '', incomplete?.value ?? '']
        .filter(Boolean)
        .join(',');
      const result: FormResult | string[] = await client.dispatch(
        action === 'save' ? { action, mode, values } : { action, mode },
      );
      if (Array.isArray(result)) throw new Error('Expected a Django form.');
      await render(result);
      start.hidden = true;
      temporary.hidden = true;
      status.textContent = Object.keys(result.errors).length
        ? 'Django rejected these values. Your saved tags have not changed.'
        : action === 'save'
          ? 'Saved. Reload the page to check the order.'
          : 'Ready. Add tags, then save.';
      return true;
    } catch (error: unknown) {
      failure(error);
      return false;
    } finally {
      setBusy(false);
    }
  }

  jQuery.ajaxTransport(
    '+json',
    (options: JQuery.AjaxSettings): JQuery.Transport | undefined => {
      if (!options.url?.includes('/tags-input/')) return undefined;
      const requestId: number = ++suggestionId;
      let cancelled: boolean = false;
      return {
        send(
          _headers: Record<string, string>,
          complete: JQuery.Transport.SuccessCallback,
        ): void {
          const url: URL = new URL(options.url ?? '', location.href);
          void client
            .dispatch({
              action: 'suggest',
              mode,
              term: url.searchParams.get('term') ?? '',
            })
            .then((result: FormResult | string[]): void => {
              if (!cancelled)
                complete(200, 'success', {
                  json: requestId === suggestionId ? result : [],
                });
            })
            .catch((error: unknown): void => {
              if (!cancelled) {
                failure(error);
                complete(500, 'error');
              }
            });
        },
        abort(): void {
          cancelled = true;
        },
      };
    },
  );

  jQuery(field).on('input change', 'input', (): void => {
    if (rendering || busy) return;
    const value: Draft = currentDraft();
    const epoch: string = client.epoch;
    const selectedMode: Mode = mode;
    draftQueue = draftQueue
      .then(
        async (): Promise<void> =>
          client.store.draft(selectedMode, value, epoch),
      )
      .catch(failure);
  });

  async function initialise(useTemporary?: boolean): Promise<void> {
    const preserved: Draft | undefined = field.childElementCount
      ? currentDraft()
      : undefined;
    setBusy(true);
    start.disabled = true;
    temporary.disabled = true;
    status.textContent =
      'Downloading Python and Django. The first start may take a minute.';
    try {
      await client.start(useTemporary);
      required('#storage-status').textContent = client.store.persistent
        ? 'Saved in this browser. Shared across these documentation pages.'
        : 'Temporary session. Changes disappear when this page closes.';
      form.hidden = false;
      reset.hidden = false;
      start.hidden = true;
      temporary.hidden = true;
      setBusy(false);
      if (!(await perform('load'))) return;
      if (preserved) {
        rendering = true;
        try {
          restoreDraft(preserved);
        } finally {
          rendering = false;
        }
        await client.store.draft(mode, preserved, client.epoch);
      }
    } catch (error: unknown) {
      setBusy(false);
      failure(error);
      start.textContent = 'Retry';
      start.disabled = false;
      temporary.hidden = false;
      temporary.disabled = false;
    }
  }

  start.addEventListener('click', (): void => {
    void initialise();
  });
  temporary.addEventListener('click', (): void => {
    void initialise(true);
  });
  form.addEventListener('submit', (event: SubmitEvent): void => {
    event.preventDefault();
    void perform('save');
  });
  reset.addEventListener('click', (): void => {
    void perform('reset');
  });
  modeInput.addEventListener('change', (): void => {
    if (isMode(modeInput.value)) {
      suggestionId += 1;
      mode = modeInput.value;
      void perform('load');
    }
  });
}

if (root) void mount();
