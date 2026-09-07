export type Mode = 'create' | 'existing' | 'composite';

export interface FormResult {
  mode: Mode;
  field_html: string;
  field_name: string;
  selected: string[];
  stored: string[];
  errors: Record<string, string[]>;
}

export type Action =
  | { action: 'load'; mode: Mode }
  | { action: 'save'; mode: Mode; values: string }
  | { action: 'suggest'; mode: Mode; term: string }
  | { action: 'reset'; mode: Mode };

export type WorkerRequest =
  | { id: number; kind: 'start' }
  | {
      id: number;
      kind: 'dispatch';
      payload: Action;
      database: Uint8Array | null;
    }
  | { id: number; kind: 'stop' };

export type WorkerReply =
  | {
      id: number;
      ok: true;
      result: FormResult | string[] | null;
      database: Uint8Array | null;
    }
  | { id: number; ok: false; error: string };

export function isMode(value: unknown): value is Mode {
  return value === 'create' || value === 'existing' || value === 'composite';
}

export function isStrings(value: unknown): value is string[] {
  return (
    Array.isArray(value) &&
    value.every((item: unknown): boolean => typeof item === 'string')
  );
}

export function parseResult(value: unknown): FormResult | string[] {
  if (isStrings(value)) return value;
  if (typeof value !== 'object' || value === null)
    throw new Error('Invalid Django response.');
  const item: Record<string, unknown> = value as Record<string, unknown>;
  if (
    !isMode(item.mode) ||
    typeof item.field_html !== 'string' ||
    typeof item.field_name !== 'string' ||
    !isStrings(item.selected) ||
    !isStrings(item.stored) ||
    typeof item.errors !== 'object' ||
    item.errors === null ||
    !Object.values(item.errors).every(isStrings)
  ) {
    throw new Error('Invalid Django form response.');
  }
  return item as unknown as FormResult;
}
