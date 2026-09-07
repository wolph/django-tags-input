import { expect, type Page, test } from '@playwright/test';

async function start(page: Page): Promise<void> {
  await page.goto('/_static/playground/index.html');
  await page.locator('#start').click();
  await expect(page.locator('#status')).toHaveText(
    'Ready. Add tags, then save.',
    { timeout: 150_000 },
  );
}

test('real Django saves new tags in order and restores them', async ({
  page,
}): Promise<void> => {
  const leaked: string[] = [];
  page.on('request', (request): void => {
    if (
      `${request.url()} ${request.postData() ?? ''}`.includes('BrowserOnlySpam')
    )
      leaked.push(request.url());
  });
  await start(page);
  await page.locator('#id_tags_tags_input_tag').fill('BrowserOnlySpam');
  await page.locator('#id_tags_tags_input_tag').press('Enter');
  await page.getByRole('button', { name: 'Save with Django' }).click();
  await expect(page.locator('#status')).toContainText('Saved.');
  await expect(page.locator('#saved-tags')).toContainText('BrowserOnlySpam');
  const order: string[] = await page
    .locator('#saved-tags li')
    .allTextContents();
  await start(page);
  await expect(page.locator('#saved-tags li')).toHaveText(order);
  expect(leaked).toEqual([]);
});

test('autocomplete is served by Django in the worker', async ({
  page,
}): Promise<void> => {
  await start(page);
  await page.locator('#mode').selectOption('composite');
  await expect(page.locator('#id_contacts_tags_input_tag')).toBeVisible();
  await page.locator('#id_contacts_tags_input_tag').fill('Ada');
  await expect(page.locator('.ui-menu-item')).toContainText(['Ada - Lovelace']);
});

test('every initial has suggestions in all demo modes', async ({
  page,
}): Promise<void> => {
  await start(page);
  for (const mode of ['create', 'existing', 'composite']) {
    await page.locator('#mode').selectOption(mode);
    await expect(page.locator('#status')).toHaveText(
      'Ready. Add tags, then save.',
    );
    for (const letter of 'abcdefghijklmnopqrstuvwxyz') {
      await page.locator('.tagsinput input').fill(letter);
      await expect(
        page
          .locator('.ui-menu-item')
          .filter({
            hasText: new RegExp(`^${letter}`, 'i'),
          })
          .first(),
      ).toBeVisible();
    }
  }
});
