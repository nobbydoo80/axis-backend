import { filter } from 'lodash';

export const menus = {
  COMPANIES: '.navbar-collapse > .nav > li:nth-child(1) > a',
  PLACES: '.navbar-collapse > .nav > li:nth-child(2) > a',
  TASKS: '.navbar-collapse > .nav > li:nth-child(3) > a',
  REPORTS: '.navbar-collapse > .nav > li:nth-child(4) > a',
  RESOURCES: '.navbar-collapse > .nav > li:nth-child(5) > a',
  SUPPORT: '.navbar-collapse > .nav > li:nth-child(6) > a',
}
export const publicMenus = {
  HOME: '.navbar-collapse > .nav > li:nth-child(1) > a',
  PRODUCTS: '.navbar-collapse > .nav > li:nth-child(2) > a',
  PRICING: '.navbar-collapse > .nav > li:nth-child(3) > a',
  NEWS: '.navbar-collapse > .nav > li:nth-child(4) > a',
  ABOUT: '.navbar-collapse > .nav > li:nth-child(5) > a',
  CONTACT: '.navbar-collapse > .nav > li:nth-child(6) > a',
}

const impersonateIcon = '.fa-shield'

export async function login(username, password) {
  if (password === undefined) {
    password = 'password'
  }
  const icon = '.btn-group > span.sign-in > a'
  const inputUsername = '[login] > form input[placeholder="Email Address or Username"]'
  const inputPassword = '[login] > form input[type="password"]'
  const submit = '[login] > form button[type="submit"]'

  await page.goto(SITE_URL)
  if (await page.$(icon) === null) {
    await logout()
  }
  await page.waitForSelector(icon)
  await page.click(icon)
  await page.waitForSelector(inputUsername)
  await page.type(inputUsername, username)
  await page.type(inputPassword, password)
  await page.click(submit)
  await page.waitForNavigation()
}

export async function logout() {
  const icon = 'a#logout'

  if (await page.$(impersonateIcon) !== null) {
    await page.click(impersonateIcon)
    await page.waitForSelector(icon, { visible: true })
  }
  if (await page.$(icon) !== null) {
    await page.click(icon)
  }
}

export async function impersonate(username) {
  const icon = impersonateIcon;
  const input = '.navbar-right > .dropdown.open > form input[typeahead]'
  const submit = '.navbar-right > .dropdown.open > form button[type="submit"]'

  if (await page.$(icon) === null) {
    await login(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
  }
  await page.waitForSelector(icon, { visible: true })
  await page.click(icon)
  await page.click(input)
  await page.type(input, username)
  await page.keyboard.press('Enter')
  await page.click(submit)
}

export async function impersonateType(company_type) {
  // Obtain a list of viable users
  await login(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
  const username = await page.evaulate(() => {
    var app = angular.element($('[ng-app="axis"]'))
    var Impersonate = app.injector().get('Impersonate')
    return Promise.resolve(filter(Impersonate.all(), { company_type })[0])
  })
  impersonate(username)
}

export async function hasMenuLink(menu, url) {
  await page.click(menu)
  const item = await page.$(`.nav > .dropdown.open > .dropdown-menu a[href="${url}"]`)
  return item
}
