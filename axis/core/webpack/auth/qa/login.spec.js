import { logout } from '@/qaUtils'

describe('Auth tests', () => {
  test('has login button', async () => {
    await page.goto(SITE_URL)
    await logout()
    await page.waitForSelector('.fa-sign-in');
  });
  // test('has public menus', async () => {})
  // test('rejects inactive user', async () => {})
  // test('rejects unapproved user', async () => {})
  // test('sends errors to dedicated login page', async () => {})
})
