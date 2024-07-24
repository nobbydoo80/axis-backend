import { impersonate, menus, hasMenuLink } from '@/qaUtils'
import settings from './settings'

describe("Enrollment menu item ", () => {
  test('has enrollments list menu item', async (done) => {
    await impersonate(settings.enrolleeUsername)
    const item = await hasMenuLink(menus.TASKS, settings.ENROLLEE_URL)
    await item.click()
    done()
  })
})
